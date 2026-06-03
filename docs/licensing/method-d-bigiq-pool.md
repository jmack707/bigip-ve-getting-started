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

## D.4 Copy the script to BIG-IQ and run it

The `regkey-pool-license.py` script (Python 2, for the BIG-IQ system Python) is located in this repo at:

```
scripts/ccn-licensing/regkey-pool-license.py
```

If you are running from a modern workstation inside the network, use the Python 3 version instead:

```
scripts/ccn-licensing/regkey-pool-license-py3.py
```

### Copy to BIG-IQ

```bash
scp scripts/ccn-licensing/regkey-pool-license.py admin@<bigiq-ip>:/shared/
```

### Run on BIG-IQ

```bash
ssh admin@<bigiq-ip>
cd /shared
python regkey-pool-license.py
```

### Interactive prompts

The script prompts for the following. Enter each value exactly:

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

| Hypervisor | Enter |
|------------|-------|
| VMware ESXi | `vmware` |
| KVM / Proxmox / Nutanix AHV | `kvm` |
| Hyper-V | `hyperv` |
| AWS | `aws` |
| Azure | `azure` |
| Google Cloud | `gce` |
| XenServer | `xen` |

The script authenticates to BIG-IQ, submits the license request, waits ~30 seconds, then writes a file named `<bigip-mgmt-ip>_bigip.license` to the current directory.

**Expected success output:**
```
***** License has been assigned *****
***** SUCCESS — license stored at: 10.1.1.10_bigip.license *****
```

> [!WARNING]
> If you see `***** License Assignment Failed *****`, a license is already checked out for that MAC address. Revoke it in BIG-IQ first (see [D.6 — Revoking a license](#d6-revoking-a-license)), then re-run.

---

## D.5 Non-interactive mode: lic-data.json

To skip interactive prompts — useful for scripting or repeat runs — create a `lic-data.json` file in the same directory as the script before running. See the examples in this repo:

```
scripts/ccn-licensing/lic-data.json.example
scripts/ccn-licensing/lic-data.json.example-with-optional-fields
```

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

## D.6 Revoking a license

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
| K26521163: BIG-IQ pool-based licensing for BIG-IP VE | https://support.f5.com/csp/article/K26521163 |
| BIG-IQ License Manager deployment guide | https://techdocs.f5.com/en-us/bigiq-8-0-0/managing-big-ip-ve-subscriptions-from-big-iq/deploy-license-iq-license-manager.html |
| Script reference | [scripts/ccn-licensing/README.md](../../scripts/ccn-licensing/README.md) |

---

## Done?

Proceed to **[Step 6: Module Provisioning →](../06-provisioning.md)**
