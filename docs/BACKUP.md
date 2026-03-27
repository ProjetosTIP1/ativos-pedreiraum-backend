# 🗄️ Backup & Restore Documentation

This document explains the technical details, configuration, and execution of the PostgreSQL database and image uploads backup and restoration tools.

## 📌 Overview

The project includes Python-based scripts to manage system state securely and efficiently:

1.  **Database Backup (`backup.py`)**: Performs a full PostgreSQL dump, compresses it with gzip, and saves it.
2.  **Images Backup (`backup.py`)**: Compresses the `images` directory into a `.tar.gz` archive.
3.  **Database Restore (`restore.py`)**: Provides an interactive interface to select and restore a database backup.

Both database scripts use a **streaming approach**, piping data directly between the Docker container and the host filesystem to minimize disk I/O and memory usage.

---

## 🛠️ Prerequisites

To run these scripts, the system must have:

-   **Docker**: Installed and running.
-   **Python 3.x**: With `pydantic-settings` installed.
-   **tar**: Available on the host system (for image backups).
-   **Database Access**: The host must be authorized to run `docker exec` commands.

---

## ⚙️ Configuration

Both scripts share the same configuration environment variables defined in `.env` and managed by `core/config.py`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_DB` | Name of the database | `valemix` |
| `POSTGRES_CONTAINER_ID` | Docker container name or ID | (required) |
| `UPLOAD_DIR` | Directory where images are stored | `images` |
| `BACKUP_DIR` | Directory for backup files | `backups` |

---

## 🚀 Technical Implementation Details

### Efficient Resource Usage
The scripts use `subprocess.Popen` and `subprocess.run` to stream data:
-   **Database Backup**: `pg_dump` output from the Docker container is piped directly into `gzip.open`.
-   **Images Backup**: Uses `tar -czf` to archive the images volume directly.
-   **Database Restore**: `gzip.open` (read mode) is piped directly into the `psql` process's `stdin` inside the container.

### Safety Features in `restore.py`
-   **Interactive Selection**: Lists all files in `BACKUP_DIR` with timestamps and sizes.
-   **Confirmation Prompt**: Requires the user to type `RESTORE` to prevent accidental overwrites.
-   **Atomic Restoration**: Uses `--single-transaction` so that if an error occurs mid-restore, the database remains in its previous state.

---

## 📅 Backup Automation

The `backup.py` script automatically performs both database and image backups when executed. To automate backups daily on a Linux host via Cron:

1. `crontab -e`
2. Add:
   ```bash
   0 3 * * * /usr/bin/python3 /absolute/path/to/backend/backup.py >> /var/log/ativos_backup.log 2>&1
   ```

---

## 🔄 Restoration Guide

### 🗄️ Database Restoration

#### Method 1: Interactive Script (Recommended)
Run the script and follow the prompts:
```bash
python restore.py
```
1.  Select the backup number from the list.
2.  Review the warning about the target container.
3.  Type `RESTORE` to confirm.

#### Method 2: Manual (CLI)
If the script is unavailable, you can restore manually:
1. **Decompress**: `gunzip -k <file>.sql.gz` (keeps the original compressed file).
2. **Restore**:
   ```bash
   cat <file>.sql | docker exec -i <container_id> psql -U <user> -d <database>
   ```

### 🖼️ Images Restoration

To restore images from a backup archive:
1. **Locate the backup**: Find the desired `.tar.gz` file in the `backups/` directory.
2. **Extract**:
   ```bash
   tar -xzf <backup_filename>.tar.gz -C /path/to/backend/images/
   ```
   > [!NOTE]
   > The `-C` flag ensures files are extracted into the correct directory. The backup is created using `.` as source, so it extracts directly into the target.
