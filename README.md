# 🤖 Distributed AI Agent System

**Production-ready distributed AI agent system with three-machine architecture, real-time chat interface, OpenHands SDK integration, and self-healing infrastructure.**

---

## 🏗️ Architecture

### Three-Machine Design

```
┌─────────────────┐
│   HP OMEN       │  Command Center (Port 8080)
│  Orchestrator   │  - Coordinates tasks
│                 │  - SSE streaming to frontend
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
┌────────▼────────┐  ┌──────▼──────────┐
│ Predator Helios │  │    Lenovo       │
│   AI Worker     │  │ Production      │
│  (Port 9000)    │  │   Server        │
│                 │  │                 │
│ - WebSocket     │  │ - PostgreSQL    │
│ - OpenHands SDK │  │ - Redis Queue   │
│ - Claude AI     │  │ - Agent API     │
└─────────────────┘  │ - Worker        │
                     │ - Backups       │
                     └─────────────────┘
```

### Components

1. **HP OMEN (Orchestrator)**
   - FastAPI server on port 8080
   - Coordinates between chat interface and worker
   - Server-Sent Events (SSE) for real-time streaming
   - Task creation and status polling

2. **Predator Helios (AI Brain)**
   - WebSocket worker on port 9000
   - OpenHands SDK integration
   - Claude Sonnet 4.5 execution
   - Runs on Windows with Docker Desktop + WSL2

3. **Lenovo (Production Server)**
   - PostgreSQL 16.6 (persistent storage)
   - Redis 7.4.2 (job queue)
   - FastAPI API server (port 8088)
   - RQ background worker
   - Ubuntu Server LTS

4. **Frontend (Chat Interface)**
   - Real-time chat UI
   - SSE streaming for live updates
   - Responsive design
   - Served on port 80

5. **Health Monitor (Self-Healing)**
   - Monitors all services every 30 seconds
   - Auto-restarts failed components
   - Tracks failure counts and recovery

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed on all machines
- **Ubuntu Server LTS** on Lenovo (or Windows with WSL2)
- **Windows 11/10 Pro** on Predator Helios (optional, can run on Lenovo)
- **Anthropic API key** (for OpenHands mode)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/distributed-ai-agent-system.git
cd distributed-ai-agent-system
```

2. **Configure environment:**
```bash
cp .env.example .env
nano .env
```

**Required settings:**
```env
RUNNER_MODE=openhands
LLM_MODEL=anthropic/claude-sonnet-4-5-20250929
LLM_API_KEY=your_anthropic_key_here
```

3. **Start all services:**
```bash
docker compose up -d
```

4. **Verify services:**
```bash
docker compose ps
curl http://localhost:8080/health
curl http://localhost:8088/healthz
```

5. **Open chat interface:**
```
http://localhost
```

---

## 📋 Service Endpoints

| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| Frontend | 80 | http://localhost | Chat interface |
| HP OMEN | 8080 | http://localhost:8080/health | Orchestrator health |
| Lenovo API | 8088 | http://localhost:8088/healthz | Agent API health |
| PostgreSQL | 54328 | localhost:54328 | Database |
| Redis | 63798 | localhost:63798 | Queue |

---

## 🧪 Testing

### Mock Mode (No API Key)

```bash
# Set in .env
RUNNER_MODE=mock

# Test via API
curl -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test task", "workspace": "/tmp/test"}'

# Check status
curl http://localhost:8088/v1/runs/{run_id}
```

### OpenHands Mode (Real AI)

```bash
# Set in .env
RUNNER_MODE=openhands
LLM_API_KEY=sk-ant-...

# Test via chat interface
# Open http://localhost and type: "Create a Python hello world script"
```

---

## 🔐 Security Features

### SSH Hardening (Ubuntu)
- ✅ Key-based authentication only
- ✅ Password login disabled
- ✅ Root login disabled
- ✅ Fail2ban enabled

### Firewall (Ubuntu)
- ✅ UFW enabled
- ✅ Default deny incoming
- ✅ Only required ports open

### Application Security
- ✅ Secrets in .env files
- ✅ No secrets in git
- ✅ Database connection pooling
- ✅ Input validation

### PR-Only Workflow
- ✅ Agents create branches and PRs
- ✅ Never push directly to production
- ✅ Human approval required
- ✅ CI/CD deploys after merge

---

## 🛠️ GitHub PR Workflow

The system includes automated PR creation:

```python
from shared.github_pr_manager import GitHubPRManager

manager = GitHubPRManager(repo_path="/path/to/repo")

