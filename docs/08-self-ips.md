# Step 8 — Self-IP Addresses

> Self-IPs give BIG-IP a routable address on each VLAN. Required before creating virtual servers or testing pool connectivity.

---

## Navigation

[← Step 7: VLANs](./07-vlans.md) | **Step 8: Self-IPs** | [Step 9: Routing →](./09-routing.md)

---

## 8.1 What is a self-IP?

A self-IP is the BIG-IP system's own IP address on a specific VLAN. Used for: health monitor source IPs, SNAT origins, HA communication, and management-plane tasks on the data plane.

---

## 8.2 Port lockdown best practice

| Setting | Inbound permitted | When to use |
|---------|------------------|-------------|
| `Allow None` | Nothing | **All data-plane self-IPs in production** |
| `Allow Defaults` | F5-defined management protocols | Avoid except on HA self-IPs |
| `Allow All` | Everything | Never in production |

> [!IMPORTANT]
> Set `Allow None` on all external and internal self-IPs. DISA STIG V-236010 specifically requires restricting self-IP port lockdown. HA self-IPs are the exception — they require `Allow Default` to permit config-sync and failover traffic.

---

## 8.3 Create self-IPs

### TMSH

```bash
tmsh create /net self external-self \
    address 10.0.10.10/24 \
    vlan external \
    allow-service none

tmsh create /net self internal-self \
    address 10.0.20.10/24 \
    vlan internal \
    allow-service none

tmsh save /sys config
tmsh list /net self
```

---

## 8.4 Floating self-IPs (HA deployments only)

Floating self-IPs move to the active unit on failover. Pool members should use the floating self-IP as their gateway.

```bash
tmsh create /net self external-float \
    address 10.0.10.11/24 \
    vlan external \
    allow-service none \
    traffic-group traffic-group-1

tmsh create /net self internal-float \
    address 10.0.20.11/24 \
    vlan internal \
    allow-service none \
    traffic-group traffic-group-1

tmsh save /sys config
```

> Not required for standalone single-node lab deployments.

---

## Done with Step 8?

Proceed to **[Step 9: Default Route & Static Routes →](./09-routing.md)**
