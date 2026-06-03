# Licensing Method C — CCN Self-Service Utility (True Air-Gap)

> Use when the BIG-IP is in a fully air-gapped environment with no BIG-IQ on-site, and data transfer into the secure environment is done manually (paper, approved removable media, etc.).

---

## Navigation

[← Method B: Manual](./method-b-manual.md) | [← Licensing Overview](../05-licensing.md) | [Method D: BIG-IQ Pool →](./method-d-bigiq-pool.md)

---

## When to use this method

- The BIG-IP resides in a secured environment where security policy **strictly prohibits** transmitting any data outside the network
- No BIG-IQ is deployed inside the enclave
- Typical environments: SCIFs, classified government/military networks, high-security financial systems
- You can carry a license file **into** the secure environment via an approved transfer method

> [!IMPORTANT]
> **This method requires F5 pre-approval.** You must be on F5's authorized CCN requester list before you can use the Self-Service Utility. Complete [Section C.1 — Pre-Approval](#c1-pre-approval-required-before-first-request) before attempting to license.

> [!IMPORTANT]
> **Eligibility requirements:**
> - Device must have a **current active support contract** with F5
> - CCN licensing activates individual BIG-IP devices only — it does **not** support BIG-IQ distribution of pool, CLP, or VLS licensing
> - EOL platforms (e.g., F20, F25) are not supported — see [K5903](https://support.f5.com/csp/article/K5903) for the EOL list

---

## Overview

```
Secure environment (no internet)       Connected workstation (outside)
          │                                          │
          │ 1. Run get_dossier ──── carry out ──►   │
          │                                          │ 2. Submit to secure.f5.com/ccn
          │                                          │ 3. Download license file
          │ ◄──────── carry in (approved method) ─── │
          │
          │ 4. Apply license (reloadlic)
          ▼
     Licensed ✓
```

---

## C.1 Pre-Approval (required before first request)

CCN licensing requires that your name be on F5's authorized requester list. This is a **one-time process per contact** and must be completed before you can use the Self-Service Utility.

**Already received a CCN license from F5 Support before?** You are likely already on the list — a technician can confirm.

**Not yet authorized? Follow these steps:**

1. Create an account at [www.f5.com](https://www.f5.com) → "Sign Up"
2. Email the following to **[licensingsupport@f5.com](mailto:licensingsupport@f5.com)**:

    | Field | Your information |
    |-------|-----------------|
    | Contact Name | |
    | Contact Title | |
    | Company Name | |
    | Email Address | |
    | Phone | |

3. To add additional authorized contacts from your organization, include their information in the same email — each contact must be individually listed
4. F5 will notify you by email once your authorization is confirmed

> [!NOTE]
> Allow several business days for CCN authorization. Plan ahead before your deployment window.

---

## C.2 Collect the dossier from the BIG-IP (inside secure environment)

The dossier is the system fingerprint F5 uses to generate a locked license. Run this on the BIG-IP inside the secure environment.

**BIG-IP v12.0.0 or later (recommended):**
```bash
get_dossier -c -b <base-registration-key>
# Copy the entire output block
```

**BIG-IP prior to v12.0.0 — VE only:**
```bash
get_ccn_dossier
# No arguments; copy the entire output block
```

> [!WARNING]
> `get_ccn_dossier` supports Virtual Edition only on older versions. For hardware platforms older than v12.0.0, contact F5 Technical Support directly — do not attempt to use the Self-Service Utility.

Carry the dossier output out of the secure environment via your approved data transfer method.

---

## C.3 Submit to the Secured Environment License Utility (outside secure environment)

From a **connected** workstation outside the secure environment:

1. Navigate to: **[https://secure.f5.com/ccn/index.jsp](https://secure.f5.com/ccn/index.jsp)**

2. **Authenticate:**
   - **Requestor Email** — your authorized email address
   - **Serial Key** — the **last 7 characters** of the base registration key
   - Accept the EULA → **Next Step**

3. **Provide dossier data** — choose the method that matches how you collected the dossier:

   | Option | When to select | What to do |
   |--------|---------------|------------|
   | Paste dossier output | You ran `get_dossier` or `get_ccn_dossier` | Select *"I have output from get_ccn_dossier or get_dossier I can paste into this web portal"* → paste full output → **Next Step** |
   | Manual entry | Cannot paste | Select *"I will manually type in the licensing attributes"* → enter MAC address and fields exactly as shown → **Next Step** |

4. **Receive the license file:**
   - The portal delivers the license as text
   - Click **Save to file** to download
   - Carry the license file **into** the secure environment via your approved transfer method

---

## C.4 Apply the license to the BIG-IP (inside secure environment)

```bash
# Back up any existing license
cp /config/bigip.license /config/bigip.license.bak

# Place the received license file at /config/bigip.license
# (copy from removable media or approved transfer, then rename)
cp /path/to/received-license.txt /config/bigip.license

# Reload the license daemon
reloadlic

# Verify
tmsh show /sys license | grep -E "Licensed version|Registration Key|Active Modules"
```

Alternatively via TMUI: **System → License → Activate → Manual** → paste license text → **Accept**.

---

## C.5 Support contacts for CCN licensing failures

If the license does not activate on the intended system, contact F5 immediately:

| Method | Contact |
|--------|---------|
| Phone | **1-888-882-7535** |
| Email | **[licensingsupport@f5.com](mailto:licensingsupport@f5.com)** |

> [!IMPORTANT]
> Include **"CCN FAILURE REPORT"** in the email subject line. This routes your case directly to the specialized CCN team and ensures prompt handling.

---

## Done?

Proceed to **[Step 6: Module Provisioning →](../06-provisioning.md)**
