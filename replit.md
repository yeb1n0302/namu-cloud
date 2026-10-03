# Namu Cloud

Self-hostable Flask file storage and sharing with SQLite accounts, private uploads, and revocable public download links.

## Run & Operate

- `python file-cloud/main.py` — run the Flask app locally on port 8080 after setting `SESSION_SECRET` and `UPLOAD_FOLDER`
- `cd file-cloud && python -m pip install -r requirements.txt` — install the standalone Flask service dependencies
- `cd file-cloud && gunicorn --bind 127.0.0.1:8080 --workers 2 --threads 4 --timeout 120 wsgi:app` — production WSGI command for a reverse-proxy deployment
- `pnpm --filter @workspace/api-server run dev` — run the existing Express API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- File Cloud required env: `SESSION_SECRET`, `UPLOAD_FOLDER`; optional SQLite location: `DATABASE_PATH` (defaults to `file-cloud/app.db`)
- File Cloud uses SQLite and intentionally ignores any platform-provided `DATABASE_URL`

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Existing API: Express 5
- Existing shared DB: PostgreSQL + Drizzle ORM
- Existing validation: Zod (`zod/v4`), `drizzle-zod`
- Existing API codegen: Orval (from OpenAPI spec)
- Existing build: esbuild (CJS bundle)
- File Cloud: Python 3.11+, Flask, Flask-SQLAlchemy, SQLite, server-rendered Jinja templates, Tailwind CSS CDN, and vanilla JavaScript

## Where things live

- `file-cloud/main.py` — Flask application, auth, uploads, share links, and HTTP security headers
- `file-cloud/models.py` — SQLite user and file models
- `file-cloud/templates/` and `file-cloud/static/` — complete UI templates, CSS, and browser behavior
- `file-cloud/.env.example` — local/VPS configuration template; copy it to `.env` and set a private `SESSION_SECRET`
- `file-cloud/requirements.txt` — complete Python dependency list for VPS installation
- `file-cloud/README.md` — setup, VPS, Nginx, backup, and security notes
- `lib/api-spec/openapi.yaml` — shared Express API contract
- `lib/db/src/schema/` — shared PostgreSQL schema

## Architecture decisions

- File Cloud is a separate Flask service so it does not replace the existing Express API.
- File Cloud uses `DATABASE_PATH` for SQLite rather than the workspace's injected PostgreSQL `DATABASE_URL`.
- File bytes are stored under random keys in a private folder configured by `UPLOAD_FOLDER`; user filenames are metadata only.
- Share links are signed and revocable; anyone with an enabled link can download its file.
- The Replit File Cloud workflow uses `/files-api` routes to avoid collisions with the existing `/api` service path.

## Product

Namu Cloud provides account registration and login, drag-and-drop uploads, a searchable file list, download, rename, delete, stable public share links, and share-link revocation.

## User preferences

- Build the file-sharing service in Flask with SQLite and a vanilla HTML/CSS/JavaScript frontend, with complete source files suitable for a personal VPS.
- Use environment variables for upload storage and impose a maximum upload size.

## Gotchas

- Replit injects `DATABASE_URL` for other services; File Cloud must keep using its explicit SQLite `DATABASE_PATH`.
- The Replit development workflow uses Flask's built-in server. Use Gunicorn and HTTPS behind a reverse proxy on a VPS.
- Do not commit `.env`, the SQLite database, or uploaded files; back up the database and upload directory together.
- The signed share URLs depend on `SESSION_SECRET`; rotating it invalidates existing links.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
