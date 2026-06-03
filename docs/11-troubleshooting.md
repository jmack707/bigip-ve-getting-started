# Troubleshooting

> Common issues during initial BIG-IP VE deployment, organized by phase.

---

## Navigation

[← Step 10: Validation](./10-validation.md) | [Next Steps →](./12-next-steps.md) | [← README](../README.md)

---

## Deployment issues

### GUI is unreachable after first boot

| Check | Action |
|-------|--------|
| VM fully booted? | Allow 5 min after power-on; watch for login prompt in hypervisor console |
| Single-NIC deployment? | Try `https://<mgmt-ip>:8443` instead of `:443` |
| Management IP set? | Console: `ip addr show mgmt` or `tmsh list /sys management-ip` |
| Firewall blocking? | `curl -k https://<mgmt-ip>` from the hypervisor host itself |

### SSH "Connection refused"

SSHD may not have started yet. Wait 2–3 min after the GUI is accessible, then retry. If persistently refused:

```bash
# From the VM console (root login)
tmsh modify /sys sshd allow { ALL }
tmsh save /sys config
```

### Setting management IP from the console (no DHCP, no OVA properties)

```bash
# Log in as root (default: root / default) at the console
config
# Text-based config utility launches — select option 1 (Management Interface)
```

Or directly:

```bash
tmsh create /sys management-ip 192.168.1.245/24
tmsh create /sys management-route default gateway 192.168.1.1
tmsh save /sys config
```

---

## Licensing issues

### Online activation: "Unable to connect to activation server"

```bash
# Check DNS
tmsh run /util dig activate.f5.com

# Check outbound 443 from bash
curl -v https://activate.f5.com

# If blocked → use manual (5.2), CCN (5.3), or BIG-IQ pool (5.4)
```

### BIG-IQ pool checkout: "Authentication failure"

```bash
ping <bigiq-ip> count 3
curl -k https://<bigiq-ip>/mgmt/shared/echo
# Verify credentials by logging into BIG-IQ GUI from a browser
# Pool name is case-sensitive — confirm in BIG-IQ → License Management → Licenses
```

### BIG-IQ unreachable device script: "License Assignment Failed"

A valid license is likely already checked out for that MAC address. Revoke it in BIG-IQ (Devices → LICENSE MANAGEMENT → Licenses → [pool] → find device → Revoke) before re-running the script.

### CCN license not activating after `reloadlic`

1. Verify the file is named exactly `bigip.license` and is in `/config/`
2. Check that the file contents are plain text (not wrapped in a ZIP or email)
3. Run `tmsh show /sys license` — if still unlicensed, run `reloadlic` again
4. If the license still does not activate, call **1-888-882-7535** and reference the ticket; include "CCN FAILURE REPORT" in any email to [licensingsupport@f5.com](mailto:licensingsupport@f5.com)

### License pool exhausted

All licenses in the BIG-IQ pool are checked out.

```bash
# Identify idle instances via BIG-IQ GUI:
# Devices → LICENSE MANAGEMENT → Managed Devices → filter by Last Contact

# Revoke an idle instance (on the BIG-IP if still reachable)
tmsh revoke /sys license \
    bigiq-addr <bigiq-ip> \
    bigiq-user admin \
    bigiq-password <bigiq-password> \
    bigiq-port 443 \
    pool-name 'BIG-IP-VE-Pool-FEDRAMP'
```

Contact your F5 account team to expand the pool if needed.

---

## VLAN and interface issues

### Interface shows "down" after VLAN creation

| Check | Action |
|-------|--------|
| vNIC connected in hypervisor? | VMware: check port group; Proxmox: check bridge; Nutanix: check network assignment |
| VLAN ID mismatch? | If using tagged interfaces, confirm hypervisor port group trunk allows the VLAN ID |
| Interface number correct? | `tmsh show /net interface` — confirm 1.1, 1.2 are present |

### Self-IP creation fails: "The requested Self IP overlaps"

```bash
tmsh list /net self
# Remove conflicting entry (e.g., leftover from single-NIC auto-config)
tmsh delete /net self self_1nic
```

### Cannot ping pool members from self-IP

```bash
# Check ARP table — does BIG-IP know the pool member MAC?
tmsh show /net arp | grep <pool-member-ip>

# If no entry: check physical/virtual connectivity
# Verify pool member's default gateway points to the BIG-IP internal self-IP
tmsh list /net route
```

---

## Module provisioning issues

### System unresponsive after provisioning multiple modules

Likely insufficient RAM. Check swap:

```bash
# From bash (run 'bash' from tmsh, or log in as root)
free -m
top
```

If swap is heavily used: reduce provisioned modules or increase VM memory and reboot.

---

## Getting help

| Channel | Details |
|---------|---------|
| AskF5 Knowledge Base | https://support.f5.com/csp/home |
| F5 DevCentral community | https://community.f5.com |
| F5 Support (contract) | https://my.f5.com/manage/s/createcase |
| CCN licensing issues | 1-888-882-7535 or licensingsupport@f5.com |
| Bug tracker | https://my.f5.com/manage/s/bug-tracker |
