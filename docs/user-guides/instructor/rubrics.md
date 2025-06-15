---
layout: default
title: Rubrics
parent: Instructor Guide
grand_parent: User Guides
nav_order: 3
---

# Rubric Design Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

Well-designed rubrics are essential for generating high-quality AI feedback. This guide covers creating effective rubric templates, defining clear criteria, setting appropriate weights, and ensuring rubrics align with your learning objectives.

## Understanding Rubrics in FeedForward

### Why Rubrics Matter

In FeedForward, rubrics serve multiple purposes:

1. **Guide AI Evaluation** - Provide structured criteria for AI models
2. **Ensure Consistency** - Standardize feedback across submissions
3. **Clarify Expectations** - Show students exactly what's evaluated
4. **Track Progress** - Enable measurement of improvement
5. **Save Time** - Reusable templates streamline grading

### Rubric Components

Each rubric contains:

```yaml
Rubric Structure:
  Name: Essay Evaluation Rubric
  Description: Comprehensive rubric for academic essays
  
  Categories:
    - Name: Thesis Statement
      Weight: 20%
      Criteria: Clear, arguable, focused
      
    - Name: Evidence & Support
      Weight: 25%
      Criteria: Relevant, credible, integrated
      
  Performance Levels:
    - Excellent (90-100%)
    - Good (80-89%)
    - Satisfactory (70-79%)
    - Needs Improvement (0-69%)
```

## Creating Your First Rubric

### Step-by-Step Creation

1. **Access Rubric Creator**
   - Navigate to **"Rubric Templates"**
   - Click **"Create New Rubric"**

2. **Basic Information**
   ```yaml
   Template Details:
     Name: Research Paper Rubric
     Category: Academic Writing
     Description: |
       Evaluates research papers on content quality,
       research depth, and academic writing standards
     
     Visibility: My Courses Only
     Share with Department: Optional
   ```

3. **Add Evaluation Categories**

   **Category 1: Research Quality**
   ```yaml
   Weight: 30%
   Description: Evaluates source quality and research depth
   
   Excellent (27-30 points):
     - Uses 8+ peer-reviewed sources
     - Sources are recent and authoritative
     - Research directly supports thesis
     - Shows deep understanding of topic
   
   Good (24-26 points):
     - Uses 6-7 peer-reviewed sources
     - Most sources are appropriate
     - Research generally supports thesis
     - Shows good understanding
   
   Satisfactory (21-23 points):
     - Uses 5 peer-reviewed sources
     - Some sources may be dated
     - Research somewhat supports thesis
     - Shows basic understanding
   
   Needs Improvement (0-20 points):
     - Uses fewer than 5 sources
     - Sources lack credibility
     - Research poorly supports thesis
     - Limited understanding shown
   ```

4. **Continue Adding Categories**
   - Analysis & Argumentation (25%)
   - Organization & Structure (20%)
   - Writing & Citations (15%)
   - Originality & Insight (10%)

5. **Configure Settings**
   ```yaml
   Rubric Settings:
     Total Points: 100
     Grading Scale: Percentage
     Show Points: Yes
     Show Descriptions: Yes
     Allow Partial Credit: Yes
   ```

## Rubric Best Practices

### Clear, Measurable Criteria

#### Good Criteria Examples
✅ "Uses 5+ peer-reviewed sources published within last 10 years"
✅ "Thesis statement appears in first paragraph, is one sentence"
✅ "Each body paragraph begins with clear topic sentence"
✅ "Citations follow APA 7th edition format with no errors"

#### Poor Criteria Examples
❌ "Shows good understanding" (too vague)
❌ "Writing is engaging" (subjective)
❌ "Appropriate length" (undefined)
❌ "Quality sources" (unclear standard)

### Appropriate Weighting

Align weights with learning objectives:

```yaml
Essay Assignment Focus:
  Critical Thinking: 40%
    - Analysis (25%)
    - Argumentation (15%)
  
  Writing Skills: 35%
    - Organization (20%)
    - Style & Grammar (15%)
  
  Content Knowledge: 25%
    - Understanding (15%)
    - Application (10%)
```

### Progressive Difficulty

Design rubrics that show clear progression:

```yaml
Performance Levels:
  Excellent:
    - Exceeds all requirements
    - Shows mastery
    - Original insights
    - Publication quality
  
  Good:
    - Meets all requirements
    - Shows proficiency
    - Clear understanding
    - Minor issues only
  
  Satisfactory:
    - Meets most requirements
    - Shows competence
    - Basic understanding
    - Some notable issues
  
  Needs Improvement:
    - Meets few requirements
    - Shows developing skills
    - Limited understanding
    - Significant issues
```

## Rubric Templates Library

### Pre-Built Templates

FeedForward includes templates for common assignments:

#### Academic Essay Rubric
```yaml
Categories:
  - Thesis & Introduction (20%)
  - Body Paragraphs & Evidence (30%)
  - Analysis & Critical Thinking (25%)
  - Conclusion (10%)
  - Grammar & Style (15%)

Best For: General essays, argumentative papers
```

#### Research Paper Rubric
```yaml
Categories:
  - Research Question (15%)
  - Literature Review (25%)
  - Methodology (20%)
  - Analysis & Results (25%)
  - Academic Writing (15%)

Best For: Research papers, thesis work
```

#### Creative Writing Rubric
```yaml
Categories:
  - Plot & Structure (25%)
  - Character Development (25%)
  - Style & Voice (20%)
  - Creativity & Originality (20%)
  - Technical Writing (10%)

Best For: Short stories, creative essays
```

