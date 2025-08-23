---
title: "FeedForward: Elevate Your Learning"
subtitle: "Transforming feedback into a path to success"
author: "Michael Borck"
format: 
  pdf:
      toc: false
      colourlinks: true
  docx:
      toc: false
      highlight-style: github
  html:
      toc: true
      toc-expand: 2
      embed-resources: true
---

# FeedForward System Specification

## 1. Executive Summary

FeedForward is an AI-powered multi-engine feedback system designed to facilitate iterative, reflective learning in higher education. Rather than simply correcting student work, FeedForward delivers structured, formative feedback that empowers students to improve their drafts independently.

The system's key differentiators include:

-   **Iterative Draft Improvement**: Students can submit multiple drafts of the same assignment, tracking progress across iterations.
-   **Multi-Engine AI**: Leverages diverse AI models (ChatGPT, Claude, Llama 3, etc.) to provide balanced, comprehensive feedback.
-   **Reflective Learning**: Focuses on highlighting strengths and areas for improvement rather than directly editing student work.
-   **Rubric-Aligned Feedback**: Customizable feedback criteria that match specific assessment objectives.

Primary user types include:

-   **Students**: Submit drafts, review feedback, and track improvement.
-   **Instructors**: Create assignments, design rubrics, monitor student progress, and review AI-generated feedback.

This specification serves as a comprehensive guide for developers to implement the FeedForward system, including both student and instructor interfaces, core functionalities, and technical requirements.


## 2. Description

FeedForward is an AI-driven feedback system designed to enhance iterative and reflective learning in higher education. Instead of simply correcting student work, it provides structured, rubric-aligned feedback to help students refine their drafts independently. The platform allows students to submit multiple drafts, tracks their progress over time, and leverages multiple AI engines (such as ChatGPT, Claude, and Llama 3) to ensure balanced and comprehensive feedback. Designed for both students and instructors, the system enables students to improve their writing while allowing instructors to efficiently monitor progress, create assignments, and configure AI-generated feedback. This specification outlines the key features, user interactions, and technical requirements necessary for implementing the system.

The initial Minimum Viable Product (MVP) focuses on core functionalities, including student and instructor authentication, course and assignment creation, basic rubric setup, draft submissions, and AI-generated feedback. Students can submit up to three drafts per assignment, receiving structured feedback on strengths and areas for improvement. Instructors can manage courses, upload assignment specifications, and select AI models for feedback generation. The AI integration in the MVP supports 2-3 major providers, utilizing prompt engineering to generate structured feedback. Data storage will use SQLite for initial deployment, ensuring flexibility for future enhancements. Advanced analytics, additional content types (e.g., code, video), self-hosted AI models, and LMS integration are planned for later phases.

The system supports distinct user experiences for students and instructors. Students interact with a dashboard displaying active assignments, submission status, and feedback history, including visual progress indicators. Instructors manage courses, create assignments using a structured five-step workflow, and review feedback analytics to track student improvement. A dedicated analytics dashboard provides insights into performance trends and common issues across courses. The system architecture consists of a responsive frontend, a FastAPI-powered backend, an AI feedback processing layer, and secure data storage. Future scalability includes integrating additional AI models, expanding feedback customization, and optimizing system performance for larger cohorts.

Development follows an agile approach, starting with core functionality before expanding features in future phases. The MVP will be deployed on a university research server for initial testing, using a lightweight Python-based stack with FastAPI, HTMX, and SQLite. AI integration will focus on API-based models to simplify deployment. Testing strategies include unit tests, performance benchmarks, and usability studies with students and instructors. As the system evolves, improvements will include broader AI capabilities, richer analytics, and deeper integration with external platforms, ensuring FeedForward becomes a robust tool for iterative, data-driven learning.

## 2. MVP Scope and Deliverables

The initial implementation of FeedForward will focus on delivering a Minimum Viable Product (MVP) that demonstrates the core value proposition while maintaining a manageable development scope. This MVP will establish the foundation for future enhancements based on user feedback and performance data.

### 2.1 Simplified MVP Scope

For the MVP, the focus is on validating the core value proposition with minimal complexity. Key features include:

1.  **Authentication & User Roles**
    -   Basic login for students and instructors
    -   Role-based access control

2.  **Single AI Model Integration**
    -   Integrate one robust AI model (e.g., ChatGPT) for evaluating submissions and generating feedback
    -   Implement basic prompt engineering to incorporate rubrics into feedback generation

3.  **Instructor Features**
    -   Course creation with minimal details (course code, title, term)
    -   Assignment creation with basic details (title, description, due date) and a simple rubric builder (2-3 criteria)
    -   Basic student roster management via manual entry or CSV import
    -   Feedback review capability, allowing instructors to either release AI feedback immediately or review and modify it before release

4.  **Student Features**
    -   Dashboard to view active assignments
    -   Draft submission interface (supporting up to 3 iterations per assignment)
    -   Clear feedback view displaying strengths, improvement areas, and overall score

5.  **Data Storage & Basic Analytics**
    -   Utilize SQLite with SQLAlchemy for storing user data, submissions, and feedback
    -   Provide essential analytics focused on submission status and progress tracking

6.  **UI/UX Simplicity**
    -   Develop responsive, accessible interfaces with a focus on clear navigation and ease-of-use
    -   Prioritize core functionality and intuitive user flows, with plans for enhanced accessibility and responsiveness in future phases

**Note:** Advanced features—such as multi-model AI integration, comprehensive analytics, LMS integration, and extensive customization—will be deferred to later phases.

### 2.2 Deferred for Future Phases

The following capabilities, while important to the overall vision, will be implemented after the MVP:

1.  **Advanced Analytics**
    -   Detailed visualization dashboards
    -   Comparative analysis across courses

2.  **Complex Assignment Types**
    -   Support for code assignments
    -   Audio/video/presentation feedback

3.  **Advanced AI Features**
    -   Self-hosted models
    -   Detailed model performance tracking

4.  **Integration Capabilities**
    -   LMS integration
    -   External API for third-party applications

5.  **Advanced UI Features**
    -   Mobile-optimized views
    -   Extensive customization options

### 2.3 Success Criteria for MVP

The MVP will be considered successful if it:

-   Demonstrates the iterative feedback workflow from end to end
-   Processes assignment submissions through multiple AI models
-   Provides meaningful, actionable feedback to students
-   Enables instructors to configure rubrics and monitor progress
-   Maintains acceptable performance with a test cohort of 1-2 courses

## 3. User Personas and Journeys

### 3.1 Student Persona: Maya Johnson

-   20-year-old undergraduate student
-   English major with a focus on creative writing
-   Wants to improve writing skills but struggles with academic structure
-   Needs clear, actionable feedback that explains both strengths and weaknesses
-   Tech-savvy but values intuitive interfaces

**Journey Map: Assignment Submission and Improvement**

1.  Logs into FeedForward
2.  Views active assignments on dashboard
3.  Selects an assignment and reviews requirements
4.  Uploads first draft
5.  Receives AI-generated feedback aligned with assignment rubric
6.  Reviews feedback highlighting strengths and areas for improvement
7.  Revises work based on feedback
8.  Submits second draft
9.  Compares new feedback to see improvements
10. Repeats until satisfied or reaches draft limit
11. Views progress analytics in Feedback History

### 3.2 Instructor Persona: Dr. Thomas Chen

-   Associate Professor in Computer Science
-   Teaches multiple courses with 30-40 students each
-   Limited time for providing detailed feedback to all students
-   Wants to ensure consistent, fair assessment
-   Values data-driven insights about student performance

**Journey Map: Assignment Creation and Monitoring**

1.  Logs into FeedForward instructor portal
2.  Creates a new course or selects existing course
3.  Creates a new assignment (5-step process)
    -   Enters assignment details
    -   Uploads specifications document
    -   Creates custom rubric
    -   Configures AI feedback settings
    -   Reviews and publishes
4.  Monitors student submissions and engagement
5.  Reviews feedback quality for selected submissions
6.  Analyzes course-level stats to identify common issues
7.  Adjusts future instruction based on analytics

### 3.3 User Story Integration for Capturing and Refining Edge Cases

**Overview:**

In addition to detailed persona journeys, incorporating targeted user stories helps identify and address edge cases that may not be covered by typical workflows. This proactive approach ensures that the system is robust, user-friendly, and capable of handling unexpected scenarios.

**Purpose:**

-   **Identify Edge Cases:** Capture scenarios that fall outside the normal usage patterns (e.g., technical errors, unclear feedback, accessibility challenges).
-   **Refine Requirements:** Enhance system requirements by addressing these edge cases early in the development process.
-   **Improve Error Handling:** Inform the design of error messages, fallback processes, and user support mechanisms.
-   **Enhance Usability:** Ensure that all users, including those with accessibility needs, can interact with the system effectively.

**Key Edge Cases and User Stories:**

1.  **Draft Submission Failures:**
    -   **User Story:** 
    
    > "As a student, if my draft fails to upload due to network issues or file
    > format errors, I want to receive a clear error message and guidance on
    > how to retry, so that I can complete my submission without losing
    > progress."

    -   **Considerations:**
        -   Provide immediate, actionable error messages.
        -   Implement auto-save or local caching to prevent data loss.
        -   Include a retry mechanism with minimal friction.

1.  **Unclear or Generic AI Feedback:**
    -   **User Story:** 
    
    > "As a student, if the AI-generated feedback is unclear
    > or overly generic, I want the ability to flag the feedback for review or
    > request additional details, so I can better understand how to improve my
    > work."

    -   **Considerations:**
        -   Offer a feedback loop where students can request clarification.
        -   Allow for flagging and escalation to instructor review when needed.
        -   Provide an option to compare similar feedback across submissions.

1.  **Instructor Review Overload:**
    -   **User Story:** 
  
    > "As an instructor managing multiple courses, if I
    > receive a high volume of submissions with AI feedback, I want the system
    > to prioritize notifications and group similar issues, so that I can
    > efficiently review and make necessary adjustments."

    -   **Considerations:**
        -   Implement sorting and filtering options to group similar feedback items.
        -   Enable batch processing for common issues.
        -   Introduce priority flags for urgent or outlier cases.

2.  **Accessibility and Compatibility Challenges:**
    -   **User Story:** 
    
    > "As a user with accessibility needs, I want the
    > interface to support keyboard navigation, screen readers, and
    > high-contrast settings, ensuring that I can use the system effectively
    > regardless of my abilities."

    -   **Considerations:**
        -   Ensure compliance with accessibility standards (e.g., WCAG 2.1).
        -   Validate that all interactive elements are accessible via keyboard.
        -   Test compatibility with various assistive technologies and devices.

**Integration Approach:**

-   **Documentation:**
    Include these user stories in your project backlog and requirements documentation. This ensures that they are visible during planning and development phases.
-   **Development Planning:**
    Incorporate edge case scenarios into your sprint planning. Ensure that test cases cover these stories so that any deviations are caught early.
-   **Continuous Feedback:**
    Regularly update the user stories based on real-world usage and feedback. This helps in refining system behavior and error handling over time.
-   **Prioritization:**
    Focus on the most critical edge cases—those that impact user experience or system stability the most—in early iterations.

By embedding these user stories into your development process, you create a safety net that helps anticipate and resolve issues before they affect a larger user base. This proactive approach not only enhances the robustness of the system but also builds trust with both students and instructors.

## 4. Feature Requirements

### 4.1 Student Interface

#### 4.1.1 Dashboard

**Purpose**: Central hub showing active assignments and their status.

**Functionality**:

-   Display active assignments with due dates and draft status
-   Highlight assignments needing attention
-   Show progress indicators for assignments with multiple drafts
-   Provide quick access to assignment details and feedback

**Interactions**:

