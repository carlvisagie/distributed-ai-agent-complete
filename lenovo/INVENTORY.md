# Agent Ops Complete System Inventory

## 📦 Complete File List

### Core Application Files
```
agent_ops/
├── __init__.py          # Package initialization
├── api.py               # FastAPI server (POST /v1/runs, GET /v1/runs/{id})
├── config.py            # Pydantic settings (alias for settings.py)
├── database.py          # SQLAlchemy session management (alias for db.py)
├── db.py                # Database session factory
├── models.py            # SQLAlchemy Run model with status tracking
├── queue.py             # Redis Queue connection
├── runner.py            # Task execution engine (mock + OpenHands modes)
├── settings.py          # Environment configuration
└── worker.py            # RQ worker for background job processing
```

### Infrastructure Files
```
Dockerfile               # Python 3.12-slim with git and SSH
docker-compose.yml       # 4 services: api, worker, db (PostgreSQL 16.6), redis (7.4.2)
pyproject.toml           # Python dependencies with OpenHands SDK
.env.example             # Environment variable template
README.md                # Project documentation
```

### Setup Scripts
```
scripts/
├── ubuntu_server_setup.sh       # Production-grade Ubuntu baseline (SSH, Docker, firewall)
├── windows_server_setup.ps1     # Windows server baseline (RDP, SSH, WSL2, Docker)
└── windows_set_static_ip.ps1    # Windows static IP configuration
```

### Tests
```
tests/
├── __init__.py
└── test_api.py          # API endpoint tests (healthz, create_run, get_run)
```

### Documentation
```
DEPLOYMENT_GUIDE.md      # Complete deployment instructions for all three machines
INVENTORY.md             # This file - complete system inventory
```

---

## 🏗️ Architecture Components

### 1. FastAPI Server (api.py)
**Port**: 8088  
**Endpoints**:
- `GET /healthz` - Health check
- `POST /v1/runs` - Create new agent task
- `GET /v1/runs/{id}` - Get task status and results

**Features**:
- Automatic database table creation
- Request validation with Pydantic
- Background job queuing with RQ
- JSON serialization for specs and results

### 2. RQ Worker (worker.py)
**Function**: Background job processor  
**Responsibilities**:
- Poll Redis queue for new tasks
- Execute tasks via runner.py
- Update database with results
- Handle errors with full traceback

**State Machine**:
```
queued → running → succeeded/failed
```

### 3. Task Runner (runner.py)
**Modes**:
- **mock**: Deterministic testing (no API key required)
- **openhands**: Real AI execution with Claude Sonnet 4.5

**OpenHands Integration**:
- LLM: Anthropic Claude Sonnet 4.5
- Tools: Terminal, FileEditor, TaskTracker
- Workspace: Isolated directory per task
- Conversation: Multi-turn agent interaction

### 4. Database (PostgreSQL 16.6)
**Tables**:
```sql
runs (
  id VARCHAR(36) PRIMARY KEY,
  created_utc TIMESTAMP,
  status VARCHAR(16),
  spec_json TEXT,
  result_json TEXT,
  error TEXT
)
```

**Connection**:
- Pool pre-ping enabled (auto-reconnect)
- Session management with context manager
- Automatic rollback on errors

### 5. Queue (Redis 7.4.2)
**Queue Name**: default  
**Job Format**: `agent_ops.worker.execute_run(run_id)`  
**Features**:
- Persistent job storage
- Automatic retry on worker failure
- Job result TTL

---

## 🔧 Technology Stack

### Backend
- **FastAPI** 0.128.0 - Modern async web framework
- **Uvicorn** 0.40.0 - ASGI server
- **Pydantic** 2.12.5 - Data validation
- **SQLAlchemy** 2.0.45 - ORM
- **psycopg** 3.2.9 - PostgreSQL driver
- **Redis** 7.1.0 - In-memory data store
- **RQ** 2.6.1 - Background job queue

### AI Agent
- **OpenHands SDK** 0.4.2 - Software agent framework
- **OpenHands Tools** 0.4.2 - Terminal, FileEditor, TaskTracker
- **Anthropic Claude** Sonnet 4.5 - LLM

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** 16.6 - Production database
- **Redis** 7.4.2 - Job queue backend

### Testing
- **pytest** 8.3.4 - Test framework
- **pytest-asyncio** 0.25.2 - Async test support
- **requests** 2.32.3 - HTTP client for tests

---

## 🌐 Network Architecture

### Port Mapping
```
Service         Internal    External    Purpose
---------------------------------------------------------
API             8088        8088        HTTP API
Database        5432        54328       PostgreSQL
Redis           6379        63798       Queue backend
```

