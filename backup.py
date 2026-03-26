import subprocess
import gzip
import os
import shutil
from datetime import datetime
from core.config import settings


def run_postgres_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"pg_ativos_{timestamp}.sql.gz"
    filepath = os.path.join(settings.BACKUP_DIR, filename)

    # In Docker, we use the container name defined in docker-compose.yml
    CONTAINER_NAME = "5a59c5f9e3a1"

    # Use PGPASSWORD env var so pg_dump doesn't prompt for it
    os.environ["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    # Construct the command to execute INSIDE the container
    # We pipe the output directly to our local gzip stream
    dump_args = [
        "docker",
        "exec",
        CONTAINER_NAME,
        "pg_dump",
        "-U",
        settings.POSTGRES_USER,
        "-d",
        settings.POSTGRES_DB,
        "--clean",  # Includes DROP TABLE statements
        "--if-exists",
        "--no-owner",  # Makes restoration easier on different systems
    ]

    try:
        with gzip.open(filepath, "wb") as f_out:
            # We stream stdout from the process and write it to the gzip file
            process = subprocess.Popen(
                dump_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            if process.stdout:
                shutil.copyfileobj(process.stdout, f_out)

            _, stderr = process.communicate()

            if process.returncode != 0:
                raise Exception(f"pg_dump failed: {stderr.decode()}")

        print(f"✅ Backup successful: {filepath}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
    finally:
        # Clean up sensitive env var
        if "PGPASSWORD" in os.environ:
            del os.environ["PGPASSWORD"]


if __name__ == "__main__":
    run_postgres_backup()
