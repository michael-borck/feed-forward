---
layout: default
title: Assignments
parent: Instructor Guide
grand_parent: User Guides
nav_order: 2
---

# Assignment Creation Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Assignments are the core of the FeedForward learning experience. This guide covers creating effective assignments, configuring AI feedback settings, managing submissions, and optimizing the assignment workflow for student success.

## Creating Your First Assignment

### Quick Start

1. Navigate to your course
2. Click **"Create Assignment"**
3. Fill in basic details:
   - Title: "Essay 1: Personal Narrative"
   - Instructions: Clear, detailed requirements
   - Due date: Allow adequate time
   - Max drafts: 3 (recommended)

### Detailed Assignment Creation

#### Step 1: Basic Information

```yaml
Assignment Details:
  Title: Research Paper - Climate Change Solutions
  Module: Unit 3: Research Writing (optional)
  
Instructions: |
  Write a 1500-word research paper proposing innovative
  solutions to climate change challenges. Your paper should:
  
  - Present a clear thesis statement
  - Include at least 5 peer-reviewed sources
  - Follow APA 7th edition format
  - Address counterarguments
  - Propose actionable solutions
  
Resources:
  - APA Citation Guide: [link]
  - Library Database Access: [link]
  - Sample Papers: [link]
```

#### Step 2: Submission Settings

```yaml
Submission Configuration:
  Availability:
    Open Date: March 1, 2024, 8:00 AM
    Due Date: March 15, 2024, 11:59 PM
    Close Date: March 22, 2024, 11:59 PM
  
  Draft Settings:
    Maximum Drafts: 3
    Hours Between Drafts: 24
    Show Previous Feedback: Yes
  
  File Requirements:
    Accepted Formats: PDF, DOCX, TXT
    Maximum File Size: 10 MB
    File Naming: Optional pattern
```

#### Step 3: Rubric Selection

Choose or create an evaluation rubric:

1. **Select Existing Rubric**
   - Browse rubric library
   - Preview criteria
   - Clone and modify if needed

2. **Create New Rubric**
   - Click "Create Custom Rubric"
   - Define criteria and weights
   - Save as template for reuse

#### Step 4: AI Configuration

Configure how AI models evaluate submissions:

```yaml
AI Settings:
  Primary Model: GPT-4 (Latest)
  Secondary Model: Claude-3 Opus
  Tertiary Model: None
  
Evaluation Parameters:
  Runs per Model: 3
  Temperature: 0.7
  Max Tokens: 2500
  
Aggregation Method: Weighted Average
  GPT-4 Weight: 60%
  Claude-3 Weight: 40%
  
Feedback Options:
  Feedback Level: Detailed
  Include Scores: Yes
  Show Confidence: No
  Highlight Strengths: Yes
  Suggest Improvements: Yes
```

#### Step 5: Advanced Options

```yaml
Additional Settings:
  Peer Review:
    Enabled: No
    Anonymous: N/A
  
  Plagiarism Check:
    Enabled: Yes
    Service: Turnitin
    Threshold: 15%
  
  Special Instructions:
    Late Policy: -10% per day
    Grace Period: 1 hour
    Minimum Word Count: 1400
    Maximum Word Count: 1600
```

## Assignment Types and Best Practices

### Essay Assignments

Best for: Writing skills, argumentation, analysis

```yaml
Recommended Settings:
  Drafts: 3-4
  AI Models: GPT-4, Claude-3
  Temperature: 0.7-0.8
  Focus: Structure, argumentation, evidence
  
Rubric Emphasis:
  - Thesis clarity (20%)
  - Evidence quality (25%)
  - Analysis depth (25%)
  - Organization (20%)
  - Grammar/Style (10%)
```

### Research Papers

Best for: Academic research, source integration

```yaml
Recommended Settings:
  Drafts: 2-3
  AI Models: GPT-4, Claude-3
  Temperature: 0.6-0.7
  Focus: Sources, methodology, analysis
  
Rubric Emphasis:
  - Research quality (30%)
  - Methodology (20%)
  - Analysis (25%)
  - Academic writing (15%)
  - Citations (10%)
```

### Creative Writing

Best for: Narrative skills, creativity

```yaml
Recommended Settings:
  Drafts: 3-5
  AI Models: GPT-4, Claude-3
  Temperature: 0.8-0.9
  Focus: Creativity, voice, narrative
  
Rubric Emphasis:
  - Creativity (25%)
  - Character development (25%)
  - Plot structure (20%)
  - Voice/Style (20%)
  - Technical writing (10%)
```

### Technical Reports

Best for: STEM fields, professional writing

```yaml
Recommended Settings:
  Drafts: 2-3
  AI Models: GPT-4, Claude-3
  Temperature: 0.5-0.6
  Focus: Clarity, accuracy, structure
  
Rubric Emphasis:
  - Technical accuracy (30%)
  - Clarity (25%)
  - Data presentation (20%)
  - Professional format (15%)
  - Conclusions (10%)
```

## Managing Assignments

### Assignment Dashboard

View all assignments at a glance:

```
Assignment Overview:
┌─────────────────────┬──────────┬────────────┬─────────┐
│ Assignment          │ Status   │ Submissions│ Reviews │
├─────────────────────┼──────────┼────────────┼─────────┤
│ Essay 1             │ Active   │ 45/50      │ 12      │
│ Research Paper      │ Upcoming │ 0/50       │ 0       │
│ Final Project       │ Draft    │ N/A        │ N/A     │
└─────────────────────┴──────────┴────────────┴─────────┘
```

### Assignment Status Management

Control assignment availability:

1. **Draft Status**
   - Not visible to students
   - Allows full editing
   - No submissions possible

2. **Published Status**
   - Visible to students
   - Limited editing allowed
   - Submissions enabled

