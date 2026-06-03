# Step 8 — Self-IP Addresses

> Self-IPs give BIG-IP a routable IP address on each VLAN. They are required before creating virtual servers or testing pool member connectivity.

---

## Navigation

[← Step 7: VLANs](./07-vlans.md) | **Step 8: Self-IPs** | [Step 9: Routing →](./09-routing.md)

---

## 8.1 What is a self-IP?

A self-IP is the BIG-IP system's own IP address on a specific VLAN — distinct from virtual server addresses, which are addresses BIG-IP listens on behalf of applications.

Self-IPs are used for:

- **Health monitors** — source IP when BIG-IP probes pool members
- **SNAT** — source address for outbound connections from pool members
- **Routing** — next-hop gateway for servers whose default route points to BIG-IP
- **Management-plane tasks on the data plane** — more on this below

---

## 8.2 Port lockdown — what it controls and why it matters

Every self-IP has a **Port Lockdown** setting. This controls what traffic is permitted **inbound to the BIG-IP system itself** on that IP address. It does **not** affect traffic passing through BIG-IP to pool members or virtual servers — it only governs traffic whose destination *is* the BIG-IP.

### Why this matters

If port lockdown is set permissively on a self-IP, the BIG-IP management plane becomes reachable from the data-plane network on that IP. For example:

- With **Allow Default** on the external self-IP: the BIG-IP SSH and HTTPS management interfaces are reachable by anyone who can route to `10.0.10.10` — including external clients
- With **Allow None**: no inbound management traffic is accepted on that IP

### Port lockdown settings explained

| Setting | What is accepted inbound to the self-IP | Use when |
|---------|----------------------------------------|----------|
| `Allow None` | Nothing — all inbound traffic to the self-IP is dropped | **Recommended for all production data-plane self-IPs** |
| `Allow Default` | A fixed set of F5-defined protocols: SSH (22), HTTPS (443), SNMP (161), ICMP, and a few others | Use on HA self-IPs; use cautiously elsewhere |
| `Allow Custom` | Only the specific ports and protocols you define | When a specific service must be reachable on a self-IP |
| `Allow All` | Everything | Never use in production |

### Practical example: when to allow ports on a self-IP

If you want to **manage the BIG-IP** (SSH or browser-based GUI) using a self-IP address rather than the dedicated management interface, you must open those ports in port lockdown:

```
Allow Custom:
  tcp:22    → enables SSH to the BIG-IP via this self-IP
  tcp:443   → enables TMUI (web GUI) access via this self-IP
```

> [!IMPORTANT]
> This is a deliberate, consciously scoped choice. Opening 22 and 443 on the **internal** self-IP lets server-side administrators reach the BIG-IP GUI. Opening them on the **external** self-IP exposes management to your upstream network and clients. Use the dedicated management interface whenever possible and keep self-IP port lockdown as restrictive as your environment allows.

> [!NOTE]
> **DISA STIG V-236010** requires restricting self-IP port lockdown. The compliant baseline is `Allow None` on all data-plane self-IPs, with specific ports opened only where documented and justified.

---

## 8.3 Create self-IPs

### TMUI

1. Navigate to **Network → Self IPs → Create**
2. Enter **Name**, **IP Address** (with prefix length, e.g. `10.0.10.10/24`), select the **VLAN**
3. Set **Port Lockdown** to the appropriate setting
4. Click **Finished** — repeat for each VLAN

### TMSH

```bash
# External self-IP — no management access permitted on this IP
tmsh create /net self external-self \
    address 10.0.10.10/24 \
    vlan external \
    allow-service none

# Internal self-IP — no management access permitted on this IP
tmsh create /net self internal-self \
    address 10.0.20.10/24 \
    vlan internal \
    allow-service none

tmsh save /sys config
tmsh list /net self
```

### Allow SSH and HTTPS on a self-IP (if required)

```bash
# Example: allow management access on the internal self-IP only
tmsh create /net self internal-self \
    address 10.0.20.10/24 \
    vlan internal \
    allow-service add { tcp:22 tcp:443 }
```

Or to modify an existing self-IP:

```bash
tmsh modify /net self internal-self allow-service add { tcp:22 tcp:443 }
tmsh save /sys config
```

---

## 8.4 Verify self-IPs

```bash
tmsh list /net self

# Expected output for each self-IP:
# net self external-self {
#     address 10.0.10.10/24
#     allow-service none
#     vlan external
# }
```

Test basic reachability from the hypervisor host or a device on the same subnet:

```bash
ping 10.0.10.10   # from a device on the external subnet
ping 10.0.20.10   # from a device on the internal subnet
```

---

## Done with Step 8?

Proceed to **[Step 9: Default Route & Static Routes →](./09-routing.md)**
