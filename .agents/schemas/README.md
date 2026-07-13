# SAP Router schemas

Runtime catalogs are currently stored as JSON under `.agents/registries`,
`.agents/profiles`, and `.agents/crews`. `scripts/validate_catalog.py` is the
enforced schema gate for this vertical slice.

The next hardening pass can replace these lightweight checks with full JSON
Schema files without changing the registry layout.
