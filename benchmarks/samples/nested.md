# Server Installation Guide

This guide covers installing and configuring the application server.

## Prerequisites

Before beginning, ensure you have:

- Python 3.10 or higher
- PostgreSQL 14+
- 2GB RAM minimum

### System Requirements

The following table details hardware requirements:

| Component | Minimum | Recommended |
| --------- | ------- | ----------- |
| CPU       | 2 cores | 4 cores     |
| RAM       | 2 GB    | 8 GB        |
| Disk      | 10 GB   | 50 GB       |

### Software Dependencies

Install required system packages:

```bash
sudo apt update
sudo apt install python3-pip postgresql-14 nginx
```

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/example/app.git
cd app
```

### Step 2: Configure Environment

Copy the example environment file and edit:

```bash
cp .env.example .env
vi .env
```

Set the following variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Random 64-character string

### Step 3: Install Dependencies

Create and activate a virtual environment, then install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Run Migrations

Apply database migrations to set up the schema:

```bash
python manage.py migrate
```

## Post-Installation

### Verify Service Health

After installation, check the service status:

```bash
systemctl status app-server
```

Expected output should show `active (running)`.

### Run Smoke Tests

Execute the basic test suite:

```bash
python -m pytest tests/smoke/ -v
```

All tests should pass before proceeding to production configuration.

## Troubleshooting

### Common Issues

If the service fails to start, check these common causes:

1. **Port conflict** — Ensure port 8080 is not in use
2. **Missing env vars** — Verify `.env` contains all required variables
3. **Database connection** — Test with `psql` directly

### Log Files

Application logs are stored at `/var/log/app-server/`:

```bash
tail -f /var/log/app-server/app.log
```
