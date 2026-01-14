# Autonomous Agent Guide

## 🤖 Overview

The Autonomous Agent is an MVP enhancement to the distributed AI agent system that enables **autonomous website analysis, task generation, and execution** with minimal human intervention.

### What It Does

1. **Analyzes** existing websites to understand current state
2. **Compares** against industry standards (coaching, consulting, professional services)
3. **Generates** prioritized task lists for improvements
4. **Executes** tasks autonomously using OpenHands SDK
5. **Creates** GitHub PRs for each completed task
6. **Reports** progress and results in real-time

---

## 🎯 Key Features

### Website Analyzer
- Scans website structure and pages
- Identifies broken links and missing resources
- Checks mobile responsiveness
- Analyzes performance metrics
- Detects security issues

### Industry Knowledge Base
- Pre-loaded coaching industry standards
- Professional services best practices
- Required pages and features
- SEO and conversion optimization guidelines

### Task Generator
- Creates prioritized task lists
- Estimates execution time
- Generates detailed prompts for AI execution
- Categorizes by type (create_page, add_feature, fix, security, optimize)

### Autonomous Executor
- Executes tasks one by one
- Creates GitHub branches and PRs automatically
- Handles errors gracefully
- Provides real-time progress updates
- Generates execution reports

---

## 🚀 Quick Start

### 1. Access Autonomous Mode

Open your browser and navigate to:
```
http://localhost/autonomous_mode.html
```

### 2. Analyze a Website

**Option A: Analyze Only (No Execution)**
- Enter website URL
- Click "🔍 Analyze Only"
- Review generated task list
- Decide which tasks to execute

**Option B: Full Autonomous Workflow**
- Enter website URL
- Check "Automatically create GitHub PRs"
- Click "🚀 Start Autonomous Analysis & Execution"
- Watch real-time progress
- Review PRs when complete

---

## 📋 Example Workflow

### Input
```
Website URL: https://purposefullivecoaching.com
Auto PR: ✅ Enabled
```

### Process
1. **Analysis Phase** (10-30 seconds)
   - Scans website structure
   - Identifies 5 existing pages
   - Finds 3 broken links
   - Detects missing pages: Services, Blog, Testimonials

2. **Task Generation** (5 seconds)
   - Generates 12 prioritized tasks
   - Critical: Fix broken contact form
   - High: Add services page
   - Medium: Add testimonials section
   - Low: Optimize images

3. **Execution Phase** (2-5 minutes per task)
   - Task 1: Fix contact form → PR #123 created
   - Task 2: Add services page → PR #124 created
   - Task 3: Add testimonials → PR #125 created
   - ...continues until all tasks complete

### Output
```
✅ Execution Summary
- Tasks Generated: 12
- Tasks Completed: 10
- Tasks Failed: 1
- Tasks Skipped: 1
- PRs Created: 10
- Success Rate: 83%
```

---

## 🎨 Supported Industries

### Coaching & Consulting
- Life coaching
- Business coaching
- Career coaching
- Executive coaching
- Health & wellness coaching

### Professional Services
- Legal services
- Accounting services
- Marketing agencies
- Design studios
- Consulting firms

### Coming Soon
- E-commerce
- SaaS products
- Educational platforms
- Healthcare providers

---

## 📊 Task Types

### 1. Create Page (`create_page`)
Creates new pages based on industry standards.

**Example:**
- Services page with pricing tiers
- About page with team bios
- Blog with article templates
- Testimonials page with client reviews

### 2. Add Feature (`add_feature`)
Adds functionality to existing pages.

**Example:**
- Contact form with validation
- Newsletter signup
- Social media integration
- Live chat widget

### 3. Fix (`fix`)
Fixes broken or non-functional elements.

**Example:**
- Broken links
- Form submission errors
- Mobile responsiveness issues
- Cross-browser compatibility

### 4. Security (`security`)
Implements security improvements.

**Example:**
- HTTPS enforcement
- Form validation and sanitization
- CSRF protection
- Security headers

### 5. Optimize (`optimize`)
Performance and SEO optimizations.

**Example:**
- Image compression
- Code minification
- Lazy loading
- Meta tags and structured data

---

## 🔧 API Endpoints

### POST `/v1/autonomous/analyze-and-fix`
Full autonomous workflow: analyze → generate tasks → execute → create PRs

**Request:**
```json
{
  "website_url": "https://example.com",
  "auto_pr": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Autonomous workflow completed: 10 tasks completed, 10 PRs created",
  "analysis_summary": {
    "pages_found": 5,
    "structure": "good",
    "broken_links": 3,
    "performance": "needs_improvement"
  },
  "tasks_generated": 12,
  "tasks_completed": 10,
  "tasks_failed": 1,
  "prs_created": 10,
  "report_file": "autonomous_report_20260113_150000.json"
}
```

### POST `/v1/autonomous/analyze-only`
Analyze website and generate task list (no execution)

**Request:**
```json
{
  "website_url": "https://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "analysis": {
    "url": "https://example.com",
    "pages_found": 5,
    "structure": "good",
    "features": ["contact_form", "navigation"],
    "broken_links": 3,
    "performance": "needs_improvement"
  },
  "tasks": [
    {
      "id": 1,
      "type": "fix",
      "priority": "critical",
      "title": "Fix broken contact form",
      "description": "Contact form submission fails with 500 error",
      "estimated_time": "15 minutes"
    }
  ],
  "summary": "Generated 12 tasks: 2 critical, 4 high, 4 medium, 2 low"
}
```

