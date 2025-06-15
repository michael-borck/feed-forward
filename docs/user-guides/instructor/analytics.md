---
layout: default
title: Analytics
parent: Instructor Guide
grand_parent: User Guides
nav_order: 6
---

# Analytics Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward's analytics provide powerful insights into student progress, assignment effectiveness, and overall course performance. This guide covers accessing analytics dashboards, interpreting data, generating reports, and using insights to improve your teaching.

## Analytics Dashboard

### Accessing Analytics

Navigate to analytics from multiple entry points:

1. **Course Level**: Course → Analytics tab
2. **Assignment Level**: Assignment → View Analytics
3. **Student Level**: Student Profile → Progress
4. **Dashboard Widget**: Quick stats on main page

### Dashboard Overview

Your analytics command center:

```
Course Analytics: ENGL101 - Fall 2024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Key Metrics
┌─────────────────┬─────────────────┬─────────────────┐
│ Active Students │ Avg Improvement │ Completion Rate │
│     48/50       │     +15.3%      │      89%        │
└─────────────────┴─────────────────┴─────────────────┘

📈 Recent Trends
• Draft submissions up 23% this week
• Average score improved from 72% to 81%
• 92% of students using multiple drafts

🎯 Quick Insights
• Top challenge: Thesis statements (-12 pts avg)
• Best improvement: Evidence usage (+18 pts avg)
• 5 students need attention (low engagement)

[View Detailed Reports] [Export Data] [Compare Periods]
```

## Student Progress Analytics

### Individual Student View

Track each student's journey:

```yaml
Student: Jane Smith
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Performance Summary:
  Current Average: 84% (B)
  Improvement Rate: +22% since first draft
  Drafts Submitted: 12 of 15 possible
  Engagement Level: High

Assignment Progress:
┌────────────────┬────────┬────────┬────────┬─────────┐
│ Assignment     │ Draft1 │ Draft2 │ Draft3 │ Change  │
├────────────────┼────────┼────────┼────────┼─────────┤
│ Essay 1        │  72%   │  81%   │  88%   │ +16%    │
│ Research Paper │  68%   │  78%   │  85%   │ +17%    │
│ Essay 2        │  75%   │  83%   │   -    │ +8%     │
└────────────────┴────────┴────────┴────────┴─────────┘

Strengths & Weaknesses:
  Consistent Strengths:
    ✓ Organization (+5 pts above average)
    ✓ Evidence Integration (+8 pts)
  
  Areas for Growth:
    ⚠ Grammar & Mechanics (-6 pts)
    ⚠ Conclusion Writing (-4 pts)
```

### Class-Wide Patterns

Identify trends across all students:

```
Class Performance Distribution:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A (90-100%): ████████ 8 students (16%)
B (80-89%):  ████████████████ 16 students (32%)
C (70-79%):  ██████████████ 14 students (28%)
D (60-69%):  ██████ 6 students (12%)
F (<60%):    ████ 4 students (8%)
No Submit:   ██ 2 students (4%)

Engagement Metrics:
  High (3+ drafts/assignment): 65%
  Medium (2 drafts/assignment): 25%
  Low (1 draft/assignment): 10%
```

### Progress Over Time

Visualize improvement trends:

```
Average Class Score by Week:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Week 1:  ████████████ 68%
Week 2:  ██████████████ 72%
Week 3:  ██████████████ 74%
Week 4:  ████████████████ 78%
Week 5:  █████████████████ 81%
Week 6:  █████████████████ 83%

Improvement Rate: +2.5% per week
Projected End Score: 87%
```

## Assignment Analytics

### Assignment Performance

Detailed metrics per assignment:

```yaml
Assignment: Research Paper Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Submission Statistics:
  Total Submissions: 145
  Unique Students: 48
  Average Drafts per Student: 3.02
  
Timing Patterns:
  Early Submissions (>24hr before): 35%
  On-Time Submissions: 58%
  Late Submissions: 7%
  
Score Distribution:
  Mean Score: 78.5%
  Median Score: 80%
  Standard Deviation: 12.3
  
Improvement Metrics:
  Average First Draft: 71.2%
  Average Final Draft: 82.4%
  Mean Improvement: +11.2%
  Students Who Improved: 92%
```

### Rubric Performance Analysis

See which criteria challenge students:

```
Rubric Category Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research Quality (30% weight)
├── Class Average: 24.2/30 (80.7%)
├── Range: 18-29
└── Improvement: +3.5 points avg

Thesis Statement (20% weight)
├── Class Average: 14.8/20 (74%)
├── Range: 10-19
└── Improvement: +2.1 points avg

Evidence Integration (25% weight)
├── Class Average: 19.5/25 (78%)
├── Range: 12-24
└── Improvement: +4.2 points avg

Writing Mechanics (15% weight)
├── Class Average: 11.2/15 (74.7%)
├── Range: 8-15
└── Improvement: +1.8 points avg

Organization (10% weight)
├── Class Average: 8.5/10 (85%)
├── Range: 6-10
└── Improvement: +0.9 points avg
```

