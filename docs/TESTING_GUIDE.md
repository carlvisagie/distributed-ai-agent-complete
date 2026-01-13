# Testing Guide - Distributed AI Agent System

## Overview

This guide covers testing strategies for the distributed AI agent system at all levels: unit tests, integration tests, and end-to-end tests.

---

## Test Modes

### 1. Mock Mode (Development/Testing)
- No API key required
- Deterministic responses
- Fast execution (200ms)
- Perfect for CI/CD

### 2. OpenHands Mode (Production)
- Requires Anthropic API key
- Real AI execution
- Variable execution time
- Full feature testing

---

## Quick Test Commands

### Health Checks
```bash
# All services
./test-health.sh

# Individual services
curl http://localhost:8080/health
curl http://localhost:8088/healthz
docker compose exec lenovo-db psql -U agent -d agentops -c "SELECT 1;"
docker compose exec lenovo-redis redis-cli ping
```

### API Tests
```bash
# Create a test run
RUN_ID=$(curl -s -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test task", "workspace": "/tmp/test"}' | jq -r .id)

# Check status
curl http://localhost:8088/v1/runs/$RUN_ID | jq
```

### Chat Interface Test
```bash
# Open in browser
open http://localhost

# Or test with curl
curl -N http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "stream": true}'
```

---

## Unit Tests

### Lenovo Agent-Ops Tests
```bash
cd lenovo
pytest tests/ -v
```

**Test Coverage:**
- API endpoints (healthz, create_run, get_run)
- Database models (Run creation, status updates)
- Runner (mock mode execution)
- Worker (job processing)

### Expected Output:
```
tests/test_api.py::test_healthz PASSED
tests/test_api.py::test_create_run PASSED
tests/test_api.py::test_get_run PASSED
tests/test_api.py::test_get_nonexistent_run PASSED
```

---

## Integration Tests

### Full Stack Test (Mock Mode)
```bash
# Start services
docker compose up -d

# Wait for startup
sleep 10

# Run integration test
python tests/integration_test.py
```

**Test Flow:**
1. Create run via API
2. Verify run is queued
3. Wait for worker to process
4. Verify run succeeded
5. Check result data

### Expected Output:
```
✅ Run created: abc123
✅ Status: queued
✅ Worker processing...
✅ Status: running
✅ Status: succeeded
✅ Result: {"mode": "mock", "summary": "Mock run completed."}
```

---

## End-to-End Tests

### Chat Interface E2E Test
```bash
# Using Playwright or Selenium
npm run test:e2e
```

**Test Scenarios:**
1. Load chat interface
2. Send message
3. Verify typing indicator appears
4. Verify response received
5. Check task status updates
6. Verify completion message

### Manual E2E Test
1. Open http://localhost
2. Type: "Create a Python hello world script"
3. Verify:
   - Typing indicator appears
   - Status updates show
   - Response is received
   - Task completes successfully

---

## Performance Tests

### Load Test (Mock Mode)
```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Run load test
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}' \
  http://localhost:8088/v1/runs
```

**Expected Performance (Mock Mode):**
- Throughput: 50+ req/sec
- P50 latency: <50ms
- P99 latency: <200ms
- Error rate: 0%

### Load Test (OpenHands Mode)
```bash
# Lower concurrency for real AI
hey -n 10 -c 2 -m POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create hello world", "workspace": "/tmp"}' \
  http://localhost:8088/v1/runs
```

**Expected Performance (OpenHands Mode):**
- Throughput: 1-5 req/sec
- P50 latency: 5-30 seconds
- P99 latency: <60 seconds
- Error rate: <5%

---

## Failure Scenario Tests

### 1. Database Failure
```bash
# Stop database
docker compose stop lenovo-db

# Try to create run (should fail)
curl -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}'

# Verify error response
# Expected: 500 Internal Server Error

# Restart database
docker compose start lenovo-db

# Wait for health monitor to detect recovery
sleep 60

# Verify system recovered
curl http://localhost:8088/healthz
```

### 2. Redis Failure
```bash
# Stop Redis
docker compose stop lenovo-redis

# Try to create run
curl -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}'

# Verify graceful degradation
# Expected: Run created but not queued

# Restart Redis
docker compose start lenovo-redis

# Verify recovery
docker compose exec lenovo-redis redis-cli ping
```

### 3. Worker Failure
```bash
# Stop worker
docker compose stop lenovo-worker

# Create run
RUN_ID=$(curl -s -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}' | jq -r .id)

# Verify run stays queued
curl http://localhost:8088/v1/runs/$RUN_ID | jq .status
# Expected: "queued"

# Restart worker
docker compose start lenovo-worker

# Verify run is processed
sleep 5
curl http://localhost:8088/v1/runs/$RUN_ID | jq .status
# Expected: "succeeded"
```

---

## Self-Healing Tests

