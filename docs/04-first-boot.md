# Step 4 — First Boot & Initial Setup

> After the VM powers on, complete basic system configuration before licensing. This takes about 10 minutes.

---

## Navigation

[← Step 3: Deploy](./03-deploy.md) | **Step 4: First Boot** | [Step 5: Licensing →](./05-licensing.md)

---

## 4.1 Wait for the system to be ready

BIG-IP VE takes approximately **3–5 minutes** after first power-on before it is accessible. During this time it is expanding the filesystem, seeding the configuration database, and starting core daemons.

**How to confirm it is ready:**

```bash
# SSH to the management IP (default: admin / admin)
ssh admin@<management-ip>

# Check that mcpd is in running state
tmsh show /sys mcp-state | grep running
# Expected output: "running"
```

Or wait until `https://<management-ip>` (or `:8443` for single-NIC) returns the BIG-IP login page.

---

## 4.2 Change default passwords immediately

> [!WARNING]
> **Do this before anything else.** Default BIG-IP credentials are publicly documented. Any BIG-IP reachable on a network with default passwords is a critical security exposure.

Default credentials:
- `admin` / `admin` — TMUI (web GUI), TMSH, REST API
- `root` / `default` — Linux bash shell (SSH)

### Via TMSH

```bash
tmsh modify auth user admin password <new-password>
tmsh modify auth user root  password <new-password>
tmsh save /sys config
```

### Via TMUI

1. Log in at `https://<management-ip>` with `admin` / `admin`
2. Navigate to **System → Users → User List → admin**
3. Enter a new password and confirm → **Update**
4. Repeat for the `root` user

> [!NOTE]
> **Federal environments (DISA STIG V-236007):** Passwords must meet complexity requirements. Set a compliant password before proceeding.

---

## 4.3 Set the hostname

```bash
tmsh modify /sys global-settings hostname bigip-ve-01.example.com
tmsh save /sys config
```

---

## 4.4 Configure DNS

BIG-IP needs DNS to resolve hostnames for online license activation, NTP, and pool member FQDNs.

```bash
tmsh modify /sys dns name-servers add { 8.8.8.8 8.8.4.4 }
tmsh modify /sys dns search add { example.com }
tmsh save /sys config

# Test resolution
tmsh run /util dig activate.f5.com
```

> [!NOTE]
> **Air-gapped environments:** Use an internal DNS server reachable from the management interface. If no DNS is available, use IP addresses throughout.

---

## 4.5 Configure NTP

Time synchronization is required for TLS certificate validation, log correlation, and HA failover timing.

```bash
tmsh modify /sys ntp servers add { pool.ntp.org }
tmsh modify /sys ntp timezone US/Eastern
tmsh save /sys config

# Verify synchronization (allow 1–2 minutes)
ntpq -p
```

> [!NOTE]
> **Air-gapped environments:** Use an internal NTP server. GPS-disciplined NTP appliances are common in classified environments.

---

## 4.6 Verify or set the management IP

```bash
# Confirm current management IP, mask, and gateway
tmsh list /sys management-ip
tmsh list /sys management-route

# If not set (e.g., no DHCP and no OVA properties were used):
tmsh create /sys management-ip 192.168.1.245/24
tmsh create /sys management-route default gateway 192.168.1.1
tmsh save /sys config
```

---

## 4.7 Run the Setup Utility (optional GUI wizard)

BIG-IP includes a first-run Setup Utility accessible in the TMUI that walks through hostname, DNS, NTP, and basic network configuration. If you prefer a guided GUI experience over TMSH, navigate to **System → Setup Wizard** (or it launches automatically on first login).

You can safely skip the Setup Utility if you have already completed sections 4.3–4.6 via TMSH.

---

## 4.8 Pre-licensing checklist

Before moving to Step 5, confirm:

- [ ] Management IP is reachable from your workstation (`ping <mgmt-ip>`)
- [ ] SSH and TMUI login work with the new credentials
- [ ] Hostname is set to an FQDN
- [ ] DNS resolves internal or external hostnames
- [ ] NTP is configured
- [ ] `admin` and `root` passwords have been changed from defaults

---

## Done with Step 4?

Proceed to **[Step 5: Licensing →](./05-licensing.md)**