-   Clicking on assignment opens detailed view with feedback
-   Color-coded indicators show draft status (1st, 2nd, 3rd draft, etc.)

#### 4.1.2 My Submissions

**Purpose**: Comprehensive overview of all assignments across courses.

**Functionality**:

-   List all assignments (current and past)
-   Filter by course, term, and status
-   Show submission dates, due dates, and status
-   Provide access to all drafts and their feedback

**Interactions**:

-   Filtering controls to narrow view
-   "View" button to access detailed feedback
-   Pagination for navigating large numbers of assignments

#### 4.1.3 Feedback History

**Purpose**: Analytics and insights about learning progress over time.

**Functionality**:

-   Visualize performance trends over time
-   Show skill breakdown across different competencies
-   Identify recurring feedback patterns
-   Track improvement metrics
-   Allow export of feedback reports

**Interactions**:

-   Time range selection
-   Skill filtering
-   PDF export option

#### 4.1.4 Draft Management Workflow

**Purpose**: Submit, review, and improve assignment drafts.

**Functionality**:

-   Draft upload mechanism (file or direct input)
-   Draft history with version comparison
-   Progress visualization between drafts
-   Next draft submission controls

**Interactions**:

-   Draft tab navigation to switch between versions
-   Progress indicators showing improvement percentages
-   "Submit Next Draft" button to continue iterative process

```text
┌─────────────────────┐
│ Student Views       │
│ Active Assignments  │
└─────────┬───────────┘
        ▼
┌─────────────────────┐
│ Student Selects     │
│ Assignment          │
└─────────┬───────────┘
        ▼
┌─────────────────────────────────┐
│ First Draft?                    │
└──────┬──────────────────┬───────┘
      │                  │
      ▼ Yes              ▼ No
┌─────────────┐    ┌─────────────────┐
│ Review      │    │ Review Previous │
│ Assignment  │    │ Feedback &      │
│ Requirements│    │ Drafts          │
└──────┬──────┘    └────────┬────────┘
      │                  │
      └─────────┬──────────┘
              ▼
┌─────────────────────────────────┐
│ Student Prepares Draft          │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Submit Draft                    │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Multi-Model Assessment Process  │
│ (See Assessment Workflow)       │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Student Receives Feedback       │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Decision Point                  │
│ Submit Another Draft?           │
└──────┬──────────────────┬───────┘
      │                  │
      ▼ Yes              ▼ No
┌─────────────┐    ┌─────────────────┐
│ Review      │    │ Assignment      │
│ Feedback &  │    │ Complete        │
│ Improve     │    │                 │
└──────┬──────┘    └─────────────────┘
      │
      ▼
┌─────────────────────┐
│ Submit Next Draft   │
│ (Returns to Process)│
└─────────────────────┘
```

#### 4.1.5 Feedback Visualization

**Purpose**: Present AI-generated feedback in an actionable format.

**Functionality**:

-   Overall score and progress metrics
-   Strengths and areas for improvement summaries
-   Rubric-aligned feedback categories
-   In-text annotations linking to feedback points
-   Model source transparency (which AI provided which feedback)

**Interactions**:

-   Toggle between different feedback views
-   View annotated draft with in-line feedback
-   Navigation between feedback categories

### 4.2 Instructor Interface

#### 4.2.1 Course Management

**Purpose**: Create and manage courses and their associated data.

**Functionality**:

-   Create new courses with code, title, term, and department
-   Import existing class rosters
-   View course summaries and statistics
-   Access course-specific views (assignments, students, stats)

**Interactions**:

-   "Add Course" button opening creation modal
-   "Import Class" functionality for bulk setup
-   Course selection from sidebar list

#### 4.2.2 Assignment Creation Workflow

**Purpose**: 5-step process to create and configure assignments.

**Step 1: Assignment Details**

-   Title, description, due date, maximum drafts allowed

**Step 2: Assignment Specifications**

-   Upload instructions document (PDF, DOCX, TXT)
-   Alternative text editor for creating specifications directly

**Step 3: Rubric Creation**

-   Template selection for common assignment types
-   Custom category creation with weightings
-   Detailed criteria descriptions

**Step 4: Feedback Settings**

-   AI model selection (ChatGPT, Claude, Llama 3, etc.)
-   Feedback style configuration (Balanced, Encouraging, Detailed)
-   Review threshold settings

**Step 5: Review & Publish**

-   Summary of all settings
-   Publication controls

**Interactions**:

-   Step-by-step navigation with progress indicators
-   Save as draft functionality
-   Preview capabilities

```text
┌─────────────────────┐
│ Instructor Initiates│
│ Assignment Creation │
└─────────┬───────────┘
        ▼
┌─────────────────────────────────┐
│ Step 1: Basic Assignment Details│
│ - Title, Description           │
│ - Due Date, Max Drafts         │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Step 2: Upload Specifications   │
│ - PDF/DOCX Upload               │
│ - Or Create in Text Editor      │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Decision Point                  │
│ Create Rubric or Auto-Generate? │
└──────┬──────────────────┬───────┘
      │                  │
      ▼                  ▼
┌─────────────┐    ┌─────────────────┐
│ Manual      │    │ AI-Generated    │
│ Rubric      │    │ Rubric          │
│ Creation    │    │ Creation        │
└──────┬──────┘    └────────┬────────┘
      │                  │
      └─────────┬──────────┘
              ▼
┌─────────────────────────────────┐
│ Step 3: Configure Rubric        │
│ - Add/Edit Categories           │
│ - Set Weightings                │
│ - Define Criteria               │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Step 4: Configure AI Settings   │
│ - Select Models                 │
│ - Set Runs Per Model            │
│ - Choose Aggregation Method     │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Step 5: Review & Finalize       │
│ - Preview All Settings          │
│ - Set Visibility to Students    │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Assignment Published            │
│ & Available to Students         │
└─────────────────────────────────┘
```

#### 4.2.3 Student Roster Management

**Purpose**: Manage student enrollment and monitor engagement.

**Functionality**:

-   View all enrolled students
-   Add individual students
-   Import student lists via CSV/TSV
-   Track student activity status
-   Access individual student details

**Interactions**:

-   "Add Student" button opening creation form
-   "Import Students" button for bulk additions
-   Search and filter controls
-   Pagination for large classes

#### 4.2.4 Feedback Statistics (Course Level)

**Purpose**: Analytics specific to a single course.

**Functionality**:

-   Overall engagement metrics
-   Assignment-specific improvement data
-   Performance breakdown by rubric category
-   Heatmap visualizations for score improvements
-   Export functionality for reports

**Interactions**:

-   Assignment selection dropdown
-   Export controls
-   Interactive visualizations

#### 4.2.5 Analytics Dashboard (Global)

**Purpose**: System-wide analytics across all courses.

**Functionality**:

-   Aggregate metrics (submissions, drafts, improvement)
-   Course comparison visualizations
-   AI model performance ratings
-   Time period filtering

**Interactions**:

-   Term/semester selection
-   Interactive charts for exploring data
-   Drill-down capabilities to course-specific views

```text
┌─────────────────────┐
│ Instructor Accesses │
│ Analytics Dashboard │
└─────────┬───────────┘
        ▼
┌─────────────────────────────────┐
│ Select View Level:              │
│ - Global (All Courses)          │
│ - Course Level                  │
│ - Assignment Level              │
│ - Student Level                 │
└──────┬──────────────────┬───────┘
      │                  │
      ▼                  ▼
┌─────────────┐    ┌─────────────────┐
│ View        │    │ Apply Filters:  │
│ Performance │    │ - Time Period   │
│ Metrics     │    │ - Categories    │
└──────┬──────┘    │ - Models        │
      │            └────────┬────────┘
      └─────────┬──────────┘
              ▼
┌─────────────────────────────────┐
│ Interactive Visualizations:     │
│ - Score Distributions           │
│ - Model Comparison              │
│ - Draft Improvements            │
│ - Category Performance          │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Decision Point                  │
│ Export or Configure?            │
└──────┬──────────────────┬───────┘
      │                  │
      ▼ Export             ▼ Configure
┌─────────────┐    ┌─────────────────┐
│ Generate:   │    │ Adjust:         │
│ - Reports   │    │ - Model Usage   │
│ - CSV Data  │    │ - Aggregation   │
│ - Charts    │    │ - Thresholds    │
└─────────────┘    └─────────────────┘
```

### 4.3 Additional Future Features

**1. Adaptive AI Feedback Based on Student Progress**

-   **Description**: The system will track previous feedback and student progress across drafts, even without storing full submission content.
-   **Implementation Approach**:
    -   Store structured feedback points categorized by rubric criteria
    -   Tag feedback with metadata about severity, issue type, and recommendations
    -   Include previous feedback context in AI prompts for new submissions
    -   Compare new submissions against stored feedback points (not against previous submissions)
    -   Generate differential analysis focusing on improvements and persistent issues
-   **Functionality**:
    -   Prevent repetitive feedback across submissions
    -   Reference previous feedback when issues persist ("As mentioned in your previous draft...")
    -   Explicitly acknowledge improvements in previously identified problem areas
    -   Adjust feedback depth and complexity based on draft number
    -   Track resolution of issues across multiple submissions
-   **Technical Considerations**:
    -   No need to store complete submissions, only structured feedback data
    -   Utilizes prompt engineering to guide AI awareness of previous feedback
    -   Can be implemented within the MVP's SQLite + SQLAlchemy storage model
    -   Minimal additional storage requirements (only feedback metadata)
-   **Benefits**:
    -   Creates a more personalized learning experience
    -   Reinforces improvements while still addressing remaining issues
    -   Simulates the progressive support of an attentive human instructor
    -   Maintains privacy by not retaining full submission content

**2. Instructor-Defined Feedback Templates**

-   **Description**: Allow instructors to create custom feedback templates that guide how AI generates responses.
-   **Functionality**:
    -   Template creation interface with variable placeholders
    -   Department or institution-level template sharing
    -   Ability to define standard phrasing for common issues
    -   Control over feedback tone and structure
    -   Option to include course-specific terminology or concepts
-   **Benefits**:
    -   Ensures consistency with departmental or institutional feedback styles
    -   Allows instructors to maintain their pedagogical voice
    -   Reduces the need for instructor intervention/editing of AI feedback
    -   Supports diverse teaching philosophies and approaches
    -   Enables integration of discipline-specific terminology and conventions

**3. Instructor-Defined fine-tune feedback settings**

- **Descrioption**: Instructors may have different preferences for feedback tone, detail level, or strictness. - - **Functionaliuty**
  - Allowing instructors to choose between:
    - **Encouraging vs. Critical Tone**
    - **High-level vs. Detailed Feedback**
    - **Actionable Steps vs. Conceptual Guidance**
    - **Minimal AI intervention (light suggestions) vs. Deep AI evaluation**
  - **Customizable feedback templates based on these settings**
  - **Course-level or assignment-level settings**
  - **Feedback setting presets for common scenarios (e.g., first draft, final draft)**
- **Benefits:**
  -  Aligns AI feedback with instructor preferences
  -  Supports diverse teaching styles
  -  Reduces the need for manual feedback editing
  -  Ensures consistent feedback across courses
  -  Promotes student engagement with feedback
  

**4. Instructor Intervention & Live Feedback**

- **Description** Sometimes, AI feedback may not fully capture nuanced grading needs, and instructors might want to manually adjust feedback before students see it.
- **Fuctionality:** 
  - A **live feedback review system** where instructors can quickly approve, edit, or replace AI-generated feedback before it is sent to students.
  - Instructor intervention flags that trigger manual review for specific submissions or students.
  - Feedback override options for instructors to provide their own feedback instead of AI-generated suggestions.
  - Instructor comments that can be added to AI feedback for additional context.
