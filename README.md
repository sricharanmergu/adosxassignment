# AdosX Assignment

AdosX Assignment is a small ledger review tool. It loads the supplied location map and the two transaction exports, then highlights records that need attention. The interface focuses on exceptions; successfully matched entries are not listed in the review table.

## Components

- **Django REST Framework** provides the import and reconciliation API.
- **SQLite** stores the imported records both locally and in the configured Vercel build.
- **React and Vite** render the review screen.
- **Decimal values** are used for exact monetary comparisons.

## Start locally (PowerShell)

From the repository folder, prepare the Python environment and load the supplied data:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

In another terminal, from the repository folder, start the interface:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite address printed in that terminal. Its development proxy sends `/api` requests to Django at `http://127.0.0.1:8000`. The API can also be opened directly at `http://127.0.0.1:8000/api/disagreements/?org=ORG-A`; replace `ORG-A` with `ORG-B` to view the other organization. Optional filters include `reason` and `sort=value` or `sort=-value`.

The CSV inputs are in `backend/data/`. To load a different directory, use `python manage.py import_data --data-dir PATH`. Re-running the importer updates records using their stable source IDs.

## Reconciliation behavior

System B entries are grouped by normalized record reference and checked against System A. The comparison reports records missing from B, B-only references, duplicate entries, and differences in value, date, or location. Multiple B entries count as a valid split when their sum matches A's total. Source rows and raw amount strings are retained so unusual input remains inspectable.

The location mapping determines organization ownership. A matched record follows the System A location; an orphan follows its B location. The API omits a foreign B location from the response when that location belongs to another organization.

The organization control is a demo filter, not an authentication boundary. Do not use this version to protect real tenant data.

## Deploy to Vercel

The repository is configured for a **single Vercel project using Services**. Import the repository with root directory `./` and select the Services preset. The root `vercel.json` routes `/api/...` to Django and other paths to the Vite frontend.

1. Add `DJANGO_SECRET_KEY` under the Vercel project's environment variables. Generate a value locally with `python -c "import secrets; print(secrets.token_urlsafe(50))"` and keep it private.
2. Deploy. During the backend build, migrations run and the three CSV files are imported into SQLite.
3. The deployed function reads the preloaded database. Vercel's function filesystem is read-only at runtime, so this deployment does not support persistent database edits.

The public demo has no sign-in flow. Anyone who can access its URL can inspect the assignment data.

## Review discussion prompts

### A. What did the AI assistant initially get wrong, and how did I catch it?

It tried to write Django settings into `backend/config` before that directory existed. The command reported that the path was missing; I created the package directory and continued with the setup. This was a project bootstrap issue.

### B. Which part would I ask a reviewer to examine most closely?

I would review tenant visibility. Matched records belong to the organization on the A-side location, and foreign B location details are hidden. Orphans follow their B location. I would confirm whether the product should expose even the existence and values of a cross-organization match before using this rule with real customers.

### C. What would I prioritize with one more day?

I would add authentication and derive organization access from the signed-in user's membership. The current organization selector is only a demo filter and does not establish a user's identity or permissions.

## Assistance note

Codex assisted with inspecting the assignment data, implementing the importer, comparator, API, and interface, and drafting these project notes. During setup, I corrected the missing `backend/config` directory after the shell reported the path error. I also reviewed tenant scoping and added a regression case for a B entry whose reference is associated with a different tenant.
