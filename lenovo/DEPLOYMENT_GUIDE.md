# Agent Ops Deployment Guide

## Three-Machine Architecture

### HP OMEN (Orchestrator)
- **Role**: Command center, task coordination
- **Port**: 8080 (FastAPI)
- **Access**: Local network only

### Predator Helios (AI Brain/Worker)
- **Role**: AI agent execution, OpenHands SDK
- **Port**: 9000 (WebSocket)
- **OS**: Windows 11 with Docker Desktop + WSL2
- **Access**: VPN-only (no public exposure)

### Lenovo (Production Server)
- **Role**: PostgreSQL, Redis, deployed apps, backups
- **OS**: Ubuntu Server LTS
- **Access**: SSH key-only, firewall hardened

---

## Quick Start: Lenovo Ubuntu Server Setup

### Prerequisites
1. Install Ubuntu Server LTS with OpenSSH enabled
2. Create admin user during installation
3. Boot and login locally

### One-Command Setup
```bash
sudo -i
# Then run the script in scripts/ubuntu_server_setup.sh
```

**The script will:**
- ✅ Harden SSH (key-only, no root, no passwords)
- ✅ Enable UFW firewall (deny all incoming except SSH)
- ✅ Install fail2ban (SSH brute-force protection)
- ✅ Enable automatic security updates
- ✅ Install Docker Engine + Compose plugin
- ✅ Configure static IP (optional, via Netplan)
- ✅ Create /srv/stacks, /srv/data, /srv/backups directories

### Validation Checklist
```bash
# 1. SSH hardening
sudo sshd -T | egrep 'passwordauthentication|permitrootlogin|pubkeyauthentication'
# Expected: passwordauthentication no, permitrootlogin no, pubkeyauthentication yes

# 2. Firewall active
sudo ufw status verbose
# Expected: Status active, only 22/tcp allowed

# 3. Fail2ban running
sudo fail2ban-client status sshd

# 4. Docker working
docker version
docker compose version
docker run --rm hello-world

# 5. Static IP (if configured)
ip -br addr
ip route
```

---

## Quick Start: Predator Helios Windows Setup

### Prerequisites
1. Windows 11/10 Pro
2. BIOS: Enable Virtualization (Intel VT-x)
3. Run PowerShell as Administrator

### One-Command Setup
```powershell
# Run the script in scripts/windows_server_setup.ps1
```

**The script will:**
- ✅ Disable sleep/hibernate (server mode)
- ✅ Enable Remote Desktop (RDP)
- ✅ Enable OpenSSH Server
- ✅ Enable WSL2 + Virtual Machine Platform
- ✅ Create service user (svc_agentops)
- ✅ Configure firewall rules

**After reboot:**
1. Install Docker Desktop (WSL2 backend)
2. Configure static IP (optional, use scripts/windows_set_static_ip.ps1)

---

## Deploy Agent Ops Stack

### On Lenovo (Production Server)

1. **Copy agent-ops to server:**
```bash
scp -r AGENT_OPS_BACKUP/ user@lenovo:/srv/stacks/agent-ops
```

2. **Create .env file:**
```bash
cd /srv/stacks/agent-ops
cp .env.example .env
nano .env
```

**Required environment variables:**
```env
ENV=production
DATABASE_URL=postgresql://agent:agent@db:5432/agentops
REDIS_URL=redis://redis:6379/0
RUNNER_MODE=openhands
LLM_MODEL=anthropic/claude-sonnet-4-5-20250929
LLM_API_KEY=your_anthropic_key_here
LLM_BASE_URL=https://api.anthropic.com/v1
```

3. **Start services:**
```bash
docker compose up -d
```

4. **Verify services:**
```bash
docker compose ps
docker compose logs -f api
curl http://localhost:8088/healthz
```

---

## Architecture Details

### API Server (Port 8088)
- **POST /v1/runs**: Create new agent task
- **GET /v1/runs/{id}**: Check task status
- **GET /healthz**: Health check

### Worker (Background)
- Processes tasks from Redis queue
- Executes via OpenHands SDK (real AI) or mock mode (testing)
- Updates PostgreSQL with results

### Database (PostgreSQL 16.6)
- **Port**: 54328 (external), 5432 (internal)
- **Tables**: runs (id, status, spec_json, result_json, error)

### Queue (Redis 7.4.2)
- **Port**: 63798 (external), 6379 (internal)
- **Queue name**: default

---

## Testing

### Mock Mode (No API Key Required)
```bash
# In .env
RUNNER_MODE=mock

# Test API
curl -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test task", "workspace": "/tmp/test"}'

# Check status
curl http://localhost:8088/v1/runs/{run_id}
```

### OpenHands Mode (Real AI)
```bash
# In .env
RUNNER_MODE=openhands
LLM_API_KEY=sk-ant-...

# Test real agent execution
curl -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python hello world script", "workspace": "/tmp/workspace"}'
```

---

## Security Best Practices

### Network Isolation
- ✅ Helios: No public exposure, VPN-only access
- ✅ Lenovo: SSH key-only, firewall hardened
- ✅ Agent API: Bind to 127.0.0.1 or VPN interface only

### Secrets Management
- ✅ Store secrets in .env files (never commit to git)
- ✅ Use environment variables for all credentials
- ✅ Rotate API keys regularly

### PR-Only Workflow
- ✅ Agents create branches and PRs
- ✅ Never push directly to production
- ✅ Human approval required for merges
- ✅ CI/CD deploys only after merge

---

## Backup Strategy

### Automated Backups (Lenovo)
```bash
# Add to crontab
0 2 * * * /srv/stacks/agent-ops/scripts/backup.sh
```

**Backup script should:**
- Dump PostgreSQL database
- Archive /srv/data volumes
- Copy to /srv/backups with timestamp
- Sync to external drive or NAS

---

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8088/healthz

# Database connection
docker compose exec db psql -U agent -d agentops -c "SELECT 1;"

# Redis connection
docker compose exec redis redis-cli ping

# Worker status
docker compose logs worker --tail=50
```

### Service Restart
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart api
docker compose restart worker
```

---

## Troubleshooting

### API not responding
```bash
docker compose logs api
docker compose restart api
```

### Worker not processing tasks
```bash
docker compose logs worker
# Check Redis connection
docker compose exec redis redis-cli ping
# Check queue
docker compose exec redis redis-cli llen rq:queue:default
```

### Database connection errors
```bash
docker compose logs db
docker compose exec db psql -U agent -d agentops
```

### OpenHands execution errors
```bash
# Check LLM_API_KEY is set
docker compose exec api env | grep LLM
# Check OpenHands logs
docker compose logs worker | grep openhands
```

---

## Next Steps

1. ✅ Complete Lenovo Ubuntu setup
2. ✅ Complete Helios Windows setup
3. ✅ Deploy agent-ops stack to Lenovo
4. ✅ Test mock mode end-to-end
5. ✅ Configure Anthropic API key
6. ✅ Test OpenHands mode with real AI
7. ✅ Set up automated backups
8. ✅ Configure VPN access (WireGuard)
9. ✅ Build chat interface on top of API
10. ✅ Integrate with GitHub for PR workflow

---

## Support

For issues or questions:
1. Check logs: `docker compose logs`
2. Verify environment variables: `.env` file
3. Test connectivity: health checks
4. Review OpenHands SDK docs: https://github.com/All-Hands-AI/OpenHands
