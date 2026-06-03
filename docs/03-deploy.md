# Step 3 — Deploying the VM

> Deploy the BIG-IP VE image on your hypervisor. Jump to the section for your platform.

**Sections:** [Single-NIC Warning](#single-nic-behavior) | [VMware ESXi](#31-vmware-esxi--vsphere) | [KVM / Proxmox](#32-linux-kvm--proxmox-ve) | [Nutanix AHV](#33-nutanix-ahv-prism)

---

## Navigation

[← Step 2: Download](./02-download.md) | **Step 3: Deploy** | [Step 4: First Boot →](./04-first-boot.md)

---

## Single-NIC behavior

> [!WARNING]
> **This catches most first-time deployers. Read this before creating your VM.**

When BIG-IP VE boots, it counts the number of active (connected) NICs and behaves differently based on what it finds:

| NICs at first boot | What BIG-IP does automatically |
|--------------------|-------------------------------|
| **1 NIC** | Auto-creates a VLAN named `internal`, attaches it to interface `1.0`, attempts DHCP for a self-IP, and **moves the management GUI from port 443 to port 8443** |
| **2 or more NICs** | Does nothing automatically — you create all VLANs and self-IPs manually. GUI stays on port 443. |

**Recommendation:** Attach at least 3 NICs (management + external + internal) before first boot for any real lab or production use. If you deploy with 1 NIC and add more later, the auto-config objects created at first boot may need to be cleaned up manually.

If you intentionally deploy a single-NIC instance, access the GUI at `https://<management-ip>:8443` after first boot.

---

## 3.1 VMware ESXi / vSphere

**Official F5 guide:** [Deploy BIG-IP VE in a VMware ESXi environment](https://clouddocs.f5.com/cloud/public/v1/vmware/vmware_setup.html)

> [!NOTE]
> **VMware prerequisites:** You need vSphere Client (HTML5) or the `ovftool` CLI. Confirm your ESXi version against the [supported platforms matrix](https://clouddocs.f5.com/cloud/public/v1/matrix.html) before importing. Consult [K74921042](https://support.f5.com/csp/article/K74921042) before updating any ESXi 6.7 host running BIG-IP VE.

### Deployment steps

| Step | Task |
|------|------|
| 1 | Create or confirm port groups on your vSwitch for management, external, and internal networks |
| 2 | Import the `.ova`: **File → Deploy OVF Template** in vSphere Client |
| 3 | During import wizard: map each NIC to the correct port group |
| 4 | Set the management IP via vApp properties **before** first power-on (see below) |
| 5 | Power on the VM and wait ~5 minutes for first-boot provisioning |

### Setting the management IP before first boot (recommended)

In vSphere Client, right-click the VM → **Edit Settings → vApp Options**:

```
Management IP Address:   192.168.1.245
Management Netmask:      255.255.255.0
Management Gateway:      192.168.1.1
```

Setting this before power-on avoids needing console access after boot.

### CLI: OVF Tool

```bash
ovftool \
  --name="bigip-ve-01" \
  --net:"Management Network"="VM Network" \
  --net:"Internal Network"="Internal PG" \
  --net:"External Network"="External PG" \
  --prop:net.mgmt.addr="192.168.1.245/24" \
  --prop:net.mgmt.gw="192.168.1.1" \
  BIGIP-17.1.1.3-0.0.4.ALL-vmware.ova \
  vi://admin@vcenter.example.com/datacenter/host/esxi-host
```

### VMware-specific notes

- Use **VMXNET3** NIC driver for all data-plane interfaces — do not use e1000 for production or performance testing.
- SR-IOV for accelerated packet processing: enable on the host NIC *before* deploying the VM. See [Enable SR-IOV on ESXi](https://clouddocs.f5.com/cloud/public/v1/vmware/vmware_setup.html#enable-sr-iov-on-esxi).

---

## 3.2 Linux KVM / Proxmox VE

**Official F5 guide:** [Deploy BIG-IP VE in a Linux KVM environment](https://clouddocs.f5.com/cloud/public/v1/kvm/kvm_setup.html)

> [!NOTE]
> **KVM / Proxmox prerequisites:** Ensure `libvirt` and QEMU are installed and the `kvm_intel` or `kvm_amd` kernel module is loaded. For Proxmox, you need access to the shell and a configured storage pool. Unzip the `.qcow2.zip` file before use.

### Proxmox VE (GUI method)

1. Upload the `.qcow2` file to a Proxmox storage pool: **Datacenter → Storage → Upload**
2. Create a new VM with these settings:

    | Setting | Value |
    |---------|-------|
    | OS type | Linux (5.x or later kernel) |
    | BIOS | SeaBIOS (default) |
    | CPU type | `host` |
    | CPU cores | 4 |
    | Memory | 8192 MB, no ballooning |
    | Network model | VirtIO for all interfaces |
    | Boot disk | Do not create — you will import the qcow2 |

3. Import the qcow2 as the boot disk from the Proxmox host shell:

    ```bash
    # Replace 100 with your VM ID; local-lvm with your storage pool
    qm importdisk 100 /tmp/BIGIP-17.1.1.3-0.0.4.ALL-scsi.qcow2 local-lvm
    ```

4. In the VM's **Hardware** tab, the disk appears as "Unused Disk 0" — click it → **Edit** → **Add** as `scsi0` or `virtio0`.
5. Set boot order: **Options → Boot Order** → boot from the imported disk.
6. Add NICs (one per network: management, external, internal) using **VirtIO** model, connected to the appropriate bridges.

### KVM (virt-install CLI)

```bash
# Copy the image
cp BIGIP-17.1.1.3-0.0.4.ALL-scsi.qcow2 /var/lib/libvirt/images/bigip-ve-01.qcow2

# Deploy
virt-install \
  --name bigip-ve-01 \
  --memory 8192 \
  --vcpus 4 \
  --cpu host \
  --disk /var/lib/libvirt/images/bigip-ve-01.qcow2,bus=virtio \
  --network bridge=br-mgmt,model=virtio \
  --network bridge=br-external,model=virtio \
  --network bridge=br-internal,model=virtio \
  --import \
  --os-variant rhel7 \
  --noautoconsole
```

### KVM / Proxmox notes

- Always use `virtio` NIC model for data-plane interfaces. `e1000` is functional but limits throughput.
- CPU type `host` passes through the full host instruction set — required for optimal TMM performance and some crypto acceleration paths.
- High-performance NICs: see F5 guides for [Mellanox ConnectX-5](https://clouddocs.f5.com/cloud/public/v1/kvm/kvm_mellanox.html) and [Intel X710/E810](https://clouddocs.f5.com/cloud/public/v1/kvm/kvm_intel.html).
- NIC bonding: see the [F5 KVM NIC bonding guide](https://clouddocs.f5.com/cloud/public/v1/kvm/kvm_nic_bonding.html).

---

## 3.3 Nutanix AHV (Prism)

**Official F5 guide:** [Deploy BIG-IP VE in a Nutanix AHV environment](https://clouddocs.f5.com/cloud/public/v1/nutanix/nutanix_setup.html)

> [!NOTE]
> **Nutanix prerequisites:** You need Prism Central credentials and sufficient image storage quota. The `.qcow2` format is used directly — same image as KVM.

### Steps

1. **Upload the image to the Prism image library:**
   - Prism Central → **Compute & Storage → Images → Add Image**
   - Select **File Upload** and upload the `.qcow2` file
   - Image type: **Disk**; give it a clear name (e.g., `BIGIP-17.1.1.3`)
   - Wait for processing to complete

2. **Create a new VM:**

    | Setting | Value |
    |---------|-------|
    | Name | e.g., `bigip-ve-01` |
    | vCPUs | 4 |
    | Cores per vCPU | 1 |
    | Memory | 8 GiB |

3. **Add the disk:** Click **Add Disk** → **Clone from Image Library** → select the BIG-IP image

4. **Add NICs:** Add one NIC per network (management, external, internal), each assigned to the appropriate Nutanix network/subnet

5. **Power on** and proceed to [Step 4: First Boot](./04-first-boot.md)

### Nutanix notes

- Nutanix AHV uses a `virtio`-compatible bus internally — BIG-IP VE is fully compatible.
- Cloud-init is supported for automated first-boot configuration: [Cloud-Init and BIG-IP VE](https://clouddocs.f5.com/cloud/public/v1/shared/cloudinit.html).
- **Do not** install Nutanix Guest Tools (NGT) on BIG-IP VE.

---

## Done with Step 3?

Proceed to **[Step 4: First Boot & Initial Setup →](./04-first-boot.md)**
