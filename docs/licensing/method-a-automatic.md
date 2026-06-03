# Licensing Method A — Automatic (Online) Activation

> Use when the BIG-IP management interface has direct outbound HTTPS access to the internet.

---

## Navigation

[← Back to Licensing Overview](../05-licensing.md) | [Method B: Manual →](./method-b-manual.md)

---

## When to use this method

- Your BIG-IP management interface can reach `activate.f5.com` on TCP 443
- Standard lab, PoC, or production environments without network restrictions

## When NOT to use this method

If the following check fails, use [Method B](./method-b-manual.md), [C](./method-c-ccn.md), or [D](./method-d-bigiq-pool.md) instead:

```bash
tmsh run /util ping activate.f5.com count 3
```

---

## TMUI steps

1. Navigate to **System → License → Activate**
2. Set **Activation Method** to `Automatic`
3. Paste your **Base Registration Key** (format: `XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX`)
4. Click **Next** — BIG-IP contacts `activate.f5.com`, validates the key, and returns a license summary
5. Review the licensed modules and throughput tier → click **Accept**
6. Wait ~60 seconds for licensed daemons to reload

---

## TMSH steps

```bash
# Activate with your registration key
tmsh install /sys license registration-key <XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX>

# Verify
tmsh show /sys license
```

---

## Confirm success

```bash
tmsh show /sys license | grep -E "Licensed version|Registration Key|Active Modules"
```

Expected output includes your registration key, the licensed BIG-IP version, and the list of active modules.

---

## Done?

Proceed to **[Step 6: Module Provisioning →](../06-provisioning.md)**
