# FeedForward Technical Documentation

## Overview

FeedForward is a modern AI-powered feedback system built with FastHTML + HTMX, designed to provide iterative, formative feedback on student assignments through multiple AI model integration.

## 🏗️ Architecture

### Core Components

**Backend Framework:**
- **FastHTML + HTMX** - Reactive web framework with minimal JavaScript
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy ORM** - Database abstraction with comprehensive models
- **SQLite** - Lightweight, file-based database (production-ready)

**AI Integration:**
- **LiteLLM** - Multi-provider AI model integration
- **Multi-model orchestration** - Configurable runs per model
- **Advanced aggregation** - Multiple algorithms (mean, median, trimmed mean, weighted)
- **Async processing** - Background task handling for AI requests

**Frontend:**
- **Tailwind CSS** - Utility-first styling framework
- **HTMX** - Dynamic interactions without JavaScript complexity
- **Responsive design** - Mobile-first approach

### Data Flow

```
Student Submission → Temporary Storage → Multi-Model Processing → Aggregation → Instructor Review → Student Feedback
```

## 🔧 Core Features

### Multi-Model AI Processing
- **Configurable runs**: 1-5 runs per model
- **Model diversity**: OpenAI, Anthropic, Google, Cohere, HuggingFace support
- **Aggregation methods**: Mean, median, trimmed mean, weighted mean
- **Confidence scoring**: AI confidence levels for transparency

### Draft Management
- **Iterative workflow**: Up to 5 drafts per assignment
- **Progress tracking**: Visual improvement metrics
- **Privacy-focused**: Temporary storage with automatic cleanup
- **Comparison tools**: Side-by-side draft analysis

### Rubric Integration
- **Custom rubrics**: Weighted categories with detailed criteria
- **AI alignment**: Feedback mapped to rubric components
- **Score aggregation**: Weighted overall scores
- **Visual feedback**: Emoji indicators and progress tracking

### User Roles & Security
- **Role-based access**: Student, Instructor, Admin permissions
- **JWT authentication**: Secure token-based auth
- **Data isolation**: Users only access authorized content
- **Privacy compliance**: GDPR/FERPA considerations

## 📊 Database Schema

### Core Entities
- **Users**: Authentication and role management
- **Courses**: Academic course management
- **Assignments**: Assignment configuration and rubrics
- **Drafts**: Student submissions with metadata
- **AI Models**: Configurable model definitions
- **Feedback**: AI-generated feedback and reviews

### Key Relationships
- Users → Students/Instructors (one-to-one)
- Courses → Assignments (one-to-many)
- Assignments → Drafts (one-to-many)
- Drafts → ModelRuns (one-to-many)
- ModelRuns → FeedbackItems (one-to-many)

## 🚀 Deployment

### Development Environment
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Initialize database
python app/init_db.py

# Run development server
python app.py
```

### Production Deployment
- **Docker support**: Containerized deployment
- **Nginx reverse proxy**: Production web server
- **Systemd service**: Process management
- **Automated backups**: Database and file backups

## 🔒 Security Features

- **Input validation**: Comprehensive data validation
- **SQL injection prevention**: Parameterized queries
- **XSS protection**: HTML escaping and sanitization
- **CSRF protection**: Token-based form validation
- **Rate limiting**: API request throttling
- **Audit logging**: User action tracking

## 📈 Performance Optimizations

- **Async processing**: Background AI request handling
- **Caching strategies**: AI response and data caching
- **Database optimization**: Indexed queries and efficient joins
- **File management**: Temporary file cleanup
- **Connection pooling**: Database connection management

## 🧪 Testing Strategy

- **Unit tests**: Core business logic
- **Integration tests**: API endpoints and workflows
- **End-to-end tests**: Full user journeys
- **Performance tests**: Load and stress testing
- **Security tests**: Vulnerability assessments

## 🔌 API Integration

### AI Provider Support
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude models
- **Google**: Gemini models
- **Cohere**: Command models
- **HuggingFace**: Open source models

### Configuration
```python
# Example model configuration
{
    "name": "GPT-4",
    "api_provider": "OpenAI",
    "version": "gpt-4",
    "api_config": {
        "model": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 2000
    }
}
```

## 📝 Development Guidelines

### Code Style
- **Python**: PEP 8 compliance (enforced by ruff)
- **Type hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Error handling**: Specific exception types

### Git Workflow
- **Feature branches**: `feature/amazing-feature`
- **Bug fixes**: `bugfix/issue-description`
- **Code review**: Pull request reviews required
- **Testing**: All changes must pass CI tests

### Database Migrations
- **Version control**: All schema changes tracked
- **Rollback support**: Migration reversal capability
- **Data integrity**: Constraints and validation
- **Performance**: Optimized queries and indexes

## 📚 Additional Resources

**Archived Documentation:**
- `docs/archive/` - Historical specifications and phase plans
- `docs/getting-started/` - Setup and configuration guides
- `docs/user-guides/` - Role-specific usage documentation

**Development Tools:**
- `tools/` - Utility scripts for maintenance and development
- `tools/archive/` - Development and testing utilities

---

*This technical documentation provides a current overview of the FeedForward system architecture and implementation. For detailed historical information, refer to the archived documentation.*