# Step 1 — Prerequisites & Minimum Requirements

> **Before you begin:** Gather everything on this page before touching the hypervisor or the F5 portal. Incomplete preparation is the most common reason first-time deployments stall.

---

## Navigation

[← README](../README.md) | **Step 1: Prerequisites** | [Step 2: Download →](./02-download.md)

---

## 1.1 Accounts you need

| Account | Used for | Where to get it |
|---------|----------|-----------------|
| **my.f5.com** | Downloading software, viewing license keys, opening support cases | Register at [my.f5.com](https://my.f5.com) with your work email; link to your company's contract |
| **F5 registration key** | Activating the BIG-IP license | Provided by F5 sales or reseller; also visible in my.f5.com → *My Products & Support* |
| Hypervisor admin credentials | Deploying and managing the VM | Your vCenter / Proxmox / Prism credentials |

> [!IMPORTANT]
> **Federal / classified environments:** If your BIG-IP will reside in an air-gapped or CCN environment, you must complete F5's CCN pre-approval process **before** deployment. This requires a separate authorization step with F5 Technical Support. See [Step 5: CCN Pre-Approval](./05-licensing.md#531-ccn-pre-approval-required-before-first-request) for the full process. Allow several business days for authorization.

---

## 1.2 Minimum VM resource requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| vCPUs | 2 | 4 or more |
| RAM | 4 GB | 8 GB or more |
| Boot disk | 40 GB (thin provisioning OK) | 100 GB |
| Data NICs | 1 (single-NIC mode) | 3–4 (mgmt + external + internal + optional HA) |

> [!WARNING]
> **Single-NIC throughput cap:** All single-NIC configurations are hard-capped at **1 Gbps maximum throughput** regardless of license tier. Use multi-NIC for any performance testing.

> [!NOTE]
> **Single-NIC vs. multi-NIC behavior:** BIG-IP VE behaves differently based on how many NICs are attached at first boot — this catches most first-time deployers. Read the [single-NIC warning in Step 3](./03-deploy.md#single-nic-behavior) before configuring your VM.

---

## 1.3 Host hardware requirements

Regardless of hypervisor, the host must meet these requirements:

- 64-bit x86_64 CPU architecture
- Hardware virtualization extensions enabled in BIOS: **Intel VT-x** or **AMD-V**
- Virtualization extensions exposed to the hypervisor (not masked by nested virtualization layers)
- Sufficient free RAM and CPU threads for the VM sizing above — BIG-IP vCPUs should not share physical cores with other latency-sensitive workloads

> [!NOTE]
> **Proxmox / KVM on Intel 12th/13th gen (Raptor Lake):** Some early BIOS revisions have known issues with VT-x initialization. Verify that `kvm_intel` loads cleanly before deploying: `dmesg | grep -i kvm`

---

## 1.4 Hypervisor version compatibility

Confirm your hypervisor version is in the F5 support matrix before selecting a BIG-IP VE release.

**[BIG-IP VE Supported Platforms matrix](https://clouddocs.f5.com/cloud/public/v1/matrix.html)**

| Hypervisor | Minimum supported version |
|------------|--------------------------|
| VMware ESXi | 6.7 Update 3 or later |
| Linux KVM (QEMU) | QEMU 2.x or later (RHEL / Rocky / Ubuntu) |
| Nutanix AHV | AOS 5.20 or later (Prism Central 2022.x+) |

> [!TIP]
> Unless you have a specific requirement for an older branch, deploy the latest **Long-Term Support (LTS)** release. Check [K5903](https://support.f5.com/csp/article/K5903) for the current support lifecycle schedule.

---

## 1.5 Network planning worksheet

Fill this out before starting. You will enter these values during initial setup.

```
Management IP address:    ___.___.___.___  /___
Management gateway:       ___.___.___.___
DNS server(s):            ___.___.___.___  ,  ___.___.___.___
NTP server(s):            ___________________________
External VLAN subnet:     ___.___.___.___  /___
External self-IP:         ___.___.___.___
Internal VLAN subnet:     ___.___.___.___  /___
Internal self-IP:         ___.___.___.___
Default gateway (TMM):    ___.___.___.___
Hostname (FQDN):          ___________________________.___

CCN / BIG-IQ (if applicable):
  BIG-IQ management IP:   ___.___.___.___
  License pool name:       ___________________________
  BIG-IQ port:             443
```

---

## Done with Step 1?

Proceed to **[Step 2: Downloading the BIG-IP VE Image →](./02-download.md)**
