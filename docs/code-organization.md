# Code organization audit

## Current boundaries

- `backend/erp_backend/`: Django settings, URL routing, and WSGI entrypoint.
- `backend/master_data/`: REST API views, serializers, exports, and URLs.
- `backend/domain/`: business-domain services grouped by sales, purchasing, inventory, engineering, master data, and system concerns.
- `backend/importing/`: import models, services, views, and migrations.
- `backend/management/commands/`: operational import and verification commands.
- `backend/migrations/`: Django schema history; keep these files intact.
- `src/app/`, `src/auth/`, `src/api/`, `src/components/`, `src/modules/`: frontend shell, authentication, API access, reusable UI, and business modules.

## Large-file follow-up candidates

The largest business files are `backend/models.py` (about 2,090 lines),
`backend/master_data/serializers.py` (about 834 lines), and
`src/styles.css` (about 545 lines). They are not safe to split mechanically:
the next refactor should extract one bounded domain at a time, add focused tests,
and preserve Django migration dependencies. Historical migration files are
large by design and should not be removed.

## Excluded local artifacts

Git now ignores SQLite databases and backups, uploaded media, `node_modules`,
Vite output, Python caches, temporary inspection output, IDE metadata, and
environment files. These are machine-local or generated and should not be
part of the source distribution.
