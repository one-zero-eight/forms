
# Agent guide: architecture and feature workflow

This project is a **FastAPI** service with **MongoDB** via **Motor** and **Beanie**. Agents should extend it by following the layered layout below. Router registration uses normal imports in `src/api/app.py`.ds

---

## 1. Layers and responsibilities

| Layer | Location | Role |
|--------|-----------|------|
| **Document model** | `src/storages/mongo/<entity>.py` | Beanie persistence: fields, indexes, collection behavior. Subclasses `CustomDocument` from `src/storages/mongo/__base__.py`. |
| **Model registry** | `src/storages/mongo/__init__.py` | Exports `document_models`: list passed to `init_beanie` at startup. **Every** document class must be imported here and listed in that list. |
| **API schemas** | `src/modules/<feature>/schemas.py` | Pydantic DTOs for HTTP bodies and responses (`Create*`, `View*`, etc.). Not the same as the Beanie document. |
| **Repository** | `src/modules/<feature>/repository.py` | Async data access: create/read/update/delete and queries using the document class. Expose a module-level singleton (e.g. `thing_repository = ThingRepository()`). This codebase uses **repository**, not a file named `crud.py`. |
| **Routes** | `src/modules/<feature>/routes.py` | `APIRouter`: dependencies, call repository, return schemas. |
| **App wiring** | `src/api/app.py` | Import each `router` and call `app.include_router(...)`. |

**Startup:** `src/api/lifespan.py` calls `init_beanie(..., document_models=document_models)`. If a document is missing from `document_models`, Beanie will not manage it.

**Reference module:** `src/modules/user/` plus `src/storages/mongo/user.py` demonstrates the full pattern.

---

## 2. Order of work for a new feature (e.g. `event`)

Follow this sequence so types and registration stay consistent.

### Step A — Document model

1. Add `src/storages/mongo/<entity>.py`.
2. Define field schemas (often a `*Schema` mixin inheriting `BaseSchema` from `src/pydantic_base.py`) and a document class that combines them with `CustomDocument`, mirroring `User` / `UserSchema` in `src/storages/mongo/user.py`.
3. Set `class Settings` on the document as needed (e.g. `indexes`).

### Step B — Register with Beanie

Edit `src/storages/mongo/__init__.py`:

- Import the document class.
- Append it to the inner list in `document_models` (the `cast(..., [User, ...])` value).

Without this step, the app will not initialize that collection.

### Step C — API schemas

Add or extend `src/modules/<feature>/schemas.py` with the request/response models routes will use.

### Step D — Repository

Add `src/modules/<feature>/repository.py`:

- Class with **async** methods that use the Beanie document (`insert()`, `get()`, `find`, etc.).
- Module-level singleton instance exported for routes to import.

Copy the shape of `UserRepository` / `user_repository` in `src/modules/user/repository.py`.

### Step E — Routes

Add `src/modules/<feature>/routes.py`:

- `APIRouter` with `prefix` and `tags`.
- Endpoints depend on shared deps from `src/api/dependencies.py` where auth or other cross-cutting behavior is needed.
- Call the repository; return schema types.

If the router introduces a new OpenAPI tag description, follow `user/routes.py` (e.g. append to `docs.TAGS_INFO` when appropriate).

### Step F — Register router on the app

Edit `src/api/app.py`:

1. After the CORS middleware block, add an import:
   `from src.modules.<feature>.routes import router as router_<feature>  # noqa: E402, I001`
2. Add:
   `app.include_router(router_<feature>)`
   next to the other `app.include_router` calls.

Imports live **after** middleware on purpose; keep the `# noqa: E402, I001` on those router imports so linters accept the order. Add new routers in a consistent place (e.g. alphabetical by feature name).

---

## 3. Naming and conventions

- **Entity file:** `src/storages/mongo/<entity>.py` — module name is usually lowercase plural or singular matching the domain (existing example: `user.py` for `User`).
- **Feature package:** `src/modules/<feature>/` with `routes.py`, `repository.py`, `schemas.py`, and `__init__.py` if the package needs it.
- **Router variable:** `router_<feature>` in `app.py` to avoid collisions.
- **Repositories** hold CRUD-style operations; the project standard filename is `repository.py`, not `crud.py`.

---

## 4. Verification

After changes:

- Run the linter/formatter the project uses (e.g. Ruff) on touched files.
- Ensure the app starts and MongoDB initialization succeeds so Beanie picks up new models.

---

## 5. Removing or renaming a feature

- Delete or adjust the module under `src/modules/<feature>/`.
- Remove router import and `app.include_router` from `src/api/app.py`.
- Remove or update the document file and **remove it from `document_models`** in `src/storages/mongo/__init__.py`.
- Search for remaining imports of `src.modules.<feature>` or the old document name.
