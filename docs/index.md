---
layout: home
title: Home
nav_order: 1
description: "FeedForward is an AI-powered platform for providing formative feedback on student assignments."
permalink: /
---

# FeedForward Documentation
{: .fs-9 }

AI-Powered Formative Feedback for Higher Education
{: .fs-6 .fw-300 }

[Get Started](/getting-started/installation){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/michael-borck/feed-forward){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## Welcome to FeedForward

FeedForward transforms the way students receive feedback on their assignments. Instead of simply correcting work, our AI-powered platform provides structured, constructive feedback that guides students toward improvement through iterative learning.

### 🎯 Key Features

- **Multiple AI Models**: Leverage diverse perspectives from ChatGPT, Claude, Llama, and other leading AI models
- **Rubric-Aligned Feedback**: Customizable criteria that match your specific assessment objectives
- **Iterative Learning**: Students can submit multiple drafts and track their progress
- **Privacy-First Design**: Student submissions are processed securely and not permanently stored
- **Instructor Control**: Review and approve AI-generated feedback before release

### 👥 For Different Users

<div class="grid-container">
  <div class="grid-item">
    <h4>📚 Students</h4>
    <p>Submit drafts, receive detailed feedback, and track your improvement across iterations.</p>
    <a href="/user-guides/student/" class="btn btn-outline">Student Guide →</a>
  </div>
  
  <div class="grid-item">
    <h4>👩‍🏫 Instructors</h4>
    <p>Create assignments, design rubrics, manage students, and review AI-generated feedback.</p>
    <a href="/user-guides/instructor/" class="btn btn-outline">Instructor Guide →</a>
  </div>
  
  <div class="grid-item">
    <h4>🔧 Administrators</h4>
    <p>Configure the system, manage users, and set up AI providers.</p>
    <a href="/user-guides/admin/" class="btn btn-outline">Admin Guide →</a>
  </div>
</div>

### 🚀 Quick Start

1. **[Installation Guide](/getting-started/installation)** - Set up FeedForward on your server
2. **[Configuration](/getting-started/configuration)** - Configure AI providers and system settings
3. **[Quick Start](/getting-started/quick-start)** - Get up and running in minutes

### 📖 Documentation Overview

#### Getting Started
- [Installation](/getting-started/installation) - Detailed setup instructions
- [Configuration](/getting-started/configuration) - Environment variables and AI setup
- [Quick Start](/getting-started/quick-start) - Minimal steps to get running

#### User Guides
- [Student Guide](/user-guides/student/) - For students using the platform
- [Instructor Guide](/user-guides/instructor/) - For educators managing courses
- [Admin Guide](/user-guides/admin/) - For system administrators

#### Technical Documentation
- [Architecture](/technical/architecture) - System design and components
- [Database Schema](/technical/database-schema) - Data structure reference
- [AI Integration](/technical/ai-integration) - How feedback generation works
- [API Reference](/technical/api-reference) - Endpoint documentation

#### Design & Deployment
- [Design Overview](/design/overview) - Educational philosophy and principles
- [Architecture Decisions](/design/adrs/) - Key design choices explained
- [Deployment Guide](/deployment/installation) - Production deployment

### 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/michael-borck/feed-forward/blob/main/CONTRIBUTING.md) for details.

### 📄 License

FeedForward is open source software licensed under the [MIT License](https://github.com/michael-borck/feed-forward/blob/main/LICENSE).

### 🆘 Need Help?

- Check our [Troubleshooting Guide](/deployment/troubleshooting)
- Open an [issue on GitHub](https://github.com/michael-borck/feed-forward/issues)
- Contact the maintainers

---

<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.grid-item {
  padding: 1.5rem;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  background: #f6f8fa;
}

.grid-item h4 {
  margin-top: 0;
  color: #0366d6;
}

.grid-item p {
  margin: 1rem 0;
}
</style>