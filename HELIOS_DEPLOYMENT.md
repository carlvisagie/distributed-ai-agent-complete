# Helios Deployment Guide

## Cost-Optimized Autonomous Agent for Production Use

**Target Cost:** <$1 per task (70-90% reduction from $5-10)

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/carlvisagie/distributed-ai-agent-complete.git
cd distributed-ai-agent-complete

# Install dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run cost-optimized agent
python3 examples/run_cost_optimized.py
```

---

## Cost Optimization Features

### 1. **Prompt Caching** (90% discount)
- Project structure cached for 5 minutes
- Reused across multiple tasks
- **Savings:** $3-5 per task

### 2. **Model Tiering** (10x cheaper)
- **Haiku** ($0.25/M tokens): Analysis, validation, retries
- **Sonnet** ($3/M tokens): Complex code generation only
- **Savings:** $2-3 per task

### 3. **Batch Operations** (fewer API calls)
- Generate ALL edits in one call
- No separate calls per file
- **Savings:** $1-2 per task

### 4. **Smart Retries** (avoid wasted calls)
- Only retry fixable errors (imports, types)
- Skip unfixable errors (logic issues)
- **Savings:** $1-2 per task

### 5. **Aggressive Limits** (minimal context)
- 50 files max (vs 100)
- 1.5K per file (vs 2K)
- **Savings:** $0.50 per task

---

## Usage Examples

### Basic Task Execution

```python
from shared.autonomous.cost_optimized_agent import CostOptimizedAgent

agent = CostOptimizedAgent(
    workspace_path="/path/to/project",
    cost_limit=10.0  # Stop after $10
)

task = {
    "id": "TASK_001",
    "title": "Add user authentication",
    "requirements": """
    Add login/logout endpoints to server/routers.ts
    Use JWT tokens for session management
    """
}

result = agent.execute_task(task)

print(f"Status: {result['status']}")
print(f"Cost: ${result['cost']:.2f}")
print(f"Success Rate: {result['success_rate']*100:.0f}%")

# Get detailed cost report
report = agent.get_cost_report()
print(f"Session Cost: ${report['session_cost']:.2f}")
print(f"Tokens Saved: {report['tokens_saved']:,}")
```

### Multi-Task Session with Cost Tracking

```python
agent = CostOptimizedAgent(
    workspace_path="/path/to/project",
    cost_limit=5.0  # $5 budget
)

tasks = [
    {"id": "T1", "title": "Add database schema", "requirements": "..."},
    {"id": "T2", "title": "Add API endpoints", "requirements": "..."},
    {"id": "T3", "title": "Add validation", "requirements": "..."}
]

for task in tasks:
    result = agent.execute_task(task)
    
    print(f"\nTask {task['id']}: {result['status']}")
    print(f"Cost: ${result['cost']:.2f}")
    
    # Check if approaching limit
    report = agent.get_cost_report()
    if report['remaining_budget'] < 1.0:
        print(f"⚠️  Low budget: ${report['remaining_budget']:.2f} remaining")
        break

# Final report
report = agent.get_cost_report()
print(f"\n📊 SESSION SUMMARY")
print(f"Total Cost: ${report['session_cost']:.2f}")
print(f"API Calls: {report['api_calls']}")
print(f"Cached Calls: {report['cached_calls']}")
print(f"Tokens Saved: {report['tokens_saved']:,}")
print(f"Avg Cost/Call: ${report['average_cost_per_call']:.4f}")
```

---

## Cost Comparison

| Feature | Old Agent | Cost-Optimized | Savings |
|---------|-----------|----------------|---------|
| **Analysis** | Sonnet ($3/M) | Haiku + Cache ($0.03/M) | 99% |
| **Generation** | Sonnet ($3/M) | Sonnet ($3/M) | 0% |
| **Validation** | Sonnet ($3/M) | Haiku ($0.25/M) | 92% |
| **Retries** | Sonnet ($3/M) | Haiku + Smart ($0.25/M) | 92% |
| **Context** | 100 files × 2K | 50 files × 1.5K | 62% |
| **Total/Task** | $5-10 | <$1 | **70-90%** |

---

## Production Deployment

### 1. **Environment Setup**

```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your-key-here
COST_LIMIT=10.0
WORKSPACE_PATH=/path/to/project
EOF

