#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

TIMESTAMP=$(date +%Y-%m-%d_%H%M)
BACKUP_DIR="/root/backups/ativos"
SOURCE_IMAGES="/root/projetos/ativos/backend/images"

# Ensure backup directory exists (Architecture Precedes Automation)
mkdir -p "$BACKUP_DIR"

echo "[$TIMESTAMP] Starting Backup..."

# 1. Database Backup 
docker exec ativos-pg-db pg_dump -U postgres -d ativos | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
echo "Database dumped successfully."

# 2. Images Backup
# -C changes to the source dir so the tar doesn't contain the full absolute path
tar -czf "$BACKUP_DIR/images_$TIMESTAMP.tar.gz" -C "$SOURCE_IMAGES" .
echo "Images compressed successfully."

# 3. Cleanup
# Only delete if we have at least a few successful backups (safety check)
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "[$TIMESTAMP] Backup Completed."