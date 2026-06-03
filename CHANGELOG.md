# Changelog

All notable changes to this guide are documented here.

## [1.1.0] — 2024-06

### Added
- `docs/quick-start.md` — minimal TMSH command sequence for experienced users
- Mermaid workflow diagram in `README.md`
- GitHub Actions link-checker workflow (`.github/workflows/link-check.yml`)
- `CHANGELOG.md`
- `> [!NOTE]` / `> [!WARNING]` / `> [!IMPORTANT]` GitHub alert syntax throughout
- Platform-specific prerequisite callouts at top of each hypervisor deploy section

### Expanded — `docs/05-licensing.md`
- **Section 5.3: CCN Self-Service Utility** — full pre-approval process, authorized contact registration, dossier collection methods by version (get_dossier vs get_ccn_dossier), Secured Environment License Utility step-by-step, CCN failure contact procedures
- **Section 5.4: BIG-IQ Pool Licensing for Unreachable Devices** — architecture diagram, BIG-IQ RegKey Pool setup, management MAC collection, `regkey-pool-license.py` usage (interactive and `lic-data.json` file modes), license file transfer and application via `reloadlic`, pool license revocation
- Updated licensing method overview table to include all four paths
- Added CCN-specific entries to `docs/11-troubleshooting.md`

### Updated
- `docs/01-prerequisites.md` — added CCN pre-approval note and BIG-IQ fields to network planning worksheet
- `README.md` — updated licensing table to show all four paths; added repo layout section
- All docs — navigation links verified

## [1.0.0] — 2024-05

### Added
- Initial guide: 12 step documents covering prerequisites through next steps
- Hypervisor coverage: VMware ESXi, Linux KVM / Proxmox VE, Nutanix AHV
- Licensing coverage: automatic online, manual file-based, CCN/BIG-IQ pool (initial)
