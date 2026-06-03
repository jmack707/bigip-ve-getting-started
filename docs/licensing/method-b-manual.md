# Licensing Method B — Manual (File-Based) Activation

> Use when the BIG-IP cannot reach the internet directly, but an engineer workstation or jump host can.

---

## Navigation

[← Method A: Automatic](./method-a-automatic.md) | [← Licensing Overview](../05-licensing.md) | [Method C: CCN →](./method-c-ccn.md)

---

## When to use this method

- BIG-IP management has no outbound internet access
- An engineer workstation or jump host outside the BIG-IP's network segment **can** reach `activate.f5.com`
- No BIG-IQ is deployed

---

## Overview

```
BIG-IP (no internet)                 Connected workstation
     │                                        │
     │ 1. Export dossier ──────────────────► │
     │                                        │ 2. Submit to activate.f5.com
     │                                        │ 3. Download license file
     │ ◄─────────────── 4. Copy license ───── │
     │
     │ 5. Install license
     ▼
Licensed ✓
```

---

## Step 1 — Collect the dossier from the BIG-IP

The dossier is a system fingerprint that F5 uses to generate a locked license file.

**TMSH:**
```bash
tmsh run /util get-dossier registration-key <your-reg-key>
# Copy the entire output — every character matters
```

**TMUI:** System → License → Activate → select **Manual** → copy the full contents of the Dossier text box

---

## Step 2 — Generate the license file (on a connected workstation)

1. Open a browser on your connected workstation and navigate to:
   **[https://activate.f5.com/license](https://activate.f5.com/license)**
2. Paste the dossier text into the provided field
3. Enter your **Base Registration Key**
4. Submit — the portal generates and returns a license file
5. Click **Save to file** (typically saves as `License.txt`)

---

## Step 3 — Transfer the license file to the BIG-IP

Use whatever transfer method is available in your environment (SCP, SFTP, approved USB, etc.):

```bash
scp License.txt admin@<management-ip>:/shared/tmp/
```

---

## Step 4 — Apply the license

**TMSH:**
```bash
tmsh install /sys license file /shared/tmp/License.txt

# Verify
tmsh show /sys license | grep -E "Licensed version|Registration Key|Active Modules"
```

**TMUI:** System → License → Activate → **Manual** → paste the license file contents into the License text box → **Next** → **Accept**

---

## Done?

Proceed to **[Step 6: Module Provisioning →](../06-provisioning.md)**