- **Benefits:**
  - Ensures feedback accuracy and alignment with course objectives
  - Allows instructors to maintain control over feedback quality
  - Supports personalized feedback for individual students
  - Facilitates rapid intervention for exceptional cases
  - Enhances instructor-student communication and engagement

**5. Gamification & Engagement Features**

- **Description** Encouraging students to engage with AI feedback and resubmit improved drafts could be enhanced with **progress tracking and gamification**.
- **Functionality:** 
  - Progress Badges (e.g., “Most Improved,” “Master of Revision”)
  - Feedback Streaks (encouraging students to engage with AI feedback over multiple assignments)
  - Peer Collaboration Challenges (students help each other refine drafts)
  - Leaderboards (based on improvement metrics or feedback engagement)
- **Benefits:**
  - Increases student motivation to engage with feedback
  - Promotes iterative learning and revision
  - Fosters a sense of community and collaboration
  - Provides additional insights into student engagement patterns

**4. Customizable Assessment Display Options**

-   **Description**: Give instructors control over how assessment information is presented to students.
-   **Functionality**:
    -   Toggle numerical scores on/off for assignments
    -   Replace numerical scores with alternative visualizations:
        -   Directional indicators (up/down arrows with color coding)
        -   Icon-based assessment (e.g., "bullseye" for excellent work, "first aid" for needs improvement, "path" for on-track)
        -   Text-only descriptions without quantitative elements
    -   Configure display options at course or assignment level
    -   Ability to gradually introduce numerical scores in later drafts
-   **Technical Implementation**:
    -   Simple configuration options in the assignment settings
    -   Visual design library of alternative assessment indicators
    -   Integration with the feedback display component
-   **Benefits**:
    -   Helps students focus on qualitative feedback rather than fixating on numerical scores
    -   Supports different pedagogical approaches to assessment
    -   Reduces anxiety around numerical evaluation during draft phases
    -   Encourages revision based on content feedback rather than grade improvement
    -   Allows instructors to align assessment display with their teaching philosophy

**5. AI-Generated Rubric Creation**

-   **Description**: Automatically generate assignment rubrics from uploaded specifications to reduce instructor workload.
-   **Functionality**:
    -   Option to auto-generate rubric during assignment creation
    -   AI analysis of uploaded assignment specifications to identify key assessment criteria
    -   Suggested rubric categories with appropriate weightings
    -   Editable generated rubrics (instructors can modify before finalizing)
    -   Transparency indicator for students when AI-generated rubrics are used
-   **Technical Implementation**:
    -   Integration with the assignment creation workflow
    -   Specialized prompt engineering for rubric extraction
    -   Rubric template library for different assignment types
    -   Simple editor for instructors to refine generated rubrics
-   **Benefits**:
    -   Lowers barrier to entry for instructors new to rubric-based assessment
    -   Reduces time required to create comprehensive assignments
    -   Ensures all assignments have structured assessment criteria
    -   Promotes consistency across courses and departments
    -   Allows rapid deployment while maintaining instructor oversight


**6. Plagiarism & AI-Generated Content Detection**

- **Description** As AI-generated assignments become more common, distinguishing between student work and AI-written content is important.
- **Functionality:** 
  - Integration with **plagiarism detection tools** (Turnitin, Copyleaks)
  - Integration with **AI-generated text detection** to help instructors verify authenticity.
  - **Transparency indicators** for students when AI-generated content is detected.
  - **Instructor override options** for cases where AI-generated content is acceptable.
  - **Detailed audit logs** for content analysis and detection results.
- **Technical Implementation:** 
  - API integration with plagiarism detection services 
  - Custom AI models for content analysis, metadata tagging for AI-generated content.
  - Secure storage and audit trail for detection results.
- **Benefits:**
  - Supports academic integrity
  - Prevents misuse of AI-generated content
  - Protects students from unintentional plagiarism
  - Maintains trust in the educational process

### **8. Code and Multimedia Support**

- **Description** While FeedForward focuses on essay-style feedback, expanding to support **coding assignments, presentations, and multimedia submissions** would increase its versatility.
- **Functionality:** 
  - Code feedback using AI models trained in programming languages
  - Presentation feedback with AI-generated suggestions for clarity, structure, and delivery
  - Video/audio feedback for speech-based assignments
- **Technical Implementation:** 
  - Integration with code analysis tools (e.g., Codecademy, GitHub)
  - Speech-to-text and sentiment analysis for multimedia feedback
  - Secure storage and processing of multimedia content
- **Benefits:**
  - Expands the range of assignments supported by FeedForward
  - Provides comprehensive feedback across different assignment types
  - Enhances student learning in diverse formats
  - Supports instructors in assessing a variety of skills



### 4.4 Multi-Model Assessment and Feedback System

#### 4.4.1 Overview

FeedForward enhances assessment reliability through a multi-model approach that leverages multiple Large Language Models (LLMs) with multiple runs per submission. This system improves consistency, reduces bias, and provides more comprehensive feedback while giving instructors full control over the assessment process.

#### 4.4.2 Core Components

**1. Multiple LLM Assessment Engine**

-   **Description**: Processes student submissions through multiple AI models with multiple runs per model.
-   **Functionality**:
    -   Configure which LLMs to include in assessment (e.g., GPT-4, Claude, Llama)
    -   Set number of runs per LLM (1-5 recommended)
    -   View performance metrics for each LLM across submissions
    -   Enable/disable specific models based on performance analysis

**2. Mark Aggregation System**

-   **Description**: Combines scores from multiple LLMs and runs using configurable methods.
-   **Functionality**:
    -   Select aggregation method from multiple options (mean, median, trimmed mean, etc.)
    -   Set weights for different models based on reliability
    -   Apply confidence thresholds to exclude uncertain assessments
    -   View statistical distribution of marks across models and runs

**3. Feedback Consolidation**

-   **Description**: Synthesizes feedback from multiple sources into coherent, actionable guidance.
-   **Functionality**:
    -   Select a primary model for organizing combined feedback
    -   Filter feedback based on included models from mark aggregation
    -   Configure feedback detail level (overall, rubric categories, or both)
    -   Highlight areas of consensus and divergence between models

**4. Instructor Review Interface**

-   **Description**: Dashboard for reviewing and fine-tuning multi-model assessments.
-   **Functionality**:
    -   Side-by-side comparison of individual model assessments
    -   Visual representation of mark distribution (boxplots, histograms)
    -   Override options for adjusting automated assessments
    -   Individual feedback review with accept/edit/reject options
    -   Analysis of model performance trends across assignments

#### 4.4.3 Technical Implementation

-   Storage system for multiple assessment runs
-   Parallel processing to minimize latency when running multiple models
-   Caching system for model evaluations to improve performance
-   Statistical analysis module for aggregation and reliability metrics

#### 4.4.4 Integration with Core FeedForward Features

-   Compatible with iterative draft submissions
-   Configurable application to specific drafts (e.g., final drafts only)
-   Works alongside adaptive feedback system to track improvement
-   Support for both AI-generated and instructor-created rubrics

### 4.5 Multi-Model Assessment: Student Experience

#### 4.5.1 MVP Approach: Simplified Student Interface

The student experience in the FeedForward system's MVP will prioritize simplicity and clarity while leveraging the benefits of multi-model assessment behind the scenes:

**1. Unified Feedback Presentation**

-   Students receive a single, consolidated view of feedback without visibility into which specific models contributed
-   Feedback is presented as a unified voice rather than as separate model opinions
-   Clear separation between strengths and areas for improvement
-   Simple indicator noting that multiple AI models were used in assessment (e.g., "Assessed by 3 AI models")

**2. Confidence Communication**

-   Consensus levels are indicated through simple badges (e.g., "Strong Consensus," "Consensus")
-   Higher consensus feedback points are prioritized in the presentation
-   Confidence is communicated through language choices rather than technical metrics
-   No exposure to raw confidence scores or inter-model variance

**3. Disclaimer Implementation**

-   Clear disclaimer indicating the purpose and limitations of AI feedback:
    > "This AI-generated feedback is provided to help you identify patterns and improve your drafts. It is not a final assessment and may differ from instructor evaluation. The feedback represents probable areas for improvement but should be considered as a learning tool rather than definitive grading."
-   Disclaimer appears in a non-intrusive but visible location on feedback pages

**4. Focus on Improvement Metrics**

-   Clear visualization of progress between drafts
-   Percentage improvements by category
-   Progress bars showing movement toward learning goals
-   De-emphasis on absolute scores in favor of improvement indicators

#### 4.5.2 Future Enhancements (Post-MVP)

As the system matures beyond the MVP stage, a balanced approach to additional transparency may be implemented:

**1. Opt-in Detailed Views**

-   Advanced toggle option for students who wish to see more details about model assessment
-   Ability to view individual model feedback in a separate view (not the default)
-   Option to compare assessment approaches without overwhelming the main interface

**2. Enhanced Confidence Visualization**

-   More nuanced representation of agreement/disagreement between models
-   Visual indicators of assessment reliability on specific feedback points
-   Optional view of distribution charts for students interested in assessment patterns

**3. Selective Model Visibility**

-   Potential for students to see which models contributed to specific feedback *only* when significant disagreement exists
-   Maintaining unified presentation for high-consensus feedback points
-   Clear explanation of why model diversity matters in assessment

**4. Personalization Options**

-   Future implementation may allow students to optionally indicate which model's feedback they find most helpful
-   Instructors could still control which models are used in assessment
-   System could adapt to emphasize feedback from preferred models without eliminating others

#### 4.5.3 Technical Implementation Considerations

-   Student interfaces must render quickly despite the complexity of multi-model processing
-   Feedback data structure must support both simplified and detailed representations
-   Clear separation between assessment processing (multiple models, multiple runs) and presentation layer
-   Caching of processed feedback to ensure responsive user experience

## 5. Technical Considerations

### 5.1 Error Handling & Resilience

**Overview:**

Robust error handling is critical to ensuring system stability, especially when integrating with external AI models. The system must gracefully handle scenarios such as timeouts, rate limits, and inconsistent feedback, thereby preserving a smooth user experience even when external services face issues.

**Key Strategies:**

1.  **AI Model Integration Resilience**
    -   **Retry Logic:** Implement retries with exponential backoff to address intermittent API timeouts or temporary rate limit errors.
    -   **Circuit Breaker Pattern:** Utilize circuit breakers to temporarily halt requests to an unresponsive AI model, preventing cascading failures across the system.
    -   **Dynamic Model Selection:** Monitor the performance of integrated models and dynamically adjust the selection, excluding those with persistent issues from the current assessment cycle.

2.  **Fallback Mechanisms**
    -   **Default Responses:** Provide a default fallback response or notification when AI-generated feedback cannot be retrieved, ensuring that users understand the system is experiencing temporary issues.
    -   **Manual Overrides:** Enable instructors to manually trigger a re-assessment or override the AI-generated feedback if critical errors occur.
    -   **Caching Strategies:** Maintain a cache of recent AI responses to serve as temporary feedback during service disruptions, thereby minimizing delays in delivering feedback to students.

3.  **User Communication**
    -   **Clear Error Messages:** Display user-friendly error messages that clearly explain the issue (e.g., “The system is experiencing delays due to high traffic. Please try again shortly.”).
    -   **Guidance for Remediation:** Provide actionable steps or alternative options (like re-submitting a draft) for students and instructors when an error occurs.

4.  **Logging and Monitoring**
    -   **Detailed Logging:** Record error details, including API response times, error codes, and data anomalies, to facilitate troubleshooting and system improvements.
    -   **Real-Time Monitoring:** Set up monitoring dashboards and alerts to detect and respond to high error rates or performance degradation quickly.
    -   **Metrics Tracking:** Monitor key performance indicators such as error frequency, response times, and system uptime to evaluate the effectiveness of error handling measures over time.