### GET `/v1/autonomous/status`
Get autonomous agent system status

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0-mvp",
  "capabilities": [
    "website_analysis",
    "task_generation",
    "autonomous_execution",
    "github_pr_creation"
  ],
  "supported_industries": [
    "coaching",
    "consulting",
    "professional_services"
  ]
}
```

---

## 🎯 Priority Levels

### Critical (🔴)
- Security vulnerabilities
- Broken core functionality
- Major user experience issues
- **Execute first**

### High (🟠)
- Missing essential pages
- Important features
- SEO issues
- **Execute second**

### Medium (🟡)
- Nice-to-have features
- Minor improvements
- Content enhancements
- **Execute third**

### Low (🟢)
- Optimizations
- Polish
- Future enhancements
- **Execute last**

---

## 📝 Execution Reports

After each autonomous workflow, a detailed JSON report is generated:

```json
{
  "website_url": "https://example.com",
  "analysis": {
    "url": "https://example.com",
    "pages_found": 5,
    "structure": "good",
    "features": ["contact_form", "navigation"],
    "broken_links": 3,
    "performance": "needs_improvement"
  },
  "tasks": [...],
  "execution": {
    "total_tasks": 12,
    "completed": 10,
    "failed": 1,
    "skipped": 1,
    "prs_created": 10,
    "start_time": "2026-01-13T15:00:00Z",
    "end_time": "2026-01-13T15:45:00Z",
    "task_results": [...]
  }
}
```

---

## 🔄 GitHub PR Workflow

### Automatic PR Creation

For each completed task, the system automatically:

1. **Creates branch**: `task-{id}-{type}-{timestamp}`
2. **Commits changes**: With detailed commit message
3. **Opens PR**: With comprehensive description
4. **Adds labels**: Based on priority and type
5. **Requests review**: From designated reviewers

### PR Template

```markdown
## Task #{id}: {title}

**Priority:** {priority}
**Type:** {type}

### Changes Made
{detailed description of changes}

### Files Modified
- file1.html
- file2.css
- file3.js

### Execution Time
{execution_time}

### Testing
- [x] Task executed successfully
- [x] No errors encountered
- [ ] Manual review required

---
*Generated by Autonomous Agent*
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# HP OMEN Orchestrator
LENOVO_API_URL=http://lenovo:8088

# Autonomous Agent
AUTONOMOUS_MODE=enabled
AUTO_PR=true
GITHUB_TOKEN=your_token_here
```

### Customization

**Add New Industry Standards:**
Edit `shared/autonomous/coaching_standards.py`:

```python
INDUSTRY_STANDARDS = {
    "your_industry": {
        "required_pages": [...],
        "essential_features": [...],
        "best_practices": [...]
    }
}
```

**Modify Task Priorities:**
Edit `shared/autonomous/task_generator.py`:

```python
def _determine_priority(self, task_type, severity):
    # Your custom priority logic
    pass
```

---

## 🐛 Troubleshooting

### Issue: "Autonomous endpoints not available"
**Solution:** Ensure HP OMEN orchestrator has autonomous module installed:
```bash
cd hp_omen
pip install beautifulsoup4 lxml
```

### Issue: "Website analysis failed"
**Solution:** Check website is publicly accessible and not behind authentication

### Issue: "PR creation failed"
**Solution:** Verify GitHub token has correct permissions:
- `repo` scope
- Write access to repository

### Issue: "Task execution timeout"
**Solution:** Complex tasks may take longer. Increase timeout in orchestrator config.

---

## 📈 Performance Tips

### Optimize Analysis Speed
- Use cached results for repeated analyses
- Limit page depth for large sites
- Skip external resources

### Improve Task Execution
- Enable parallel execution (future enhancement)
- Use mock mode for testing
- Pre-validate prompts

### Reduce API Costs
- Batch similar tasks
- Use analyze-only mode first
- Review task list before execution

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Parallel task execution
- [ ] Custom industry templates
- [ ] A/B testing integration
- [ ] Performance benchmarking
- [ ] Multi-language support
- [ ] Visual regression testing
- [ ] Automated accessibility audits
- [ ] SEO score tracking

### Roadmap
- **Q1 2026**: Multi-industry support
- **Q2 2026**: Advanced analytics
- **Q3 2026**: AI-powered design suggestions
- **Q4 2026**: Full autonomous deployment

---

## 💡 Best Practices

### 1. Start with Analyze-Only
Always review the generated task list before executing.

### 2. Review PRs Promptly
Don't let PRs pile up - review and merge regularly.

### 3. Test in Staging First
Run autonomous agent on staging environment before production.

### 4. Monitor Execution
Watch real-time progress to catch issues early.

### 5. Customize for Your Needs
Adapt industry standards to match your specific requirements.

---

## 📚 Additional Resources

- [Main README](../README.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)

---

## 🤝 Support

For issues or questions:
1. Check this guide first
2. Review execution reports
3. Check GitHub issues
4. Contact support

---

**Built with ❤️ by the Distributed AI Agent Team**
