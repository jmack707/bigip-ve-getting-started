# Step 9 — Default Route & Static Routes

> Add the default route so BIG-IP's data plane can reach pool members and return traffic to clients.

---

## Navigation

[← Step 8: Self-IPs](./08-self-ips.md) | **Step 9: Routing** | [Step 10: Validation →](./10-validation.md)

---

## 9.1 Default route

The default route is used by TMM for all traffic that does not match a more specific route. In most deployments it points to the external subnet gateway.

> [!NOTE]
> This is separate from the **management route** configured in Step 4. The management route only affects the management interface. This default route affects all traffic-carrying VLANs.

```bash
tmsh create /net route default gw 10.0.10.1
tmsh list /net route

# Test reachability to the upstream gateway
ping -I 10.0.10.10 10.0.10.1 count 3
```

---

## 9.2 Static routes (optional)

```bash
# Route to a server subnet not directly connected
tmsh create /net route 172.16.0.0/16 gw 10.0.20.1

tmsh save /sys config
```

---

## 9.3 Verify data-plane connectivity

```bash
# From the internal self-IP toward a pool member
ping -I 10.0.20.10 <pool-member-ip> count 5

# From the external self-IP toward the upstream gateway
ping -I 10.0.10.10 10.0.10.1 count 5

# Full route table
tmsh list /net route
```

All pings should succeed before proceeding.

---

## Done with Step 9?

Proceed to **[Step 10: Save & Validation Checklist →](./10-validation.md)**
