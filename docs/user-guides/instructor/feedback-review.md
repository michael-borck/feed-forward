---
layout: default
title: Feedback Review
parent: Instructor Guide
grand_parent: User Guides
nav_order: 5
---

# Feedback Review Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Feedback review is a critical quality control step in FeedForward. As an instructor, you review AI-generated feedback before it's released to students, ensuring it aligns with your teaching goals and maintains appropriate standards. This guide covers the review workflow, editing options, and best practices.

## Understanding Feedback Review

### Why Review AI Feedback?

1. **Quality Assurance** - Ensure feedback meets your standards
2. **Personalization** - Add instructor insights and context
3. **Safety Check** - Catch any inappropriate content
4. **Learning Alignment** - Verify feedback supports objectives
5. **Student Support** - Identify students needing extra help

### The Review Workflow

```
1. Student submits draft
   ↓
2. AI generates feedback
   ↓
3. Instructor notified
   ↓
4. Instructor reviews
   ↓
5. Instructor approves/edits
   ↓
6. Student receives feedback
```

## Accessing Feedback for Review

### Review Dashboard

Your central hub for pending reviews:

```
Feedback Review Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pending Reviews: 12
├── ENGL101 - Essay 1: 8 submissions
├── ENGL101 - Essay 2: 3 submissions
└── ENGL201 - Research Paper: 1 submission

Recent Activity:
• 3 new submissions in last hour
• 15 reviews completed today
• 2 flagged for attention

Quick Actions:
[Review All] [Filter] [Export] [Settings]
```

### Navigation Options

1. **From Dashboard**
   - Click notification badge
   - Select "Pending Reviews"
   - View all awaiting feedback

2. **From Course**
   - Navigate to course
   - Click "Assignments"
   - See review count per assignment

3. **From Assignment**
   - Open specific assignment
   - Click "Review Feedback"
   - See all submissions

## The Review Interface

### Submission Overview

When reviewing a submission:

```
┌─────────────────────────────────────────────────┐
│ Student: Jane Smith                             │
│ Assignment: Essay 1 - Personal Narrative        │
│ Draft: 2 of 3                                   │
│ Submitted: 2 hours ago                         │
│ Word Count: 847                                 │
│ Processing Time: 45 seconds                     │
│                                                 │
│ AI Models Used:                                 │
│ • GPT-4: 3 runs (averaged)                     │
│ • Claude-3: 3 runs (averaged)                  │
│                                                 │
│ Overall Score: 82% (B)                          │
└─────────────────────────────────────────────────┘
```

### Three-Panel Layout

The review interface shows:

```
┌─────────────┬──────────────┬─────────────────┐
│   Student   │      AI      │    Instructor   │
│ Submission  │   Feedback   │     Actions     │
│             │              │                 │
│ [Original   │ [Generated   │ [Edit Options]  │
│  Text]      │  Feedback]   │ [Scoring]       │
│             │              │ [Comments]      │
│             │              │ [Approve/Reject]│
└─────────────┴──────────────┴─────────────────┘
```

### Reading the Submission

Features for easier review:

- **Highlighting** - Mark important sections
- **Zoom** - Adjust text size
- **Search** - Find specific content
- **Navigation** - Jump between sections
- **Previous Drafts** - Compare improvements

## Understanding AI Feedback

### Feedback Components

AI feedback typically includes:

```yaml
Overall Assessment:
  Summary: Brief overview of submission quality
  Score: Numerical/letter grade
  Key Strengths: Top 2-3 positive aspects
  Main Areas for Improvement: Top 2-3 concerns

Rubric-Based Evaluation:
  For each criterion:
    - Score (points/percentage)
    - Specific feedback
    - Examples from text
    - Suggestions for improvement

Detailed Comments:
  - Paragraph-level observations
  - Writing mechanics notes
  - Content-specific feedback
  - Next steps recommendations
```

### AI Confidence Indicators

Understanding AI certainty:

