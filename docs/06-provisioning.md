# Step 6 — Module Provisioning

> Licensing activates the platform. Provisioning allocates memory and CPU to specific modules so they can run. Only provision what you need.

---

## Navigation

[← Step 5: Licensing](./05-licensing.md) | **Step 6: Module Provisioning** | [Step 7: VLANs →](./07-vlans.md)

---

## 6.1 What is provisioning?

BIG-IP modules (LTM, APM, AWAF, etc.) are not enabled just because they appear in your license. Each module must be **provisioned** — which reserves a slice of the system's RAM and CPU for that module's daemons.

| Provisioning level | Meaning |
|-------------------|---------|
| `none` | Module is not running; consumes no resources |
| `minimum` | Loaded with minimal resources; limited functionality |
| `nominal` | Standard allocation — use this for lab and production |
| `dedicated` | All available resources to one module only |

Use `nominal` for all modules in standard deployments.

---

## 6.2 Common module combinations

| Use case | Modules to provision |
|----------|---------------------|
| Basic load balancing (L4/L7) | `ltm` |
| Load balancing + WAF | `ltm`, `asm` |
| Load balancing + remote access VPN | `ltm`, `apm` |
| DNS / GSLB | `ltm`, `gtm` |
| Network firewall | `ltm`, `afm` |
| Full security stack | `ltm`, `asm`, `afm`, `apm` |

> [!WARNING]
> Each additional module increases memory consumption. On a 4 GB VE, provisioning LTM + ASM + APM simultaneously may cause swap usage and degraded performance. Size the VM before provisioning multiple modules.

---

## 6.3 Provision modules

### TMUI

Navigate to **System → Resource Provisioning**, set target modules to `Nominal`, click **Submit**. Wait for all services to return green.

### TMSH

```bash
# LTM is required for virtually all configs
tmsh modify /sys provision ltm level nominal

# Add others as licensed
tmsh modify /sys provision asm level nominal   # AWAF / ASM
tmsh modify /sys provision apm level nominal   # APM
tmsh modify /sys provision afm level nominal   # AFM
tmsh modify /sys provision gtm level nominal   # DNS / GTM

tmsh save /sys config

# Monitor — wait for all modules to show 'running'
watch -n 3 'tmsh show /sys mcp-state | grep running'
```

Provisioning changes take **60–120 seconds** to apply. Do not proceed to VLAN configuration until the system is fully back up.

---

## 6.4 Verify

```bash
tmsh list /sys provision
# Target modules should show: level nominal

tmsh show /sys service | grep -E "tmm|mcpd"
```

---

## Done with Step 6?

Proceed to **[Step 7: VLAN Configuration →](./07-vlans.md)**
