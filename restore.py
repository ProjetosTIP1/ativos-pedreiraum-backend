from datetime import datetime
import os
import subprocess
import gzip
import glob
from core.config import settings

# --- POSTGRES CONFIG ---
CONTAINER_NAME = "5a59c5f9e3a1"
DB_USER = settings.POSTGRES_USER
DB_NAME = settings.POSTGRES_DB
BACKUP_DIR = settings.BACKUP_DIR


def list_backups():
    """Finds .sql.gz files on the VPS host."""
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql.gz"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def restore_backup(backup_path):
    print(f"WARNING: Restoring to container '{CONTAINER_NAME}'")
    print(f"Source: {os.path.basename(backup_path)}")
    print("This will overwrite existing data. Type 'RESTORE' to confirm:")

    if input("> ") != "RESTORE":
        print("Aborted.")
        return

    # Use environment variable for the password to avoid interactive prompts
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    # The Command: docker exec -i (interactive) allows us to pipe stdin
    restore_args = [
        "docker",
        "exec",
        "-i",
        CONTAINER_NAME,
        "psql",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
        "--quiet",
        "--single-transaction",  # Ensure it succeeds fully or fails fully
    ]

    print(f"Streaming {os.path.basename(backup_path)} into container...")

    try:
        with gzip.open(backup_path, "rb") as f_in:
            # We connect the decompressed file stream to the container's stdin
            process = subprocess.Popen(
                restore_args, stdin=f_in, stderr=subprocess.PIPE, env=env
            )

            _, stderr = process.communicate()

            if process.returncode != 0:
                raise Exception(f"Postgres restore failed: {stderr.decode()}")

        print("✅ Restore completed successfully.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")


def run_restore():

    if not os.path.exists(BACKUP_DIR):
        print(f"Diretório de backup não encontrado em {BACKUP_DIR}")
        return

    backups = list_backups()

    if not backups:
        print("Nenhum arquivo de backup (.sql.gz) encontrado para restaurar.")
        return

    print(f"--- Backups Disponíveis em {BACKUP_DIR} ---")
    for i, f in enumerate(backups):
        # Mostra tamanho em MB e data
        stats = os.stat(f)
        size_mb = stats.st_size / (1024 * 1024)
        date_str = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{i}] {date_str} - {os.path.basename(f)} ({size_mb:.2f} MB)")

    try:
        print("Escolha o número do backup para restaurar (ou Ctrl+C para sair): ")
        choice = input("> ")
        idx = int(choice)
        if 0 <= idx < len(backups):
            restore_backup(backups[idx])
        else:
            print("Opção inválida.")
    except ValueError:
        print("Entrada inválida. Digite apenas o número.")
    except KeyboardInterrupt:
        print("Saindo...")


if __name__ == "__main__":
    run_restore()
