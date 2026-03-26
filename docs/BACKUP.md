# 🗄️ Database Backup & Restore Documentation

This document explains the technical details, configuration, and execution of the PostgreSQL backup and restoration tools implemented in `backup.py` and `restore.py`.

## 📌 Overview

The project includes two Python-based scripts to manage database state securely and efficiently:

1.  **`backup.py`**: Performs a full database dump, compresses it, and saves it locally.
2.  **`restore.py`**: Provides an interactive interface to select and restore a backup into the database container.

Both scripts use a **streaming approach**, piping data directly between the Docker container and the host filesystem to minimize disk I/O and memory usage.

---

## 🛠️ Prerequisites

To run these scripts, the system must have:

-   **Docker**: Installed and running.
-   **Python 3.x**: With `pydantic-settings` installed.
-   **Database Access**: The host must be authorized to run `docker exec` commands.

---

## ⚙️ Configuration

Both scripts share the same configuration environment variables defined in `.env` and managed by `core/config.py`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_DB` | Name of the database | `valemix` |
| `BACKUP_DIR` | Directory for `.sql.gz` files | `backups` |

### ⚠️ Important Note on Container Name
Both scripts currently target a specific container name/ID:
```python
CONTAINER_NAME = "5a59c5f9e3a1"
```
> [!WARNING]
> If your database service name changes (e.g., in `docker-compose.yml`), you must update `CONTAINER_NAME` in both `backup.py` and `restore.py`.

---

## 🚀 Technical Implementation Details

### Efficient Resource Usage
The scripts use `subprocess.Popen` to stream data:
-   **Backup**: `pg_dump` output is piped directly into `gzip.open`.
-   **Restore**: `gzip.open` (read mode) is piped directly into the `psql` process's `stdin`.

### Safety Features in `restore.py`
-   **Interactive Selection**: Lists all files in `BACKUP_DIR` with timestamps and sizes.
-   **Confirmation Prompt**: Requires the user to type `RESTORE` to prevent accidental overwrites.
-   **Atomic Restoration**: Uses `--single-transaction` so that if an error occurs mid-restore, the database remains in its previous state.

---

## 📅 Backup Automation

To automate backups daily on a Linux host via Cron:

1. `crontab -e`
2. Add:
   ```bash
   0 3 * * * /usr/bin/python3 /absolute/path/to/backend/backup.py >> /var/log/db_backup.log 2>&1
   ```

---

## 🔄 Restoration Guide

### Method 1: Interactive Script (Recommended)
Run the script and follow the prompts:
```bash
python restore.py
```
1.  Select the backup number from the list.
2.  Review the warning about the target container.
3.  Type `RESTORE` to confirm.

### Method 2: Manual (CLI)
If the script is unavailable, you can restore manually:
1. **Decompress**: `gunzip -k <file>.sql.gz` (keeps the original compressed file).
2. **Restore**:
   ```bash
   cat <file>.sql | docker exec -i <container_id> psql -U <user> -d <database>
   ```