3. **Closed Status**
   - No new submissions
   - Existing submissions processed
   - Read-only for students

### Editing Assignments

Make changes to existing assignments:

#### Safe Edits (Always Allowed)
- Instructions clarification
- Resource additions
- Extended deadlines
- Rubric descriptions

#### Restricted Edits (With Warnings)
- Due date reduction
- Rubric criteria changes
- AI model changes
- Draft limit reduction

#### Not Recommended
- Changing file formats mid-assignment
- Major rubric overhauls
- Reducing maximum drafts

## Submission Management

### Monitoring Submissions

Track student progress:

1. **Submission Overview**
   ```
   Real-time Status:
   - Not Started: 5 students
   - In Progress: 15 students
   - Submitted: 25 students
   - Completed: 5 students
   ```

2. **Individual Progress**
   - Draft history
   - Improvement tracking
   - Time between drafts
   - Feedback viewed status

### Handling Late Submissions

Configure late submission policies:

```yaml
Late Submission Options:
  Accept Late Work: Yes
  Penalty Type: Percentage
  Penalty Amount: 10% per day
  Maximum Penalty: 50%
  
Grace Period:
  Duration: 1 hour
  Apply Penalty: No
  
Exceptions:
  Allow Individual Extensions: Yes
  Require Documentation: Optional
```

### Bulk Operations

Manage multiple submissions efficiently:

1. **Bulk Actions Available**
   - Mark as reviewed
   - Grant extensions
   - Export submissions
   - Send reminders

2. **Filtering Options**
   - By status
   - By submission date
   - By number of drafts
   - By review status

## AI Feedback Configuration

### Understanding AI Models

Choose appropriate models for your content:

#### GPT-4 (OpenAI)
- **Strengths**: General purpose, creative writing, analysis
- **Best for**: Essays, creative work, complex reasoning
- **Temperature**: 0.7-0.8 for balanced output

#### Claude-3 (Anthropic)
- **Strengths**: Academic writing, detailed analysis, safety
- **Best for**: Research papers, technical writing
- **Temperature**: 0.6-0.7 for consistency

#### Gemini (Google)
- **Strengths**: Multilingual, factual accuracy
- **Best for**: International students, fact-based content
- **Temperature**: 0.5-0.7 for accuracy

### Optimizing AI Settings

#### Number of Runs
- **1-2 runs**: Quick assignments, formative feedback
- **3-4 runs**: Standard assignments, balanced perspective
- **5+ runs**: High-stakes assignments, maximum consistency

#### Temperature Settings
- **0.3-0.5**: Consistent, conservative feedback
- **0.6-0.7**: Balanced creativity and consistency
- **0.8-1.0**: Creative, varied perspectives

#### Aggregation Methods

1. **Average**
   - Use when: All models equally trusted
   - Result: Balanced consensus
   - Best for: Standard assignments

2. **Weighted Average**
   - Use when: Some models preferred
   - Result: Biased toward better models
   - Best for: Specialized content

3. **Maximum**
   - Use when: Encouraging improvement
   - Result: Most optimistic scores
   - Best for: Early drafts

4. **Median**
   - Use when: Avoiding outliers
   - Result: Middle ground feedback
   - Best for: Consistent grading

## Advanced Features

### Assignment Templates

Save time with reusable templates:

1. **Create Template**
   - Design assignment
   - Click "Save as Template"
   - Name and categorize

2. **Use Template**
   - Select from template library
   - Modify as needed
   - Deploy quickly

### Conditional Release

Set prerequisites for assignments:

```yaml
Prerequisites:
  Require Completion Of:
    - Assignment: Essay 1
    - Minimum Score: 70%
  
  Or Time-Based:
    - After Date: March 1
    - Complete Module: Unit 2
```

### Assignment Analytics

Track assignment effectiveness:

1. **Performance Metrics**
   - Average scores by draft
   - Improvement rates
   - Time to completion
   - Feedback utilization

2. **AI Usage Analytics**
   - Model performance comparison
   - Cost per submission
   - Processing time
   - Feedback quality scores

## Best Practices

### Clear Instructions
1. **Structure Instructions**
   - Use bullet points
   - Highlight key requirements
   - Provide examples
   - Link resources

2. **Avoid Ambiguity**
   - Specific word counts
   - Clear formatting requirements
   - Explicit evaluation criteria
   - Defined expectations

### Effective Rubrics
1. **Align with Objectives**
   - Match learning goals
   - Measure intended skills
   - Progressive difficulty
   - Clear indicators

2. **Student-Friendly Language**
   - Avoid jargon
   - Provide examples
   - Explain criteria
   - Show growth path

### Feedback Timing
1. **Quick Turnaround**
   - Review within 48 hours
   - Enable rapid iteration
   - Maintain momentum
   - Support learning

2. **Strategic Release**
   - Consider class schedule
   - Allow revision time
   - Coordinate with lessons
   - Build on feedback

## Troubleshooting

### Common Issues

**Students Can't Submit**
- Check assignment dates
- Verify file format settings
- Confirm course enrollment
- Test with student account

**AI Feedback Delayed**
- Check system status
- Verify API keys active
- Review model availability
- Contact admin if persistent

**Inconsistent Scoring**
- Review rubric clarity
- Check AI temperature
- Increase run count
- Consider different models

**File Upload Errors**
- Verify file size limits
- Check format restrictions
- Test with sample file
- Clear browser cache

## Next Steps

- Master [Rubric Design](./rubrics)
- Learn about [Student Management](./student-invites)
- Understand [Feedback Review](./feedback-review)

---

{: .tip }
> Start with simple assignments and gradually increase complexity as you and your students become comfortable with the system.

{: .note }
> Remember that AI feedback is meant to supplement, not replace, your expertise. Always review and enhance AI suggestions before release.