# Next Steps

> Your BIG-IP VE baseline is complete. Here is what to build next.

---

## Navigation

[← Step 10: Validation](./10-validation.md) | [← README](../README.md)

---

## Immediate next tasks

| Task | Starting point |
|------|----------------|
| Create first virtual server and pool | [K14894: Overview of BIG-IP LTM virtual servers](https://support.f5.com/csp/article/K14894) |
| Write an iRule for custom traffic policy | [DevCentral iRules Wiki](https://community.f5.com/t5/technical-articles/irules-wiki/ta-p/286140) |
| Deploy config via AS3 (declarative) | [F5 AS3 documentation](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/) |
| Deploy config via Ansible | [f5-ansible on GitHub](https://github.com/F5Networks/f5-ansible) |

---

## Kubernetes / cloud-native integration

| Integration | Use case |
|-------------|----------|
| **BIG-IP CIS** (Container Ingress Services) | Watches Kubernetes resources and automatically configures BIG-IP virtual servers and pools |
| **IngressLink** (BIG-IP + NGINX Ingress) | CIS manages the BIG-IP front-end; NGINX Ingress handles L7 routing inside the cluster |

Reference lab: [acme-f5-demo — two-site Kubernetes lab](https://github.com/jmack707/acme-f5-demo)

---

## High availability (active/standby pair)

Deploy a second BIG-IP VE, complete this guide for the second unit, then:

1. Configure Device Trust between the two units
2. Create a Sync-Failover Device Group
3. Add floating self-IPs to each VLAN (traffic-group-1)
4. Perform an initial config sync

Reference: [K2333: Overview of BIG-IP device service clustering](https://support.f5.com/csp/article/K2333)

---

## Security hardening (Federal / STIG)

Apply the DISA STIG after baseline configuration is confirmed working.

| Resource | URL |
|----------|-----|
| DISA BIG-IP STIG | https://public.cyber.mil/stigs/downloads/ |
| F5 STIG readiness guide | https://support.f5.com/csp/article/K02099340 |
| NIST SP 800-207 Zero Trust | https://csrc.nist.gov/publications/detail/sp/800-207/final |

---

## Reference documentation

| Resource | URL |
|----------|-----|
| F5 CloudDocs home | https://clouddocs.f5.com |
| AskF5 Knowledge Base | https://support.f5.com/csp/home |
| TMSH Reference (17.x) | https://techdocs.f5.com/en-us/bigip-17-1-0/big-ip-tmsh-reference.html |
| BIG-IP Release Notes | https://my.f5.com/manage/s/tech-documents |
| F5 DevCentral | https://community.f5.com |

---

*If you found an error or want to contribute an improvement, see [CONTRIBUTING.md](../CONTRIBUTING.md).*
