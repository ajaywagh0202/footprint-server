# Footprint Server Code Summary

## 1. Project Overview

This project is a FastAPI backend for railway master data, train schedules, users, authentication tokens, and department manual PDF management.

Main stack:

- API framework: FastAPI
- ORM: SQLAlchemy
- Validation: Pydantic v2
- Database driver: psycopg2-binary, intended for PostgreSQL
- Auth token: JWT using python-jose
- Password utilities: passlib with Argon2 support
- Import utilities: pandas for CSV import
- File upload: python-multipart and FastAPI UploadFile

Main entry point:

- `src/main.py`

Application startup behavior:

- Creates the FastAPI app.
- Enables CORS for all origins, methods, and headers.
- Calls `Base.metadata.create_all(bind=engine)` to create all loaded SQLAlchemy tables.
- Registers routers for zones, divisions, stations, train schedules, users, and department manuals.

Database configuration:

- `src/database.py` creates the SQLAlchemy engine from `settings.database_url`.
- `src/security/config.py` loads settings from `.env`.
- Required environment variables:
  - `database_url`
  - `secret_key`
  - `algorithm`
  - `access_token_expire_minutes`, optional, default `30`

## 2. Project Folder Structure

Important folders:

- `src/main.py`: FastAPI app setup and router registration.
- `src/database.py`: SQLAlchemy engine, session factory, and `get_db` dependency.
- `src/security/`: auth and configuration logic.
- `src/models/Master/`: SQLAlchemy master tables.
- `src/models/Transaction/`: SQLAlchemy transaction tables.
- `src/routers/master_route/`: CRUD APIs for zones, divisions, stations, users.
- `src/routers/transaction_route/`: CRUD APIs for train schedules.
- `src/routers/manual_route/`: department manual APIs.
- `src/schemas/`: Pydantic request and response schemas.
- `scripts/`: data import scripts.
- `ai_chroma_db/`: present in the project, but no active source code references were found.
- `src/ai/`: folder exists, but currently contains no active source files.
- `src/models/Logs/`: folder exists, but currently contains no active model files.

## 3. Database Tables

### 3.1 `zone_master`

Model file:

- `src/models/Master/zone_master.py`

Purpose:

- Stores railway zone master data.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `zone` | String | Yes | Zone name |
| `zone_code` | String | Yes | Unique, indexed |
| `headquarter` | String | Yes | Zone headquarter |
| `region` | String | No | Optional region |

Relationships:

- One zone has many divisions through `zone_code`.
- Related table: `division_master`.

### 3.2 `division_master`

Model file:

- `src/models/Master/division_master.py`

Purpose:

- Stores railway division master data.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `division` | String | Yes | Division name |
| `division_code` | String | Yes | Unique, indexed |
| `headquarter` | String | Yes | Division headquarter |
| `zone_code` | String | Yes | Foreign key to `zone_master.zone_code`, indexed |

Relationships:

- Many divisions belong to one zone.
- One division has many stations.
- Related tables: `zone_master`, `station_master`.

### 3.3 `station_master`

Model file:

- `src/models/Master/station_master.py`

Purpose:

- Stores station master data.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `station` | String | Yes | Station name |
| `station_code` | String | Yes | Unique, indexed |
| `station_category` | String | Yes | Station category |
| `district` | String | Yes | District |
| `state` | String | Yes | State |
| `division_code` | String | Yes | Foreign key to `division_master.division_code`, indexed |

Relationships:

- Many stations belong to one division.
- One station can be referenced by train schedules in three ways:
  - as the schedule stop station through `train_schedule.station_code`
  - as the source station through `train_schedule.from_station_code`
  - as the destination station through `train_schedule.to_station_code`

Important note:

- `StationCreate` and `StationUpdate` schemas include `station_type`, but the `station_master` model does not define a `station_type` column.

### 3.4 `train_schedule`

Model file:

- `src/models/Transaction/train_schedule.py`

Purpose:

- Stores train schedule rows by train, station sequence, station, source, and destination.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `train_no` | String | Yes | Train number |
| `train_name` | String | Yes | Train name |
| `islno` | String | Yes | Station sequence or serial number |
| `station_name` | String | Yes | Current station name |
| `station_code` | String | Yes | Foreign key to `station_master.station_code`, indexed |
| `arrival_time` | String | Yes | Arrival time stored as text |
| `departure_time` | String | Yes | Departure time stored as text |
| `distance` | Integer | Yes | Distance value |
| `from_station_name` | String | Yes | Source station name |
| `from_station_code` | String | Yes | Foreign key to `station_master.station_code`, indexed |
| `to_station_name` | String | Yes | Destination station name |
| `to_station_code` | String | Yes | Foreign key to `station_master.station_code`, indexed |

