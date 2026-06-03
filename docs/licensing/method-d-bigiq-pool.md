# Licensing Method D — BIG-IQ Pool Licensing (Unreachable Device)

> Use when BIG-IQ Centralized Management is deployed and has internet access, but the BIG-IP being licensed cannot be reached by BIG-IQ over the network. BIG-IQ generates a license file that is manually transferred to and applied on the BIG-IP.

---

## Navigation

[← Method C: CCN](./method-c-ccn.md) | [← Licensing Overview](../05-licensing.md)

---

## When to use this method

- **BIG-IQ** is deployed and licensed (it has internet access or has synced its license pool from F5)
- The **BIG-IP** to be licensed is isolated — BIG-IQ cannot reach the BIG-IP management IP over the network
- You are using ELA, BYOL pool, or subscription licensing managed in a BIG-IQ RegKey Pool
- You can transfer a file from BIG-IQ to the BIG-IP via an approved method

> [!NOTE]
> **How this differs from the CCN Self-Service Utility (Method C):**
> Method C requires no BIG-IQ — you interact directly with F5's portal. Method D requires BIG-IQ but does not require you to interact with F5's portal at all. BIG-IQ holds the license pool and generates the license file internally.

---

## Overview

```
     BIG-IQ CM
  (has internet access,
   holds license pool)
          │
          │ 1. Engineer runs regkey-pool-license.py on BIG-IQ
          │    BIG-IQ REST API generates license file
          │
          │ 2. SCP license file from BIG-IQ to engineer workstation
          │
          ▼
  Engineer workstation
          │
          │ 3. Transfer license file to BIG-IP
          │    (SCP, approved removable media, etc.)
          ▼
     BIG-IP VE
  (isolated — no network
   path to BIG-IQ)
          │
          │ 4. Place file at /config/bigip.license
          │    Run reloadlic
          ▼
     Licensed ✓
```

---

## D.1 Prerequisites

Before starting, confirm:

- [ ] BIG-IQ Centralized Management **5.2.0 or later** is deployed and licensed
- [ ] BIG-IQ has been used to activate its own license pool (internet access used at BIG-IQ level, not BIG-IP level)
- [ ] A **RegKey Pool** has been created in BIG-IQ containing the registration key(s) for this BIG-IP
- [ ] You have BIG-IQ admin credentials
- [ ] You have the BIG-IP's **management IP address** and **management interface MAC address**
- [ ] You can SCP a file from BIG-IQ to your workstation, and from there to the BIG-IP

