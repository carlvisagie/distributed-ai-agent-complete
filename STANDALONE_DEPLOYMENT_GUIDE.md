# 🤖 Standalone AI Agent System - Deployment Guide

## Overview

This is a **production-ready, standalone AI agent system** that can autonomously complete ANY software project with perfect continuity across sessions.

**Key Features:**
- ✅ Autonomous task execution with Claude Sonnet 4.5
- ✅ Perfect continuity (never loses context or repeats work)
- ✅ Works on ANY project (not tied to specific tech stack)
- ✅ GitHub PR automation
- ✅ Self-healing infrastructure
- ✅ Real-time progress tracking
- ✅ Checkpoint/resume capability

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│     Autonomous AI Agent System          │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Autonomous Executor V2        │   │
│  │   - Task orchestration          │   │
│  │   - LLM-powered execution       │   │
│  │   - Error recovery              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Perfect Continuity System     │   │
│  │   - Context Manager             │   │
│  │   - Task State Manager          │   │
│  │   - Session Manager             │   │
│  │   - Knowledge Graph             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   GitHub Integration            │   │
│  │   - Automatic PR creation       │   │
│  │   - Branch management           │   │
│  │   - Commit automation           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 📦 What's Included

### Core Components

1. **Autonomous Executor V2** (`shared/autonomous/autonomous_executor_v2.py`)
   - Main orchestration engine
   - Integrates all subsystems
   - Handles task execution

2. **Perfect Continuity System**
   - `context_manager.py` - Project knowledge persistence
   - `task_state_manager.py` - Task tracking and state
   - `session_manager.py` - Session and checkpoint management
   - `knowledge_graph.py` - Codebase understanding

3. **Real Executor** (`shared/autonomous/real_executor.py`)
   - Three-phase LLM execution
   - Code generation and modification
   - Git operations

4. **GitHub PR Manager** (`shared/github_pr_manager.py`)
   - Automatic branch creation
   - PR automation
   - Review checklist generation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Git** configured with GitHub access
- **Anthropic API Key** (for Claude Sonnet 4.5)
- **Project to complete** (any codebase)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/carlvisagie/distributed-ai-agent-complete.git
cd distributed-ai-agent-complete
```

2. **Install dependencies:**
```bash
pip install anthropic gitpython
```

3. **Set up environment:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export USE_REAL_EXECUTION="true"
```

4. **Configure for your project:**
```bash
# Edit the configuration
nano standalone_config.json
```

```json
{
  "project_id": "my_project",
  "project_path": "/path/to/your/project",
  "project_name": "My Project",
  "auto_pr": true,
  "checkpoint_interval": 5
}
```

5. **Run the agent:**
```bash
python3 run_standalone_agent.py
```

---

## 📋 How It Works

### First Run (New Project)

1. **Analysis Phase:**
   - Agent scans your entire codebase
   - Builds knowledge graph of components
   - Identifies incomplete features
   - Generates prioritized task list

2. **Execution Phase:**
   - Executes tasks one by one
   - Uses Claude Sonnet 4.5 for code generation
   - Creates checkpoints every N tasks
   - Commits changes with detailed messages

3. **PR Phase:**
   - Creates feature branch
   - Pushes changes to GitHub
   - Opens PR with review checklist
   - Waits for human approval

### Subsequent Runs (Resume)

1. **Load State:**
   - Loads project context from disk
   - Finds last checkpoint
   - Identifies completed tasks

2. **Resume Execution:**
   - Continues from where it left off
   - Never repeats completed work
   - Maintains full continuity

3. **Complete:**
   - Finishes remaining tasks
   - Creates final PR
   - Reports completion stats

---

## 🎯 Usage Examples

### Example 1: Complete a Web App

```python
from autonomous.autonomous_executor_v2 import AutonomousExecutorV2
import asyncio

async def complete_webapp():
    executor = AutonomousExecutorV2(
        project_id="my_webapp",
        project_path="/home/user/my-webapp"
    )
    
    await executor.initialize()
    
    result = await executor.execute_tasks(
        auto_pr=True,
        checkpoint_interval=5
    )
    
    print(f"Completed: {result['completed']}/{result['total']}")

asyncio.run(complete_webapp())
```

### Example 2: Complete Specific Tasks

```python
from autonomous.task_state_manager import TaskState

tasks = [
    TaskState(
        task_id="add_auth",
        project_id="my_project",
        title="Add user authentication",
        description="Implement JWT-based auth with login/logout",
        priority="high",
        task_type="feature"
    ),
    TaskState(
        task_id="add_dashboard",
        project_id="my_project",
        title="Create admin dashboard",
        description="Build admin panel with user management",
        priority="medium",
        task_type="feature"
    )
]

result = await executor.execute_tasks(tasks=tasks)
```

### Example 3: Parse TODO.md