Relationships:

- `station_code` links to `station_master.station_code`.
- `from_station_code` links to `station_master.station_code`.
- `to_station_code` links to `station_master.station_code`.

### 3.5 `users`

Model file:

- `src/models/Master/user.py`

Purpose:

- Stores application users and login data.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `name` | String | Yes | Full name |
| `username` | String | Yes | Unique |
| `password` | String | Yes | Stored password |
| `phone` | String | Yes | Phone number |
| `email` | String | Yes | Unique |
| `employee_no` | String | Yes | Unique |
| `user_type` | Integer | Yes | `0` admin, `1` regular user |
| `is_active` | Integer | Yes | `0` inactive, `1` active |
| `created_at` | String | Yes | ISO datetime string |

Important note:

- `src/security/auth.py` contains password hashing helpers, but the current login route compares plain text password values directly.

### 3.6 `departments`

Model file:

- `src/models/Master/department.py`

Purpose:

- Stores department master data for department manuals.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `department_code` | String(60) | Yes | Unique, indexed |
| `department_name` | String(120) | Yes | Department name |
| `created_at` | DateTime | Yes | Defaults to UTC now |

Relationships:

- One department has many department manuals.

Important note:

- The current API exposes department listing through manual routes, but there is no dedicated CRUD router for creating or updating departments.

### 3.7 `department_manuals`

Model file:

- `src/models/Master/department_manual.py`

Purpose:

- Stores metadata for department manual PDF files.

Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | Integer | Yes | Primary key, indexed |
| `department_code` | String(60) | Yes | Foreign key to `departments.department_code`, indexed |
| `file_name` | String(300) | Yes | PDF file name |
| `display_title` | String(300) | Yes | Display title shown to users |
| `version_type` | String(10) | Yes | Must be `Original` or `Revised` |
| `revision_number` | Integer | No | Optional revision number |
| `description` | Text | No | Optional description |
| `file_path` | String(500) | Yes | Relative or absolute file path |
| `file_size_kb` | Integer | No | File size in KB |
| `uploaded_by` | String(120) | No | Uploader name |
| `is_active` | Boolean | Yes | Soft delete flag |
| `created_at` | DateTime | Yes | Defaults to UTC now |
| `updated_at` | DateTime | Yes | Defaults to UTC now, updates on change |

Constraints:

- `version_type` is restricted by check constraint:
  - `Original`
  - `Revised`

Relationships:

- Many manuals belong to one department.

## 4. API Routes

### 4.1 Root API

Router:

- `src/main.py`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Health check. Returns `{"status": "Backend is running"}` |

### 4.2 Zone APIs

Router:

- `src/routers/master_route/zone.py`

Prefix:

- `/zones`

Table used:

- `zone_master`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/zones/` | Create zone |
| GET | `/zones/` | List all zones |
| GET | `/zones/{zone_id}` | Get one zone by ID |
| GET | `/zones/{zone_id}/divisions` | List divisions under a zone |
| PUT | `/zones/{zone_id}` | Update zone |
| DELETE | `/zones/{zone_id}` | Delete zone |

Main logic:

- Uses `_commit()` helper to commit database changes.
- Catches `IntegrityError` and returns HTTP `409 Conflict`.
- Returns HTTP `404 Not Found` when a zone ID does not exist.
- `GET /zones/{zone_id}/divisions` first finds the zone, then filters divisions by `zone_code`.

Schemas:

- Create: `ZoneCreate`
- Response: `ZoneGet`
- Update: `ZoneUpdate`

### 4.3 Division APIs

Router:

- `src/routers/master_route/division.py`

Prefix:

- `/divisions`

Tables used:

- `division_master`
- `zone_master`
- `station_master`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/divisions/` | Create division |
| GET | `/divisions/` | List divisions with zone name |
| GET | `/divisions/{division_id}` | Get one division by ID |
| GET | `/divisions/{division_id}/stations` | List stations under a division |
| PUT | `/divisions/{division_id}` | Update division |
| DELETE | `/divisions/{division_id}` | Delete division |

Main logic:

- `_ensure_zone()` checks whether `zone_code` exists before creating or updating a division.
- `GET /divisions/` joins `division_master` with `zone_master` and returns extra `zone_name`.
- `GET /divisions/{division_id}/stations` first finds the division, then filters stations by `division_code`.
- Duplicate or foreign key errors return HTTP `409 Conflict`.

Schemas:

- Create: `DivisionCreate`
- Response: `DivisionGet`
- List response with zone: `DivisionWithZone`
- Update: `DivisionUpdate`

