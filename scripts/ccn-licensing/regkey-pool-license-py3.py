"""
regkey-pool-license-py3.py
==========================
Python 3 port of regkey-pool-license.py.

Use this version on modern workstations or jump hosts running Python 3.
The original script (regkey-pool-license.py) uses Python 2 syntax and is
intended for execution directly on BIG-IQ appliances where Python 2 is the
system default.

Requirements
------------
    pip install requests

Usage
-----
Interactive (prompts for all values):
    python3 regkey-pool-license-py3.py

Non-interactive (read values from lic-data.json in same directory):
    # Create lic-data.json first — see lic-data.json.example
    python3 regkey-pool-license-py3.py

Output
------
On success, writes:
    <bigip-management-ip>_bigip.license

SCP that file to the BIG-IP, place it at /config/bigip.license, then:
    reloadlic

See docs/05-licensing.md#54-big-iq-pool-licensing-for-unreachable-dark-site-devices
for the full procedure.

Changes from Python 2 original
-------------------------------
- raw_input() → input()
- print statements → print() functions (already functions in original)
- urllib3 InsecureRequestWarning suppressed explicitly
- f-strings used where cleaner than .format()
- Exit on authentication failure instead of silent continue
"""

import getpass
import json
import os
import sys
import requests
import urllib3

# Suppress the SSL verification warning — BIG-IQ uses a self-signed cert by default.
# Remove this if your BIG-IQ has a valid CA-signed certificate and you pass verify=True.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BIGIQ_AUTH_PATH    = "/mgmt/shared/authn/login"
BIGIQ_LICENSE_PATH = "/mgmt/cm/device/tasks/licensing/pool/member-management"
LICENSE_WAIT_SECS  = 30


def bigiq_auth(session, bigiq_url, credentials):
    """
    Authenticate with BIG-IQ. Returns auth header dict, or None on failure.
    """
    auth_url = f"https://{bigiq_url}{BIGIQ_AUTH_PATH}"
    try:
        resp = session.post(auth_url, data=json.dumps(credentials), verify=False)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Authentication HTTP error: {err}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"Cannot reach BIG-IQ at {bigiq_url}: {err}")
        return None

    token = resp.json().get("token", {}).get("token")
    if not token:
        print("Authentication response did not contain a token.")
        return None

    print("** Completed Authentication **")
    return {"X-F5-Auth-Token": token}


def extract_license(license_json):
    """
    Extract the license text from the BIG-IQ task result.
    Returns the license string, or 'FAILED' if the task did not finish.
    """
    status = license_json.get("status", "")
    if status != "FINISHED":
        print(f"Task status: {status} — expected FINISHED")
        return "FAILED"

    license_text = license_json.get("licenseText")
    if not license_text:
        print("Task finished but licenseText was empty.")
        return "FAILED"

    print("***** License has been assigned *****")
    return license_text


def load_license_data():
    """
    Load license request payload from lic-data.json if present,
    otherwise prompt interactively.
    """
    if os.path.exists("lic-data.json"):
        print("Found lic-data.json — loading values from file.")
        with open("lic-data.json") as f:
            return json.load(f)

    bigip_address  = input("Enter Management IP address of BIG-IP to be licensed: ").strip()
    bigip_mac      = input("Enter Management MAC address of BIG-IP to be licensed: ").strip()
    pool_name      = input("Enter the name of the License Pool: ").strip()
    hypervisor     = input("Enter hypervisor (aws/azure/gce/hyperv/kvm/vmware/xen): ").strip()
    chargeback_tag = input("Optional: Enter chargeback tag (press Enter to skip): ").strip()
    tenant         = input("Optional: Enter tenant name (press Enter to skip): ").strip()

    data = {
        "licensePoolName": pool_name,
        "command":         "assign",
        "address":         bigip_address,
        "assignmentType":  "UNREACHABLE",
        "macAddress":      bigip_mac,
        "hypervisor":      hypervisor,
    }
    if chargeback_tag:
        data["chargebackTag"] = chargeback_tag
    if tenant:
        data["tenant"] = tenant

    return data


def rewrite_selflink(selflink_url, bigiq_ip):
    """
    BIG-IQ returns selfLink URLs with 'localhost' as the host.
    Rewrite to use the actual BIG-IQ management IP.
    """
    return selflink_url.replace("https://localhost/", f"https://{bigiq_ip}/")


def main():
    # ── Collect BIG-IQ credentials ──────────────────────────────────────────
    bigiq_user    = input("Enter BIG-IQ user ID: ").strip()
    bigiq_pass    = getpass.getpass("Enter BIG-IQ Password: ")
    bigiq_address = input("Enter Management IP address of BIG-IQ: ").strip()

    credentials = {
        "username":           bigiq_user,
        "password":           bigiq_pass,
        "loginProvideriName": "RadiusServer",
    }

    # ── Load BIG-IP license target data ─────────────────────────────────────
    license_payload = load_license_data()
    bigip_address   = license_payload["address"]
    print(f"BIG-IP to be licensed: {bigip_address}")

    # ── Authenticate ─────────────────────────────────────────────────────────
    session     = requests.Session()
    auth_header = bigiq_auth(session, bigiq_address, credentials)
    if auth_header is None:
        print("Unable to authenticate with BIG-IQ. Check reachability and credentials.")
        sys.exit(1)

    # ── Submit license request ───────────────────────────────────────────────
    license_url = f"https://{bigiq_address}{BIGIQ_LICENSE_PATH}"
    try:
        resp = session.post(
            license_url,
            headers=auth_header,
            data=json.dumps(license_payload),
            verify=False,
        )
        resp.raise_for_status()
        print(f"License request submitted. Response code: {resp.status_code}")
    except requests.exceptions.HTTPError as err:
        print(f"License request failed: {err}")
        sys.exit(1)

    # ── Poll for completion ───────────────────────────────────────────────────
    task_response  = resp.json()
    selflink       = task_response.get("selfLink", "")
    status_url     = rewrite_selflink(selflink, bigiq_address)
    print(f"Task URL: {status_url}")
    print(f"--- Waiting {LICENSE_WAIT_SECS} seconds for BIG-IQ to generate license ---")

    import time
    time.sleep(LICENSE_WAIT_SECS)

    try:
        status_resp = session.get(status_url, headers=auth_header, verify=False)
        status_resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Failed to retrieve license task status: {err}")
        sys.exit(1)

    # ── Extract and save license ──────────────────────────────────────────────
    license_text = extract_license(status_resp.json())

    if license_text == "FAILED":
        print(
            "***** License Assignment Failed. *****\n"
            "Most likely a valid license is already checked out for this device.\n"
            "Revoke it in BIG-IQ (License Management → Licenses → [pool] → Revoke)\n"
            "before re-running this script."
        )
        sys.exit(1)

    output_filename = f"{bigip_address}_bigip.license"
    with open(output_filename, "w") as lf:
        lf.write(license_text)

    print(license_text)
    print(f"\n***** SUCCESS — license written to: {output_filename} *****")
    print(
        f"\nNext steps:\n"
        f"  1. SCP {output_filename} to the BIG-IP\n"
        f"  2. cp /path/to/{output_filename} /config/bigip.license\n"
        f"  3. reloadlic\n"
        f"  4. tmsh show /sys license"
    )


if __name__ == "__main__":
    main()