### Auto-Restart Test
```bash
# Kill a service
docker compose kill lenovo-api

# Watch health monitor logs
docker compose logs -f health-monitor

# Expected behavior:
# 1. Health check fails
# 2. Consecutive failures increment
# 3. After 3 failures, auto-restart triggered
# 4. Service recovers
# 5. Health check passes
```

### Recovery Time Test
```bash
# Measure recovery time
time (docker compose kill lenovo-api && \
      while ! curl -s http://localhost:8088/healthz > /dev/null; do sleep 1; done)

# Expected: <2 minutes
```

---

## OpenHands Mode Tests

### Real AI Execution Test
```bash
# Set environment
export RUNNER_MODE=openhands
export LLM_API_KEY=sk-ant-...
export LLM_MODEL=anthropic/claude-sonnet-4-5-20250929

# Restart services
docker compose restart lenovo-api lenovo-worker

# Create real AI task
RUN_ID=$(curl -s -X POST http://localhost:8088/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python script that prints hello world",
    "workspace": "/tmp/test-workspace"
  }' | jq -r .id)

# Poll for completion
while true; do
  STATUS=$(curl -s http://localhost:8088/v1/runs/$RUN_ID | jq -r .status)
  echo "Status: $STATUS"
  if [ "$STATUS" == "succeeded" ] || [ "$STATUS" == "failed" ]; then
    break
  fi
  sleep 5
done

# Get result
curl http://localhost:8088/v1/runs/$RUN_ID | jq .result
```

### Expected Result:
```json
{
  "mode": "openhands",
  "workspace": "/tmp/test-workspace",
  "prompt": "Create a Python script that prints hello world",
  "artifacts": [
    {
      "type": "file",
      "name": "hello.py",
      "content": "print('Hello, World!')"
    }
  ]
}
```

---

## GitHub PR Workflow Test

### PR Creation Test
```bash
# Set environment
export GITHUB_TOKEN=ghp_...

# Test PR manager
python shared/github_pr_manager.py

# Verify:
# 1. Branch created: agent/{task_id}-{timestamp}
# 2. Changes committed
# 3. Branch pushed
# 4. PR created
# 5. PR URL returned
```

### Manual PR Test
1. Make changes in a test repo
2. Run agent with PR workflow enabled
3. Verify branch created on GitHub
4. Verify PR created with:
   - Proper title: [Agent] Task description
   - Detailed body with task ID
   - Review checklist
5. Verify no direct push to main

---

## Continuous Integration Tests

### CI Pipeline Test
```bash
# Run full CI suite
./ci-test.sh

# Steps:
# 1. Lint code (ruff)
# 2. Run unit tests (pytest)
# 3. Build Docker images
# 4. Start services
# 5. Run integration tests
# 6. Run E2E tests
# 7. Stop services
# 8. Generate coverage report
```

### Expected CI Output:
```
✅ Linting passed
✅ Unit tests: 15/15 passed
✅ Docker build: success
✅ Services started
✅ Integration tests: 8/8 passed
✅ E2E tests: 5/5 passed
✅ Coverage: 85%
```

---

## Troubleshooting Tests

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart services
docker compose restart

# View detailed logs
docker compose logs -f
```

### Test Data Cleanup
```bash
# Clear test database
docker compose exec lenovo-db psql -U agent -d agentops -c "TRUNCATE TABLE runs;"

# Clear Redis queue
docker compose exec lenovo-redis redis-cli FLUSHDB

# Restart worker
docker compose restart lenovo-worker
```

---

## Test Checklist

### Before Deployment
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Load tests meet performance targets
- [ ] Failure scenarios handled gracefully
- [ ] Self-healing works
- [ ] Mock mode works
- [ ] OpenHands mode works (if API key available)
- [ ] PR workflow tested
- [ ] Documentation updated

### After Deployment
- [ ] Health checks pass
- [ ] Services auto-start
- [ ] Logs are clean
- [ ] Database accessible
- [ ] Redis accessible
- [ ] Chat interface loads
- [ ] Can create runs
- [ ] Worker processes jobs
- [ ] Self-healing active

---

## Test Automation

### Automated Test Script
```bash
#!/bin/bash
# tests/run-all-tests.sh

set -e

echo "Running all tests..."

# Unit tests
echo "1. Unit tests..."
cd lenovo && pytest tests/ -v

# Integration tests
echo "2. Integration tests..."
python tests/integration_test.py

# Health checks
echo "3. Health checks..."
./test-health.sh

# Load tests
echo "4. Load tests..."
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "workspace": "/tmp"}' \
  http://localhost:8088/v1/runs

echo "✅ All tests passed!"
```

---

## Performance Benchmarks

### Target Metrics
- **API Response Time**: <100ms (P95)
- **Task Creation**: <50ms
- **Worker Throughput**: 10+ tasks/min (mock mode)
- **Database Queries**: <10ms (P95)
- **Redis Operations**: <5ms (P95)
- **Self-Healing Recovery**: <2 minutes
- **System Uptime**: >99.9%

---

**Test early, test often, test everything!** 🧪✅