### 4.4 Station APIs

Router:

- `src/routers/master_route/station.py`

Prefix:

- `/stations`

Tables used:

- `station_master`
- `division_master`
- `zone_master`
- `train_schedule`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/stations/` | Create station |
| GET | `/stations/` | List stations with division and zone names |
| GET | `/stations/{station_id}` | Get one station by ID |
| GET | `/stations/{station_id}/train-schedules` | List train schedules for a station |
| PUT | `/stations/{station_id}` | Update station |
| DELETE | `/stations/{station_id}` | Delete station |

Main logic:

- `_ensure_division()` checks whether `division_code` exists before creating or updating a station.
- `GET /stations/` joins station, division, and zone tables to return:
  - station fields
  - `division_name`
  - `zone_name`
  - `zone_code`
- `GET /stations/{station_id}/train-schedules` first finds the station, then filters train schedules by `station_code`.
- Duplicate or foreign key errors return HTTP `409 Conflict`.

Schemas:

- Create: `StationCreate`
- Response: `StationGet`
- List response with division and zone: `StationWithDivisionZone`
- Update: `StationUpdate`

### 4.5 Train Schedule APIs

Router:

- `src/routers/transaction_route/train_schedule.py`

Prefix:

- `/train-schedules`

Tables used:

- `train_schedule`
- `station_master`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/train-schedules/` | Create train schedule |
| GET | `/train-schedules/` | List all train schedules |
| GET | `/train-schedules/{schedule_id}` | Get one train schedule by ID |
| PUT | `/train-schedules/{schedule_id}` | Update train schedule |
| DELETE | `/train-schedules/{schedule_id}` | Delete train schedule |

Main logic:

- `_ensure_station()` checks whether a station code exists.
- `_ensure_schedule_stations()` validates:
  - `station_code`
  - `from_station_code`
  - `to_station_code`
- Create and update use `_ensure_schedule_stations()` before writing data.
- Duplicate or foreign key errors return HTTP `409 Conflict`.

Schemas:

- Create: `TrainScheduleCreate`
- Response: `TrainScheduleGet`
- Update: `TrainScheduleUpdate`

Important note:

- `TrainScheduleCreate` makes `station_name`, `from_station_name`, and `to_station_name` optional, but the database model marks those columns as required.
- `TrainScheduleUpdate` does not expose all train schedule fields, such as `islno`, `station_name`, `from_station_name`, and `to_station_name`.

### 4.6 User APIs

Router:

- `src/routers/master_route/user.py`

Prefix:

- `/users`

Table used:

- `users`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/users/` | Create user |
| GET | `/users/` | List all users |
| POST | `/users/login` | Login and receive JWT token |
| GET | `/users/verifyToken` | Verify bearer token and return current user |
| GET | `/users/{user_id}` | Get one user by ID |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |

Main logic:

- `create_user()` stores the user and sets `created_at` to `datetime.utcnow().isoformat()`.
- `login()` checks username and password in the database.
- On successful login, `auth.create_access_token()` creates a JWT with `sub` set to username.
- `verifyToken` uses `auth.get_current_user`, which:
  - reads bearer token from Authorization header
  - decodes JWT
  - extracts username from `sub`
  - loads the matching user from the database
- Duplicate username, email, or employee number returns HTTP `409 Conflict`.

Schemas:

- Create: `UserCreate`
- Response: `UserOut`
- Update: `UserUpdate`
- Login request: `UserLogin`
- Login response: `UserLoginOut`
- Verify response: `VerifyTokenOut`

Important note:

- The password is compared directly in `login()`.
- `auth.hash_password()` and `auth.verify_password()` exist but are not currently used by the user route.

### 4.7 Department Manual APIs

Router:

- `src/routers/manual_route/manuals.py`

Prefix:

- `/api/manuals`

Tables used:

- `departments`
- `department_manuals`

File storage:

- Base storage path is resolved as:
  - parent of project root + `Data_WareHouse/Department_Manuals_Warehouse`
- Manual file paths are stored like:
  - `{department_code}/{file_name}`

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/manuals/departments` | List departments with active manual count |
| GET | `/api/manuals/departments/list` | List departments only |
| GET | `/api/manuals/department/{department_code}` | Get department with manuals |
| POST | `/api/manuals/upload` | Upload a PDF manual or create metadata-only record |
| GET | `/api/manuals/{manual_id}/file` | Open active manual PDF by manual ID |
| GET | `/api/manuals/files/{department_code}/{file_name}` | Open active manual PDF by department and file name |
| DELETE | `/api/manuals/{manual_id}` | Soft-delete a manual by setting `is_active` to false |