5.  **Testing and Validation**
    -   **Simulated Failures:** Incorporate automated tests that simulate API failures, rate limiting, and timeouts to ensure error handling mechanisms work as intended.
    -   **Stress Testing:** Conduct load testing to identify and address potential failure points under high-usage scenarios, ensuring the system remains resilient during peak times.

6.  **Documentation and Support**
    -   **Clear Documentation:** Provide comprehensive documentation on error codes, retry policies, and fallback procedures for both developers and end users.
    -   **Support Pathways:** Establish clear escalation procedures and support channels for unresolved issues, ensuring timely resolution and minimal disruption to users.

By integrating these error handling and resilience strategies, the system will be better prepared to manage real-world challenges. This ensures that even in the event of external service disruptions, students and instructors experience minimal interruption, maintaining trust in the system’s reliability and consistency.

### 5.2 Security & Data Privacy

**Overview:**

Given the sensitivity of student submissions, iterative drafts, and AI-generated feedback, robust security and data privacy measures are critical. This section outlines the practices and protocols that will be implemented to protect sensitive data, ensure compliance with applicable regulations (e.g., GDPR, FERPA), and maintain user trust.

**Key Components:**

1.  **Data Encryption:**
    -   **At-Rest Encryption:** All sensitive data—including student submissions, feedback histories, and personal information—will be stored using strong encryption (e.g., AES-256) to protect against unauthorized access.
    -   **In-Transit Encryption:** Secure communication protocols (e.g., TLS/SSL) will be used for data transmission between the frontend, backend, and third-party APIs to safeguard data in transit.

2.  **Authentication & Access Control:**
    -   **Role-Based Access Control (RBAC):** Different access levels will be enforced for students, instructors, and administrators, ensuring that users only have access to the data and functionality appropriate to their role.
    -   **Multi-Factor Authentication (MFA):** Where feasible, MFA will be implemented to add an extra layer of security for user authentication, particularly for instructor and administrative accounts.
    -   **Session Management:** Secure session handling and regular session expiration policies will be in place to mitigate unauthorized access risks.

3.  **Audit Logging & Monitoring:**
    -   **Detailed Logging:** The system will maintain comprehensive audit logs that record user actions, changes to submissions, and system events. These logs will be securely stored and periodically reviewed to detect and investigate suspicious activities.
    -   **Real-Time Monitoring:** Automated monitoring tools will be used to track access patterns, detect anomalies, and trigger alerts in case of security incidents.

4.  **Data Privacy & Compliance:**
    -   **Regulatory Compliance:** The system will adhere to relevant data protection regulations, such as GDPR and FERPA. This includes implementing data minimization practices, providing users with transparency about data usage, and offering mechanisms for data access, correction, or deletion.
    -   **Data Retention Policies:** Clear policies will be defined for the retention and archival of student submissions and feedback data. Data will be stored only as long as necessary for educational and compliance purposes, and securely deleted or anonymized when no longer required.
    -   **User Consent & Transparency:** Users will be informed about how their data is collected, stored, and used. Consent mechanisms will be implemented where required, ensuring that users understand and agree to the data practices.

5.  **Secure API Integration:**
    -   **Encrypted API Communication:** When integrating with external AI providers, secure API communication channels (e.g., HTTPS with proper authentication tokens) will be enforced to protect data exchanged with third-party services.
    -   **API Key Management:** API keys and secrets will be securely stored and rotated regularly, minimizing the risk of exposure.

6.  **Regular Security Testing & Incident Response:**
    -   **Vulnerability Scanning & Penetration Testing:** Routine security assessments, including vulnerability scans and penetration testing, will be conducted to identify and remediate potential security issues before they impact users.
    -   **Incident Response Plan:** A detailed incident response plan will be in place, outlining the steps for detection, containment, and resolution of any security breaches, along with communication protocols for affected users.

7.  **Data Backup & Disaster Recovery:**
    -   **Regular Backups:** Automated, encrypted backups of critical data will be performed at regular intervals.
    -   **Disaster Recovery:** A disaster recovery plan will ensure that the system can be quickly restored in the event of data loss or other catastrophic events.

By implementing these security and data privacy measures, the system will protect sensitive student and instructor data, maintain compliance with regulatory requirements, and provide a secure foundation for iterative learning and AI-based feedback. These practices not only mitigate risks but also build user trust and confidence in the system's reliability and integrity.

### 5.3 Performance & Scalability

**Overview:**

As the system transitions from a university research server to full production, it is essential to ensure that it remains responsive and reliable even under increasing load. This section outlines strategies to benchmark performance, manage caching, and scale the system effectively.

**Key Considerations:**

1.  **Performance Benchmarking and Testing**
    -   **Load & Stress Testing:** Regularly simulate high-usage scenarios to identify potential bottlenecks in the submission, feedback generation, and API integration processes.
    -   **Response Time Monitoring:** Track key metrics such as AI feedback generation times, draft processing, and API call latency to ensure the system meets performance standards.
    -   **Resource Utilization:** Monitor CPU, memory, and network usage to determine if the current infrastructure supports peak loads.

2.  **Caching Strategies**
    -   **AI Feedback Caching:** Implement caching for recent AI responses to reduce redundant API calls, ensuring faster feedback delivery during high-demand periods or temporary service disruptions.
    -   **Data Caching:** Utilize caching mechanisms for frequently accessed data (e.g., assignment details, rubric criteria) to decrease database load and improve overall responsiveness.

3.  **Scalability Planning**
    -   **Horizontal Scaling:** Design the architecture to allow for horizontal scaling—adding more server instances and employing load balancing—to handle increased user activity.
    -   **Database Migration & Scaling:** Develop a migration plan from SQLite to a more robust database (e.g., PostgreSQL) as data volumes grow, including strategies for read replicas, partitioning, and indexing to maintain performance.
    -   **Parallel Processing:** Leverage parallel processing techniques to handle multiple AI model runs concurrently, reducing overall latency in feedback generation.

4.  **Monitoring and Alerting**
    -   **Real-Time Dashboards:** Set up monitoring dashboards that provide insights into system performance, API response times, error rates, and resource usage.
    -   **Automated Alerts:** Implement alerts that trigger when performance metrics exceed predefined thresholds, enabling proactive adjustments or scaling measures.

5.  **Deployment Considerations**
    -   **Staged Rollouts:** Use phased deployment strategies to incrementally roll out performance enhancements, ensuring stability and enabling rollback if issues arise.
    -   **Cloud Integration:** Consider leveraging cloud-based services for dynamic resource allocation, making it easier to scale on-demand as the system transitions to production.

6.  **Optimization Strategies**
    -   **Code and Query Optimization:** Regularly review and refine code, database queries, and API calls to minimize latency and enhance overall performance.
    -   **Asynchronous Processing:** Utilize asynchronous processing for non-blocking operations—such as background AI assessments and batch updates—to maintain a smooth user experience during heavy loads.

By establishing rigorous performance benchmarks, implementing effective caching strategies, and designing a scalable architecture, the system will be well-equipped to handle increased user demand and data volume. Continuous monitoring and proactive optimization will ensure that the platform remains responsive, reliable, and capable of delivering high-quality, AI-driven feedback as it evolves from a university research project to a full-scale production system.

## 6. Future Enhancements and Roadmap

### 6.1 Integration with Existing Systems

**Overview:**

While immediate integration with Learning Management Systems (LMS) and other educational tools is deferred for the MVP, planning for future interoperability is essential. This section outlines potential strategies to ensure the system can seamlessly integrate with widely used educational platforms and align with industry standards.

**Key Strategies:**

1.  **Standards-Based Integration:**
    -   **LTI (Learning Tools Interoperability):**
        Plan to support the LTI standard, which will allow seamless integration with major LMS platforms (e.g., Canvas, Blackboard, Moodle). This enables single sign-on (SSO) and smooth data exchange between systems.
    -   **RESTful APIs:**
        Develop a robust API framework that facilitates data sharing with external systems. This will allow third-party tools to access assignment data, feedback reports, and analytics, ensuring interoperability with various educational platforms.

2.  **Single Sign-On (SSO) and Identity Management:**
    -   **Federated Authentication:**
        Integrate with common SSO providers and educational identity services (e.g., SAML, OAuth) to allow students and instructors to use their institutional credentials. This streamlines the user experience and improves security.
    -   **Role Synchronization:**
        Ensure that user roles and permissions are synchronized between the FeedForward system and integrated LMS platforms, preserving consistency in access controls.

3.  **Data Exchange and Analytics Integration:**
    -   **Seamless Data Import/Export:**
        Build capabilities to import student rosters, assignment data, and grades from existing LMS platforms. Likewise, export feedback and performance analytics in formats that can be ingested by other systems.
    -   **Standardized Reporting:**
        Develop data reporting tools that align with common educational standards, ensuring that performance and analytics data can be easily incorporated into institutional dashboards.

4.  **Modular and Scalable Architecture:**
    -   **Plug-and-Play Modules:**
        Design the system with modular components that can be independently updated or replaced to support integrations with various third-party platforms. This ensures flexibility as industry standards evolve.
    -   **Future-Proofing:**
        Keep the integration framework extensible to accommodate emerging educational technologies and tools, ensuring long-term viability and ease of expansion.

5.  **Collaboration and Pilot Programs:**
    -   **Institutional Partnerships:**
        Engage with educational institutions during pilot phases to gather feedback on integration needs and test interoperability with their existing systems.
    -   **Feedback-Driven Enhancements:**
        Use pilot program insights to refine integration strategies, ensuring that future developments meet the practical requirements of academic environments.

By planning for standards-based integration and a modular architecture, the system is poised to expand its capabilities beyond the MVP. Future integration with LMS platforms and other educational tools will not only enhance the user experience but also position the system within a broader ecosystem of digital education solutions, ensuring alignment with industry standards and long-term sustainability.

### 6.2 Risk Assessment

**Overview:**

Early identification and proactive management of potential risks are critical to ensuring the long-term success and sustainability of the system. This risk assessment outlines key challenges—ranging from technical complexity and API cost management to scalability, data security, and user adoption—along with targeted mitigation strategies to address each area.

---

#### 6.2.1 Technical Complexity of Multi-Model Integration

-   **Risk Description:**
    Integrating multiple AI models (LLMs) introduces complexity in handling diverse response formats, varying processing times, and potential inconsistencies in feedback.

-   **Mitigation Strategies:**
    -   **Incremental Integration:** Begin with a single, robust AI model for the MVP, and gradually introduce additional models as the system stabilizes.
    -   **Modular Architecture:** Design a modular integration framework that isolates each model’s functionality, simplifying updates or model swaps without impacting the overall system.
    -   **Comprehensive Testing:** Implement rigorous unit, integration, and stress tests—including integration testing with external providers—to ensure each component functions reliably under varying conditions.
    -   **Fallback Logic:** Develop mechanisms to handle outlier or unexpected outputs, ensuring consistency even when individual model responses deviate.

---

#### 6.2.2 API Cost Management

-   **Risk Description:**
    Relying on external AI provider APIs (e.g., OpenAI, Anthropic) can result in substantial operational costs, particularly during high usage or peak demand periods.

-   **Mitigation Strategies:**
    -   **Usage Monitoring:** Track API call volumes and implement rate limiting to control costs.
    -   **Cost Forecasting & Budgeting:** Develop forecasting tools to predict API usage and costs, enabling proactive budget management.
    -   **Negotiation and Alternative Options:** Evaluate and negotiate cost-efficient plans with providers, and maintain a shortlist of alternative providers to switch to if pricing becomes unsustainable.
    -   **Caching Mechanisms:** Implement caching strategies to reuse recent AI responses when applicable, reducing redundant API calls and managing expenses.

