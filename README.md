# FeedForward

<!-- BADGES:START -->
[![ai](https://img.shields.io/badge/-ai-ff6f00?style=flat-square)](https://github.com/topics/ai) [![education](https://img.shields.io/badge/-education-blue?style=flat-square)](https://github.com/topics/education) [![fastapi](https://img.shields.io/badge/-fastapi-009688?style=flat-square)](https://github.com/topics/fastapi) [![feedback](https://img.shields.io/badge/-feedback-blue?style=flat-square)](https://github.com/topics/feedback) [![git](https://img.shields.io/badge/-git-blue?style=flat-square)](https://github.com/topics/git) [![python](https://img.shields.io/badge/-python-3776ab?style=flat-square)](https://github.com/topics/python) [![shell](https://img.shields.io/badge/-shell-blue?style=flat-square)](https://github.com/topics/shell) [![sqlite](https://img.shields.io/badge/-sqlite-blue?style=flat-square)](https://github.com/topics/sqlite) [![tailwindcss](https://img.shields.io/badge/-tailwindcss-blue?style=flat-square)](https://github.com/topics/tailwindcss) [![web-app](https://img.shields.io/badge/-web--app-blue?style=flat-square)](https://github.com/topics/web-app)
<!-- BADGES:END -->

FeedForward is an advanced AI-powered platform for providing formative feedback on student assignments. The system leverages multiple AI models with sophisticated aggregation methods to generate comprehensive, constructive feedback aligned with custom rubric criteria.

## 🌟 Key Features

### For Students
- **Multi-draft submissions** with iterative feedback improvement
- **Progress tracking** across assignment versions with detailed comparisons
- **Visual feedback display** with emoji indicators and performance tracking
- **Real-time feedback** with instructor review workflow
- **Privacy-focused** design with temporary draft storage

### For Instructors
- **Custom rubric creation** with weighted categories and detailed criteria
- **Multi-model AI integration** supporting OpenAI, Anthropic, and other providers
- **Flexible aggregation methods** (mean, weighted mean, median, trimmed mean)
- **Advanced feedback review** with AI response comparison and editing
- **Course and student management** with enrollment and progress oversight
- **Plugin architecture** for extensible assessment types

### Technical Excellence
- **Multi-model orchestration** with configurable runs per model
- **Async processing pipeline** for efficient draft handling
- **SQLite database** with comprehensive data models
- **FastHTML + HTMX** for responsive web interface
- **Tailwind CSS** for modern, accessible UI
- **Comprehensive testing** and quality assurance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- API keys for at least one AI provider (OpenAI, Anthropic, etc.)

### Installation

1. **Clone and setup:**
```bash
git clone https://github.com/BARG-Curtin-University/feedforward.git
cd feedforward
```

2. **Using uv (recommended):**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

3. **Or using pip:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your settings and API keys
```

5. **Initialize and run:**
```bash
# Initialize database
python app/init_db.py

# Run the application
python app.py
```

### 🔧 Configuration

Key environment variables:
- `SECRET_KEY` - Flask secret key for sessions
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key (optional)
- `DATABASE_URL` - Database connection string (default: SQLite)
- `SMTP_*` - Email configuration (optional)

### 🛠️ Development Tools

```bash
# Code quality
ruff format .          # Format code
ruff check . --fix     # Lint and fix
mypy app/              # Type checking

# Testing
pytest                 # Run all tests
python tools/test_ai_integration.py    # Test AI features
python tools/test_instructor_feedback_ui.py  # Test UI

# Database
python app/init_db.py                    # Initialize database
python tools/create_demo_accounts.py     # Create demo users
```

## 🏗️ Architecture

### Core Components
- **FastHTML + HTMX** - Modern web framework with reactive UI
- **SQLAlchemy ORM** - Database abstraction with comprehensive models
- **LiteLLM** - Multi-provider AI model integration
- **SQLite Database** - Lightweight, file-based storage
- **Tailwind CSS** - Utility-first styling framework

### Key Features
- **Plugin Architecture** - Extensible assessment types
- **Multi-Model Support** - OpenAI, Anthropic, Google, Cohere, HuggingFace
- **Advanced Aggregation** - Multiple algorithms for feedback synthesis
- **Async Processing** - Background task handling for AI requests
- **Role-Based Security** - Separate interfaces for students, instructors, admins

### Data Flow
1. Student submits draft → Temporary storage
2. Background processing → Multi-model AI evaluation
3. Score aggregation → Rubric-aligned feedback synthesis
4. Instructor review → Optional feedback editing
5. Student access → Progress tracking and comparison

## 📖 Usage Guide

### For Students
1. **Login** with institutional credentials
2. **View assignments** on the dashboard
3. **Submit drafts** with iterative improvements
4. **Review feedback** with emoji indicators and detailed analysis
5. **Track progress** across multiple draft versions

### For Instructors
1. **Create courses** and manage enrollments
2. **Design assignments** with custom rubrics
3. **Configure AI settings** (models, runs, aggregation)
4. **Review submissions** with AI-generated feedback
5. **Edit and approve** feedback before student release

### For Administrators
1. **System configuration** and user management
2. **AI provider setup** and API key management
3. **Analytics and reporting** on system usage
4. **Plugin management** for custom assessment types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style: `ruff format . && ruff check . --fix`
4. Add tests for new functionality
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines
- Use type hints for all function signatures
- Follow PEP 8 style guidelines (enforced by ruff)
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

[MIT License](LICENSE) - see LICENSE file for details

## 🙏 Acknowledgments

- Built for educational innovation at Curtin University
- Powered by state-of-the-art AI language models
- Designed for scalable, privacy-focused learning environments