Main helper logic:

- `clean_optional(value)`: trims string values and converts empty values to `None`.
- `normalize_version_type(value)`: accepts case-insensitive `original` or `revised`, returns `Original` or `Revised`.
- `parse_bool(value)`: accepts `true`, `1`, `yes`, `false`, `0`, `no`.
- `parse_revision_number(value)`: converts revision number to integer or returns `None`.
- `detect_version_type(file_name)`: checks whether PDF filename ends with `Original` or `Revised`.
- `manual_file_url(request, manual_id)`: builds file URL for a manual.
- `resolve_manual_file_path(manual)`: checks several candidate locations for the stored file path.
- `manual_file_response(manual)`: returns the PDF using `FileResponse`.

Department listing logic:

- `/api/manuals/departments` performs an outer join between departments and active manuals.
- It returns active manual count per department.
- Departments are ordered by `created_at` descending.

Department manual listing logic:

- `/api/manuals/department/{department_code}`:
  - validates `is_active` query parameter
  - optionally validates and filters `version_type`
  - finds department case-insensitively by `department_code`
  - returns manuals ordered by `created_at` descending
  - adds `file_url` to each manual

Manual upload logic:

- Supports two request styles:
  - multipart form upload with actual PDF file
  - JSON request for metadata-only record
- Required fields:
  - `department_code`
  - `display_title`
  - `version_type`
- Optional fields:
  - `revision_number`
  - `description`
  - `uploaded_by`, only from multipart flow
- Multipart upload rules:
  - `file` is required.
  - File extension must be `.pdf`.
  - File name must end with `Original` or `Revised` before `.pdf`.
  - `version_type` must match the file name.
  - Existing file path causes HTTP `409 Conflict`.
- JSON metadata-only rules:
  - No PDF is saved.
  - `file_name` is generated as `{display_title_with_underscores}_{version_type}.pdf`.
- For `Original` manuals:
  - `revision_number` is forced to `None`.
- Duplicate manual check:
  - Same `department_code` and same `file_name` is rejected.
- On upload failure:
  - Database transaction is rolled back.
  - Uploaded file is deleted if it was already written.

Manual deletion logic:

- DELETE does not remove the physical file.
- It sets:
  - `is_active = False`
  - `updated_at = datetime.utcnow()`

Schemas:

- Department response: `DepartmentGet`
- Department with count: `DepartmentWithManualCount`
- Manual response: `DepartmentManualGet`
- Department with manuals: `DepartmentWithManuals`

## 5. Authentication Logic

File:

- `src/security/auth.py`

Functions:

- `hash_password(password)`: hashes a password using Argon2.
- `verify_password(plain_password, hashed_password)`: verifies plain password against hash.
- `create_access_token(data)`: creates JWT with expiry.
- `verify_token(token)`: decodes JWT and returns username from `sub`.
- `get_current_user(token, db)`: resolves current user from bearer token.

Token details:

- OAuth2 bearer token dependency uses `tokenUrl="/users/login"`.
- JWT expiry is controlled by `settings.access_token_expire_minutes`.
- JWT secret and algorithm come from `.env`.

Current implementation note:

- Password hashing helpers are available, but user creation and login currently store and compare plain text passwords.

## 6. Data Import Scripts

### 6.1 Station Master Import

Script:

- `scripts/import_station_master_data.py`

Target table:

- `station_master`

Related tables:

- `division_master`
- `zone_master`
- `train_schedule`, imported only so SQLAlchemy metadata is aware of it

Input:

- CSV file.
- Default path is hardcoded to a local Windows download path.

Required CSV columns:

- `station`
- `station_code`
- `station_category`
- `division_code`
- `district`
- `state`

Logic:

- Normalizes CSV column names to lowercase snake case.
- Validates required columns.
- Converts station, district, and state to title case.
- Trims station code, station category, and division code.
- Drops rows with missing required values.
- Drops duplicate station codes.
- Skips rows where station code already exists.
- Skips rows where division code is not found in `division_master`.
- Inserts valid rows and returns counters:
  - `csv_rows_after_cleaning`
  - `inserted`
  - `skipped_duplicates`
  - `skipped_missing_division`

### 6.2 Train Schedule Import

Script:

- `scripts/import_train_schedule_data.py`

Target table:

- `train_schedule`

Related tables:

- `station_master`
- `division_master`
- `zone_master`

Input:

- CSV file.
- Default path is `sample/Train Master Data.csv`.

Required CSV columns:

