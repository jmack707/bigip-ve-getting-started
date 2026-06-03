# Step 10 — Save & Validation Checklist

> Confirm the baseline configuration is complete and back it up before building application-specific config.

---

## Navigation

[← Step 9: Routing](./09-routing.md) | **Step 10: Validation** | [Troubleshooting →](./11-troubleshooting.md) | [Next Steps →](./12-next-steps.md)

---

## 10.1 Save and back up

```bash
# Write running config to disk
tmsh save /sys config

# Create a UCS backup (contains full config, certs, and license)
tmsh save /sys ucs /shared/tmp/bigip_baseline_$(date +%Y%m%d).ucs passphrase <secure-passphrase>

ls -lh /shared/tmp/*.ucs
```

> [!IMPORTANT]
> Copy the UCS file off the BIG-IP to a secure location. This is your restore point. If deploying in a CCN/air-gapped environment, follow your organization's approved data handling procedures for the backup file.

---

## 10.2 Validation checklist

| # | Item | Verification command | Expected result |
|---|------|---------------------|-----------------|
| 1 | Licensed | `tmsh show /sys license` | Shows registration key and `licensed` status |
| 2 | Modules provisioned | `tmsh list /sys provision` | Target modules: `level nominal` |
| 3 | Hostname set | `tmsh list /sys global-settings hostname` | Your FQDN |
| 4 | DNS resolves | `tmsh run /util dig activate.f5.com` | Returns an IP |
| 5 | NTP synchronized | `ntpq -p` | At least one peer shows `*` |
| 6 | Default passwords changed | Attempt login with `admin`/`admin` | Login fails |
| 7 | External VLAN | `tmsh list /net vlan external` | VLAN listed |
| 8 | Internal VLAN | `tmsh list /net vlan internal` | VLAN listed |
| 9 | External self-IP | `tmsh list /net self external-self` | IP address shown |
| 10 | Internal self-IP | `tmsh list /net self internal-self` | IP address shown |
| 11 | Default route | `tmsh list /net route default` | Gateway IP shown |
| 12 | Pool member reachable | `ping -I <internal-self-ip> <pool-member-ip>` | 0% packet loss |
| 13 | UCS backup saved | `ls -lh /shared/tmp/*.ucs` | File present, non-zero size |

---

## 10.3 One-shot status summary

```bash
echo "=== License ===" && tmsh show /sys license | grep -E "licensed|Registration|Active Mod" \
  && echo "=== Provision ===" && tmsh list /sys provision \
  && echo "=== VLANs ===" && tmsh list /net vlan \
  && echo "=== Self-IPs ===" && tmsh list /net self \
  && echo "=== Routes ===" && tmsh list /net route \
  && echo "=== NTP ===" && ntpq -pn
```

---

## Baseline complete

Your BIG-IP VE is ready for workload configuration.

- Something wrong? → **[Troubleshooting →](./11-troubleshooting.md)**
- Ready to build? → **[Next Steps →](./12-next-steps.md)**