---

#### 6.2.3 Scalability Issues

-   **Risk Description:**
    As the system evolves from a university research project to a production environment, performance bottlenecks, increased load, and database limitations may impact the user experience.

-   **Mitigation Strategies:**
    -   **Scalable Architecture:** Design the system to support horizontal scaling with load balancing, and explore cloud-based resource management for dynamic scaling.
    -   **Auto-Scaling Solutions:** Leverage auto-scaling features to dynamically adjust resources based on user load and demand.
    -   **Performance Benchmarking and Latency Monitoring:** Regularly monitor key performance metrics (e.g., response times, resource utilization, and latency) to identify bottlenecks early.
    -   **Database Migration Plan:** Prepare for a smooth transition from SQLite to a more robust solution (e.g., PostgreSQL) as data volumes and user numbers increase.

---

#### 6.2.4 Data Privacy and Security Risks

-   **Risk Description:**
    Handling sensitive student submissions and iterative feedback data raises concerns about data breaches and non-compliance with regulations such as GDPR and FERPA.

-   **Mitigation Strategies:**
    -   **Data Encryption:** Implement strong encryption protocols (e.g., AES-256) for both data at rest and in transit using secure communication channels (e.g., TLS/SSL).
    -   **Access Controls & Secure Authentication:** Enforce role-based access control (RBAC) and consider multi-factor authentication for sensitive operations.
    -   **Regular Audits and Security Frameworks:** Conduct periodic security audits, vulnerability assessments, and adopt industry-standard security frameworks to maintain robust protection.
    -   **Compliance and Data Retention Policies:** Ensure that all data handling practices align with regulatory requirements by establishing clear data retention, user consent, and privacy policies.
    -   **Incident Response Training:** Provide ongoing security training for the development and operations teams to ensure preparedness for potential security incidents.

---

#### 6.2.5 User Adoption and Usability

-  **Risk Description:**
    If the system’s interface is not intuitive or fails to meet the needs of students and instructors, user adoption may be lower than expected, impacting overall effectiveness.

-   **Mitigation Strategies:**
    -   **User-Centric Design and Onboarding:** Focus on intuitive design principles, and develop comprehensive onboarding materials, tutorials, and training sessions for both students and instructors.
    -   **Iterative Feedback Collection:** Set up continuous mechanisms to gather and analyze user feedback during beta and post-launch phases, enabling rapid usability improvements.
    -   **Accessibility Focus:** Ensure the platform complies with modern accessibility standards (e.g., WCAG 2.1) to serve all users effectively, including those with diverse accessibility needs.
    -   **Comprehensive Documentation and Support:** Provide clear documentation and establish robust support channels to assist users in navigating and adopting the system.

---

By proactively addressing these risks with targeted mitigation strategies, the project team can enhance system robustness and scalability while ensuring user trust and regulatory compliance. Regularly reviewing and updating this risk assessment as the project evolves will be critical for maintaining stakeholder confidence and guiding the system's long-term roadmap.

## 7. Technical Architecture

### 7.1 System Components

#### 7.1.1 Frontend

-   **Web Application**: Responsive interface for both student and instructor users
-   **Component Library**: Reusable UI elements maintaining design consistency
-   **State Management**: Centralized data store for application state
-   **Visualization Layer**: Charts, graphs, and interactive elements for analytics

#### 7.1.2 Backend

-   **API Layer**: RESTful endpoints for frontend-backend communication
-   **Authentication Service**: User identity and access management
-   **Assignment Service**: Managing assignment lifecycle
-   **Feedback Service**: Coordinating AI model interactions
-   **Analytics Service**: Data processing for insights and visualizations
-   **Export Service**: Generation of reports and downloadable content

#### 7.1.3 AI Engine Layer

-   **Model Coordinator**: Orchestrates requests to multiple AI models
-   **Prompt Engineering Module**: Transforms rubrics and specifications into effective prompts
-   **Feedback Aggregator**: Combines and normalizes responses from different models
-   **Feedback Formatter**: Structures AI outputs into consistent, actionable feedback

#### 7.1.4 Data Storage

-   **User Database**: Student and instructor profiles
-   **Course Database**: Course configurations and relationships
-   **Assignment Database**: Assignment definitions, rubrics, and specifications
-   **Submission Database**: Student drafts and version history
-   **Feedback Database**: AI-generated feedback and improvement metrics
-   **Rubric**: Categories, criteria, and descriptions.
-   **Analytics Database**: Aggregated data.

### 7.2 Multi-Model Assessment Workflow
#### 7.2.1 Approach to Calculating Marks and Aggregating Feedback

To improve the consistency and fairness of AI-based grading, a **multi-model approach** using multiple LLMs and multiple runs per submission is used to aggregate both marks and feedback. Each selected LLM evaluates a student's submission based on the rubric and assigns a score for each category. Running multiple evaluations across different LLMs helps mitigate biases and variability from any single model. The instructor has full control over what the student sees but will always have access to the aggregated mark and detailed breakdowns from individual LLMs.

Using **multiple LLMs across multiple runs** ensures that no single model or individual evaluation dominates the grading process, reducing inconsistencies caused by model variations or prompt sensitivity. However, some models may perform better than others in certain contexts. Therefore, instructors have the ability to **review individual model performance** and choose which LLMs to include or exclude from the grading process.

---

#### 7.2.2 Aggregation of Marks

Since different LLMs may assign slightly different marks across multiple runs, **aggregation is necessary** to generate a final score. The instructor can choose from several aggregation methods, including:

-   **Arithmetic Mean (Default)** – A simple average of all marks across multiple LLMs and runs.
-   **Median** – The middle score, reducing sensitivity to outliers.
-   **Mode** – The most frequently assigned score, useful when scores cluster around a value.
-   **Mid-Range** – The average of the highest and lowest marks, balancing extreme values.
-   **Trimmed Mean** – A refined average that removes the highest and lowest scores to reduce the impact of outliers.
-   **Weighted Mean** – Assigns different weights to marks based on model reliability, variance, or confidence scores, allowing more consistent LLMs to have greater influence.
-   **Adaptive Weighting** – Dynamically adjusts weights based on score variance, giving lower influence to models or runs with inconsistent scoring.

By using **multiple LLMs and multiple runs**, the system **minimizes random fluctuations in scoring** and **provides a fairer representation of student performance**. Additionally, by allowing instructors to choose the aggregation method, they can balance **stability and differentiation** in grading.

---

#### 7.2.3 Aggregation of Feedback

To ensure feedback is as useful as possible, only responses from **included LLMs** (based on the chosen aggregation method) are considered. For example, if the instructor selects a **trimmed mean**, the highest and lowest scoring LLMs will be excluded from both the final mark and the feedback aggregation.

Since multiple runs generate multiple feedback responses, a **preferred LLM** can be used to summarize feedback from all included runs and models, ensuring a **cohesive and structured** response for students. Additionally, instructors can access:

-   **Individual LLM Feedback** – The raw, unprocessed feedback from each selected model and run.
-   **Summarized Feedback** – A synthesized version combining insights from multiple LLMs and multiple runs.

The instructor also controls **how much feedback the student receives**, with the following options:

1.  **Overall Feedback Only** – A general summary of the submission.
2.  **Rubric Category Feedback Only** – Breakdown per rubric section.
3.  **Both Overall and Rubric Category Feedback (Default)** – Provides comprehensive feedback at both levels.

By allowing flexibility in feedback display, instructors can decide how much detail students should receive, ensuring clarity without overwhelming them.

A **multi-model, multi-run approach** enhances fairness and reduces variability in AI-based grading by aggregating marks from different LLMs across multiple runs. The instructor has control over which models are included, how marks are aggregated, and how feedback is presented to students. By offering different aggregation methods—such as mean, median, mode, and weighted approaches—this system balances **consistency with differentiation**. Additionally, structured feedback aggregation ensures that students receive meaningful insights while allowing instructors to fine-tune the grading process for accuracy and reliability.

```text
┌─────────────────────┐
│ Student Submits     │
│ Assignment Draft    │
└─────────┬───────────┘
        ▼
┌─────────────────────┐
│ System Retrieves    │
│ Instructor Config   │◄────┐
└─────────┬───────────┘      │
        ▼                 │
┌─────────────────────┐      │     ┌────────────────────┐
│ Assignment Processed│      │     │ Instructor         │
│ by Multiple AI Models├─────────┤ Configuration      │
└─────────┬───────────┘      │     │ - Selected Models  │
        │                 │     │ - Number of Runs   │
┌─────────▼───────────┐      │     │ - Aggregation Method│
│ For each selected   │      │     └────────────────────┘
│ model, perform N runs├────┘
└─────────┬───────────┘
        ▼
┌─────────────────────────────────────┐
│ For each run of each model:         │
│ 1. Generate rubric-based assessment │
│ 2. Assign scores to categories     │
│ 3. Generate feedback text           │
│ 4. Store assessment data           │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ Aggregation Process:                │
│ 1. Collect all assessment scores    │
│ 2. Apply selected aggregation method│
│ 3. Calculate confidence metrics     │
│ 4. Identify consensus feedback      │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ Feedback Compilation:               │
│ 1. Combine feedback by category     │
│ 2. Prioritize high-consensus items  │
│ 3. Format feedback for presentation │
│ 4. Calculate improvement metrics     │
└─────────────────┬───────────────────┘
                  ▼
        ┌───────────────┐
        │ Assessment    │
        │ Database      │
        └───────┬───────┘
              ▼
┌─────────────────────────────────────┐
│ Instructor Review (Optional):       │
│ 1. View aggregated assessment       │
│ 2. Examine model distribution       │
│ 3. Adjust/approve feedback          │
│ 4. Release to student               │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ Student Receives:                   │
│ 1. Unified feedback presentation   │
│ 2. Improvement metrics vs prior     │
│    drafts (if applicable)            │
│ 3. Confidence indicators             │
└─────────────────────────────────────┘
```

#### 7.2.4 Instructor Review and Feedback Workflow: Introduction and Explanation

This workflow outlines how instructors can oversee and refine AI-generated feedback before it reaches students, ensuring both accuracy and fairness. The process begins once the AI has completed its assessment, and it offers instructors a choice between immediate feedback release and a review process.

**Workflow Overview:**

1.  **AI Assessment Completed & Notification**
    Once the AI has evaluated a submission using the multi-model assessment, the instructor receives a notification that the assessment is complete. This ensures that instructors are promptly informed of new feedback ready for review.

2.  **Review Configuration Options**
    The instructor then determines the release strategy:

    -   **Immediate Release:** The student receives the feedback directly without further intervention.
    -   **Review Before Release:** The instructor opts to review the detailed, aggregated feedback from the multiple AI models before it is shared with the student.

3.  **Instructor Review Process**
    If review is chosen, the instructor views the comprehensive multi-model assessment, which includes a breakdown of scores and feedback from different AI runs. Here, the instructor is presented with several review options:

    -   **Accept as-is:** Approve the AI-generated feedback without changes.
    -   **Adjust Scores:** Modify the numerical scores if they seem inconsistent or require calibration.
    -   **Edit Feedback Text:** Tweak the qualitative feedback to improve clarity or address any issues.
    -   **Reject and Reassess:** Discard the current assessment entirely, triggering a re-assessment if necessary.

4.  **Decision and Release**
    After selecting one of the review options, the instructor makes the final decision. If any adjustments are made, these changes are incorporated before the final feedback is released to the student. The system then automatically delivers the approved feedback, ensuring that students receive clear, accurate, and pedagogically sound insights into their work.

