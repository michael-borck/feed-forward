---
layout: default
title: Quick Start
parent: Getting Started
nav_order: 3
---

# Quick Start Guide
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

This guide will help you get FeedForward up and running quickly with a minimal setup. We'll create your first course, assignment, and generate AI feedback in just a few minutes.

{: .note }
> This guide assumes you've already completed the [Installation](./installation) and [Configuration](./configuration) steps.

## Step 1: Start FeedForward

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```

3. **Open your browser** to [http://localhost:5001](http://localhost:5001)

## Step 2: Log In as Administrator

1. Click **"Login"** in the navigation bar
2. Use the admin credentials you created during installation
3. You'll be redirected to the Admin Dashboard

{: .tip }
> If you haven't created an admin account yet, run:
> ```bash
> python tools/create_admin.py
> ```

## Step 3: Configure Your First AI Model

1. From the Admin Dashboard, click **"AI Models"**
2. Click **"Add New Model"**
3. Fill in the basic configuration:
   - **Provider**: Select your configured provider (e.g., OpenAI)
   - **Model Name**: Enter model identifier (e.g., `gpt-4`)
   - **Display Name**: Friendly name (e.g., "GPT-4 Latest")
   - **Description**: Brief description of the model
4. Click **"Save Model"**

{: .note }
> Make sure you've added the appropriate API key in your `.env` file for the provider you selected.

## Step 4: Create an Instructor Account

1. Go to **"User Management"** in the Admin Dashboard
2. Click **"Create Instructor"**
3. Enter instructor details:
   - Name: Dr. Jane Smith
   - Email: instructor@example.com
   - Password: (set a secure password)
4. Click **"Create Account"**

## Step 5: Log In as Instructor

1. **Log out** from the admin account
2. **Log in** with the instructor credentials
3. You'll see the Instructor Dashboard

## Step 6: Create Your First Course

1. Click **"Create New Course"**
2. Fill in course details:
   - **Course Name**: Introduction to Writing
   - **Course Code**: WRIT101
   - **Description**: Foundational writing skills course
3. Click **"Create Course"**

## Step 7: Create a Rubric Template

1. Navigate to **"Rubric Templates"**
2. Click **"Create New Template"**
3. Enter template details:
   - **Name**: Basic Essay Rubric
   - **Description**: Standard rubric for essay assignments
4. Add rubric categories:
   - **Thesis Statement** (Weight: 25%)
   - **Evidence & Support** (Weight: 25%)
   - **Organization** (Weight: 25%)
   - **Grammar & Style** (Weight: 25%)
5. Click **"Save Template"**

## Step 8: Create Your First Assignment

1. Go to your course page
2. Click **"Create Assignment"**
3. Fill in assignment details:
   ```
   Title: Essay Draft 1
   Instructions: Write a 500-word essay on a topic of your choice
   Due Date: [Set to 1 week from now]
   Max Drafts: 3
   ```
4. Select your rubric template
5. Configure AI settings:
   - **AI Model**: Select the model you configured
   - **Number of Runs**: 3
   - **Aggregation Method**: Average
6. Click **"Create Assignment"**

## Step 9: Add Students

1. In the course page, click **"Manage Students"**
2. Choose one of these methods:

   **Option A: Quick Test (Single Student)**
   - Click **"Add Single Student"**
   - Email: `student@example.com`
   - The system will send an invitation

   **Option B: CSV Upload**
   - Download the CSV template
   - Add student emails (one per line)
   - Upload the file

## Step 10: Submit as Student

1. **Check the invitation email** (if email is configured)
2. **Register** using the invitation link
3. **Log in** as the student
4. Navigate to **"My Courses"** → **"WRIT101"**
5. Click on **"Essay Draft 1"**
6. Submit your draft:
   ```
   This is my essay about the importance of continuous learning.
   Learning is a lifelong journey that enriches our lives...
   [Add more content for better feedback]
   ```
7. Click **"Submit Draft"**

## Step 11: View AI Feedback

1. After submission, the system will process your draft
2. Wait a few moments (processing typically takes 30-60 seconds)
3. Click **"View Feedback"** when available
4. Review the AI-generated feedback for each rubric category

{: .tip }
> The page auto-refreshes every 5 seconds while processing.

## Step 12: Review as Instructor

1. **Log back in** as the instructor
2. Go to your course → assignment
3. Click **"Review Feedback"**
4. You'll see all student submissions
5. Click on a submission to review the AI feedback
6. You can:
   - Approve the feedback as-is
   - Edit feedback before approval
   - Adjust scores if needed

## What's Next?

Congratulations! You've successfully:
- ✅ Set up FeedForward
- ✅ Configured an AI model
- ✅ Created a course and assignment
- ✅ Submitted student work
- ✅ Generated and reviewed AI feedback

### Explore More Features

- **Multiple AI Models**: Configure different models and compare their feedback
- **Custom Rubrics**: Create detailed rubrics with specific criteria
- **Feedback Styles**: Experiment with different feedback tones and approaches
- **Progress Tracking**: Submit multiple drafts to see improvement
- **Bulk Operations**: Process multiple students efficiently

### Recommended Next Steps

1. **Read the full guides:**
   - [Student Guide](/user-guides/student/) - Complete student workflow
   - [Instructor Guide](/user-guides/instructor/) - Advanced features
   - [Admin Guide](/user-guides/admin/) - System management

2. **Configure additional features:**
   - Set up more AI providers
   - Create feedback style templates
   - Configure automated cleanup

3. **Deploy to production:**
   - Review [Deployment Guide](/deployment/)
   - Set up SSL/TLS
   - Configure backup procedures

## Getting Help

- 📚 Check the [User Guides](/user-guides/) for detailed documentation
- 🔧 See [Troubleshooting](/deployment/troubleshooting) for common issues
- 💬 [Open an issue](https://github.com/michael-borck/feed-forward/issues) on GitHub
- 📧 Contact your system administrator

---

{: .note }
> Remember: FeedForward is designed for formative feedback. The AI suggestions should supplement, not replace, instructor expertise.