### Draft Utilization

Understanding revision patterns:

```yaml
Draft Usage Patterns:
  
  Students Using All Drafts: 73%
  Average Time Between Drafts: 3.2 days
  
  Score Improvement by Draft:
    Draft 1→2: +8.5% average
    Draft 2→3: +4.2% average
    Draft 3→4: +2.1% average
  
  Optimal Draft Count: 3 (diminishing returns after)
```

## AI Feedback Analytics

### Model Performance Comparison

Compare AI model effectiveness:

```
AI Model Analytics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GPT-4 Performance:
├── Feedback Accepted Rate: 89%
├── Average Edit Time: 2.3 min
├── Student Satisfaction: 4.2/5
└── Cost per Feedback: $0.18

Claude-3 Performance:
├── Feedback Accepted Rate: 85%
├── Average Edit Time: 3.1 min
├── Student Satisfaction: 4.0/5
└── Cost per Feedback: $0.15

Gemini Performance:
├── Feedback Accepted Rate: 82%
├── Average Edit Time: 3.5 min
├── Student Satisfaction: 3.8/5
└── Cost per Feedback: $0.12
```

### Feedback Quality Metrics

Track feedback effectiveness:

```yaml
Feedback Impact Analysis:
  
  Student Actions After Feedback:
    Revised Based on Feedback: 87%
    Viewed Multiple Times: 65%
    Requested Clarification: 12%
  
  Improvement Correlation:
    High Engagement with Feedback: +18% improvement
    Medium Engagement: +11% improvement
    Low Engagement: +4% improvement
  
  Most Helpful Feedback Types:
    1. Specific examples (92% helpful)
    2. Step-by-step guidance (89% helpful)
    3. Resource links (78% helpful)
```

## Engagement Analytics

### Student Engagement Levels

Identify engagement patterns:

```
Engagement Scoring:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Highly Engaged (15 students - 30%):
✓ Submit all drafts
✓ View feedback within 24hr
✓ Consistent improvement
✓ Regular platform access

Moderately Engaged (25 students - 50%):
• Submit most drafts
• View feedback within 48hr
• Some improvement
• Weekly platform access

Low Engagement (8 students - 16%):
⚠ Minimal draft submission
⚠ Delayed feedback viewing
⚠ Limited improvement
⚠ Infrequent access

At Risk (2 students - 4%):
❌ Missing submissions
❌ No feedback viewing
❌ No improvement
❌ Rare/no access
```

### Time-Based Patterns

When students are most active:

```
Platform Activity Heatmap:
━━━━━━━━━━━━━━━━━━━━━━━━━━

       12a 6a  12p 6p  12a
Mon:   ░░░░▒▒▒▒████▓▓▓▓░░░░
Tue:   ░░░░▒▒▒▒████████▓▓▓▓
Wed:   ░░░░▒▒▒▒████▓▓▓▓░░░░
Thu:   ░░░░▒▒▒▒████████▓▓▓▓
Fri:   ░░░░▒▒▒▒▓▓▓▓▓▓▓▓░░░░
Sat:   ░░░░▒▒▒▒▓▓▓▓████▓▓▓▓
Sun:   ▓▓▓▓████████████████

Peak Times:
- Weekdays: 2-4 PM, 8-11 PM
- Weekends: 2-6 PM, 9 PM-12 AM
```

## Custom Reports

### Report Builder

Create tailored analytics reports:

```yaml
Report Configuration:
  Name: "Mid-Semester Progress Report"
  
  Date Range:
    Start: September 1, 2024
    End: October 15, 2024
  
  Include Sections:
    ✓ Executive Summary
    ✓ Individual Student Progress
    ✓ Assignment Performance
    ✓ Rubric Analysis
    ✓ Engagement Metrics
    ✓ AI Feedback Statistics
    ☐ Detailed Submission Logs
    
  Grouping:
    By: Assignment
    Then By: Student
  
  Format Options:
    Type: PDF
    Include Charts: Yes
    Privacy Level: Aggregate Only
```

### Automated Reports

Schedule regular report generation:

```yaml
Scheduled Reports:
  
  Weekly Summary:
    Schedule: Every Monday 8 AM
    Recipients: Instructor only
    Content: Week's activity overview
  
  Monthly Progress:
    Schedule: First of month
    Recipients: Department chair
    Content: Detailed course analytics
  
  Student Reports:
    Schedule: After each assignment
    Recipients: Individual students
    Content: Personal progress summary
```

## Using Analytics for Improvement

### Identifying Struggling Students

Early intervention indicators:

```yaml
At-Risk Indicators:
  Academic:
    - Scores below 60%
    - No improvement across drafts
    - Missing submissions
    - Declining performance
  
  Engagement:
    - Not viewing feedback
    - Single draft only
    - Late submissions pattern
    - Minimal platform time
  
  Recommended Actions:
    1. Personal outreach email
    2. Office hours invitation
    3. Additional resources
    4. Peer support connection
```

### Curriculum Adjustments

Data-driven teaching improvements:

```yaml
Insights → Actions:
  
  Low Rubric Category Scores:
    Finding: "Thesis statements averaging 65%"
    Action: Add thesis workshop in Week 3
  
  High Draft 1→2 Improvement:
    Finding: "+15% average improvement"
    Action: Encourage all students to revise
  
  Late Submission Patterns:
    Finding: "40% submit within last hour"
    Action: Send 24-hour reminders
  
  Feedback Engagement:
    Finding: "Videos linked 3x more viewed"
    Action: Include more video resources
```

### Assignment Optimization

Refine assignments based on data:

```
Assignment Refinement Process:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Analyze Performance Data
   - Identify problem areas
   - Review score distributions
   - Check completion rates

2. Gather Feedback Patterns
   - Common AI suggestions
   - Instructor edit patterns
   - Student clarifications

3. Adjust Assignment
   - Clarify instructions
   - Modify rubric weights
   - Add resources
   - Adjust difficulty

4. Monitor Impact
   - Track next cohort
   - Compare metrics
   - Iterate as needed
```

## Privacy and Ethics

### Data Privacy Controls

Manage sensitive information:

```yaml
Privacy Settings:
  Student Names: Show/Hide/Initials
  ID Numbers: Never Display
  
  Sharing Permissions:
    Individual Data: Instructor Only
    Aggregate Data: Department Allowed
    Anonymous Data: Research Allowed
  
  Export Controls:
    Include PII: Requires Confirmation
    Anonymize Option: Always Available
    Audit Trail: All Exports Logged
```

### Ethical Considerations

Using analytics responsibly:

1. **Transparency**
   - Inform students about tracking
   - Explain how data helps them
   - Allow opt-out where possible

2. **Fairness**
   - Don't penalize exploration
   - Account for circumstances
   - Focus on growth, not comparison

3. **Support Focus**
   - Use data to help, not punish
   - Identify support needs
   - Celebrate improvements

## Advanced Analytics

### Predictive Analytics

Future performance indicators:

```yaml
Predictive Models:
  
  Final Grade Prediction:
    Current Performance: B (82%)
    Engagement Level: High
    Improvement Trend: +2.1%/week
    Predicted Final: B+ (87%)
    Confidence: 78%
  
  Risk Predictions:
    Drop Risk: Low (12%)
    Failure Risk: Low (8%)
    Improvement Potential: High
```

### Comparative Analytics

Benchmark against standards:

```
Comparative Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Course vs Department Average:
├── Completion Rate: 89% vs 82% ✓
├── Average Score: 81% vs 78% ✓
├── Improvement Rate: 15% vs 11% ✓
└── Engagement: 85% vs 73% ✓

Your Course vs Previous Terms:
├── Fall 2024: 81% average
├── Spring 2024: 78% average
├── Fall 2023: 76% average
└── Trend: Improving +2.5%/term
```

### Export and Integration

Share data with other systems:

```yaml
Export Options:
  
  Formats:
    - CSV (Raw Data)
    - Excel (Formatted)
    - PDF (Reports)
    - JSON (API)
  
  Integration:
    - LMS Grade Sync
    - Institutional Research
    - Accreditation Reports
    - Research Datasets
  
  Scheduling:
    - Manual Export
    - Automated Weekly
    - End of Term
    - Custom Schedule
```

## Analytics Best Practices

### Regular Review Schedule

1. **Daily** - Check pending reviews
2. **Weekly** - Review engagement alerts
3. **After Each Assignment** - Analyze performance
4. **Monthly** - Generate progress reports
5. **End of Term** - Comprehensive analysis

### Action-Oriented Analysis

Don't just collect data—use it:

```
Data → Insight → Action Framework:

Data: "30% of students score low on conclusions"
Insight: "Students struggle with synthesis"
Action: "Add conclusion workshop before Essay 2"

Data: "Feedback viewed average 3.2 times"
Insight: "Students value detailed feedback"
Action: "Maintain comprehensive feedback approach"
```

### Student Privacy First

Always prioritize student privacy:
- Aggregate when possible
- Anonymize for sharing
- Secure all exports
- Delete when unnecessary

## Next Steps

- Return to [Instructor Overview](./index)
- Learn about [Course Management](./course-management)
- Explore [Assignment Creation](./assignments)

---

{: .tip }
> Set up weekly analytics review sessions to catch trends early and adjust your teaching accordingly.

{: .note }
> Remember that analytics are tools to support your teaching intuition, not replace it. Use data to confirm observations and discover hidden patterns.