This workflow effectively balances the efficiency of automated assessments with the critical oversight of instructors. It empowers instructors to tailor the feedback process—either by validating and enhancing AI-generated insights or by letting high-quality automated results pass through—ensuring that the feedback provided supports meaningful learning and improvement.

```text
┌─────────────────────┐
│ AI Assessment       │
│ Completed           │
└─────────┬───────────┘
        ▼
┌─────────────────────────────────┐
│ Instructor Notification         │
└─────────────────┬───────────────┘
                  ▼
┌─────────────────────────────────┐
│ Instructor Review Configuration │
│ - Immediate Release to Student? │
│ - Review Before Release?        │
└──────┬──────────────────┬───────┘
      │                  │
      ▼ Immediate        ▼ Review
┌─────────────┐    ┌─────────────────┐
│ Student     │    │ Instructor Views│
│ Receives    │    │ Multi-Model     │
│ Feedback    │    │ Assessment      │
└─────────────┘    └────────┬────────┘
                      │
                      ▼
      ┌─────────────────────────┐
      │ Review Options:         │
      │ 1. Accept as-is       │
      │ 2. Adjust scores      │
      │ 3. Edit feedback text │
      │ 4. Reject and reassess│
      └───────────┬─────────────┘
                  │
                  ▼
      ┌─────────────────────────┐
      │ Instructor Decision     │
      └───────┬─────┬───────────┘
            │     │
            │     ▼
            │   ┌─────────────┐
            │   │ Make        │
            │   │ Adjustments │
            │   └──────┬──────┘
            │         │
            ▼         ▼
      ┌─────────────────────────┐
      │ Release Feedback        │
      │ to Student              │
      └─────────────────────────┘
```

### 7.3 Data Model

#### 7.3.1 Key Entities:

-   **User**: Authentication details, role (student/instructor), profile
-   **Course**: Course metadata, term, instructor, enrolled students
-   **Assignment**: Specifications, rubric, due date, feedback settings
-   **Draft**: Submission content, timestamp, version number, status
-   **Feedback**: AI-generated content linked to rubric criteria, model source, confidence
-   **Rubric**: Categories, criteria, weightings, descriptions
-  **Analytics**: Aggregated data for reporting

### 7.4 Security and Compliance

- **Data Privacy**: All student data and submissions will be securely stored.
- **Access Control**: Role-based permissions for students and instructors.
- **Audit Logging**: Track system usage and feedback generation events.
- **Data Retention**:  Policies for the storage and archival of submissions will be implemented.
- **Compliance**:  Adherence to educational data privacy regulations (e.g., FERPA, GDPR) will be prioritized.

## 8. UI/UX Specifications

### 8.1 Design System

-   **Color Palette**:
    -   Primary: #3498db (blue)
    -   Secondary: #2ecc71 (green)
    -   Accent: #e74c3c (red)
    -   Neutrals: #2c3e50 (dark blue), #7f8c8d (gray)
    -   Background: #f5f7fa (light gray)
-   **Typography**: Arial (for mockups, can be replaced with system font stack)
-   **Component Library**: Custom components with consistent styling
-   **Responsive Breakpoints**: Desktop, tablet, mobile views

### 8.2 Common UI Elements

-   **Navigation**: Global header with role-specific menu items
-   **Buttons**: Primary (blue), Secondary (white outlined), Success (green)
-   **Forms**: Consistent input styling with validation
-   **Cards**: Content containers with consistent padding and borders
-   **Tables**: Data presentation with sorting and filtering
-   **Charts**: Visualization components for analytics
-   **Modals**: Overlay dialogs for focused interactions

### 8.3 Student Interface UI

The student interface follows a clean, task-focused design with:

-   Dashboard showing active assignments
-   Detailed feedback view with progress visualization
-   Comparison tools for viewing improvement across drafts
-   Analytics section showing long-term progress

### 8.4 Instructor Interface UI

The instructor interface provides:

-   Course management sidebar
-   Tabbed navigation within courses
-   Step-by-step workflows for complex tasks
-   Data visualization for analytics
-   Import/export functionality
-   Student roster management

## 9. Technical Recommendations

### 9.1 Technology Stack for MVP and Proof of Concept

Based on the need for rapid development, maintainability, and a focus on the core AI feedback functionality, we recommend a simplified Python-centric technology stack for the MVP:

**Recommended MVP Stack**:

-   **Framework**: FastAPI + FastHTML
    -   Justification: Allows development entirely in Python, reducing complexity
    -   FastAPI provides modern, high-performance API endpoints
    -   FastHTML with HTMX enables interactive UI without complex JavaScript frameworks

-   **Frontend Tools**:
    -   HTMX for browser interactions and dynamic content
    -   Tailwind CSS for styling (keeps everything in HTML templates)
    -   Alpine.js (minimal) for any required client-side interactions
    -   Justification: Dramatically reduces frontend complexity while providing a responsive, interactive experience

-  **Authentication**:
    -    Simple session-based authentication for MVP
    -    JWT approach can be implemented later
    -  Justification: Simpler to implement and debug.

-   **Database**:
    -   SQLite with SQLAlchemy ORM
    -   Justification: Zero-configuration setup, perfect for proof of concept
    -   SQLAlchemy provides migration path to PostgreSQL when needed without code changes

-   **API Documentation**:
    -   Automatic OpenAPI/Swagger docs via FastAPI
    -   Justification: Built-in, no additional work required

### 9.2 AI Integration for MVP

**Approach: API-based Integration**

-   Integrate with OpenAI (ChatGPT) and Anthropic (Claude) via their APIs
-   Focus on just 2-3 models for the MVP to simplify implementation
-   Advantages:
    -   Faster development, no model hosting required
    -   Higher quality feedback from established models
    -   Simplified error handling and monitoring
-   Considerations:
    -   API costs should be contained during proof-of-concept stage
    -   Rate limiting unlikely to be an issue at MVP scale

**Future Path**:

-   Design the integration layer to be model-agnostic
-   Document API patterns for adding additional models
-   Plan for potential self-hosted options in future phases

### 9.3 Deployment Architecture for MVP

**Development Environment**:

-   Local development using Python virtual environments
-   Simple git-based version control workflow

**MVP Deployment**:

-   **University Research Server (Recommended for POC)**:
    -   Single-server deployment on existing infrastructure
    -   Nginx as a simple reverse proxy
    -   SQLite database with regular backups
    -   Simple systemd service or Docker container
    -   Justification: Minimizes infrastructure complexity during proof of concept

**Scaling Path**:

-   Document transition path to more robust infrastructure:
    -   Database migration to PostgreSQL
    -   Containerization with Docker
    -   Load balancing for increased traffic
    -   These can be implemented *after* the MVP proves successful

## 10. Implementation Roadmap

### 10.1 Phase 1: MVP / Proof of Concept (2-3 months)

-   Implement core functionality defined in MVP scope
-   Focus on the main student and instructor workflows
-   Text-based assignment feedback only (essays)
-   Integration with 2-3 AI models via APIs
-   Simple analytics focused on improvement metrics
-   Basic user interfaces using FastHTML + HTMX
-   Deploy to university research server for testing

### 10.2 Phase 2: Refinement and Feedback (1-2 months)

-   Gather feedback from initial user testing
-   Address usability issues and bugs
-   Implement key refinements based on user feedback
-   Improve prompt engineering for better AI responses
-   Document lessons learned and plan for expansion

### 10.3 Phase 3: Enhanced Features (If MVP Successful) (2-3 months)

-   Advanced analytics and reporting
-   Additional AI model integrations
-   Improved visualization of feedback
-   Expanded rubric capabilities
-   Import/export functionality
-   Performance optimizations for larger classes

### 10.4 Phase 4: Expansion (Based on Adoption) (3-4 months)

-   Support for code assignments
-   Batch processing capabilities
-   Advanced comparative analytics
-   LMS integration possibilities
-   Migration to PostgreSQL if needed for scale
-   Additional export formats

### 10.5 Phase 5: Future Directions (Post-successful deployment)

-   Support for additional content types (presentations, audio, video)
-   AI model performance analysis and optimization
-   Learning analytics and predictive insights
-   API for third-party integrations
-   Advanced customization options for institutions

## 11. Testing Strategy

### 11.1 Automated Testing

-   **Unit Tests**: Core business logic, utilities, helpers
-   **Integration Tests**: API endpoints, service interactions
-   **UI Tests**: Component rendering, user interactions
-   **End-to-End Tests**: Critical user journeys

### 11.2 Performance Testing

-   Load testing for submission processing
-   Response time benchmarks for feedback generation
-   Database query optimization
-   Frontend rendering performance

### 11.3 User Testing

-   Usability testing with student and instructor representatives
-   Feedback collection on interface intuitiveness
-   Accessibility testing for inclusive design
-   Beta testing period with limited user group

## 12. Development Process Recommendations

### 12.1 Development Methodology

-   Agile development with 2-week sprints
-   Regular demos with stakeholder feedback
-   Continuous integration and deployment
-   Feature flagging for controlled rollout

### 12.2 Team Composition for MVP

-   **Full-Stack Python Developer**: FastAPI and FastHTML implementation
-   **AI Integration Specialist**: Prompt engineering, model integration
-   **Database Developer**: Data modeling and SQLAlchemy implementation
-   **UX Designer**: Interface design (part-time)
-   **QA Tester**: Manual testing and feedback collection (part-time)
-   **Project Manager/Product Owner**: Coordination, requirements clarification

For the MVP, a smaller, more versatile team is recommended, with individuals potentially filling multiple roles. The simplified technology stack allows for fewer specialized roles compared to a more complex implementation.

### 12.3 Documentation Requirements

-   API documentation (OpenAPI/Swagger)
-   Component library documentation
-   Administrator guide
-   User guides (student and instructor)
-   Development setup documentation
-   Deployment procedures

## 13. Appendix: Mockups and Wireframes

Here are some text-based wireframes for those UI elements. We use a combination of:

*   **ASCII art:** For basic layout and structure.
*   **Descriptive text:** To explain the purpose and content of each element.
*   **`[ ]` for input fields:** Representing text boxes, dropdowns, etc.
*   `( )` for radio buttons or selectable options.
*   `{ }` for buttons.
*   `---` For Horizontal lines.

These text-based wireframes provide a structural blueprint for each UI element. They outline the necessary components, their arrangement, and the basic user flow, serving as a guide for the actual visual design and development. These wireframes will focus on the *structure and content*, not the visual styling (colors, fonts, etc.).  They are meant to convey the information architecture and user flow. 

**1. Student Dashboard**

```text
┌────────────────────────────────────────────────────────────────────────┐
│  FeedForward - Student Dashboard                                       │
│  [Navigation: Dashboard | My Submissions | Feedback History]  {Logout} │
├────────────────────────────────────────────────────────────────────────┤
│  Welcome, [Student Name]!                                              │
├────────────────────────────────────────────────────────────────────────┤
│  Active Assignments:                                                   │
│  ---                                                                   │
│  | Assignment Title 1 | [Course Code] | Due: [Date]  |                 │
│  | Status: [Draft 2/3 Submitted] {View Feedback}     |                 │
│  ---                                                                   │
│  | Assignment Title 2 | [Course Code] | Due: [Date]  |                 │
│  | Status: [Draft 1/3 Submitted] {View Feedback}     |                 │
│  ---                                                                   │
│  | Assignment Title 3 | [Course Code] | Due: [Date]  |                 │
│  | Status: [Awaiting Submission]  {Submit Draft}     |                 │
│  ---                                                                   │
│  (More Assignments...)                                                 │
└────────────────────────────────────────────────────────────────────────┘

Description:
- Top navigation bar.
- Welcome message.
- List of active assignments, each with:
    - Title and Course Code.
    - Due Date.
    - Submission Status (Draft number, or "Awaiting Submission").
    - Action buttons ("View Feedback" if available, "Submit Draft" otherwise).
```
![Student Dashboard Mockup](png/student-dashboard-mockup.png)


