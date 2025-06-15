---
layout: default
title: Installation
parent: Getting Started
nav_order: 1
---

# Installation Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## System Requirements

Before installing FeedForward, ensure your system meets these requirements:

### Minimum Requirements
- **Operating System**: Linux, macOS, or Windows 10/11
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 1GB free disk space (plus space for database)
- **Network**: Internet connection for AI API calls

### Software Dependencies
- Python 3.8+ with pip
- SQLite 3 (usually included with Python)
- Git (for cloning the repository)
- Virtual environment support (venv)

## Installation Steps

### 1. Clone the Repository

First, clone the FeedForward repository from GitHub:

```bash
git clone https://github.com/michael-borck/feed-forward.git
cd feed-forward
```

{: .note }
> If you don't have Git installed, you can [download it here](https://git-scm.com/downloads) or download the repository as a ZIP file from GitHub.

### 2. Create Virtual Environment

Create and activate a Python virtual environment to isolate dependencies:

**On Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

{: .tip }
> Your command prompt should now show `(venv)` to indicate the virtual environment is active.

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- FastHTML (web framework)
- SQLite database support
- AI provider integrations (LiteLLM)
- File processing libraries
- Security and encryption tools

### 4. Environment Configuration

Create a `.env` file in the project root with your configuration:

```bash
# Create .env file
cp .env.example .env  # or create manually
```

Edit the `.env` file with your settings:

```env
# Security
SECRET_KEY=your-secret-key-here  # Generate a strong random key

# Email Configuration (for invitations)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@example.com

# Application Settings
APP_DOMAIN=http://localhost:5001
APP_NAME=FeedForward
DEBUG=false

# AI Provider Keys (add as needed)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
# Add other provider keys as needed
```

{: .warning }
> **Security Note**: Never commit your `.env` file to version control. The `.gitignore` file should already exclude it.

### 5. Initialize Database

Create the database and tables:

```bash
# Create data directory
mkdir -p data

# Initialize database
python app/init_db.py
```

You should see output confirming successful database creation:
```
✓ Database initialized successfully
✓ All tables created
✓ Default data inserted
```

### 6. Create Admin User

Create your first administrator account:

```bash
python tools/create_admin.py
```

Follow the prompts to set up the admin credentials.

### 7. Run the Application

Start the FeedForward server:

```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://localhost:5001 (Press CTRL+C to quit)
```

{: .tip }
> Visit [http://localhost:5001](http://localhost:5001) in your web browser to access FeedForward.

## Optional Setup

### Automated Draft Cleanup

FeedForward includes a privacy-focused cleanup script that removes student submission content after feedback is generated. Set this up as a scheduled task:

**Manual execution:**
```bash
python tools/cleanup_drafts.py
```

**Cron job (Linux/macOS):**
```bash
# Add to crontab for daily 2 AM execution
0 2 * * * cd /path/to/feed-forward && /path/to/venv/bin/python tools/cleanup_drafts.py >> logs/cleanup.log 2>&1
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily)
4. Set action to run: `C:\path\to\venv\Scripts\python.exe C:\path\to\feed-forward\tools\cleanup_drafts.py`

### Development Mode

For development with auto-reload:

```bash
# Set debug mode in .env
DEBUG=true

# Run with auto-reload
python app.py
```

## Verification

To verify your installation:

1. **Check the homepage** loads at [http://localhost:5001](http://localhost:5001)
2. **Log in** with your admin credentials
3. **Navigate** to Admin Dashboard
4. **Create** a test AI model configuration
5. **Verify** email settings by sending a test invitation

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in app.py or use environment variable
PORT=5002 python app.py
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install -r requirements.txt
```

**Database errors:**
```bash
# Re-initialize database
rm data/feedforward.db
python app/init_db.py
```

**Permission errors (Linux/macOS):**
```bash
# Ensure data directory is writable
chmod 755 data/
```

## Next Steps

- Continue to [Configuration](./configuration) to set up AI providers
- See [Quick Start](./quick-start) for creating your first assignment
- Review the [Admin Guide](/user-guides/admin/) for system management

---

{: .note }
> Need help? Check our [Troubleshooting Guide](/deployment/troubleshooting) or [open an issue](https://github.com/michael-borck/feed-forward/issues) on GitHub.