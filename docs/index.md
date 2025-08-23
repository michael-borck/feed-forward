# FeedForward Documentation

Welcome to the FeedForward documentation hub. This system provides AI-powered formative feedback for student assignments, featuring multi-model AI integration and iterative draft improvement.

## 🚀 Quick Start

**New to FeedForward?** Start here:
- **[Installation Guide](getting-started/installation)** - Set up your development environment
- **[Configuration](getting-started/configuration)** - Configure AI providers and settings
- **[Quick Start](getting-started/quick-start)** - Get running in minutes

## 📖 User Guides

### For Students
- **Dashboard** - View assignments and track progress
- **Draft Submission** - Submit and improve assignments iteratively
- **Feedback Review** - Understand AI feedback and improvement suggestions
- **Progress Tracking** - Monitor learning and development over time

### For Instructors
- **Course Management** - Create and organize courses
- **Assignment Creation** - Build assignments with custom rubrics
- **AI Configuration** - Set up multi-model feedback systems
- **Student Monitoring** - Track progress and review submissions
- **Analytics Dashboard** - View course and assignment insights

## 🛠️ Technical Documentation

### System Architecture
- **[Technical Overview](technical.md)** - System architecture and components
- **[AI Integration](AI_Integration_Architecture.md)** - Multi-model AI processing
- **[Database Design](technical/database.md)** - Data models and relationships

### Development
- **[Code Quality Plan](CODE_QUALITY_PLAN.md)** - Development standards and practices
- **[API Documentation](technical/api.md)** - REST API reference
- **[Deployment Guide](deployment.md)** - Production deployment instructions

### Security & Compliance
- **[Security Guidelines](technical/security.md)** - Security best practices
- **[Privacy Compliance](legal/privacy.md)** - Data privacy and compliance
- **[Audit Logging](technical/audit.md)** - System activity tracking

## 🎯 Key Features

### Multi-Model AI Processing
- Support for OpenAI, Anthropic, Google, Cohere, and HuggingFace models
- Configurable number of runs per model (1-5)
- Advanced aggregation methods (mean, median, trimmed mean, weighted)
- Confidence scoring and transparency

### Iterative Learning
- Up to 5 drafts per assignment
- Progress visualization and improvement tracking
- Draft comparison and historical analysis
- Learning analytics and insights

### Custom Assessment
- Flexible rubric creation with weighted categories
- AI feedback aligned with assessment criteria
- Visual feedback options (numeric, icons, hidden)
- Instructor review and customization

## 📁 Documentation Archive

Historical and detailed documentation is available in the `docs/archive/` directory:
- **MVP Technical Specification** - Original system design (2164 lines)
- **System Specification** - Comprehensive feature overview (3585 lines)
- **Phase 1 Tasks** - Detailed implementation planning
- **Future Work** - Planned enhancements and features

## 🔍 Additional Resources

### Development Tools
- **[Tools Directory](../tools/)** - Utility scripts for maintenance
- **[Docker Deployment](DOCKER_DEPLOYMENT.md)** - Containerized deployment
- **[LLM Setup Guide](LLM_SETUP_GUIDE.md)** - AI model configuration

### Community & Support
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community questions and answers
- **Contributing Guide** - Development and contribution guidelines

## 📊 System Status

| Component | Status | Documentation |
|-----------|--------|---------------|
| Core System | ✅ Production Ready | [Technical Overview](technical.md) |
| AI Integration | ✅ Multi-Model Support | [AI Integration](AI_Integration_Architecture.md) |
| User Interface | ✅ Responsive Design | [UI Guidelines](web-ui.md) |
| Database | ✅ SQLite/PostgreSQL | [Database Design](technical/database.md) |
| Security | ✅ Production Secure | [Security Guidelines](technical/security.md) |
| Documentation | ✅ Current & Comprehensive | [Getting Started](getting-started/) |

## 🎓 Educational Impact

FeedForward is designed to enhance learning through:
- **Formative feedback** that guides improvement
- **Iterative practice** with structured progression
- **AI transparency** showing how feedback is generated
- **Instructor oversight** ensuring quality and appropriateness
- **Data-driven insights** for both students and educators

---

*FeedForward empowers students with AI-driven formative feedback while giving instructors powerful tools for course management and assessment design.*