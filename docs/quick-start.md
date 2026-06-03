# Quick-Start Cheat Sheet

> Minimal command sequence for experienced engineers. No prose, just the steps. All commands assume BIG-IP 15.x+.

---

## 0 — Download

| Hypervisor | Image | Source |
|------------|-------|--------|
| VMware ESXi | `.ova` | [my.f5.com](https://my.f5.com) → Downloads → BIG-IP → Virtual Edition |
| KVM / Proxmox | `.qcow2` | Same |
| Nutanix AHV | `.qcow2` | Same |

---

## 1 — Deploy & boot

```bash
# VMware — import OVA
ovftool --name="bigip-ve-01" \
  --prop:net.mgmt.addr="192.168.1.245/24" \
  --prop:net.mgmt.gw="192.168.1.1" \
  BIGIP-17.x.x.ova  vi://admin@vcenter/dc/host/esxi

# KVM — deploy qcow2
cp BIGIP-17.x.x.qcow2 /var/lib/libvirt/images/bigip-ve-01.qcow2
virt-install --name bigip-ve-01 --memory 8192 --vcpus 4 --cpu host \
  --disk /var/lib/libvirt/images/bigip-ve-01.qcow2,bus=virtio \
  --network bridge=br-mgmt,model=virtio \
  --network bridge=br-ext,model=virtio \
  --network bridge=br-int,model=virtio \
  --import --os-variant rhel7 --noautoconsole

# Proxmox — import disk after VM creation
qm importdisk <vmid> BIGIP-17.x.x.qcow2 <storage-pool>
```

---

## 2 — First boot (SSH or console)

```bash
# Change passwords
tmsh modify auth user admin password <new-password>
tmsh modify auth user root  password <new-password>

# Hostname, DNS, NTP
tmsh modify /sys global-settings hostname bigip-ve-01.example.com
tmsh modify /sys dns name-servers replace-all-with { 8.8.8.8 8.8.4.4 }
tmsh modify /sys ntp servers replace-all-with { pool.ntp.org }
tmsh save /sys config
```

---

## 3 — License

```bash
# Option A: Online
tmsh install /sys license registration-key <XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX>

# Option B: BIG-IQ pool (unreachable/air-gapped)
tmsh install /sys license \
  bigiq-addr <bigiq-ip> bigiq-user admin bigiq-password <pass> \
  bigiq-port 443 pool-name '<pool-name>' skipped-discovery true

# Option C: CCN Self-Service — collect dossier, submit to portal
tmsh run /util get-dossier registration-key <reg-key>
# Submit output to https://secure.f5.com/ccn/index.jsp
# Apply returned license file:
tmsh install /sys license file /shared/tmp/bigip.license
```

---

## 4 — Provision modules

```bash
tmsh modify /sys provision ltm level nominal
# Add others as licensed: asm, apm, afm, gtm
tmsh save /sys config
watch -n 3 'tmsh show /sys mcp-state | grep running'
```

---

## 5 — VLANs

```bash
tmsh create /net vlan external interfaces add { 1.1 { untagged } }
tmsh create /net vlan internal interfaces add { 1.2 { untagged } }
```

---

## 6 — Self-IPs

```bash
tmsh create /net self external-self address 10.0.10.10/24 vlan external allow-service none
tmsh create /net self internal-self address 10.0.20.10/24 vlan internal allow-service none
```

---

## 7 — Route & save

```bash
tmsh create /net route default gw 10.0.10.1
tmsh save /sys config
tmsh save /sys ucs /shared/tmp/bigip_baseline_$(date +%Y%m%d).ucs passphrase <passphrase>
```

---

## 8 — Verify

```bash
tmsh show /sys license | grep -E "licensed|Active"
tmsh list /sys provision
tmsh list /net vlan
tmsh list /net self
tmsh list /net route
ntpq -pn
```

---

[← README](../README.md) | [Full guide: Step 1 →](./01-prerequisites.md)