# Load environment
source .env
```

### 2. **Run as Service**

```bash
# Create systemd service
sudo tee /etc/systemd/system/ai-agent.service << EOF
[Unit]
Description=Cost-Optimized AI Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/distributed-ai-agent-complete
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/usr/bin/python3 server/agent_service.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable ai-agent
sudo systemctl start ai-agent
sudo systemctl status ai-agent
```

### 3. **Monitor Costs**

```bash
# View real-time costs
tail -f /var/log/ai-agent/costs.log

# Daily cost report
python3 scripts/cost_report.py --date today

# Set alerts
python3 scripts/cost_alerts.py --threshold 50.0
```

---

## Best Practices

### Cost Management

1. **Set Cost Limits**
   ```python
   agent = CostOptimizedAgent(cost_limit=5.0)  # Stop at $5
   ```

2. **Monitor Per-Task Costs**
   ```python
   if result['cost'] > 2.0:
       logger.warning(f"Expensive task: ${result['cost']:.2f}")
   ```

3. **Use Batch Operations**
   ```python
   # Good: Process multiple related tasks together
   tasks = get_related_tasks()
   for task in tasks:
       agent.execute_task(task)  # Reuses cached context
   
   # Bad: Process unrelated tasks (cache misses)
   ```

4. **Review Cost Reports**
   ```python
   report = agent.get_cost_report()
   for call in report['call_breakdown']:
       if call['cost'] > 0.50:
           print(f"Expensive call: {call}")
   ```

### Performance Optimization

1. **Cache Warm-Up**
   ```python
   # Warm up cache before processing tasks
   agent._get_cached_project_map()
   ```

2. **Batch Similar Tasks**
   ```python
   # Group tasks by file to maximize cache hits
   tasks_by_file = group_tasks_by_affected_files(tasks)
   for file_group in tasks_by_file:
       for task in file_group:
           agent.execute_task(task)
   ```

3. **Limit Context**
   ```python
   # Only include essential files in task requirements
   task = {
       "requirements": "Modify server/routers.ts only",
       # Not: "Review entire codebase and modify..."
   }
   ```

---

## Troubleshooting

### High Costs

**Problem:** Task costs >$2

**Solutions:**
1. Check if retrying too many times
2. Reduce file context (fewer files, shorter content)
3. Use more specific task requirements
4. Review call breakdown for expensive operations

### Cache Misses

**Problem:** Not seeing cache savings

**Solutions:**
1. Process related tasks together
2. Increase cache TTL (default 5 min)
3. Warm up cache before batch processing

### Low Success Rate

**Problem:** Many edits failing

**Solutions:**
1. Make task requirements more specific
2. Include relevant file context
3. Check if errors are fixable (smart retry logic)

---

## Monitoring Dashboard

### Real-Time Metrics

```python
# Get live metrics
metrics = agent.metrics

print(f"Tasks Completed: {metrics['tasks_completed']}")
print(f"Total Cost: ${metrics['total_cost']:.2f}")
print(f"API Calls: {metrics['api_calls']}")
print(f"Cached Calls: {metrics['cached_calls']} ({metrics['cached_calls']/metrics['api_calls']*100:.0f}%)")
print(f"Tokens Saved: {metrics['tokens_saved']:,}")
```

### Cost Alerts

```python
def check_cost_alerts(agent):
    report = agent.get_cost_report()
    
    if report['session_cost'] > report['cost_limit'] * 0.8:
        send_alert(f"⚠️  80% of budget used: ${report['session_cost']:.2f}")
    
    if report['average_cost_per_call'] > 0.50:
        send_alert(f"⚠️  High per-call cost: ${report['average_cost_per_call']:.2f}")
```

---

## Next Steps

1. **Test on Helios** with real API key
2. **Monitor costs** for first 10 tasks
3. **Adjust limits** based on actual usage
4. **Scale up** once costs are validated

**Expected Performance:**
- **Speed:** 15-30s per task
- **Cost:** $0.50-1.00 per task
- **Success Rate:** 60-80%
- **Daily Budget:** $20-50 for 20-50 tasks

---

## Support

- **GitHub:** https://github.com/carlvisagie/distributed-ai-agent-complete
- **Issues:** Report cost anomalies or optimization ideas
- **Docs:** See PRODUCTION_AGENT_V2.md for technical details
