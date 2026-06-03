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

## 7.2 Baseline two-VLAN design

| VLAN name | Interface | Purpose |
|-----------|-----------|---------|
| `external` | `1.1` | Client-facing / upstream traffic |
| `internal` | `1.2` | Server-facing / pool members |
| `ha` (optional) | `1.3` | HA heartbeat for active/standby pair |

---

## 7.3 Create VLANs

### TMUI

1. **Network → VLANs → Create**
2. Set **Name** (e.g., `external`)
3. Under **Interfaces** → **Add** → select `1.1` → **Tagging**: `Untagged`
4. **Finished** — repeat for `internal` (interface `1.2`)

### TMSH

```bash
tmsh create /net vlan external interfaces add { 1.1 { untagged } }
tmsh create /net vlan internal interfaces add { 1.2 { untagged } }
tmsh create /net vlan ha      interfaces add { 1.3 { untagged } }  # optional

tmsh list /net vlan
```

---

## 7.4 Tagged vs. untagged

| Setting | When to use |
|---------|-------------|
| `Untagged` | One VLAN per interface — hypervisor port group carries untagged traffic. Most common for VE. |
| `Tagged` | 802.1Q trunking — multiple VLANs share one interface. Requires the hypervisor port group configured as a trunk. |

Use `Untagged` on dedicated interfaces for a getting-started deployment.

---

## 7.5 Verify interface status

```bash
tmsh show /net interface

# Interface 1.1 and 1.2 should show status: up
# If down: check vNIC → port group / bridge assignment in hypervisor
```

---

## Done with Step 7?

Proceed to **[Step 8: Self-IP Addresses →](./08-self-ips.md)**
