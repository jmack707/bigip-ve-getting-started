# Contributing

Corrections, additions, and hypervisor-specific improvements are welcome.

## Editorial standards

- Write for a reader who knows their hypervisor but has never touched BIG-IP
- Prefer TMSH commands over GUI-only instructions — they are reproducible and scriptable
- Test every TMSH command on BIG-IP 16.x or 17.x before submitting
- Link to official F5 documentation rather than reproducing it — F5 docs change; we link, not copy
- Keep each step document independently navigable — a reader may enter at any step
- Use GitHub alert syntax for callouts:
  - `> [!NOTE]` — informational
  - `> [!TIP]` — helpful suggestion
  - `> [!WARNING]` — something that commonly causes failure
  - `> [!IMPORTANT]` — critical, e.g. security or federal compliance

## Pull request checklist

- [ ] Markdown renders correctly in GitHub preview
- [ ] All hyperlinks resolve (the link-check CI will verify on push)
- [ ] TMSH commands tested on a real or UDF-based BIG-IP instance
- [ ] Navigation links at top and bottom updated if new sections are added
- [ ] CHANGELOG.md updated with a summary of the change

## Reporting issues

Open a GitHub Issue:
- Label `doc-error` for broken links or factual errors
- Label `enhancement` for suggestions and additions
- Label `platform-specific` for hypervisor-specific corrections