### Security Model
```
HP OMEN (Orchestrator)
  ↓ HTTP (local network)
Predator Helios (Worker)
  ↓ PostgreSQL/Redis (VPN)
Lenovo (Server)
  ↑ SSH (key-only)
```

---

## 📋 Environment Variables

### Required (All Modes)
```env
ENV=dev|production
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db
```

### Optional (Mock Mode)
```env
RUNNER_MODE=mock
LOG_LEVEL=INFO
RQ_QUEUE=default
```

### Required (OpenHands Mode)
```env
RUNNER_MODE=openhands
LLM_MODEL=anthropic/claude-sonnet-4-5-20250929
LLM_API_KEY=sk-ant-...
LLM_BASE_URL=https://api.anthropic.com/v1
```

---

## 🚀 Deployment Targets

### Development (Local)
```bash
docker compose up
# API: http://localhost:8088
# DB: localhost:54328
# Redis: localhost:63798
```

### Production (Three Machines)

**Lenovo (Ubuntu Server)**:
- PostgreSQL 16.6 (persistent data)
- Redis 7.4.2 (job queue)
- API server (port 8088)
- Worker (background)

**Predator Helios (Windows + Docker)**:
- Development environment
- Fast iteration
- VPN-only access

**HP OMEN (Orchestrator)**:
- Command center
- Task coordination
- Local network only

---

## 🔐 Security Features

### SSH Hardening (Ubuntu)
- ✅ Key-based authentication only
- ✅ Password login disabled
- ✅ Root login disabled
- ✅ Fail2ban enabled (5 retries, 1-hour ban)

### Firewall (Ubuntu)
- ✅ UFW enabled
- ✅ Default deny incoming
- ✅ Only SSH (22/tcp) allowed by default

### Windows Security
- ✅ RDP enabled with firewall rules
- ✅ OpenSSH server enabled
- ✅ Service user created (svc_agentops)
- ✅ Sleep/hibernate disabled

### Application Security
- ✅ Secrets in .env files (never committed)
- ✅ Database connection pooling
- ✅ Input validation with Pydantic
- ✅ Error handling with rollback

---

## 📊 Monitoring & Observability

### Health Checks
```bash
# API health
curl http://localhost:8088/healthz

# Database
docker compose exec db psql -U agent -d agentops -c "SELECT COUNT(*) FROM runs;"

# Redis
docker compose exec redis redis-cli ping

# Worker
docker compose logs worker --tail=50
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f worker

# Filter by time
docker compose logs --since 1h api
```

### Metrics
- Run count by status
- Average execution time
- Error rate
- Queue depth

---

## 🧪 Testing Strategy

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Start services
docker compose up -d

# Run tests
pytest tests/test_api.py

# Cleanup
docker compose down
```

### End-to-End Tests
```bash
# Create run
RUN_ID=$(curl -s -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}' | jq -r .id)

# Check status
curl http://localhost:8088/v1/runs/$RUN_ID
```

---

## 📚 Additional Resources

### OpenHands SDK
- GitHub: https://github.com/All-Hands-AI/OpenHands
- Docs: https://docs.all-hands.dev/
- Tools: Terminal, FileEditor, TaskTracker

### Anthropic Claude
- API Docs: https://docs.anthropic.com/
- Model: claude-sonnet-4-5-20250929
- Rate Limits: Check dashboard

### Docker
- Compose Docs: https://docs.docker.com/compose/
- Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

## ✅ Verification Checklist

### Pre-Deployment
- [ ] All files present (see file list above)
- [ ] .env file created from .env.example
- [ ] Secrets configured (DATABASE_URL, REDIS_URL, LLM_API_KEY)
- [ ] Docker and Docker Compose installed

### Post-Deployment
- [ ] All containers running (`docker compose ps`)
- [ ] Health check passes (`curl /healthz`)
- [ ] Database accessible
- [ ] Redis accessible
- [ ] Worker processing jobs
- [ ] Mock mode tested
- [ ] OpenHands mode tested (if API key provided)

### Security
- [ ] SSH key-only authentication
- [ ] Firewall enabled
- [ ] Fail2ban active
- [ ] No public exposure of agent API
- [ ] Secrets not in git

---

## 🎯 Success Criteria

**System is production-ready when:**
1. ✅ All services start automatically
2. ✅ Health checks pass
3. ✅ Mock mode executes tasks successfully
4. ✅ OpenHands mode executes real AI tasks
5. ✅ Database persists data across restarts
6. ✅ Worker recovers from failures
7. ✅ Logs are accessible and readable
8. ✅ Security hardening complete
9. ✅ Backups configured
10. ✅ Monitoring in place

---

**Last Updated**: 2026-01-13  
**Version**: 1.0.0  
**Status**: Production-Ready ✅
