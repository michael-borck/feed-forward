# Quick FeedForward Demo Setup

## 🚀 Simplified Demo Setup (5 minutes)

### Step 1: Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with default admin user
python app/init_db.py

# Create demo accounts and course
python tools/create_demo_accounts.py
```

### Step 2: Start the Application
```bash
# Start the app
python app.py
```

**Access at**: http://localhost:5001

### Step 3: Demo Login Credentials

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Admin** | admin@example.com | Admin123! | System configuration |
| **Instructor** | instructor@demo.com | instructor123 | Course management, feedback review |
| **Student 1** | student1@demo.com | student123 | Alice Johnson - Assignment submission |
| **Student 2** | student2@demo.com | student123 | Bob Wilson - Assignment submission |

## 🎭 Quick Demo Flow

### Phase 1: Admin Overview (3 minutes)
1. **Login** as admin@example.com / Admin123!
2. **Navigate to Admin Dashboard**
3. **Show AI Models Management**
   - Point out GPT-4o, Claude 3 Sonnet, Gemini 1.5 Pro
   - Explain: "Multiple AI providers for balanced feedback"
4. **Show User Management**
   - Instructor approval workflow
   - Domain-based auto-approval

### Phase 2: Current Architecture Demo (7 minutes)
1. **Show Database Schema**
   - Complete user management system
   - Course and assignment models
   - AI model configuration
   - Feedback pipeline structure

2. **Highlight Key Features**
   - Role-based authentication ✅
   - Multi-AI model support ✅
   - Rubric-based assignments ✅
   - Privacy-first design ✅
   - Instructor feedback interfaces ✅

3. **Code Walkthrough** (if technical audience)
   - Show `app/utils/ai_client.py` - LiteLLM integration
   - Show `app/routes/instructor.py` - Feedback interfaces
   - Explain aggregation algorithms

### Phase 3: Value Proposition (5 minutes)

**Key Talking Points:**

1. **Multi-AI Advantage**
   > "Instead of relying on one AI model, FeedForward combines multiple AI engines (GPT-4, Claude, Gemini) for balanced, unbiased feedback."

2. **Instructor Control**
   > "AI handles initial assessment, but instructors review and approve all feedback before students see it."

3. **Educational Focus**
   > "Designed specifically for iterative learning - students submit multiple drafts and track improvement over time."

4. **Privacy & Security**
   > "Student content is automatically removed after feedback generation. FERPA-compliant design."

5. **Scalability**
   > "Handle 200 submissions as easily as 20, while maintaining educational quality."

## 🎪 Demo Highlights to Show

### 1. **AI Model Configuration Interface**
```
Location: /admin/models
Show: Multiple provider support, encrypted API key storage
```

### 2. **User Management System**
```
Location: /admin/users  
Show: Role-based access, instructor approval workflow
```

### 3. **Feedback Interface Architecture**
```
Files to highlight:
- app/routes/instructor.py (lines 3900+) - New feedback interfaces
- app/utils/ai_client.py - AI integration
- app/utils/feedback_orchestrator.py - Multi-model coordination
```

### 4. **Database Schema**
```
Show: Comprehensive data model for educational feedback
- User roles and permissions
- Course and assignment management  
- AI model configurations
- Feedback pipeline tables
```

## 💡 Demo Scripts & Talking Points

### For Technical Audience:
"Let me show you the architecture. We have a complete FastHTML application with multi-AI integration. The system uses LiteLLM to support any AI provider, implements sophisticated feedback aggregation algorithms, and provides comprehensive instructor oversight interfaces."

### For Educational Audience:
"FeedForward solves the feedback bottleneck in education. Instructors can provide detailed, consistent feedback to all students while maintaining pedagogical control. Students get faster turnaround times and more comprehensive guidance."

### For Administrative Audience:
"This system reduces instructor workload while improving feedback quality. It's scalable to your entire institution and provides data insights to improve educational outcomes."

## 🔧 Demo Troubleshooting

### If Nothing Loads:
1. Check virtual environment is activated
2. Verify all dependencies installed: `pip list | grep fasthtml`
3. Check port 5001 is available: `lsof -i :5001`

### If Database Issues:
1. Delete data directory: `rm -rf data/`
2. Re-run initialization: `python app/init_db.py`

### If Import Errors:
1. Ensure you're in project root directory
2. Check Python path: `python -c "import sys; print(sys.path)"`

## 📊 Success Metrics for Demo

### Technical Success:
- ✅ Application starts without errors
- ✅ Admin login works
- ✅ AI models interface loads
- ✅ Database properly initialized

### Business Success:
- ✅ Audience understands multi-AI value proposition
- ✅ Instructor control benefits are clear
- ✅ Scalability advantages demonstrated
- ✅ Educational benefits articulated

## 🎯 Next Steps After Demo

1. **For Interested Parties:**
   - Provide access to demo environment
   - Schedule technical deep-dive
   - Discuss integration requirements

2. **For Developers:**
   - Share GitHub repository
   - Provide development setup guide
   - Discuss API key configuration

3. **For Institutions:**
   - Pilot program discussion
   - LMS integration planning
   - Deployment strategy consultation

---

**Remember**: The goal is to show the vision and architecture. Even without full test data, the comprehensive system design and AI integration demonstrate the platform's potential.