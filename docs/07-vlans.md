# Step 7 — VLAN Configuration

> VLANs logically segment traffic on BIG-IP data-plane interfaces. Define them before creating self-IPs or virtual servers.

---

## Navigation

[← Step 6: Provisioning](./06-provisioning.md) | **Step 7: VLANs** | [Step 8: Self-IPs →](./08-self-ips.md)

---

## 7.1 How BIG-IP VLANs map to hypervisor networks

```
Hypervisor port group / bridge / Nutanix network
        │
    vNIC (e.g., eth1 inside the VM)
        │
    BIG-IP interface (e.g., 1.1)
        │
    BIG-IP VLAN (e.g., "external")
        │
    Self-IP (e.g., 10.0.10.10/24)
```

> [!NOTE]
> BIG-IP VE numbers data-plane interfaces starting at `1.1`. The management interface is separate (`mgmt`) and never appears in VLAN config. Interface `1.1` = second vNIC = first data NIC.

---

## 7.2 Untagged vs. tagged interfaces — choose your model

The tagging mode you choose on a BIG-IP interface must match how the hypervisor port group or bridge is configured.

### Untagged (one VLAN per interface)

The most common model for VE deployments. Each physical or virtual interface carries traffic for exactly one VLAN. The hypervisor port group passes frames **without** an 802.1Q tag.

```
vNIC 1.1  ──►  port group "External-PG" (no VLAN tag)  ──►  VLAN "external"
vNIC 1.2  ──►  port group "Internal-PG" (no VLAN tag)  ──►  VLAN "internal"
```

Use this when:
- Each network segment has its own dedicated vNIC
- The hypervisor port group is configured as an **access port** (VMware: VLAN ID = 0 or blank; Proxmox: no VLAN tag on bridge port; Nutanix: single subnet assigned)

### Tagged / Trunked (multiple VLANs per interface)

A single vNIC carries multiple VLANs using 802.1Q tags. The hypervisor port group or bridge must be configured as a **trunk** that allows the relevant VLAN IDs.

```
vNIC 1.1  ──►  port group "Trunk-PG" (allows VLANs 10, 20, 30)
                    │
                    ├──►  VLAN "external"  (tag 10)
                    ├──►  VLAN "internal"  (tag 20)
                    └──►  VLAN "dmz"       (tag 30)
```

Use this when:
- You need more VLANs than available vNICs
- The hypervisor port group is configured as a trunk with the VLAN IDs allowed
- VMware: set port group VLAN ID to `4095` (VLAN trunking); Proxmox: enable VLAN-aware bridge; Nutanix: configure VLAN trunk on the network

> [!WARNING]
> Tagged and untagged modes cannot be mixed on the same BIG-IP interface. An interface is either all-untagged (one VLAN) or all-tagged (one or more VLANs with explicit tags). Attempting to add an untagged VLAN to an interface already carrying tagged VLANs will produce an error.

---

## 7.3 Baseline VLAN design

For a standard single-tenant deployment, create at minimum two VLANs:

| VLAN name | Interface | Tag | Purpose |
|-----------|-----------|-----|---------|
| `external` | `1.1` | untagged or 10 | Client-facing / upstream traffic |
| `internal` | `1.2` | untagged or 20 | Server-facing / pool members |

---

## 7.4 Create untagged VLANs

### TMUI

1. **Network → VLANs → Create**
2. **Name:** `external`
3. Under **Interfaces** → **Add** → select `1.1` → **Tagging:** `Untagged`
4. Click **Finished**
5. Repeat for `internal` (interface `1.2`, untagged)

### TMSH

```bash
# Untagged — one VLAN per dedicated interface
tmsh create /net vlan external interfaces add { 1.1 { untagged } }
tmsh create /net vlan internal interfaces add { 1.2 { untagged } }

tmsh list /net vlan
```

---

## 7.5 Create tagged VLANs (trunk mode)

Use when multiple VLANs share a single interface. Each VLAN must have a unique 802.1Q tag, and the hypervisor port group must be configured as a trunk allowing those tags.

### TMUI

1. **Network → VLANs → Create**
2. **Name:** `external`, **Tag:** `10`
3. Under **Interfaces** → **Add** → select `1.1` → **Tagging:** `Tagged`
4. Click **Finished**
5. Repeat for `internal` (same interface `1.1`, tag `20`, tagged)
6. Repeat for additional VLANs as needed

### TMSH

```bash
# Tagged — multiple VLANs sharing interface 1.1
tmsh create /net vlan external tag 10 interfaces add { 1.1 { tagged } }
tmsh create /net vlan internal tag 20 interfaces add { 1.1 { tagged } }
tmsh create /net vlan dmz      tag 30 interfaces add { 1.1 { tagged } }

tmsh list /net vlan
```

> [!NOTE]
> The `tag` value in the TMSH command is the 802.1Q VLAN ID — it must match the VLAN ID configured on the upstream switch or hypervisor trunk port.

---

## 7.6 Hypervisor trunk configuration quick reference

| Hypervisor | How to configure a trunk port group |
|------------|-------------------------------------|
| **VMware ESXi** | Edit the port group → set **VLAN ID** to `4095` (promiscuous trunking) or use a distributed vSwitch port group with a VLAN trunk range |
| **Proxmox VE** | Enable **VLAN aware** on the Linux bridge; set the VLAN tag on the VM's network device, or leave untagged for the bridge to pass raw tagged frames |
| **Nutanix AHV** | Create a network with **VLAN trunking** enabled in Prism; assign the trunk network to the VM NIC |

---

## 7.7 Verify interface and VLAN status

```bash
# Check interface link state
tmsh show /net interface

# Confirm VLANs are created correctly
tmsh list /net vlan

# Expected: each VLAN shows its interface(s) and tag/untagged setting
```

If an interface shows `down`: verify the vNIC is connected to the correct port group or bridge in the hypervisor.

---

## Done with Step 7?

Proceed to **[Step 8: Self-IP Addresses →](./08-self-ips.md)**