**2. My Submissions View**

```text
┌────────────────────────────────────────────────────────────────────────┐
│  FeedForward - My Submissions                                          │
│  [Navigation: Dashboard | My Submissions | Feedback History]  {Logout} │
├────────────────────────────────────────────────────────────────────────┤
│  Filter: [Course: (All) v] [Term: (All) v] [Status: (All) v]           │
├────────────────────────────────────────────────────────────────────────┤
│  Assignments:                                                          │
│  ---                                                                   │
│  | [Course Code] - Assignment Title 1 | Due: [Date]   |                │
│  | Status: [Completed]                                |                │
│  | Submitted: [Date]  {View Feedback}                 |                │
│  ---                                                                   │
│  | [Course Code] - Assignment Title 2 | Due: [Date]   |                │
│  | Status: [Draft 2/3]                                |                │
│  | Submitted: [Date]  {View Feedback} {Submit Draft}  |                │
│  ---                                                                   │
│  (More Assignments, potentially with pagination)                       │
└────────────────────────────────────────────────────────────────────────┘

Description:
- Top navigation.
- Filter controls for Course, Term, and Status.
- List of assignments (current and past), each with:
    - Course Code and Title.
    - Due Date.
    - Status (Completed, Draft number).
    - Submission Date.
    - Action buttons ("View Feedback", and "Submit Draft" if applicable).
```

![Student My Submissions Mockup](png/student-my-submissions-mockup.png)


**3. Feedback History View**

```text
┌────────────────────────────────────────────────────────────────────────┐
│  FeedForward - Feedback History                                        │
│  [Navigation: Dashboard | My Submissions | Feedback History]  {Logout} │
├────────────────────────────────────────────────────────────────────────┤
│  Select Time Range: [Start Date] - [End Date] {Apply}                  │
├────────────────────────────────────────────────────────────────────────┤
│  Overall Progress:                                                     │
│  [Progress Chart (e.g., line graph showing score over time)]           │
│  ---                                                                   │
│  Skill Breakdown:                                                      │
│  | Skill 1: [Progress Bar] [Improvement Percentage]     |              │
│  | Skill 2: [Progress Bar] [Improvement Percentage]     |              │
│  | Skill 3: [Progress Bar] [Improvement Percentage]     |              │
│  ---                                                                   │
│  Feedback Patterns:                                                    │
│  [List of recurring feedback comments, with frequency]                 |
└────────────────────────────────────────────────────────────────────────┘

Description:
- Top navigation.
- Time range selector.
- Overall progress chart (e.g., line graph of scores).
- Skill breakdown with progress bars and improvement percentages.
- List of recurring feedback patterns and their frequency.
```

![Student Feedback History Mockup](png/student-feedback-history-mockup.png)


**4. Assignment Feedback Interface**

```text
┌─────────────────────────────────────────────────────────────────────┐
│ FeedForward - Assignment Feedback: [Assignment Title]               │
│ [Navigation: Dashboard | My Submissions | Feedback History] {Logout}│
├─────────────────────────────────────────────────────────────────────┤
│ Course: [Course Code]  |  Draft: [1/3] {Draft 1 v}                  │
├─────────────────────────────────────────────────────────────────────┤
│ Overall Score: [Score/Percentage]  |  Improvement: [+X%]            │
├─────────────────────────────────────────────────────────────────────┤
│ Strengths:                                                          │
│ - [Strength 1 from AI]                                              │
│ - [Strength 2 from AI]                                              │
│ ...                                                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Areas for Improvement:                                              │
│ - [Improvement Area 1 from AI]                                      │
│ - [Improvement Area 2 from AI]                                      │
│ ...                                                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Rubric Feedback:                                                    │
│  ---                                                                │
│  | Category 1: [Score]  [Feedback from AI]             |            │
│  ---                                                                │
│  | Category 2: [Score]  [Feedback from AI]             |            │
│  ---                                                                │
│  (More Rubric Categories)                              |            │
├─────────────────────────────────────────────────────────────────────┤
│ {Submit Next Draft}  (If applicable)                                │
└─────────────────────────────────────────────────────────────────────┘

Description:
- Top Navigation.
- Course and Draft information.
- Overall Score and Improvement percentage (compared to previous draft).
- Summarized Strengths.
- Summarized Areas for Improvement.
- Rubric-aligned feedback, with scores and AI comments for each category.
- "Submit Next Draft" button (if allowed).
-  Draft Drop down to move between drafts.
```

**5. Instructor Course View**

```text
┌────────────────────────────────────────────────────────────────┐
│ FeedForward - Instructor Portal: [Course Code] - [Course Name] │
│ [Navigation: Courses | Analytics] {Logout}                     │
├────────────────────────────────────────────────────────────────┤
│  [Sidebar: Course List (Selected: [Course Code])]              │
│                                                                │
│  [Tabs: Assignments | Students | Stats]                        │
├────────────────────────────────────────────────────────────────┤
│  (Content of selected tab - see below)                         │
└────────────────────────────────────────────────────────────────┘

Description:
- Top Navigation.
- Sidebar with a list of courses (the current course is highlighted).
- Tabbed navigation for Assignments, Students, and Stats within the course.  The content of the selected tab would appear below.
```

**5a. Instructor Course View - Assignments Tab**

```text
(Content of Assignments Tab)
├──────────────────────────────────────────────────────────────┤
│  Assignments:                                                │
│  ---                                                         │
│  | Assignment Title 1 | Due: [Date] | Status: [Published] |  │
│  | [Number] Submissions  {View Submissions} {Edit}        |  │
│  ---                                                         │
│  | Assignment Title 2 | Due: [Date] | Status: [Draft]     |  │
│  | [Number] Submissions  {View Submissions} {Edit}        |  │
│  ---                                                         │
│  {Create New Assignment}                                     │
└──────────────────────────────────────────────────────────────┘
```


**5b. Instructor Course View - Students Tab**

```text
(Content of Students Tab)
├───────────────────────────────────────────────────────────┤
│  Students:                                                │
│  [Search: [             ]]                                │
│  ---                                                      │
│  | Student Name 1 | [Email] | Last Activity: [Date]    |  │
│  | {View Details}                                      |  │
│  ---                                                      │
│  | Student Name 2 | [Email] | Last Activity: [Date]    |  │
│  | {View Details}                                      |  │
│  ---                                                      │
│  {Add Student} {Import Students}                          │
└───────────────────────────────────────────────────────────┘
```

![Instructor Course View - Students Tab Mockup](png/instructor-course-view-students-tab-mockup.png)

**5c. Instructor Course View - Stats Tab**

```text
(Content of Stats Tab)
├───────────────────────────────────────────────────────────┤
│  Course Statistics:                                       │
│  Select Assignment: [Assignment Title v] {View Stats}     │
├───────────────────────────────────────────────────────────┤
│  (Assignment-specific stats would appear here, similar to │
│   the "Course Feedback Stats" wireframe, #8)              │
└───────────────────────────────────────────────────────────┘
```

**6. Assignment Creation Workflow (5 steps)**

This is a multi-step process, so each step is a separate wireframe.

**Step 1: Assignment Details**

```text
┌───────────────────────────────────────────────────────────┐
│ FeedForward - Create Assignment: Step 1/5                 │
├───────────────────────────────────────────────────────────┤
│ Assignment Title: [                                  ]    │
│ Description: [                                       ]    │
│                                                           │
│ Due Date: [Date Picker]                                   │
│ Maximum Drafts Allowed: [Number Input]                    │
│                                                           │
│ {Save as Draft} {Next >}                                  │
└───────────────────────────────────────────────────────────┘
```

![Assignment Creation Step 1 Mockup](png/instructor-assignment-creation-step1-mockup.png)

**Step 2: Assignment Specifications**

```text
┌───────────────────────────────────────────────────────────┐
│ FeedForward - Create Assignment: Step 2/5                 │
├───────────────────────────────────────────────────────────┤
│ Option 1: Upload Specifications Document                  │
│ [File Upload: {Choose File}] {Upload}                     │
├───────────────────────────────────────────────────────────┤
│ Option 2: Create in Text Editor                           │
│ [Large Text Area for writing specifications]              │
│                                                           │
│ {< Back} {Save as Draft} {Next >}                         │
└───────────────────────────────────────────────────────────┘
```

![Assignment Creation Step 2 Mockup](png/instructor-assignment-creation-step2-mockup.png)

**Step 3: Rubric Creation**

```text
┌───────────────────────────────────────────────────────────┐
│ FeedForward - Create Assignment: Step 3/5                 │
├───────────────────────────────────────────────────────────┤
│ Option 1:  Create Manually | Create Rubric using AI       |
│ [Table for adding rubric categories and criteria]         │
│  | Category | Weight (%) | Description                 |  │
│  | [       ] | [       ]  | [                       ]  |  │
│  | [       ] | [       ]  | [                       ]  |  │
│  | {Add Category}                                      |  │
│                                                           │
│ {< Back} {Save as Draft} {Next >}                         │
└───────────────────────────────────────────────────────────┘
```

![Assignment Creation Step 3 Mockup](png/instructor-assignment-creation-step3-mockup.png)

**Step 4: Feedback Settings**

```text
┌────────────────────────────────────────────────────────────────────┐
│ FeedForward - Create Assignment: Step 4/5                          │
├────────────────────────────────────────────────────────────────────┤
│ AI Model Selection:                                                │
│ ( ) ChatGPT   ( ) Claude   ( ) Llama 3                             │
│                                                                    │
│ Feedback Style: [ (Balanced) (Encouraging) (Detailed) v ]          │
│                                                                    │
│ Review Threshold: [ (Always Review) (Review if Low Confidence) v ] |
│                                                                    │
│ {< Back} {Save as Draft} {Next >}                                  │
└────────────────────────────────────────────────────────────────────┘
```

![Assignment Creation Step 4 Mockup](png/instructor-assignment-creation-step4-mockup.png)

**Step 5: Review & Publish**

```text
┌───────────────────────────────────────────────────────────────┐
│ FeedForward - Create Assignment: Step 5/5                     │
├───────────────────────────────────────────────────────────────┤
│ Summary of all settings (read-only display of previous steps) │
│                                                               │
│ {< Back} {Save as Draft} {Publish Assignment}                 │
└───────────────────────────────────────────────────────────────┘
```

![Assignment Creation Step 5 Mockup](png/instructor-assignment-creation-step5-mockup.png)

**7. Student Roster Management**