> [!NOTE]
> **Getting BIG-IQ License Manager:** For BIG-IQ 7.1.0 and earlier, the License Management feature is available as a free license. Download from [my.f5.com](https://my.f5.com) → Downloads → BIG-IQ. For licensing the BIG-IQ system itself, see [K15094](https://techdocs.f5.com/en-us/bigiq-8-0-0/managing-big-ip-ve-subscriptions-from-big-iq/deploy-license-iq-license-manager.html).

---

## D.2 Create a RegKey Pool in BIG-IQ (if not already done)

1. Log in to the BIG-IQ TMUI
2. Click the **Devices** tab at the top
3. In the left nav: **LICENSE MANAGEMENT → Licenses**
4. Click **Add RegKey Pool**
5. Enter a pool **Name** (e.g., `BIG-IP-VE-Pool-Lab`) → **OK**
6. Add registration keys: click **Add RegKey** or **Import CSV**

---

## D.3 Collect the BIG-IP management MAC address

The MAC address is required to generate the license. Run on the BIG-IP:

```bash
# BIG-IP v11+
tmsh show net interface mgmt all-properties | grep -i mac

# Alternative from bash shell
ip link show mgmt | grep ether
```

Record the MAC in the format `xx:xx:xx:xx:xx:xx`.

---

## D.4 The scripts

Two versions are provided — use the one that matches the Python available in your environment.

| Script | Python | Where to run |
|--------|--------|-------------|
| `regkey-pool-license.py` | Python 2 | Directly on the BIG-IQ appliance (system Python) |
| `regkey-pool-license-py3.py` | Python 3 | Modern workstation or jump host inside the network |

Both scripts are in `scripts/ccn-licensing/` in this repo.

> [!NOTE]
> **Typo fix applied:** Both scripts correct `loginProvideriName` → `loginProviderName` in the authentication payload. The extra `i` in the original causes authentication to fail against BIG-IQ instances using the default local auth provider.

---

### D.4a `regkey-pool-license.py` (Python 2 — run on BIG-IQ)

```python
import getpass
import json
import os
import requests
from time import sleep

def bigiqAuth(_bigiqAuthUrl, _bigiqCredentials):
    """Authenticate with BIG-IQ and return the auth token header dict."""
    _errFlag = 0
    try:
        _bigiqAuthInfo = _bigiq_session.post(
            _bigiqAuthUrl, data=json.dumps(_bigiqCredentials), verify=False
        )
        print(_bigiqAuthUrl)
        _bigiqAuthInfo.raise_for_status()
        print("Response code: %s" % _bigiqAuthInfo.status_code)
    except requests.exceptions.HTTPError as err:
        print(err)
        _errFlag = 1
    if _errFlag == 0:
        _bigiqResponse = _bigiqAuthInfo.json()
        _bigiqToken = _bigiqResponse['token']
        for _token in _bigiqToken:
            if _token == 'token':
                _bigiqAuthToken = _bigiqToken[_token]
        _authHeaders = {
            "X-F5-Auth-Token": "{_authToken}".format(_authToken=_bigiqAuthToken)
        }
    else:
        _authHeaders = 0
    print("** Completed Authentication ***")
    return(_authHeaders)

def extractLicense(_rawLicenseJSON):
    """Pull the generated license text from the BIG-IQ response JSON."""
    for _license in _rawLicenseJSON:
        if _license == 'licenseText':
            _extractedLicense = _rawLicenseJSON[_license]
        if _license == 'status':
            if _rawLicenseJSON[_license] == "FINISHED":
                print("***** License has been assigned *****")
            else:
                _extractedLicense = "FAILED"
    return(_extractedLicense)

def licenseData():
    """Read lic-data.json if present; otherwise prompt interactively."""
    if os.path.exists('lic-data.json'):
        with open('./lic-data.json') as licfile:
            _licdata = json.load(licfile)
    else:
        _bigipAddress    = raw_input("Enter Management IP address of BIG-IP to be licensed: ")
        _bigipMACaddress = raw_input("Enter Management MAC address of BIG-IP to be licensed: ")
        _licensePoolName = raw_input("Enter the name of the License Pool: ")
        _hypervisorType  = raw_input("Enter hypervisor (aws/azure/gce/hyperv/kvm/vmware/xen): ")
        _chargebackTag   = raw_input("Optional: Enter chargeback tag if required: ")
        _tenantTag       = raw_input("Optional: Enter tenant name if required: ")
        _licdata = {
            "licensePoolName": _licensePoolName,
            "command":         "assign",
            "address":         _bigipAddress,
            "assignmentType":  "UNREACHABLE",
            "macAddress":      _bigipMACaddress,
            "hypervisor":      _hypervisorType,
            "chargebackTag":   _chargebackTag,
            "tenant":          _tenantTag,
        }
    return(_licdata)

def urlConstruction(_bigiqUrl, _bigiqIP):
    """Rewrite selfLink URL: replace 'localhost' with the actual BIG-IQ IP."""
    _urlDeConstruct = _bigiqUrl.split("/")
    _urlReConstruct = ""
    for _urlElement in _urlDeConstruct:
        if _urlElement == "https:":
            _urlReConstruct = _urlReConstruct + _urlElement + "//"
        elif _urlElement == "localhost":
            _urlReConstruct = _urlReConstruct + _bigiqIP
        else:
            if _urlElement != "":
                _urlReConstruct = _urlReConstruct + "/" + _urlElement
    return(_urlReConstruct)

# ── Main ──────────────────────────────────────────────────────────────────────
_userID       = raw_input("Enter BIG-IQ user ID: ")
_password     = getpass.getpass(prompt="Enter BIG-IQ Password: ")
_bigiqAddress = raw_input("Enter Management IP address of BIG-IQ: ")

_credPostBody = {
    "username":          _userID,
    "password":          _password,
    "loginProviderName": "RadiusServer"   # NOTE: was loginProvideriName in original
}

_deviceToBeLicensed = licenseData()
_bigipAddress = _deviceToBeLicensed['address']
print("BIG-IP Address is:  %s" % _bigipAddress)
_bigiq_session = requests.session()

_bigiq_auth_url = "https://{_bigiqIP}/mgmt/shared/authn/login".format(_bigiqIP=_bigiqAddress)
_bigiqAuthHeader = bigiqAuth(_bigiq_auth_url, _credPostBody)

if _bigiqAuthHeader == 0:
    print("Unable to authenticate with BIG-IQ. Check BIG-IQ reachability and credentials.")
else:
    _bigiq_url1 = (
        "https://{_bigiqIP}/mgmt/cm/device/tasks/licensing/pool/member-management"
        .format(_bigiqIP=_bigiqAddress)
    )
    _errFlag = 0
    try:
        _bigiqLicenseDevice = _bigiq_session.post(
            _bigiq_url1, headers=_bigiqAuthHeader,
            data=json.dumps(_deviceToBeLicensed), verify=False
        )
        _bigiqLicenseDevice.raise_for_status()
        print("Response code: %s" % _bigiqLicenseDevice.status_code)
    except requests.exceptions.HTTPError as err:
        print("Issue received, check request and/or connectivity: %s" % err)
        _errFlag = 1

    if _errFlag == 0:
        _bigiqResponse = _bigiqLicenseDevice.json()
        _bigiqLicenseStatus_url = urlConstruction(_bigiqResponse['selfLink'], _bigiqAddress)
        print("--- Standby for 30 seconds whilst BIG-IQ generates license ---")
        sleep(30)
        try:
            _licenseStatus = _bigiq_session.get(
                _bigiqLicenseStatus_url, headers=_bigiqAuthHeader, verify=False
            )
            _licenseStatus.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Issue received: %s" % err)
            _errFlag = 1

        if _errFlag == 0:
            _licenseOutput = extractLicense(_licenseStatus.json())
            if _licenseOutput == "FAILED":
                print("***** License Assignment Failed. Revoke existing license in BIG-IQ before retrying. *****")
            else:
                _licenseFname = _bigipAddress + "_bigip.license"
                with open(_licenseFname, "w") as _lf:
                    _lf.write("%s" % _licenseOutput)
                print("***** SUCCESS — license stored at: %s *****" % _licenseFname)
```

**Copy and run:**

```bash
# Copy from this repo to BIG-IQ
scp scripts/ccn-licensing/regkey-pool-license.py admin@<bigiq-ip>:/shared/

# Run on BIG-IQ
ssh admin@<bigiq-ip>
cd /shared
python regkey-pool-license.py
```

---

### D.4b `regkey-pool-license-py3.py` (Python 3 — run on workstation or jump host)

```python
import getpass
import json
import os
import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BIGIQ_AUTH_PATH    = "/mgmt/shared/authn/login"
BIGIQ_LICENSE_PATH = "/mgmt/cm/device/tasks/licensing/pool/member-management"
LICENSE_WAIT_SECS  = 30


def bigiq_auth(session, bigiq_ip, credentials):
    """Authenticate with BIG-IQ. Returns auth header dict, or None on failure."""
    auth_url = f"https://{bigiq_ip}{BIGIQ_AUTH_PATH}"
    try:
        resp = session.post(auth_url, data=json.dumps(credentials), verify=False)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Authentication HTTP error: {err}")
        return None
    except requests.exceptions.ConnectionError as err:
        print(f"Cannot reach BIG-IQ at {bigiq_ip}: {err}")
        return None
    token = resp.json().get("token", {}).get("token")
    if not token:
        print("Authentication response did not contain a token.")
        return None
    print("** Completed Authentication **")
    return {"X-F5-Auth-Token": token}


def extract_license(license_json):
    """Extract license text from BIG-IQ task result. Returns 'FAILED' if not finished."""
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
    """Load from lic-data.json if present, otherwise prompt interactively."""
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
    """Replace 'localhost' in BIG-IQ selfLink with the actual management IP."""
    return selflink_url.replace("https://localhost/", f"https://{bigiq_ip}/")


def main():
    bigiq_user    = input("Enter BIG-IQ user ID: ").strip()
    bigiq_pass    = getpass.getpass("Enter BIG-IQ Password: ")
    bigiq_address = input("Enter Management IP address of BIG-IQ: ").strip()

    credentials = {
        "username":          bigiq_user,
        "password":          bigiq_pass,
        "loginProviderName": "RadiusServer",   # NOTE: was loginProvideriName in original
    }

    license_payload = load_license_data()
    bigip_address   = license_payload["address"]
    print(f"BIG-IP to be licensed: {bigip_address}")

    session     = requests.Session()
    auth_header = bigiq_auth(session, bigiq_address, credentials)
    if auth_header is None:
        print("Unable to authenticate with BIG-IQ. Check reachability and credentials.")
        sys.exit(1)

    license_url = f"https://{bigiq_address}{BIGIQ_LICENSE_PATH}"
    try:
        resp = session.post(
            license_url, headers=auth_header,
            data=json.dumps(license_payload), verify=False,
        )
        resp.raise_for_status()
        print(f"License request submitted. Response code: {resp.status_code}")
    except requests.exceptions.HTTPError as err:
        print(f"License request failed: {err}")
        sys.exit(1)

    status_url = rewrite_selflink(resp.json().get("selfLink", ""), bigiq_address)
    print(f"--- Waiting {LICENSE_WAIT_SECS} seconds for BIG-IQ to generate license ---")

    import time
    time.sleep(LICENSE_WAIT_SECS)

    try:
        status_resp = session.get(status_url, headers=auth_header, verify=False)
        status_resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Failed to retrieve license task status: {err}")
        sys.exit(1)

    license_text = extract_license(status_resp.json())
    if license_text == "FAILED":
        print(
            "***** License Assignment Failed. *****\n"
            "Revoke the existing license in BIG-IQ before re-running:\n"
            "  Devices → LICENSE MANAGEMENT → Licenses → [pool] → Revoke"
        )
        sys.exit(1)

    output_filename = f"{bigip_address}_bigip.license"
    with open(output_filename, "w") as lf:
        lf.write(license_text)
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
```

**Run:**

```bash
pip3 install requests
python3 scripts/ccn-licensing/regkey-pool-license-py3.py
```

---

### D.4c Interactive prompts (both scripts)

When no `lic-data.json` is present, both scripts prompt for the same values:

```
Enter BIG-IQ user ID:                          admin
Enter BIG-IQ Password:                         <bigiq-admin-password>
Enter Management IP address of BIG-IQ:         <bigiq-mgmt-ip>
Enter Management IP address of BIG-IP:         <bigip-mgmt-ip>
Enter Management MAC address of BIG-IP:        xx:xx:xx:xx:xx:xx
Enter the name of the License Pool:            BIG-IP-VE-Pool-Lab
Enter hypervisor (aws/azure/gce/hyperv/kvm/vmware/xen):  vmware
Optional: Enter chargeback tag:                <Enter to skip>
Optional: Enter tenant name:                   <Enter to skip>
```

**Hypervisor values:**

| Hypervisor | Value |
|------------|-------|
| VMware ESXi | `vmware` |
| KVM / Proxmox / Nutanix AHV | `kvm` |
| Hyper-V | `hyperv` |
| AWS | `aws` |
| Azure | `azure` |
| Google Cloud | `gce` |
| XenServer | `xen` |

The script authenticates to BIG-IQ, submits the request, waits ~30 seconds, then writes `<bigip-mgmt-ip>_bigip.license` to the current directory.

**Expected success output:**
```
***** License has been assigned *****
***** SUCCESS — license stored at: 10.1.1.10_bigip.license *****
```

> [!WARNING]
> If you see `***** License Assignment Failed *****`, a license is already checked out for that MAC address. Revoke it in BIG-IQ first (see [D.7 — Revoking a license](#d7-revoking-a-license)), then re-run.

---

## D.5 Non-interactive mode: lic-data.json

To skip interactive prompts — useful for repeat runs or automation — create a `lic-data.json` file in the same directory as the script before running.

**Minimal `lic-data.json`:**
```json
{
    "licensePoolName": "BIG-IP-VE-Pool-Lab",
    "command": "assign",
    "address": "10.1.1.10",
    "assignmentType": "UNREACHABLE",
    "macAddress": "06:ce:c2:43:b3:05",
    "hypervisor": "vmware"
}
```

**With optional chargeback and tenant tags:**
```json
{
    "licensePoolName": "BIG-IP-VE-Pool-Lab",
    "command": "assign",
    "address": "10.1.1.10",
    "assignmentType": "UNREACHABLE",
    "macAddress": "06:ce:c2:43:b3:05",
    "hypervisor": "vmware",
    "chargebackTag": "PROJ-2024",
    "tenant": "Agency-XYZ"
}
```

Example files are in `scripts/ccn-licensing/`:
- `lic-data.json.example`
- `lic-data.json.example-with-optional-fields`

> [!WARNING]
> Do not commit a populated `lic-data.json` to the repository — it contains sensitive device information. The `.gitignore` in this repo already excludes it.

---

## D.6 Transfer and apply the license file

```bash
# 1. SCP the generated license file from BIG-IQ to your workstation
scp admin@<bigiq-ip>:/shared/<bigip-ip>_bigip.license ./

# 2. Transfer the file to the BIG-IP (SCP or approved method)

# 3. On the BIG-IP — back up any existing license
cp /config/bigip.license /config/bigip.license.bak

# 4. Place the new license file
cp /path/to/<bigip-ip>_bigip.license /config/bigip.license

# 5. Reload the license daemon
reloadlic

# 6. Verify
tmsh show /sys license | grep -E "Licensed version|Registration Key|Active Modules"
```

---

## D.7 Revoking a license

Always return a license to the pool when decommissioning a BIG-IP VE to avoid pool exhaustion.

**Via TMSH on the BIG-IP (if management network path to BIG-IQ exists):**
```bash
tmsh revoke /sys license \
    bigiq-addr <bigiq-ip> \
    bigiq-user admin \
    bigiq-password <bigiq-password> \
    bigiq-port 443 \
    pool-name 'BIG-IP-VE-Pool-Lab'
```

**Via BIG-IQ TMUI (when BIG-IP is no longer reachable):**
Devices → LICENSE MANAGEMENT → Licenses → [pool name] → locate the device → **Revoke**

> [!NOTE]
> If a BIG-IP is deleted without revoking, BIG-IQ reclaims the license automatically after a grace period (default: 24 hours for unresponsive devices). Confirm the grace period with your BIG-IQ administrator.

---

## Further reading

| Resource | URL |
|----------|-----|
| K15690: Overview of BIG-IP VE licensing | https://support.f5.com/csp/article/K15690 |
| K02061834: License BIG-IP VE from BIG-IQ License Manager | https://my.f5.com/manage/s/article/K02061834 |
| BIG-IQ License Manager deployment guide | https://techdocs.f5.com/en-us/bigiq-8-0-0/managing-big-ip-ve-subscriptions-from-big-iq/deploy-license-iq-license-manager.html |
| Script reference | [scripts/ccn-licensing/README.md](../../scripts/ccn-licensing/README.md) |

---

## Done?

Proceed to **[Step 6: Module Provisioning →](../06-provisioning.md)**
