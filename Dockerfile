FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    # General build tools and utilities
    build-essential \
    curl \
    gnupg \
    software-properties-common \
    pkg-config \
    # ODBC dependencies
    unixodbc-dev \
    # PostgreSQL client library
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Add MariaDB repository and install the C connector
RUN mkdir -p /etc/apt/keyrings \
    && curl -o /etc/apt/keyrings/mariadb-keyring.pgp 'https://mariadb.org/mariadb_release_signing_key.pgp' \
    && echo "deb [signed-by=/etc/apt/keyrings/mariadb-keyring.pgp] https://deb.mariadb.org/11.4/debian bullseye main" > /etc/apt/sources.list.d/mariadb.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends libmariadb3 libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# WORKAROUND V2: Forcefully append a new config section to openssl.cnf
RUN echo "" >> /etc/ssl/openssl.cnf && \
    echo "[system_default_sect]" >> /etc/ssl/openssl.cnf && \
    echo "MinProtocol = TLSv1.0" >> /etc/ssl/openssl.cnf && \
    echo "CipherString = DEFAULT@SECLEVEL=1" >> /etc/ssl/openssl.cnf

# Install required dependencies for Microsoft ODBC Driver
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 mssql-tools18 \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for ODBC
ENV PATH="/opt/mssql-tools18/bin:${PATH}"

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Verify gunicorn is installed (fail fast if missing)
RUN which gunicorn && gunicorn --version

# Copy source code
COPY . .

# Security: Never run as root.
RUN adduser --disabled-password --gecos '' django_user \
    && chown -R django_user:django_user /app
USER django_user

# Expose port 8000
EXPOSE 8000

# Health check to ensure the container is running properly
# Uses the dedicated health endpoint that checks database and Redis connectivity
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/ || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]