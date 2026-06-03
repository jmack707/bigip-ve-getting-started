# Step 5 — Licensing

> Activate your BIG-IP VE license. Choose the method that matches your network environment and follow it end to end.

---

## Navigation

[← Step 4: First Boot](./04-first-boot.md) | **Step 5: Licensing** | [Step 6: Module Provisioning →](./06-provisioning.md)

---

## Choose your licensing method

| Method | BIG-IP internet access? | BIG-IQ required? | When to use |
|--------|------------------------|------------------|-------------|
| [Method A — Automatic (online)](./licensing/method-a-automatic.md) | ✅ Yes | ❌ No | BIG-IP management can reach `activate.f5.com:443` directly |
| [Method B — Manual (file-based)](./licensing/method-b-manual.md) | ❌ No | ❌ No | A jump host can reach the F5 portal; the BIG-IP cannot |
| [Method C — CCN Self-Service Utility](./licensing/method-c-ccn.md) | ❌ No | ❌ No | True air-gap; no BIG-IQ on-site; requires F5 CCN pre-approval |
| [Method D — BIG-IQ Pool (unreachable device)](./licensing/method-d-bigiq-pool.md) | ❌ No | ✅ Yes | BIG-IQ has internet access; generates license and transfers it to BIG-IP |

> [!TIP]
> **Not sure which to use? Run this first:**
> ```bash
> tmsh run /util ping activate.f5.com count 3
> ```
> If it succeeds → **Method A**. If it fails → choose B, C, or D based on your environment.

---

## After licensing

Once your BIG-IP shows a valid license, return here and proceed to:

**[Step 6: Module Provisioning →](./06-provisioning.md)**
