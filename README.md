# BIG-IP VE — Customer Getting Started Guide

> **From download to first virtual server** — a complete guide for customers new to F5 BIG-IP Virtual Edition on on-premises hypervisors.

---

## Who this guide is for

Infrastructure engineers and architects deploying BIG-IP Virtual Edition (VE) for the first time on an on-premises or private-cloud hypervisor. It assumes working hypervisor admin knowledge but **no prior BIG-IP experience**.

For public cloud deployments (AWS, Azure, GCP), see the [F5 CloudDocs public cloud index](https://clouddocs.f5.com/cloud/public/v1/index.html) instead.

---

## Deployment workflow

```mermaid
flowchart LR
    A([Start]) --> B[1. Prerequisites]
    B --> C[2. Download Image]
    C --> D[3. Deploy VM]
    D --> E[4. First Boot]
    E --> F{License\nmethod?}
    F -->|Online| G[Auto Activation]
    F -->|Jump host| H[File-Based]
    F -->|Air-gapped / Federal| I[CCN / BIG-IQ Pool]
    G --> J[6. Provision Modules]
    H --> J
    I --> J
    J --> K[7. VLANs]
    K --> L[8. Self-IPs]
    L --> M[9. Routing]
    M --> N[10. Validate & Backup]
    N --> O([Done ✓])

    style I fill:#c00,color:#fff
    style F fill:#2E5FA3,color:#fff
```

---

## Guide structure

Work through these in order. Each is a standalone document in [`docs/`](./docs/).

| Step | Document | Est. time |
|------|----------|-----------|
| 1 | [Prerequisites & Minimum Requirements](./docs/01-prerequisites.md) | 10 min |
| 2 | [Downloading the BIG-IP VE Image](./docs/02-download.md) | 10 min |
| 3 | [Deploying the VM](./docs/03-deploy.md) | 15–30 min |
| 4 | [First Boot & Initial Setup](./docs/04-first-boot.md) | 10 min |
| 5 | [Licensing](./docs/05-licensing.md) | 5–15 min |
| 6 | [Module Provisioning](./docs/06-provisioning.md) | 5 min |
| 7 | [VLAN Configuration](./docs/07-vlans.md) | 10 min |
| 8 | [Self-IP Addresses](./docs/08-self-ips.md) | 5 min |
| 9 | [Default Route & Static Routes](./docs/09-routing.md) | 5 min |
| 10 | [Save & Validation Checklist](./docs/10-validation.md) | 5 min |
| — | [Quick-Start Cheat Sheet](./docs/quick-start.md) | Reference |
| — | [Troubleshooting](./docs/11-troubleshooting.md) | Reference |
| — | [Next Steps](./docs/12-next-steps.md) | Reference |

---

## Experienced user?

If you've deployed BIG-IP before and just need the command sequence, go straight to the **[Quick-Start Cheat Sheet](./docs/quick-start.md)**.

---

## Hypervisor coverage

| Hypervisor | Covered | Image format | F5 CloudDocs |
|------------|---------|--------------|--------------|
| VMware ESXi (vSphere 6.7+) | ✅ | `.ova` | [vmware_index](https://clouddocs.f5.com/cloud/public/v1/vmware_index.html) |
| Linux KVM / Proxmox VE | ✅ | `.qcow2` | [kvm_index](https://clouddocs.f5.com/cloud/public/v1/kvm_index.html) |
| Nutanix AHV (Prism Central) | ✅ | `.qcow2` | [nutanixAHV_index](https://clouddocs.f5.com/cloud/public/v1/nutanixAHV_index.html) |

---

## BIG-IP version coverage

Applies to BIG-IP VE **15.x, 16.x, and 17.x**. Always cross-check hypervisor compatibility against the [BIG-IP VE Supported Platforms matrix](https://clouddocs.f5.com/cloud/public/v1/matrix.html) before deploying. Check [K5903](https://support.f5.com/csp/article/K5903) for the technical support lifecycle of your chosen version.

---

## Licensing paths covered

| Method | Requires internet? | When to use |
|--------|--------------------|-------------|
| Automatic (online) | ✅ Yes | Internet-connected labs and standard environments |
| Manual (file-based) | ❌ No | Jump host can reach portal; BIG-IP cannot |
| CCN Self-Service Utility | ❌ No | True air-gap; no BIG-IQ on-site; requires F5 pre-approval |
| BIG-IQ Pool (unreachable device) | ❌ No | BIG-IQ deployed inside the restricted enclave; ELA/pool licensing |

---

## Repository layout

```
bigip-ve-getting-started/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       └── link-check.yml
└── docs/
    ├── quick-start.md
    ├── 01-prerequisites.md
    ├── 02-download.md
    ├── 03-deploy.md
    ├── 04-first-boot.md
    ├── 05-licensing.md          ← expanded with CCN + BIG-IQ unreachable device
    ├── 06-provisioning.md
    ├── 07-vlans.md
    ├── 08-self-ips.md
    ├── 09-routing.md
    ├── 10-validation.md
    ├── 11-troubleshooting.md
    └── 12-next-steps.md
```

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

---

*Maintained by the F5 Federal Solutions Engineering team. Not an official F5 product document.*
