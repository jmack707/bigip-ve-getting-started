# Step 5 — Licensing

> Activate your BIG-IP VE license using the method appropriate for your network environment. Choose one path from the table below and follow it end to end.

---

## Navigation

[← Step 4: First Boot](./04-first-boot.md) | **Step 5: Licensing** | [Step 6: Module Provisioning →](./06-provisioning.md)

---

## 5.0 Choose your licensing method

| Method | BIG-IP needs internet? | When to use |
|--------|----------------------|-------------|
| [5.1 Automatic (online)](#51-automatic-online-activation) | ✅ Yes | BIG-IP management can reach `activate.f5.com:443` directly |
| [5.2 Manual (file-based)](#52-manual-file-based-activation) | ❌ No | A jump host or workstation can reach the F5 portal; the BIG-IP cannot |
| [5.3 CCN Self-Service Utility](#53-ccn-self-service-utility-true-air-gap) | ❌ No | True air-gap; no BIG-IQ on-site; requires F5 CCN pre-approval |
| [5.4 BIG-IQ Pool — Unreachable Device](#54-big-iq-pool-licensing-for-unreachable-dark-site-devices) | ❌ No | BIG-IQ deployed inside the restricted enclave; ELA or pool licensing |

> [!TIP]
> **Quick connectivity check:**
> ```bash
> tmsh run /util ping activate.f5.com count 3
> # If this fails → use 5.2, 5.3, or 5.4
> ```

---

## 5.1 Automatic (online) activation

The simplest path when the BIG-IP management interface has direct outbound HTTPS access.

### TMUI method

1. Navigate to **System → License → Activate**
2. Set **Activation Method** to `Automatic`
3. Paste your **Base Registration Key** (format: `XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX`)
4. Click **Next** — the system contacts `activate.f5.com`, validates the key, and returns a license summary
5. Review licensed modules and throughput tier → click **Accept**
6. Wait ~60 seconds for services to reload

### TMSH method

```bash
tmsh install /sys license registration-key <XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX>

# Verify
tmsh show /sys license
```

---

## 5.2 Manual (file-based) activation

Use when the BIG-IP cannot reach the internet but an engineer workstation can.

### Step 1 — Collect the dossier from the BIG-IP

**TMSH:**
```bash
tmsh run /util get-dossier registration-key <your-reg-key>
# Copy the entire output block — this is the dossier string
```

**TMUI:** System → License → Activate → select **Manual** → copy the Dossier text box

### Step 2 — Generate the license file on a connected host

1. Navigate to **[https://activate.f5.com/license](https://activate.f5.com/license)** from a connected workstation
2. Paste the dossier text and enter your registration key → submit
3. Download the resulting license file (typically `License.txt`)

### Step 3 — Apply the license

```bash
# Copy the license file to the BIG-IP
scp License.txt admin@<management-ip>:/shared/tmp/

# Apply
tmsh install /sys license file /shared/tmp/License.txt

# Verify
tmsh show /sys license | grep -E "licensed|Active|Registration"
```

**TMUI:** System → License → Activate → **Manual** → paste license file contents → **Next** → **Accept**

---

## 5.3 CCN Self-Service Utility (true air-gap)

Use this method when:
- The BIG-IP has **no internet path**, and
- There is **no BIG-IQ license server** inside the restricted network, and
- You can carry a license file into the secured environment via approved data transfer

This is the F5-managed Closed Circuit Network (CCN) licensing process. It uses the **F5 Secured Environment License Utility** portal and requires pre-authorization from F5.

> [!IMPORTANT]
> **CCN licensing has specific eligibility requirements:**
> - The device must run in an environment where security policy strictly prohibits transmitting data outside the network (government, military, banking, or similar)
> - The device must have a **current active support contract** with F5
> - CCN licensing only supports licensing the BIG-IQ unit itself — it does **not** support BIG-IQ distribution of pool, CLP, or VLS licensing
> - EOL platforms (e.g., F20, F25) are not supported — see [AskF5 EOL list](https://support.f5.com/csp/article/K5903)

---

### 5.3.1 CCN Pre-Approval (required before first request)

CCN licensing requires that your contact be on F5's authorized requester list. This is a one-time process per contact.

**If you have previously received a CCN license from F5 Technical Support**, you are likely already on the list. The F5 technician can verify this.

**If you are not yet authorized:**

1. Create an account at [www.f5.com](https://www.f5.com) (click "Sign Up")
2. Prepare the following information:

    | Field | Your information |
    |-------|-----------------|
    | Contact Name | |
    | Contact Title | |
    | Company Name | |
    | Email Address | |
    | Phone | |

3. Email this information to **[licensingsupport@f5.com](mailto:licensingsupport@f5.com)**
4. To add additional authorized contacts from your organization, include their information in the same email

You will receive notification once you are authorized to initiate CCN licensing requests.

> [!NOTE]
> To add contacts to an existing approval, submit their information using the same process. Each authorized contact must be individually pre-approved.

---

### 5.3.2 Collect the dossier from the BIG-IP

The collection method depends on your BIG-IP / BIG-IQ version:

**BIG-IP v12.0.0 or later / BIG-IQ v4.6.0 or later (Method 1 — recommended):**

```bash
# Run on the BIG-IP (bash shell or TMSH)
get_dossier -c -b <base-registration-key>
# Copy the entire output block
```

**BIG-IP prior to v12.0.0 / BIG-IQ prior to v4.6.0 — VE only (Method 2):**

```bash
get_ccn_dossier
# No arguments required; copy the entire output block
```

> [!WARNING]
> The `get_ccn_dossier` utility (Method 2) supports Virtual Edition only. For hardware platforms on older versions, contact F5 Technical Support directly.

---

### 5.3.3 Submit to the Secured Environment License Utility

1. From a **connected** workstation (outside the secure environment), navigate to:
   **[https://secure.f5.com/ccn/index.jsp](https://secure.f5.com/ccn/index.jsp)**

2. **Step 1 — Authenticate:**
   - Enter your authorized email address in the **Requestor Email** box
   - Enter the **last 7 characters** of the base registration key in the **Serial Key** box
   - Accept the EULA → click **Next Step**

3. **Step 2 — Provide data** (choose one method):

   | Method | When to use | What to do |
   |--------|-------------|------------|
   | Paste dossier output | You ran `get_dossier` or `get_ccn_dossier` | Select *"I have output from get_ccn_dossier or get_dossier I can paste into this web portal"* → paste the full output → **Next Step** |
   | Manual entry | Dossier output not available | Select *"I will manually type in the licensing attributes"* → enter MAC address and other fields exactly as shown by the utility → **Next Step** |

4. **Step 3 — Receive license file:**
   - The portal delivers the license file as text
   - Click **Save to file** to download
   - Transport the license file into the secured environment using your approved data transfer method

---

### 5.3.4 Apply the CCN license file to the BIG-IP

```bash
# Back up the existing license (if any)
cp /config/bigip.license /config/bigip.license.bak

# Copy the new license file to the BIG-IP (SCP or approved transfer)
# then rename it:
cp /path/to/received-license.txt /config/bigip.license

# Reload the license daemon
reloadlic

# Verify
tmsh show /sys license
```

Alternatively, apply via TMUI: **System → License → Activate → Manual** → paste the license text → **Accept**.

---

### 5.3.5 CCN licensing support contacts

If the license you receive does not activate correctly on the intended system, contact F5 immediately:

| Contact method | Details |
|----------------|---------|
| Phone | **1-888-882-7535** |
| Email | **[licensingsupport@f5.com](mailto:licensingsupport@f5.com)** |

> [!IMPORTANT]
> When emailing about a failed CCN license, include **"CCN FAILURE REPORT"** in the subject line to ensure routing to the specialized CCN team and prompt response.

---

## 5.4 BIG-IQ Pool Licensing for Unreachable (Dark-Site) Devices

Use this method when:
- A **BIG-IQ Centralized Management** instance is deployed inside the restricted network, and
- The BIG-IP to be licensed is **unreachable** from BIG-IQ (no management-plane connectivity between them), and
- You are using ELA or pool-based licensing managed through BIG-IQ

This method uses the **`regkey-pool-license.py`** script executed on the BIG-IQ itself, leveraging the BIG-IQ REST API to generate a license file for an unreachable BIG-IP. The generated license file is then manually transferred and applied.

> [!NOTE]
> This approach was developed specifically for closed-network customers who have BIG-IQ deployed inside the enclave but whose BIG-IP management addresses are not reachable from BIG-IQ at the time of licensing. It does not require network connectivity between BIG-IQ and the target BIG-IP — only between the engineer's session and BIG-IQ.

---

### 5.4.1 Architecture

```
Engineer workstation (inside enclave)
        │
        │  SSH/SCP
        ▼
  BIG-IQ CM (inside enclave)
        │
        │  REST API (localhost)
        ▼
  License Pool (BIG-IQ internal)
        │
        │  Generated license file (text)
        ▼
  SCP to engineer workstation
        │
        │  SCP or approved transfer
        ▼
  BIG-IP VE (unreachable dark-site device)
        │
        │  reloadlic
        ▼
  Licensed ✓
```

---

### 5.4.2 Prerequisites

Before running the script:

- [ ] BIG-IQ Centralized Management 5.2.0 or later is deployed and licensed inside the enclave
- [ ] A RegKey Pool has been created in BIG-IQ containing the registration key(s) for the target BIG-IP
- [ ] You have BIG-IQ admin credentials
- [ ] You have the BIG-IP's **management IP address** and **management interface MAC address**
- [ ] Python 2 is available on the BIG-IQ (the script uses `raw_input` — Python 2 syntax)
- [ ] The `requests` library is available on the BIG-IQ

> [!NOTE]
> **Obtaining BIG-IQ License Manager:** For BIG-IQ version 7.1.0 and earlier, the License Management functionality is available as a free license. Download BIG-IQ Centralized Management from the [F5 Downloads page](https://my.f5.com). For licensing the BIG-IQ system itself, see [K15094](https://techdocs.f5.com/en-us/bigiq-8-0-0/managing-big-ip-ve-subscriptions-from-big-iq/deploy-license-iq-license-manager.html).

---

### 5.4.3 Create a Registration Key Pool in BIG-IQ

1. In the BIG-IQ TMUI, click the **Devices** tab
2. In the left nav: **LICENSE MANAGEMENT → Licenses**
3. Click **Add RegKey Pool**
4. Enter a **Name** for the pool (e.g., `BIG-IP-VE-Pool-FEDRAMP`) → **OK**
5. Add registration keys using **Add RegKey** or **Import CSV**

---

### 5.4.4 Collect the BIG-IP's management MAC address

You need this to generate the license. Run on the BIG-IP:

```bash
# BIG-IP v11+
tmsh show net interface mgmt all-properties | grep -i mac

# Alternatively from bash
ip link show mgmt | grep ether
```

Note the MAC address — format: `xx:xx:xx:xx:xx:xx`

---

### 5.4.5 Run `regkey-pool-license.py` on BIG-IQ

1. Copy the script to the BIG-IQ `/shared` directory:

    ```bash
    scp regkey-pool-license.py admin@<bigiq-ip>:/shared/
    ```

2. SSH to BIG-IQ and run the script:

    ```bash
    ssh admin@<bigiq-ip>
    cd /shared
    python regkey-pool-license.py
    ```

3. The script prompts for the following. Enter each value carefully:

    ```
    Enter BIG-IQ user ID:                          admin
    Enter BIG-IQ Password:                         <bigiq-password>
    Enter Management IP address of BIG-IQ:         <bigiq-mgmt-ip>
    Enter Management IP address of BIG-IP:         <bigip-mgmt-ip>
    Enter Management MAC address of BIG-IP:        xx:xx:xx:xx:xx:xx
    Enter the name of the License Pool:            BIG-IP-VE-Pool-FEDRAMP
    Enter hypervisor (aws/azure/gce/hyperv/kvm/vmware/xen):  vmware
    Optional: Enter chargeback tag:                <or press Enter to skip>
    Optional: Enter tenant name:                   <or press Enter to skip>
    ```

    **Hypervisor values:** `aws` | `azure` | `gce` | `hyperv` | `kvm` | `vmware` | `xen`

4. The script authenticates to BIG-IQ, submits the license request, waits ~30 seconds for BIG-IQ to generate the license, then writes the output to a file named `<bigip-ip>_bigip.license` in the current directory.

    Expected success output:
    ```
    ***** License has been assigned *****
    ***** SUCCESS, the license is stored here <bigip-ip>_bigip.license *****
    ```

> [!WARNING]
> If the script returns `***** License Assignment Failed *****`, a valid license may already be checked out for that device's MAC address. Revoke the existing license in BIG-IQ before re-running.

---

### 5.4.6 Using a `lic-data.json` file (non-interactive)

Instead of interactive prompts, the script accepts a pre-populated `lic-data.json` file in the same directory. This is useful for automation or repeat licensing runs.

```json
{
    "licensePoolName": "BIG-IP-VE-Pool-FEDRAMP",
    "command": "assign",
    "address": "10.1.1.10",
    "assignmentType": "UNREACHABLE",
    "macAddress": "06:ce:c2:43:b3:05",
    "hypervisor": "vmware"
}
```

Optional fields (remove if not needed):
```json
{
    "licensePoolName": "BIG-IP-VE-Pool-FEDRAMP",
    "command": "assign",
    "address": "10.1.1.10",
    "assignmentType": "UNREACHABLE",
    "macAddress": "06:ce:c2:43:b3:05",
    "hypervisor": "vmware",
    "chargebackTag": "PROJ-2024-DOD",
    "tenant": "Agency-XYZ"
}
```

Place `lic-data.json` in the same directory as the script before running. If the file is present, the script skips interactive prompts.

---

### 5.4.7 Transfer and apply the license file

```bash
# 1. SCP the generated license file from BIG-IQ to your workstation
scp admin@<bigiq-ip>:/shared/<bigip-ip>_bigip.license ./

# 2. Transfer to the BIG-IP via approved method, then on the BIG-IP:

# Back up the existing license
cp /config/bigip.license /config/bigip.license.bak

# Copy the new license to /config and rename
cp /path/to/<bigip-ip>_bigip.license /config/bigip.license

# Reload the license
reloadlic

# Verify
tmsh show /sys license
```

---

### 5.4.8 Revoking a pool license

Always return a license to the pool when decommissioning a BIG-IP VE to prevent pool exhaustion.

**Via TMSH on the BIG-IP (if still reachable from BIG-IQ):**

```bash
tmsh revoke /sys license \
    bigiq-addr <bigiq-ip> \
    bigiq-user admin \
    bigiq-password <bigiq-password> \
    bigiq-port 443 \
    pool-name 'BIG-IP-VE-Pool-FEDRAMP'
```

**Via BIG-IQ TMUI (if BIG-IP is no longer reachable):**

Navigate to **Devices → LICENSE MANAGEMENT → Licenses → [pool name]** → find the device → **Revoke**.

> [!NOTE]
> If a BIG-IP instance is deleted without revoking its license, BIG-IQ will reclaim it automatically after a configurable grace period (default: 24 hours for unresponsive devices). Confirm the grace period setting with your BIG-IQ administrator.

---

## 5.5 Confirm licensing succeeded

Regardless of activation method:

```bash
tmsh show /sys license

# Look for:
# Licensed version    17.1.x
# Registration Key    XXXXX-XXXXX-...
# Active Modules      LTM, ...
```

The output must show your registration key, licensed version, and active modules before proceeding.

---

## Further reading

| Resource | URL |
|----------|-----|
| K15690: Overview of BIG-IP VE licensing | https://support.f5.com/csp/article/K15690 |
| K26521163: BIG-IQ pool-based licensing | https://support.f5.com/csp/article/K26521163 |
| CCN Self-Service Utility | https://secure.f5.com/ccn/index.jsp |
| F5 CloudDocs: Licensing BIG-IP VE | https://clouddocs.f5.com/cloud/public/v1/licensing/licensing.html |
| BIG-IQ License Manager deployment guide | https://techdocs.f5.com/en-us/bigiq-8-0-0/managing-big-ip-ve-subscriptions-from-big-iq/deploy-license-iq-license-manager.html |

---

## Done with Step 5?

Proceed to **[Step 6: Module Provisioning →](./06-provisioning.md)**
