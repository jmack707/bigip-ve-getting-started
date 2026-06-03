# Step 2 — Downloading the BIG-IP VE Image

> Download the correct image format for your hypervisor from the F5 software portal before proceeding to deployment. Downloading the wrong format is the most common first-time mistake.

---

## Navigation

[← Step 1: Prerequisites](./01-prerequisites.md) | **Step 2: Download** | [Step 3: Deploy →](./03-deploy.md)

---

## 2.1 Which image format do you need?

| Hypervisor | Required format | Notes |
|------------|-----------------|-------|
| VMware ESXi / vSphere | `.ova` | Single-file OVA package; imported directly via vSphere Client or `ovftool` |
| Linux KVM / Proxmox VE | `.qcow2` | QEMU disk image; attach as a virtual disk |
| Nutanix AHV (Prism) | `.qcow2` | Same format as KVM; upload via Prism image library |
| Microsoft Hyper-V | `.vhd` | Not covered in this guide — see [F5 CloudDocs Hyper-V](https://clouddocs.f5.com/cloud/public/v1/hyperv_index.html) |

---

## 2.2 Downloading from my.f5.com

1. Log in at **[my.f5.com](https://my.f5.com)**
2. Navigate to **Downloads** → **Find a Download**
3. Product tree: **BIG-IP** → **Virtual Edition**
4. Select your target **version** (see [version guidance](#23-choosing-a-version) below)
5. Locate the file matching your hypervisor format from the table above
6. Accept the EULA and download

> [!NOTE]
> **File naming convention:** F5 image filenames follow the pattern `BIGIP-<version>.<build>-<platform>.<format>`. Examples:
> ```
> BIGIP-17.1.1.3-0.0.4.ALL-vmware.ova        ← VMware
> BIGIP-17.1.1.3-0.0.4.ALL-scsi.qcow2.zip    ← KVM / Nutanix (unzip before use)
> ```
> Download the `ALL` variant unless you have a specific reason for a module-specific image.

---

## 2.3 Choosing a version

| Situation | Recommendation |
|-----------|----------------|
| New lab or PoC | Latest release in the current LTS branch |
| Production deployment | Match your organization's approved software standard |
| Federal / STIG-required | Verify a current DISA STIG exists at [public.cyber.mil](https://public.cyber.mil/stigs/downloads/) |
| Hypervisor compatibility | Cross-check the [supported platforms matrix](https://clouddocs.f5.com/cloud/public/v1/matrix.html) |

> [!WARNING]
> BIG-IP versions have defined End of Technical Support dates. Always check [K5903](https://support.f5.com/csp/article/K5903) before deploying to avoid starting on an already-EOL release.

---

## 2.4 Verifying the download (checksum)

F5 publishes MD5 checksums on the download page alongside each file. Verify before deploying — a mismatch means re-download.

```bash
# Linux / macOS
md5sum BIGIP-17.1.1.3-0.0.4.ALL-vmware.ova

# PowerShell (Windows)
Get-FileHash .\BIGIP-17.1.1.3-0.0.4.ALL-vmware.ova -Algorithm MD5
```

Compare the output against the checksum on the my.f5.com download page.

---

## 2.5 Air-gapped / offline environments

Download to a connected workstation and transfer to the hypervisor host via your approved data-transfer method (SCP to a bastion, removable media through your sanitization process, etc.).

The image file itself requires no internet connection to deploy. Only the **licensing step** requires connectivity — or a CCN license server. See [Step 5: Licensing](./05-licensing.md) for all air-gapped options.

---

## 2.6 Optional: F5 BIG-IP Image Generator Tool

If you need a customized image — to pre-seed cloud-init, embed specific modules, or build for a non-standard platform — F5 provides the **BIG-IP Image Generator Tool**.

[F5 BIG-IP Image Generator Tool documentation](https://clouddocs.f5.com/cloud/public/v1/ve-image-gen_index.html)

This is an advanced workflow not required for standard deployments.

---

## Done with Step 2?

Proceed to **[Step 3: Deploying the VM →](./03-deploy.md)**