(This is essentially the same as the "Students" tab in the Instructor Course View - 5b.  I'll repeat it here for completeness.)

```text
┌──────────────────────────────────────────────────────────────┐
│  FeedForward - Student Roster: [Course Code] - [Course Name] │
│ [Navigation: Courses | Analytics] {Logout}                   │
├──────────────────────────────────────────────────────────────┤
│  [Sidebar: Course List (Selected: [Course Code])]            │
│                                                              │
│  [Tabs: Assignments | Students | Stats]                      │
├──────────────────────────────────────────────────────────────┤
│  Students:                                                   │
│  [Search: [             ]]                                   │
│  ---                                                         │
│  | Student Name 1 | [Email] | Last Activity: [Date]     |    │
│  | {View Details}                                       |    │
│  ---                                                         │
│  | Student Name 2 | [Email] | Last Activity: [Date]     |    │
│  | {View Details}                                       |    │
│  ---                                                         │
│  {Add Student} {Import Students}                             │
└──────────────────────────────────────────────────────────────┘
```

![Instructor Course View - Students Tab Mockup](png/instructor-course-view-students-tab-mockup.png)


**8. Course Feedback Stats**

```text
┌───────────────────────────────────────────────────────────┐
│ FeedForward - Course Feedback Stats: [Course Code]        │
│ [Navigation: Courses | Analytics] {Logout}                │
├───────────────────────────────────────────────────────────┤
│  [Sidebar: Course List (Selected: [Course Code])]         │
│                                                           │
│  [Tabs: Assignments | Students | Stats]                   │
├───────────────────────────────────────────────────────────┤
│ Select Assignment: [Assignment Title v]                   │
├───────────────────────────────────────────────────────────┤
│ Overall Engagement:                                       │
│ - Total Submissions: [Number]                             │
│ - Average Drafts per Student: [Number]                    │
│ - Completion Rate: [Percentage]                           │
├───────────────────────────────────────────────────────────┤
│ Assignment Improvement:                                   │
│ [Chart showing score distribution across drafts]          │
├───────────────────────────────────────────────────────────┤
│ Performance by Rubric Category:                           │
│ [Table or chart showing average scores for each category] │
├───────────────────────────────────────────────────────────┤
│ {Export Data}                                             │
└───────────────────────────────────────────────────────────┘

Description:
- Top Navigation and Sidebar (as in Instructor Course View).
- Assignment selection dropdown.
- Overall engagement metrics (submissions, drafts, completion).
- Chart showing score improvement across drafts.
- Breakdown of performance by rubric category (table or chart).
- Export button.
```

![Course Feedback Stats Mockup](png/instructor-course-feedback-stats-mockup.png)

**9. Global Analytics Dashboard**

```text
┌─────────────────────────────────────────────────────────────┐
│ FeedForward - Analytics Dashboard                           │
│ [Navigation: Courses | Analytics] {Logout}                  │
├─────────────────────────────────────────────────────────────┤
│ Select Term: [Term v] {Apply}                               │
├─────────────────────────────────────────────────────────────┤
│ Overall System Usage:                                       │
│ - Total Courses: [Number]                                   │
│ - Total Assignments: [Number]                               │
│ - Total Students: [Number]                                  │
│ - Total Submissions: [Number]                               │
├─────────────────────────────────────────────────────────────┤
│ Course Comparison:                                          │
│ [Chart comparing key metrics across courses]                │
├─────────────────────────────────────────────────────────────┤
│ AI Model Performance:                                       │
│ [Table showing usage and average confidence for each model] |
├─────────────────────────────────────────────────────────────┤
│ (Drill-down links to course-specific views)                 │
└─────────────────────────────────────────────────────────────┘

Description:
- Top navigation.
- Term selection.
- Overall system usage statistics.
- Chart for comparing courses.
- AI model performance table.
- Links to drill down to course-level statistics.
```

![Global Analytics Dashboard Mockup](png/instructor-global-analytics-dashboard-mockup.png)

**10. Add Course Dialog**

```text
┌─────────────────────────────────────┐
│ Add New Course                      │
├─────────────────────────────────────┤
│ Course Code: [          ]           │
│ Course Title: [         ]           │
│ Term: [ (Fall) (Spring) (Summer) ]  |
│ Department: [          ]            |
│                                     │
│ {Cancel} {Create Course}            │
└─────────────────────────────────────┘
Description:
-   Simple modal dialog.
-   Input fields for Course Code, Title, Term, and Department.
-   Cancel and Create Course buttons.
```

![Add Course Dialog Mockup](png/instructor-add-course-dialog-mockup.png)

**11. Import Students Dialog**

```text
┌───────────────────────────────┐
│ Import Students               │
├───────────────────────────────┤
│ Method: [ (CSV) (TSV) ]       |
│                               │
│ [File Upload: {Choose File}]  |
│                               │
│ {Cancel} {Upload and Import}  |
└───────────────────────────────┘
Description:

-   Simple modal dialog.
-   Radio buttons to choose the import file format (CSV or TSV).
-   File upload control.
-    Cancel and Upload and Import buttons.
```

![Import Students Dialog Mockup](png/instructor-import-students-dialog-mockup.png)


## 14. Appendix – Competitive Analysis: FeedForward vs. Co-Grader

## Competitive Analysis: FeedForward vs. Co-Grader
**A Comparative Review of AI-Driven Feedback Systems in Education**

### **Similarities Between FeedForward and Co-Grader**
1. **AI-Assisted Feedback Generation** – Both FeedForward and Co-Grader utilize AI to generate feedback on student submissions. They integrate AI models to automate the feedback process, making grading more efficient while still allowing human oversight.
2. **Rubric-Based Assessment** – Both systems rely on rubrics for structured feedback. FeedForward aligns feedback with customizable rubrics for formative assessment, while Co-Grader allows teachers to create or import rubrics and applies them to grading.
3. **Iterative Improvement Focus** – Both platforms support iterative learning by enabling students to refine their work based on AI-generated feedback. FeedForward emphasizes multiple draft submissions, while Co-Grader provides insights to guide student progress.
4. **Instructor Control and Oversight** – Each system includes a “human-in-the-loop” approach, ensuring that teachers can review, modify, and approve AI-generated feedback before providing it to students. This maintains quality and avoids fully automated grading.
5. **Time-Saving for Educators** – Both platforms are designed to reduce the time educators spend on grading, with Co-Grader claiming up to 80% time savings, while FeedForward streamlines the feedback loop to allow instructors to focus on targeted interventions.

### **Key Differences Between FeedForward and Co-Grader**
1. **Primary Use Case** – FeedForward is designed for higher education and supports broader feedback, focusing on writing-based assignments and reflective learning. Co-Grader is more oriented toward K-12 education and includes code grading alongside essay assessments.
2. **AI Model Diversity** – FeedForward explicitly integrates multiple AI models (e.g., ChatGPT, Claude, Llama 3) to provide diverse feedback perspectives. Co-Grader focuses more on AI-driven rubric grading and feedback based on predefined criteria.
3. **Draft-Based vs. Finalized Feedback** – FeedForward is built around an iterative workflow where students submit multiple drafts, tracking progress over time. Co-Grader focuses on efficiently grading and providing structured feedback on a single submission per assignment.
4. **Assignment Import and LMS Integration** – Co-Grader integrates closely with Google Classroom, allowing automatic assignment imports and exports. FeedForward, at least in its MVP phase, does not emphasize direct LMS integration but focuses on structured feedback customization.
5. **Feedback Customization and Insights** – While both platforms allow instructors to modify AI-generated feedback, Co-Grader includes built-in analytics for identifying common class-wide issues and areas for improvement. FeedForward, on the other hand, prioritizes rubric-based structured feedback and student reflection on progress.

### **Conclusion**
FeedForward and Co-Grader share a mission to enhance grading efficiency and feedback quality using AI, with a strong emphasis on human oversight. However, FeedForward focuses on **higher education, iterative learning, and multi-model AI feedback**, whereas Co-Grader is optimized for **K-12 grading, Google Classroom integration, and rubric-driven assessment with automated insights**.

## 15. Glossary

**General Concepts & Project-Specific Terms:**

*   **Adaptive Feedback:** Feedback that adjusts its content and complexity based on the student's progress across multiple drafts.
*   **Assignment:** A task or piece of work assigned to a student.
*   **Course:** A series of lessons or lectures on a particular subject.
*   **Draft:** A version of a student's submission for an assignment.
*   **Feedback:** AI-generated comments highlighting strengths and areas for improvement.
*   **Feedback Consolidation:** The process of combining feedback from multiple AI models into a single, coherent set of recommendations.
*   **Formative Feedback:** Feedback designed to help students learn and improve, as opposed to summative feedback which is focused on evaluation.
*   **Instructor:** The person teaching a course.
*    **Iterative Learning:** Process of submitting multiple drafts and improving based on feedback.
*   **Rubric:** A set of criteria used to evaluate student work.
*   **Student:** A person who is studying at a school or college.
*   **Submission:** A piece of work submitted by a student.
* **FeedForward (System Name):**  The AI-powered feedback system being specified.

**AI and Machine Learning:**

*   **AI Model (or Model):** A specific, trained algorithm used for tasks like text analysis and generation (e.g., GPT-4, Claude).
*   **Confidence (in AI context):** A measure of the AI's certainty in its assessment or generated feedback.  Often represented as a probability or score.
*   **LLM:** Large Language Model. A type of AI model capable of understanding and generating human-like text.
*   **Multi-Engine (or Multi-Model):** Using multiple AI models to generate more comprehensive and robust feedback.
*   **Prompt Engineering:** The process of crafting input text (prompts) to guide an AI model's output effectively.
*    **Run:** in a multi-model system, one assessment from a single LLM
* **Aggregation Method:** the method used to combine the marks from the different Runs.
*   **Trimmed Mean:** An aggregation method where the highest and lowest marks from the different Runs are ignored.

**Technical Terms:**

*   **API (Application Programming Interface):** A set of rules and specifications that software programs can follow to communicate with each other.  Used here to interact with AI models.
*   **Backend:** The server-side logic and database of the application.
*   **Caching:**  Storing frequently accessed data (like AI responses) temporarily for faster retrieval.
*   **Circuit Breaker Pattern:** A design pattern that prevents cascading failures by temporarily stopping requests to an unresponsive service.
*   **Containerization (e.g., Docker):**  Packaging software and its dependencies into a standardized unit for deployment.
*   **Deployment:** The process of making the software application available for use.
*   **End-to-End Tests:** Tests that verify the complete flow of a user interaction through the system.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
*   **FastHTML:** A Python library for generating HTML directly from Python code.
*   **Frontend:** The user interface (UI) of the application that users interact with.
*   **Horizontal Scaling:** Adding more servers to handle increased load.
*    **HTMX:** A library that allows access to AJAX, CSS Transitions, WebSockets and Server Sent Events directly in HTML
*   **Integration Tests:** Tests that verify the interaction between different parts of the system.
*   **JWT (JSON Web Token):** A standard for securely transmitting information between parties as a JSON object.  Often used for authentication.
*   **Load Balancing:** Distributing incoming network traffic across multiple servers.
*   **Load Testing:**  Testing the system's performance under heavy user load.
*   **LTI (Learning Tools Interoperability):** A standard for integrating learning applications with platforms like learning management systems.
*   **ORM (Object-Relational Mapper):** A technique that lets you query and manipulate data from a database using an object-oriented paradigm (e.g., SQLAlchemy).
*   **RESTful API:** An API that follows the principles of REST (Representational State Transfer), a common architectural style for web services.
*   **SQLAlchemy:** A popular Python SQL toolkit and Object-Relational Mapper.
*   **SQLite:** A lightweight, file-based database system.  Suitable for smaller applications and development.
*   **SSO (Single Sign-On):** A system that allows users to log in once and access multiple applications.
*  **Tailwind CSS**: A low-level CSS framework for quickly styling web UIs.
*   **Unit Tests:** Tests that verify individual components or functions of the code.
*   **User Interface (UI):**  The part of the application that the user sees and interacts with.
*   **UX (User Experience):**  The overall experience a user has when interacting with the application.
*   **WCAG (Web Content Accessibility Guidelines):**  International standards for making web content accessible to people with disabilities.

**Development Process:**

*   **Agile Development:** An iterative approach to software development that emphasizes flexibility and collaboration.
*   **Continuous Integration/Continuous Deployment (CI/CD):**  A practice of automating the building, testing, and deployment of software.
*   **Feature Flagging:** A technique for enabling or disabling features in a controlled way, often used for testing new features.
*   **MVP (Minimum Viable Product):** The simplest version of a product that can be released to gather user feedback.
*    **Proof of Concept:** A small project used to show that a new feature or system is viable.
*   **Sprint:** A short, time-boxed period (often two weeks) in Agile development during which a specific set of tasks is completed.
