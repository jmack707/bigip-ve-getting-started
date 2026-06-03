"""
regkey-pool-license.py
======================
License an unreachable (dark-site / closed-network) BIG-IP VE using the
BIG-IQ License Manager REST API.

IMPORTANT: This script is written for Python 2, which is the Python version
available on BIG-IQ Centralized Management 5.x – 7.x. It must be run ON the
BIG-IQ appliance (or a host with Python 2 and network access to BIG-IQ).

Do NOT run this on a modern workstation with Python 3 — use
regkey-pool-license-py3.py instead.

Usage
-----
Interactive (prompts for all values):
    python regkey-pool-license.py

Non-interactive (read values from lic-data.json in the same directory):
    # Create lic-data.json first — see lic-data.json.example
    python regkey-pool-license.py

Output
------
On success, writes a license file named:
    <bigip-management-ip>_bigip.license

SCP this file to the BIG-IP, copy it to /config/bigip.license, then run:
    reloadlic

See docs/05-licensing.md#54-big-iq-pool-licensing-for-unreachable-dark-site-devices
for the full procedure.

Original author: F5 Networks (published via DevCentral / AskF5)
"""

import getpass  # used to hide the users password input
import json
import os
import requests
from time import sleep

"""
This script uses the BIG-IQ API to license an unreachable (dark site) BIG-IP.
The BIG-IQ licensing API needs certain details provided in order to license an
appliance. These details can either be provided in a file called lic-data.json,
or if that file does not exist you will be prompted to enter them.

Minimum lic-data.json:
{
    "licensePoolName": "<pool name from BIG-IQ GUI>",
    "command": "assign",
    "address": "<BIG-IP management IP>",
    "assignmentType": "UNREACHABLE",
    "macAddress": "<BIG-IP management interface MAC>",
    "hypervisor": "<aws|azure|gce|hyperv|kvm|vmware|xen>"
}

Optional fields:
    "chargebackTag": "<tag>",
    "tenant": "<tenant name>"

lic-data.json must reside in the directory from which you run this script.
"""


def bigiqAuth(_bigiqAuthUrl, _bigiqCredentials):
    """
    Authenticate with BIG-IQ and return the auth token header dict.
    Returns 0 on failure.
    """
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
    # end try
    if _errFlag == 0:
        _bigiqResponse = _bigiqAuthInfo.json()
        _bigiqToken = _bigiqResponse['token']
        for _token in _bigiqToken:
            if _token == 'token':
                _bigiqAuthToken = _bigiqToken[_token]
            # End if
        # Next
        _authHeaders = {
            "X-F5-Auth-Token": "{_authToken}".format(_authToken=_bigiqAuthToken)
        }
    else:
        _authHeaders = 0
    # end if
    print("** Completed Authentication ***")
    return(_authHeaders)
# End Def


def extractLicense(_rawLicenseJSON):
    """
    Pull the generated license text from the BIG-IQ response JSON.
    Returns 'FAILED' if the task did not reach FINISHED status.
    """
    for _license in _rawLicenseJSON:
        if _license == 'licenseText':
            _extractedLicense = _rawLicenseJSON[_license]
        # end if
        if _license == 'status':
            if _rawLicenseJSON[_license] == "FINISHED":
                print("***** License has been assigned *****")
            else:
                _extractedLicense = "FAILED"
            # end if
        # end if
    # next
    return(_extractedLicense)
# End def


def licenseData():
    """
    Read lic-data.json if present; otherwise prompt interactively.
    Returns the license request payload as a dict.
    """
    if os.path.exists('lic-data.json'):
        with open('./lic-data.json') as licfile:
            _licdata = json.load(licfile)
    else:
        _bigipAddress     = raw_input("Enter Management IP address of BIG-IP to be licensed: ")
        _bigipMACaddress  = raw_input("Enter Management MAC address of BIG-IP to be licensed: ")
        _licensePoolName  = raw_input("Enter the name of the License Pool from which to take BIG-IP license: ")
        _hypervisorType   = raw_input("Enter hypervisor used, valid options are: aws, azure, gce, hyperv, kvm, vmware, xen: ")
        _chargebackTag    = raw_input("Optional: Enter chargeback tag if required: ")
        _tenantTag        = raw_input("Optional: Enter tenant name if required: ")
        _licdata = {
            "licensePoolName":  "{_licensePool}".format(_licensePool=_licensePoolName),
            "command":          "assign",
            "address":          "{_bigipIP}".format(_bigipIP=_bigipAddress),
            "assignmentType":   "UNREACHABLE",
            "macAddress":       "{_bigipMAC}".format(_bigipMAC=_bigipMACaddress),
            "hypervisor":       "{_hypervisor}".format(_hypervisor=_hypervisorType),
            "chargebackTag":    "{_chargeback}".format(_chargeback=_chargebackTag),
            "tenant":           "{_tenant}".format(_tenant=_tenantTag),
        }
    # End if
    return(_licdata)