```
Confidence Levels:
🟢 High (90-100%): AI very certain about evaluation
🟡 Medium (70-89%): Some uncertainty in scoring
🔴 Low (<70%): Significant uncertainty, careful review needed

Common Low-Confidence Triggers:
- Unusual formatting
- Mixed languages
- Creative/unconventional approaches
- Technical jargon
- Very short/long submissions
```

## Review Actions

### Quick Approve

For high-quality AI feedback:

1. Read through all feedback
2. Verify accuracy and appropriateness
3. Check scoring alignment
4. Click **"Approve & Release"**
5. Feedback sent to student immediately

### Edit Before Approval

When modifications needed:

1. **Click "Edit Feedback"**
2. **Editing Options:**
   ```
   Text Editing:
   - Modify any feedback text
   - Add personal comments
   - Remove inappropriate content
   - Adjust tone or language
   
   Score Adjustments:
   - Change overall score
   - Modify rubric scores
   - Add score justification
   - Override AI calculations
   ```

3. **Save and Approve**
   - Preview changes
   - Save edited version
   - Approve for release

### Adding Instructor Comments

Personalize feedback:

```yaml
Comment Options:
  Location:
    - Top of feedback (most visible)
    - After specific rubric items
    - Bottom summary
  
  Types:
    - Encouragement
    - Specific guidance
    - Resource links
    - Meeting requests
  
  Formatting:
    - Rich text editor
    - Bullet points
    - Links
    - Emphasis (bold/italic)
```

Example comment:
```
Instructor Note: Jane, I'm impressed with your improved 
thesis statement! For your final draft, consider adding 
one more supporting example in paragraph 3. Feel free to 
visit my office hours if you'd like to discuss further.
```

### Requesting Regeneration

When AI feedback is inadequate:

1. **Click "Regenerate Feedback"**
2. **Options:**
   ```
   Regeneration Settings:
   - Use Different Model: [Select]
   - Adjust Temperature: [Slider]
   - Add Context: [Text field]
   - Focus Areas: [Checkboxes]
   ```

3. **Additional Context Example:**
   ```
   "Student is ESL learner - provide more grammar 
   explanations and examples. Focus on article usage 
   and verb tenses."
   ```

### Flagging for Attention

Mark submissions needing follow-up:

```yaml
Flag Types:
  Academic Concern:
    - Potential plagiarism
    - Off-topic submission
    - Significant regression
  
  Student Support:
    - Mental health indicators
    - Request for help
    - Technical issues
  
  Technical Issue:
    - Corrupted file
    - Wrong assignment
    - System error
```

## Bulk Review Features

### Batch Processing

Handle multiple submissions efficiently:

1. **Select Multiple**
   - Check boxes next to submissions
   - Or "Select All Similar"

2. **Bulk Actions:**
   ```
   Available Actions:
   ✓ Approve all selected
   ✓ Add same comment to all
   ✓ Apply score adjustment
   ✓ Flag for later review
   ✓ Export for offline review
   ```

### Quick Review Mode

For experienced reviewers:

```
Quick Review Settings:
├── Show only essential info
├── Keyboard shortcuts enabled
├── Auto-advance after action
└── Batch similar submissions

Keyboard Shortcuts:
A - Approve
E - Edit
R - Regenerate
F - Flag
→ - Next submission
← - Previous submission
```

### Review Filters

Organize your workflow:

```yaml
Filter Options:
  By Status:
    - Unreviewed
    - In progress
    - Flagged
    - Approved
  
  By Score:
    - High (85%+)
    - Medium (70-84%)
    - Low (<70%)
    - Outliers
  
  By Student:
    - First-time submitters
    - Multiple drafts
    - Struggling students
    - High performers
  
  By Time:
    - Oldest first
    - Newest first
    - Due soon
    - Overdue
```

## Review Best Practices

### Consistency

Maintain fair standards:

1. **Review Similar Together**
   - Group by topic
   - Compare approaches
   - Ensure fair scoring

2. **Use Rubric as Guide**
   - Reference criteria
   - Apply uniformly
   - Document exceptions