pr_url = manager.agent_workflow(
    task_id="abc123",
    task_description="Add user authentication",
    changes_summary="- Added login/logout\n- JWT auth\n- User model"
)
```

**Workflow:**
1. Agent creates branch: `agent/{task_id}-{timestamp}`
2. Commits changes with detailed message
3. Pushes to remote
4. Creates PR with review checklist
5. Human reviews and approves
6. CI/CD deploys after merge

---

## 🏥 Self-Healing Infrastructure

The health monitor automatically:
- Checks all services every 30 seconds
- Tracks consecutive failures
- Auto-restarts after 3 failures
- Logs all recovery attempts

**View health status:**
```bash
docker compose logs health-monitor
```

---

## 📊 Monitoring

### Service Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f hp-omen
docker compose logs -f lenovo-api
docker compose logs -f lenovo-worker
```

### Health Checks
```bash
# HP OMEN
curl http://localhost:8080/health

# Lenovo API
curl http://localhost:8088/healthz

# Database
docker compose exec lenovo-db psql -U agent -d agentops -c "SELECT COUNT(*) FROM runs;"

# Redis
docker compose exec lenovo-redis redis-cli ping
```

---

## 🔧 Troubleshooting

### Services not starting
```bash
docker compose down
docker compose up -d
docker compose ps
```

### Database connection errors
```bash
docker compose logs lenovo-db
docker compose restart lenovo-db
```

### Worker not processing tasks
```bash
docker compose logs lenovo-worker
docker compose exec lenovo-redis redis-cli llen rq:queue:default
```

### OpenHands execution errors
```bash
# Check API key
docker compose exec lenovo-api env | grep LLM

# Check logs
docker compose logs lenovo-worker | grep openhands
```

---

## 📁 Project Structure

```
distributed-ai-agent-system/
├── hp_omen/                    # Orchestrator service
│   ├── orchestrator.py         # FastAPI server with SSE
│   ├── Dockerfile
│   └── requirements.txt
├── predator_helios/            # AI worker service
│   ├── worker.py               # WebSocket worker
│   ├── Dockerfile
│   └── requirements.txt
├── lenovo/                     # Production server
│   ├── agent_ops/              # Agent-ops backend
│   │   ├── api.py              # FastAPI API
│   │   ├── worker.py           # RQ worker
│   │   ├── runner.py           # OpenHands integration
│   │   ├── models.py           # Database models
│   │   └── ...
│   ├── scripts/                # Setup scripts
│   │   ├── ubuntu_server_setup.sh
│   │   ├── windows_server_setup.ps1
│   │   └── windows_set_static_ip.ps1
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── pyproject.toml
├── frontend/                   # Chat interface
│   └── index.html              # Real-time chat UI
├── shared/                     # Shared utilities
│   ├── github_pr_manager.py    # PR automation
│   └── health_monitor.py       # Self-healing
├── docs/                       # Documentation
├── docker-compose.yml          # Master orchestration
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## 🎯 Features

### ✅ Core Features
- Real-time chat interface with SSE streaming
- Distributed three-machine architecture
- OpenHands SDK integration
- Claude Sonnet 4.5 AI execution
- PostgreSQL persistent storage
- Redis job queue
- Background worker processing

### ✅ Production Features
- Self-healing infrastructure
- Health monitoring
- Auto-restart on failure
- GitHub PR automation
- PR-only workflow (no direct pushes)
- Comprehensive logging
- Docker orchestration

### ✅ Security Features
- SSH hardening
- Firewall configuration
- Secrets management
- Input validation
- Database connection pooling
- No secrets in git

---

## 📚 Documentation

- [Deployment Guide](lenovo/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [System Inventory](lenovo/INVENTORY.md) - Comprehensive architecture details
- [Setup Scripts](lenovo/scripts/) - Production-grade server setup

---

## 🤝 Contributing

This is a production system. All changes must go through PR workflow:

1. Create branch: `feature/your-feature`
2. Make changes
3. Test locally
4. Create PR
5. Wait for review
6. Merge after approval

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **OpenHands SDK** - Software agent framework
- **Anthropic Claude** - AI language model
- **FastAPI** - Modern web framework
- **PostgreSQL** - Reliable database
- **Redis** - Fast queue backend

---

## 📞 Support

For issues or questions:
1. Check logs: `docker compose logs`
2. Verify environment: `.env` file
3. Test connectivity: health checks
4. Review documentation

---

**Built with ❤️ for production AI agent deployment**

**Version**: 1.0.0  
**Status**: Production-Ready ✅