```python
def parse_todo_md(todo_path: str, project_id: str):
    """Extract incomplete tasks from todo.md"""
    tasks = []
    with open(todo_path, 'r') as f:
        content = f.read()
    
    import re
    matches = re.findall(r'- \[ \] (.+)', content)
    
    for i, task_text in enumerate(matches):
        task = TaskState(
            task_id=f"task_{i+1}",
            project_id=project_id,
            title=task_text[:100],
            description=task_text,
            priority="medium",
            task_type="feature"
        )
        tasks.append(task)
    
    return tasks

# Use it
tasks = parse_todo_md("/path/to/todo.md", "my_project")
result = await executor.execute_tasks(tasks=tasks)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."
export USE_REAL_EXECUTION="true"

# Optional
export LLM_MODEL="claude-sonnet-4-20250514"
export CHECKPOINT_INTERVAL="5"
export AUTO_PR="true"
```

### Configuration File

Create `standalone_config.json`:

```json
{
  "project_id": "unique_project_id",
  "project_path": "/absolute/path/to/project",
  "project_name": "Human Readable Name",
  "auto_pr": true,
  "checkpoint_interval": 5,
  "max_retries": 3,
  "github": {
    "enabled": true,
    "branch_prefix": "agent"
  }
}
```

---

## 📊 Monitoring Progress

### Real-Time Status

```python
status = executor.get_status()

print(f"Project: {status['project_name']}")
print(f"Progress: {status['completed_tasks']}/{status['total_tasks']}")
print(f"Current task: {status['current_task']}")
print(f"Session: {status['session_status']}")
```

### Logs

All execution is logged to:
- `agent_execution_YYYYMMDD_HHMMSS.log` - Main execution log
- `context_storage/` - Project context
- `task_storage/` - Task states
- `session_storage/` - Session checkpoints

---

## 🛡️ Error Handling

The system includes comprehensive error handling:

1. **Network Errors:** Automatic retry with exponential backoff
2. **Git Errors:** Smart recovery and retry
3. **LLM Errors:** Fallback strategies
4. **Task Failures:** Retry up to 3 times, then skip
5. **Session Failures:** Restore from last checkpoint

---

## 🎨 Customization

### Custom Task Types

```python
class CustomTaskType:
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
```

### Custom Priorities

```python
class CustomPriority:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### Custom Execution Logic

Extend `RealExecutor` class:

```python
from autonomous.real_executor import RealExecutor

class MyCustomExecutor(RealExecutor):
    async def execute_task(self, task: TaskState):
        # Your custom logic
        result = await super().execute_task(task)
        # Post-processing
        return result
```

---

## 📈 Performance

**Tested with:**
- Projects up to 15,000 lines of code
- 100+ tasks per project
- Multiple programming languages
- Long-running sessions (hours)

**Typical Performance:**
- Task execution: 2-5 minutes per task
- Context loading: <1 second
- Checkpoint creation: <500ms
- Knowledge graph build: ~30 seconds

---

## 🔐 Security

**Best Practices:**
- Never commit API keys to git
- Use environment variables for secrets
- Review all PRs before merging
- Keep agent in PR-only mode (no direct pushes)

**GitHub Access:**
- Agent creates branches and PRs
- Human approval required for merge
- All changes are reviewable
- Full audit trail maintained

---

## 🚨 Troubleshooting

### Agent won't start

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
pip install anthropic gitpython

# Check API key
echo $ANTHROPIC_API_KEY
```

### Tasks failing

```bash
# Check logs
tail -f agent_execution_*.log

# Check task state
cat task_storage/my_project/task_001.json

# Verify git access
git config --list | grep user
```

### No progress after resume

```bash
# Check session state
cat session_storage/*.json

# Force new session
rm -rf session_storage/
python3 run_standalone_agent.py
```

---

## 📚 API Reference

### AutonomousExecutorV2

```python
class AutonomousExecutorV2:
    def __init__(self, project_id: str, project_path: str)
    async def initialize() -> bool
    async def execute_tasks(
        tasks: list[TaskState] = None,
        auto_pr: bool = True,
        checkpoint_interval: int = 5
    ) -> dict
    def get_status() -> dict
```

### TaskState

```python
class TaskState:
    task_id: str
    project_id: str
    title: str
    description: str
    priority: str
    task_type: str
    status: str
    created_at: float
    started_at: float
    completed_at: float
    result: dict
```

### Session Manager

```python
class SessionManager:
    def create_session(project_id: str, name: str) -> ExecutionSession
    def start_session(session_id: str)
    def pause_session(session_id: str)
    def resume_session(session_id: str)
    def create_checkpoint(session_id: str, context: dict) -> str
    def get_resume_point(project_id: str) -> ExecutionSession
```

---

## 🎯 Next Steps

1. **Test on small project** - Start with something simple
2. **Review PRs carefully** - Verify agent's work
3. **Tune configuration** - Adjust checkpoint interval, priorities
4. **Scale up** - Use on larger projects
5. **Customize** - Extend for your specific needs

---

## 📞 Support

For issues:
1. Check logs: `agent_execution_*.log`
2. Verify configuration: `standalone_config.json`
3. Review documentation: `CONTINUITY_SYSTEM_README.md`
4. Check GitHub: https://github.com/carlvisagie/distributed-ai-agent-complete

---

## 📄 License

MIT License - Use freely for any project

---

**Built for autonomous software development with perfect continuity** 🚀
