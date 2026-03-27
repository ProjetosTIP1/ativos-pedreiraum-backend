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
    CONTAINER_NAME = settings.POSTGRES_CONTAINER_ID

    if not CONTAINER_NAME:
        raise ValueError("POSTGRES_CONTAINER_ID not set in environment variables")

    print(f"📦 Archiving postgres volume: {CONTAINER_NAME}...")

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


def backup_images_volume():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    # Change 'project_images' to the actual name (usually [folder]_images)
    SOURCE_DIR = settings.UPLOAD_DIR
    output_filename = f"images_backup_{timestamp}.tar.gz"
    output_path = os.path.join(settings.BACKUP_DIR, output_filename)

    print(f"📦 Archiving images volume: {SOURCE_DIR}...")

    # -c: create, -z: gzip, -f: file
    # -C: Change to the directory first so the archive doesn't
    #     contain the whole absolute path prefix.
    cmd = ["tar", "-czf", output_path, "-C", SOURCE_DIR, "."]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Images backed up to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to backup images: {e}")


if __name__ == "__main__":
    try:
        run_postgres_backup()
        backup_images_volume()
    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