def urlConstruction(_bigiqUrl, _bigiqIP):
    """
    Rewrite the selfLink URL returned by BIG-IQ, replacing 'localhost' with
    the actual BIG-IQ management IP so subsequent GET requests work.
    """
    count = 0
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
            # end if
        # end if
        count += 1
    # Next
    return(_urlReConstruct)
# End Def


# ── Main ──────────────────────────────────────────────────────────────────────

_userID       = raw_input("Enter BIG-IQ user ID: ")
_password     = getpass.getpass(prompt="Enter BIG-IQ Password: ")
_bigiqAddress = raw_input("Enter Management IP address of BIG-IQ: ")

_credPostBody = {
    "username":           "{_uname}".format(_uname=_userID),
    "password":           "{_pword}".format(_pword=_password),
    "loginProviderName": "RadiusServer"
}

_deviceToBeLicensed = licenseData()
_bigipAddress = _deviceToBeLicensed['address']
print("BIG-IP Address is:  %s" % _bigipAddress)

_bigiq_session = requests.session()
_bigiq_auth_url = "https://{_bigiqIP}/mgmt/shared/authn/login".format(
    _bigiqIP=_bigiqAddress
)

_bigiqAuthHeader = bigiqAuth(_bigiq_auth_url, _credPostBody)

if _bigiqAuthHeader == 0:
    print("Unable to authenticate with BIG-IQ. Check BIG-IQ reachability and credentials")
else:
    _bigiq_url1 = (
        "https://{_bigiqIP}/mgmt/cm/device/tasks/licensing/pool/member-management"
        .format(_bigiqIP=_bigiqAddress)
    )

    _errFlag = 0
    try:
        _bigiqLicenseDevice = _bigiq_session.post(
            _bigiq_url1,
            headers=_bigiqAuthHeader,
            data=json.dumps(_deviceToBeLicensed),
            verify=False,
        )
        _bigiqLicenseDevice.raise_for_status()
        print("Response code: %s" % _bigiqLicenseDevice.status_code)
    except requests.exceptions.HTTPError as err:
        print("Issue received, check request and/or check connectivity: %s" % err)
        _errFlag = 1
    # end try

    if _errFlag == 0:
        _bigiqResponse = _bigiqLicenseDevice.json()
        print(_bigiqResponse)
        print(_bigiqResponse['selfLink'])
        _bigiqLicenseStatus_url = _bigiqResponse['selfLink']
        _bigiqLicenseStatus_url = urlConstruction(_bigiqLicenseStatus_url, _bigiqAddress)
        print(_bigiqLicenseStatus_url)
        print("--- Standby for 30 seconds whilst BIG-IQ generates license ---")
        sleep(30)

        _errFlag1 = 0
        try:
            _licenseStatus = _bigiq_session.get(
                _bigiqLicenseStatus_url, headers=_bigiqAuthHeader, verify=False
            )
            _licenseStatus.raise_for_status()
            print("Response code: %s" % _licenseStatus.status_code)
        except requests.exceptions.HTTPError as err:
            print("Issue received, check request and/or check connectivity: %s" % err)
            _errFlag = 1
        # end try

        if _errFlag == 0:
            print(_licenseStatus.content)
            _licenseStatusDetail = _licenseStatus.json()
            _licenseOutput = extractLicense(_licenseStatusDetail)
            if _licenseOutput == "FAILED":
                print(
                    "***** License Assignment Failed. "
                    "Most likely a valid license already exists for this device — "
                    "revoke it in BIG-IQ before applying a new license *****"
                )
            else:
                _licenseFname = _bigipAddress + "_bigip.license"
                _licensefile  = open(_licenseFname, "w")
                _licensefile.write("%s" % _licenseOutput)
                _licensefile.close()
                print(_licenseOutput)
                print("***** SUCCESS — license stored at: %s *****" % _licenseFname)
            # end if
        # end if
    # end if
# end if
