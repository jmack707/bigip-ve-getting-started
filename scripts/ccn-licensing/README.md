# CCN Licensing Scripts

Scripts for licensing BIG-IP VE devices that are unreachable from the public internet, using the BIG-IQ License Manager REST API.

For the full procedure, see **[docs/05-licensing.md — Section 5.4](../../docs/05-licensing.md#54-big-iq-pool-licensing-for-unreachable-dark-site-devices)**.

---

## Files

| File | Purpose |
|------|---------|
| `regkey-pool-license.py` | **Python 2** — original script; run directly on BIG-IQ appliance (BIG-IQ 5.x – 7.x) |
| `regkey-pool-license-py3.py` | **Python 3** — port for modern workstations / jump hosts with Python 3 |
| `lic-data.json.example` | Minimal non-interactive input file |
| `lic-data.json.example-with-optional-fields` | Input file including chargeback and tenant tags |

---

## Which script to use?

| Where you are running it | Script |
|--------------------------|--------|
| Directly on the BIG-IQ appliance (system Python) | `regkey-pool-license.py` (Python 2) |
| Modern jump host or workstation inside the enclave | `regkey-pool-license-py3.py` (Python 3) |

Both scripts are functionally identical. The Python 3 version adds explicit SSL warning suppression, cleaner error exits, and next-step instructions on success.

---

## Prerequisites

### Python 2 version (on BIG-IQ)
The `requests` library is included on BIG-IQ. No additional installation needed.

### Python 3 version (on jump host)
```bash
pip3 install requests
```

---

## Quick start

### Step 1 — Collect the BIG-IP management MAC address

```bash
# On the BIG-IP:
tmsh show net interface mgmt all-properties | grep -i mac
```

### Step 2 — Create lic-data.json (optional, for non-interactive use)

```bash
cp lic-data.json.example lic-data.json
# Edit lic-data.json with your values:
#   licensePoolName  — name of the RegKey Pool in BIG-IQ
#   address          — BIG-IP management IP
#   macAddress       — BIG-IP management interface MAC
#   hypervisor       — aws | azure | gce | hyperv | kvm | vmware | xen
```

### Step 3 — Run the script

```bash
# Copy script to BIG-IQ (or run locally for py3 version)
scp regkey-pool-license.py admin@<bigiq-ip>:/shared/
ssh admin@<bigiq-ip>
cd /shared
python regkey-pool-license.py
```

The script prompts for BIG-IQ credentials then waits ~30 seconds for the license to generate.

### Step 4 — Apply the license to the BIG-IP

```bash
# Copy generated license file from BIG-IQ to your workstation
scp admin@<bigiq-ip>:/shared/<bigip-ip>_bigip.license ./

# Transfer to BIG-IP via approved method, then on the BIG-IP:
cp /path/to/<bigip-ip>_bigip.license /config/bigip.license
reloadlic
tmsh show /sys license
```

---

## Hypervisor values

| Hypervisor | Value to enter |
|------------|----------------|
| VMware ESXi | `vmware` |
| Linux KVM / Proxmox | `kvm` |
| Nutanix AHV | `kvm` |
| Microsoft Hyper-V | `hyperv` |
| AWS | `aws` |
| Azure | `azure` |
| Google Cloud | `gce` |
| Citrix XenServer | `xen` |

---

## Troubleshooting

**"License Assignment Failed"**
A license is already checked out for that MAC address. In BIG-IQ: Devices → LICENSE MANAGEMENT → Licenses → [pool] → find device → Revoke. Then re-run.

**"Unable to authenticate"**
Verify BIG-IQ IP is reachable from your session host (`ping <bigiq-ip>`), and that the credentials are correct. Try logging into the BIG-IQ GUI from a browser to confirm.

**License file created but `reloadlic` shows no change**
Confirm the file is named exactly `bigip.license` and placed in `/config/`. Check `tmsh show /sys license` and run `reloadlic` a second time if needed.

**CCN licensing support:** 1-888-882-7535 | licensingsupport@f5.com (subject: CCN FAILURE REPORT)