- `train_no`
- `train_name`
- `islno`
- `station_code`
- `station_name`
- `arrival_time`
- `departure_time`
- `distance`
- `from_station_code`
- `from_station_name`
- `to_station_code`
- `to_station_name`

Logic:

- Normalizes CSV column names to lowercase snake case.
- Validates required columns.
- Converts train and station names to title case.
- Trims quote characters and whitespace from text fields.
- Converts distance to integer.
- Drops rows with missing required values.
- Drops duplicate schedules by:
  - `train_no`
  - `islno`
  - `station_code`
- Skips rows where the schedule key already exists.
- Skips rows where any of `station_code`, `from_station_code`, or `to_station_code` does not exist in `station_master`.
- Inserts valid rows and returns counters:
  - `csv_rows_after_cleaning`
  - `inserted`
  - `skipped_duplicates`
  - `skipped_missing_station`

### 6.3 Department Manual Folder Import

Script:

- `scripts/import_department_manuals_from_folders.py`

Target table:

- `department_manuals`

Related table:

- `departments`

Input:

- Base directory containing department folders.
- Default path points to:
  - `Data_WareHouse/Department_Manuals_Warehouse`

Expected folder format:

- Each department should have a folder named by `department_code`.
- Each folder contains PDF files.

Expected file name format:

- File name should end with `_Original.pdf` or `_Revised.pdf`.

Logic:

- Creates tables through SQLAlchemy metadata.
- Loads valid department codes from `departments`.
- Skips folders not found in `departments`.
- Scans PDF files inside each department folder.
- Detects version type from filename.
- Builds display title from filename by removing the final version segment.
- Calculates file size in KB.
- Skips duplicate manual records with same department and file name.
- Inserts manual metadata with:
  - `uploaded_by = "system_import"`
  - `is_active = True`
  - `file_path = "{department_code}/{file_name}"`
- Prints summary counters:
  - total PDFs found
  - successfully inserted
  - skipped duplicate
  - skipped no keyword
  - skipped unknown department

## 7. Common API Response Behavior

CRUD routers:

- Most master and transaction routes return Pydantic model responses.
- Missing records return HTTP `404 Not Found`.
- Database uniqueness or constraint failures return HTTP `409 Conflict`.
- Delete operations return HTTP `204 No Content`.

Manual router:

- Uses custom JSON shape:
  - success: `{"message": "...", "data": ...}`
  - error: `{"error": "..."}`
- File open endpoints return PDF `FileResponse`.

## 8. Main Business Rules

Hierarchy rules:

- Zone must exist before creating a division.
- Division must exist before creating a station.
- Station must exist before creating a train schedule.
- Train schedule checks three station references:
  - current station
  - from station
  - to station

Manual rules:

- Department must exist before adding a manual.
- Manual version must be `Original` or `Revised`.
- Uploaded file must be a PDF.
- Uploaded PDF filename version must match selected `version_type`.
- Original manuals cannot keep a revision number.
- Manual delete is a soft delete through `is_active`.

User/auth rules:

- Username, email, and employee number must be unique.
- Login returns JWT bearer token.
- Token verification returns the current user.

## 9. Important Observations And Possible Fixes

These are not changes made here, only observations from the current code.

1. `station_type` schema mismatch:
   - `StationCreate` and `StationUpdate` include `station_type`.
   - `StationMaster` model does not include `station_type`.
   - Creating a station with `payload.model_dump()` can fail because SQLAlchemy receives an unknown field.

2. Plain text password handling:
   - `auth.py` has `hash_password()` and `verify_password()`.
   - `user.py` route stores and compares passwords directly.
   - Better flow: hash password on create/update and verify hash on login.

3. Train schedule nullable mismatch:
   - Schema allows `station_name`, `from_station_name`, and `to_station_name` to be optional.
   - Database model requires them.
   - API create can fail if these names are omitted.

4. Train schedule update is partial:
   - `TrainScheduleUpdate` does not include every column, such as `islno` and station name fields.

5. Department CRUD is missing:
   - Tables and read APIs exist for departments.
   - No API currently creates, updates, or deletes department records.

6. Metadata-only manual upload can create a file record without an actual PDF:
   - JSON upload creates database metadata only.
   - File open endpoint may later return file not found if the physical PDF does not exist.

7. No migration tool is present:
   - The app relies on `Base.metadata.create_all()`.
   - For production schema changes, Alembic migrations would be safer.

8. No automated tests were found:
   - There are no visible test files in the current project tree.

## 10. How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI app:

```bash
uvicorn src.main:app --reload
```

Default interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Required before running:

- `.env` must contain valid database and JWT settings.
- PostgreSQL/database server must be reachable through `database_url`.