3. **Track Patterns**
   - Note common issues
   - Identify trends
   - Adjust instruction

### Efficiency Tips

Streamline your process:

1. **Set Review Schedule**
   ```
   Suggested Schedule:
   - Morning: Complex submissions
   - Afternoon: Quick approvals
   - Evening: Batch processing
   
   Time Allocation:
   - Quick approve: 1-2 minutes
   - Minor edits: 3-5 minutes
   - Major revision: 10+ minutes
   ```

2. **Use Templates**
   - Common comments
   - Frequent corrections
   - Standard encouragements

3. **Prioritize Reviews**
   - Final drafts first
   - Struggling students
   - Time-sensitive items

### Educational Value

Maximize learning impact:

1. **Balance Criticism**
   - Start with positives
   - Specific improvements
   - End with encouragement

2. **Be Specific**
   ```
   ❌ "Improve your thesis"
   ✅ "Your thesis 'Technology affects society' 
      is too broad. Try focusing on one specific 
      technology and its impact, such as 'Social 
      media has fundamentally changed how teenagers 
      form friendships.'"
   ```

3. **Guide Next Steps**
   - Clear action items
   - Resources to consult
   - Office hour invitations

## Handling Special Cases

### Problematic Submissions

When content concerns arise:

1. **Off-Topic Work**
   - Don't approve AI feedback
   - Add instructor comment
   - Request resubmission
   - Note in gradebook

2. **Potential Plagiarism**
   - Flag for investigation
   - Don't release feedback
   - Follow institutional policy
   - Document concerns

3. **Personal Disclosures**
   - Handle sensitively
   - Consider privacy
   - Offer support resources
   - Consult if needed

### Technical Issues

Common problems and solutions:

**Garbled AI Feedback**
- Regenerate with different model
- Check submission format
- Manual feedback if needed

**Missing Rubric Scores**
- Manually add scores
- Check rubric configuration
- Report to admin

**Processing Errors**
- Resubmit for processing
- Try different file format
- Contact support

## Analytics and Insights

### Review Statistics

Track your review patterns:

```
Your Review Analytics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This Week:
Reviews Completed: 47
Average Review Time: 3.5 minutes
Edits Made: 23%
Regenerations: 5%

This Semester:
Total Reviews: 342
Quick Approvals: 65%
Major Edits: 15%
Regenerations: 8%
Flags: 12%

Efficiency Score: 87/100
```

### Pattern Recognition

AI identifies trends:

```yaml
Detected Patterns:
  Common Issues:
    - Thesis statements (45% of edits)
    - Citation format (30% of edits)
    - Conclusion weakness (25% of edits)
  
  Student Patterns:
    - 5 students consistently low scores
    - 3 students showing improvement
    - 2 students possible support needs
  
  Feedback Patterns:
    - GPT-4 better for creative writing
    - Claude-3 better for research papers
    - Morning reviews 20% faster
```

## Integration with Grading

### Export Options

Move feedback to gradebook:

```yaml
Export Formats:
  CSV:
    - Student name
    - Assignment
    - Score
    - Feedback summary
    - Review notes
  
  LMS Integration:
    - Direct grade sync
    - Feedback upload
    - Rubric mapping
  
  PDF Reports:
    - Individual student
    - Class summary
    - Progress tracking
```

### Grade Calculation

How scores become grades:

```
Score Mapping:
93-100% → A
90-92%  → A-
87-89%  → B+
83-86%  → B
80-82%  → B-
[continues...]

Custom Mappings:
- Curve adjustments
- Weighted categories
- Drop lowest
- Bonus points
```

## Next Steps

- Explore [Analytics](./analytics) for deeper insights
- Return to [Instructor Overview](./index)
- Learn about [Course Management](./course-management)

---

{: .tip }
> Develop a consistent review routine - students appreciate timely, thoughtful feedback more than perfect feedback delivered late.

{: .note }
> Remember that you're training AI to better understand your standards. Your edits and regeneration requests help improve future feedback quality.