#### Presentation Rubric
```yaml
Categories:
  - Content Quality (30%)
  - Organization (20%)
  - Delivery (20%)
  - Visual Aids (15%)
  - Engagement (15%)

Best For: Oral presentations, video submissions
```

### Customizing Templates

1. **Clone Existing Template**
   - Select template
   - Click "Clone & Edit"
   - Modify as needed

2. **Adjust for Your Needs**
   - Change weights
   - Add/remove categories
   - Modify descriptions
   - Update point values

## Advanced Rubric Features

### Multi-Dimensional Rubrics

Create rubrics that evaluate multiple aspects:

```yaml
Holistic + Analytic Approach:
  Overall Impression: 20%
    - First reader impact
    - Coherence
    - Meeting objectives
  
  Detailed Analysis: 80%
    - Content (30%)
    - Structure (25%)
    - Style (15%)
    - Mechanics (10%)
```

### Conditional Criteria

Set criteria that depend on assignment type:

```yaml
Dynamic Rubric Elements:
  If Assignment Type = "Research":
    Add: Source Evaluation (20%)
    Add: Methodology (15%)
  
  If Assignment Type = "Creative":
    Add: Originality (25%)
    Add: Voice (20%)
  
  If Word Count > 2000:
    Add: Extended Analysis (15%)
```

### Rubric Versioning

Manage rubric evolution:

1. **Version Control**
   - Save rubric versions
   - Track changes
   - Compare versions
   - Rollback if needed

2. **Assignment Linking**
   - Rubrics linked to assignments
   - Updates don't affect past work
   - Clear version history

## Using Rubrics Effectively

### Student Communication

Share rubrics with students:

1. **Before Assignment**
   - Include in assignment description
   - Discuss in class
   - Provide examples
   - Answer questions

2. **During Drafting**
   - Students self-assess
   - Reference while writing
   - Guide revision

3. **After Feedback**
   - See scores by category
   - Understand strengths/weaknesses
   - Plan improvements

### AI Optimization

Help AI use your rubrics effectively:

```yaml
AI-Friendly Rubric Design:
  Specific Language:
    ✅ "Includes 3 supporting examples per main point"
    ❌ "Adequate support"
  
  Quantifiable Metrics:
    ✅ "750-1000 words"
    ❌ "Appropriate length"
  
  Clear Indicators:
    ✅ "Topic sentence starts each paragraph"
    ❌ "Well-organized"
```

### Calibration Sessions

Ensure consistent application:

1. **Test with Sample Papers**
   - Run AI evaluation
   - Compare to your assessment
   - Adjust rubric language
   - Refine criteria

2. **Monitor Over Time**
   - Track score distributions
   - Identify problem areas
   - Update descriptions
   - Maintain standards

## Rubric Analytics

### Performance Tracking

Monitor rubric effectiveness:

```yaml
Rubric Metrics:
  Usage Statistics:
    - Times used: 145
    - Courses: 5
    - Students evaluated: 489
  
  Score Distribution:
    - Average: 78.5%
    - Median: 80%
    - Standard deviation: 12.3
  
  Category Performance:
    - Lowest average: Grammar (65%)
    - Highest average: Organization (85%)
```

### Improvement Insights

Use data to refine rubrics:

1. **Identify Problem Areas**
   - Categories with low scores
   - High variation areas
   - Unclear criteria

2. **Student Feedback**
   - Confusion points
   - Helpful categories
   - Suggested improvements

## Sharing and Collaboration

### Department Libraries

Build shared rubric resources:

1. **Contributing Rubrics**
   - Mark as "Department Shared"
   - Add usage notes
   - Include examples
   - Update regularly

2. **Using Shared Rubrics**
   - Browse department library
   - Clone for customization
   - Provide feedback
   - Suggest improvements

### Export and Import

Transfer rubrics between systems:

```yaml
Export Options:
  Format: JSON, CSV, PDF
  Include: 
    - All criteria
    - Performance levels
    - Descriptions
    - Examples
  
Import Process:
  1. Select file
  2. Map categories
  3. Preview rubric
  4. Confirm import
```

## Common Rubric Pitfalls

### Avoid These Mistakes

1. **Too Many Categories**
   - Overwhelming for students
   - Difficult for AI to process
   - Hard to maintain focus
   - **Solution**: 4-7 categories maximum

2. **Unbalanced Weights**
   - Grammar worth 40%
   - Content worth 10%
   - **Solution**: Align with objectives

3. **Vague Language**
   - "Good organization"
   - "Appropriate style"
   - **Solution**: Specific, measurable criteria

4. **Missing Ranges**
   - Jump from "Excellent" to "Poor"
   - No middle ground
   - **Solution**: 3-5 performance levels

## Rubric Examples by Discipline

### English/Writing
```yaml
Focus Areas:
  - Argumentation
  - Evidence integration
  - Style and voice
  - Grammar and mechanics
```

### STEM Fields
```yaml
Focus Areas:
  - Problem-solving process
  - Technical accuracy
  - Data presentation
  - Scientific reasoning
```

### Social Sciences
```yaml
Focus Areas:
  - Theory application
  - Research methodology
  - Critical analysis
  - APA formatting
```

### Business
```yaml
Focus Areas:
  - Professional communication
  - Data analysis
  - Strategic thinking
  - Practical application
```

## Next Steps

- Learn about [Student Invitations](./student-invites)
- Master [Feedback Review](./feedback-review)
- Explore [Analytics](./analytics)

---

{: .tip }
> Start with simple rubrics and add complexity as you see how AI interprets your criteria. Regular refinement leads to better feedback quality.

{: .note }
> Share successful rubrics with colleagues to build a department-wide resource library.