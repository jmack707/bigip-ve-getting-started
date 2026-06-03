# Next Steps

> Your BIG-IP VE baseline is complete. Here is what to build next.

---

## Navigation

[← Step 10: Validation](./10-validation.md) | [← README](../README.md)

---

## Create your first virtual server and pool

A virtual server is the address clients connect to. BIG-IP proxies that connection to a pool of back-end servers.

| Resource | URL |
|----------|-----|
| K14894: Overview of BIG-IP LTM virtual servers | https://support.f5.com/csp/article/K14894 |
| K6459: Overview of BIG-IP LTM pools | https://support.f5.com/csp/article/K6459 |

---

## Write iRules for custom traffic policy

iRules let you inspect, redirect, modify, or log traffic at wire speed using an event-driven Tcl-based language.

| Resource | URL |
|----------|-----|
| F5 iRules API reference | https://clouddocs.f5.com/api/irules/ |
| iRules DevCentral community | https://community.f5.com/t5/technical-articles/irules-wiki/ta-p/286140 |

---

## Deploy configuration declaratively

Instead of configuring BIG-IP object by object through the GUI or TMSH, declarative tools let you describe the desired end state in a JSON document and POST it once.

### AS3 — Application Services 3 Extension

AS3 manages **application delivery configuration**: virtual servers, pools, monitors, profiles, and policies.

| Resource | URL |
|----------|-----|
| F5 AS3 documentation | https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/ |
| AS3 schema reference | https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/refguide/schema-reference.html |
| AS3 on GitHub | https://github.com/F5Networks/f5-appsvcs-extension |

### Declarative Onboarding (DO)

DO manages **device-level configuration**: licensing, provisioning, VLANs, self-IPs, DNS, NTP, and system settings — the same things you just configured manually in Steps 4–9. Use DO to automate and version-control the baseline you just built.

| Resource | URL |
|----------|-----|
| F5 Declarative Onboarding documentation | https://clouddocs.f5.com/products/extensions/f5-declarative-onboarding/latest/ |
| DO schema reference | https://clouddocs.f5.com/products/extensions/f5-declarative-onboarding/latest/schema-reference.html |
| DO on GitHub | https://github.com/F5Networks/f5-declarative-onboarding |

> [!TIP]
> If you plan to deploy multiple BIG-IP VE instances, DO is the right investment. The configuration you just built manually maps directly to a DO declaration — you can capture it once and replay it for every future deployment.

### Ansible

| Resource | URL |
|----------|-----|
| f5-ansible collection on GitHub | https://github.com/F5Networks/f5-ansible |
| F5 Ansible Galaxy collection | https://galaxy.ansible.com/f5networks/f5_modules |

---

## Reference documentation

| Resource | URL |
|----------|-----|
| F5 CloudDocs home | https://clouddocs.f5.com |
| AskF5 Knowledge Base | https://support.f5.com/csp/home |
| TMSH Reference (17.x) | https://techdocs.f5.com/en-us/bigip-17-1-0/big-ip-tmsh-reference.html |
| BIG-IP Release Notes | https://my.f5.com/manage/s/tech-documents |
| F5 DevCentral community | https://community.f5.com |

---

*Found an error or want to contribute? See [CONTRIBUTING.md](../CONTRIBUTING.md).*
