# FeedForward Demo Guide

## 🎯 Demo Overview
**Duration**: 30-45 minutes  
**Purpose**: Showcase AI-powered multi-engine feedback system for higher education  
**Audience**: Educators, administrators, edtech stakeholders

## 🚀 Quick Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python app/init_db.py

# 4. Create demo accounts and course
python tools/create_demo_accounts.py

# 5. Start application
python app.py
```

**Access**: http://localhost:5001

## 👤 Demo Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Admin** | admin@example.com | Admin123! | System configuration, AI setup |
| **Instructor** | instructor@demo.com | instructor123 | Course management, feedback review |
| **Student 1** | student1@demo.com | student123 | Alice Johnson - Assignment submission |
| **Student 2** | student2@demo.com | student123 | Bob Wilson - Assignment submission |

## 📋 Demo Flow & Talking Points

### Phase 1: Introduction (2 minutes)

**Talking Points:**
- "FeedForward transforms educational feedback using multiple AI engines"
- "Unlike single-AI tools, we combine GPT-4, Claude, and other models for balanced assessment"
- "Instructors maintain complete control while AI handles the heavy lifting"

### Phase 2: Admin Configuration (5 minutes)

**Steps:**
1. Login as admin
2. Navigate to AI Models Management
3. Show configured AI providers

**Talking Points:**
- "Flexible AI provider support - use OpenAI, Anthropic, Google, or self-hosted models"
- "Institution-wide or instructor-specific configurations"
- "Encrypted API key storage for security"

**Demo Highlight**: Show the AI model configuration interface

### Phase 3: Instructor Setup (10 minutes)

**Steps:**
1. Login as instructor
2. Show course dashboard
3. Navigate to "Test Assignment for UI Testing"
4. Display rubric with weighted categories

**Talking Points:**
- "Rubrics drive AI evaluation - ensuring educational alignment"
- "Weighted categories allow emphasis on what matters most"
- "Each assignment can use different AI models and aggregation methods"

**Demo Highlight**: Show rubric builder with categories:
- Writing Quality (40%)
- Content Knowledge (35%)
- Critical Thinking (25%)

### Phase 4: Student Experience (5 minutes)

**Steps:**
1. Login as student
2. View assignment details
3. Show submission interface
4. Submit a draft (or use existing)

**Talking Points:**
- "Simple, intuitive interface for students"
- "Privacy-first design - submissions auto-delete after feedback"
- "Supports multiple draft iterations for improvement"

**Demo Highlight**: Show privacy notice and submission confirmation

### Phase 5: AI Processing Magic (3 minutes)

**Steps:**
1. Return to instructor view
2. Show submission status changing
3. Explain background processing

**Talking Points:**
- "Multiple AI models evaluate simultaneously in background"
- "Typical processing: 30-60 seconds for comprehensive feedback"
- "Fault-tolerant - continues even if one AI provider fails"

**Visual Aid**: Status progression:
```
submitted → processing → feedback_ready
```

### Phase 6: Instructor Review - The Core Value (15 minutes)

#### 6A: Submission Overview

**Navigate to**: `/instructor/assignments/[ID]/submissions`

**Talking Points:**
- "Complete oversight of all student submissions"
- "At-a-glance AI processing status"
- "Identify submissions needing attention"

**Demo Highlight**: Point out the "2/2 models successful" indicator

#### 6B: Individual Submission Analysis

**Click**: "View Details" → `/instructor/submissions/[DRAFT_ID]`

**Key Features to Show:**

1. **Score Comparison Table**
   ```
   Category        | GPT-4 ✅  | Claude ✅ | Aggregated
   Writing Quality | 82.0/100  | 79.5/100 | 80.8/100
   ```
   
   **Talking Point**: "See exactly how each AI model evaluated the work"

2. **Individual AI Feedback**
   - Expand GPT-4 results
   - Show strengths/improvements
   - Click "View Raw AI Response"
   
   **Talking Point**: "Full transparency - see what each AI actually said"

3. **Aggregated Results**
   - Show combined feedback
   - Explain aggregation methods
   
   **Talking Point**: "Smart aggregation reduces AI bias and improves accuracy"

#### 6C: Feedback Approval Workflow

**Click**: "Review Feedback" → `/instructor/submissions/[DRAFT_ID]/review`

**Demonstrate:**
1. Edit a score (change 80.8 to 82.0)
2. Modify feedback text
3. Use "Approve All Categories" button

**Talking Points:**
- "Instructors maintain pedagogical control"
- "Edit before students see anything"
- "Bulk actions save time for large classes"

### Phase 7: Analytics & Insights (10 minutes)

**Navigate to**: `/instructor/assignments/[ID]/analytics`

#### Show Key Metrics:

1. **Summary Cards**
   - Total Submissions: 2
   - Feedback Complete: 100%
   - Processing: 0
   - Errors: 0

2. **AI Model Performance**
   ```
   Model      | Success Rate | Avg Score
   GPT-4      | 100%        | 79.2/100
   Claude     | 100%        | 80.3/100
   ```

3. **Category Performance**
   - Visual bar charts
   - Identify class-wide struggles

**Talking Points:**
- "Data-driven insights improve teaching"
- "Identify which AI models work best for your assignments"
- "Spot trends across student submissions"
- "Make informed decisions about rubric adjustments"

**Demo Highlight**: "Claude performs better for critical thinking assessment"

### Phase 8: Student Receives Feedback (5 minutes)

**Steps:**
1. Login as student
2. View approved feedback
3. Show structured feedback format

**Talking Points:**
- "Students receive polished, instructor-approved feedback"
- "Constructive format promotes improvement"
- "Detailed enough to guide revision"

**Demo Highlight**: Progress indicators and improvement suggestions

## 🎤 Key Value Propositions

### 1. **Multi-AI Advantage**
"By using multiple AI models, we reduce bias and improve accuracy. It's like getting a second opinion from different experts."

### 2. **Instructor Empowerment**
"AI handles the time-consuming initial assessment, but instructors maintain complete control over what students receive."

### 3. **Transparency & Trust**
"See exactly how each AI evaluated student work. No black box - full visibility into the process."

### 4. **Scalability with Quality**
"Handle 200 submissions as easily as 20, while maintaining educational standards and personalized feedback."

### 5. **Continuous Improvement**
"Analytics show which AI models perform best for your specific assignments. The system gets smarter over time."

## 💡 Common Questions & Answers

**Q: What if an AI model fails?**
A: "The system continues with other models. Fault tolerance is built in."

**Q: Can instructors disable specific AI models?**
A: "Yes, both globally and per-assignment. Full flexibility."

**Q: How long does processing take?**
A: "Typically 30-60 seconds per submission, running in background."

**Q: Is student data secure?**
A: "Yes - encrypted storage, automatic deletion, FERPA compliant design."

**Q: Can we use our own AI models?**
A: "Yes - supports self-hosted models via LiteLLM integration."

## 🚨 Demo Troubleshooting

### If AI processing fails:
- Explain: "In production, this connects to real AI APIs"
- Use existing test data to continue demo
- Show error handling and retry capabilities

### If login issues occur:
```bash
# Reset test users
python tools/create_test_users.py
```

### If data is missing:
```bash
# Recreate all demo data
python tools/test_instructor_feedback_ui.py
```

## 📊 Closing Summary

**Recap the journey:**
1. ✅ Multiple AI models provide balanced assessment
2. ✅ Instructors review and control all feedback
3. ✅ Students receive constructive, approved guidance
4. ✅ Analytics drive continuous improvement
5. ✅ Scalable solution for modern education

**Call to Action:**
"FeedForward transforms how educators provide feedback - saving time while improving quality. Let's discuss how this can work for your institution."

## 🎬 Demo Variations

### **Quick Demo (10 minutes)**
- Skip admin setup
- Focus on instructor review interface
- Show one submission detail view
- Highlight analytics dashboard

### **Technical Demo (45 minutes)**
- Include API configuration
- Show raw AI responses
- Explain aggregation algorithms
- Demonstrate error handling

### **Student-Focused Demo (20 minutes)**
- Emphasize student experience
- Show multiple draft iterations
- Focus on feedback quality
- Highlight privacy features

---

**Remember**: Let the interface tell the story. The goal is to show how FeedForward makes quality feedback scalable while keeping instructors in control.