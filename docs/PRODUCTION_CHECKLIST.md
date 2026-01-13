# Production Deployment Checklist

## Pre-Deployment

### Infrastructure
- [ ] Ubuntu Server LTS installed on Lenovo
- [ ] Docker and Docker Compose installed
- [ ] Static IP configured (or DHCP reservation)
- [ ] SSH key-based authentication enabled
- [ ] Password authentication disabled
- [ ] UFW firewall enabled
- [ ] Fail2ban configured
- [ ] Automatic security updates enabled

### Network
- [ ] Ports opened in firewall:
  - [ ] 22 (SSH)
  - [ ] 80 (HTTP - Frontend)
  - [ ] 8080 (HP OMEN API)
  - [ ] 8088 (Lenovo API)
- [ ] DNS records configured (if using custom domain)
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] VPN configured for Helios access (optional)

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `RUNNER_MODE` set correctly (mock or openhands)
- [ ] `LLM_API_KEY` configured (if using openhands)
- [ ] `LLM_MODEL` set to correct model
- [ ] `GITHUB_TOKEN` configured (for PR workflow)
- [ ] Database credentials secured
- [ ] Redis password set (if needed)

### Security
- [ ] All secrets in `.env` file (not in code)
- [ ] `.env` file not committed to git
- [ ] `.gitignore` includes `.env`
- [ ] SSH keys generated and distributed
- [ ] GitHub deploy keys configured
- [ ] API keys rotated regularly (documented)
- [ ] Backup encryption enabled

---

## Deployment

### Build and Start
- [ ] Repository cloned to server
- [ ] Docker images built successfully
- [ ] All services started with `docker compose up -d`
- [ ] No errors in startup logs

### Service Verification
- [ ] HP OMEN health check passes
- [ ] Lenovo API health check passes
- [ ] PostgreSQL accessible
- [ ] Redis accessible
- [ ] Frontend loads in browser
- [ ] Health monitor running

### Functional Testing
- [ ] Can create task via API
- [ ] Worker processes tasks
- [ ] Task status updates correctly
- [ ] Results stored in database
- [ ] Chat interface works
- [ ] SSE streaming works
- [ ] Error handling works

### Performance Testing
- [ ] API response time acceptable (<100ms)
- [ ] Task creation fast (<50ms)
- [ ] Worker throughput adequate
- [ ] Database queries optimized
- [ ] No memory leaks observed
- [ ] CPU usage reasonable

---

## Post-Deployment

### Monitoring Setup
- [ ] Health monitor active
- [ ] Log aggregation configured
- [ ] Metrics collection enabled
- [ ] Alerting configured
- [ ] Dashboard accessible

### Backup Configuration
- [ ] Database backup script created
- [ ] Backup schedule configured (cron)
- [ ] Backup storage location set
- [ ] Backup retention policy defined
- [ ] Restore procedure tested

### Documentation
- [ ] Deployment documented
- [ ] Runbook created
- [ ] Troubleshooting guide updated
- [ ] Contact information recorded
- [ ] Escalation procedures defined

---

## Ongoing Maintenance

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify backups completed

### Weekly
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Update dependencies (if needed)
- [ ] Test backup restore

### Monthly
- [ ] Security audit
- [ ] Rotate API keys
- [ ] Review access logs
- [ ] Update documentation
- [ ] Capacity planning review

---

## Rollback Plan

### Preparation
- [ ] Previous version tagged in git
- [ ] Database backup before deployment
- [ ] Rollback script tested
- [ ] Downtime window communicated

### Rollback Steps
1. [ ] Stop current services
2. [ ] Restore database from backup
3. [ ] Checkout previous git tag
4. [ ] Rebuild Docker images
5. [ ] Start services
6. [ ] Verify functionality
7. [ ] Notify stakeholders

---

## Emergency Contacts

### Team
- **System Admin**: [Name] - [Email] - [Phone]
- **Developer**: [Name] - [Email] - [Phone]
- **On-Call**: [Name] - [Email] - [Phone]

### External
- **Hosting Provider**: [Support URL] - [Phone]
- **DNS Provider**: [Support URL] - [Phone]
- **SSL Provider**: [Support URL] - [Phone]

---

## Service Level Objectives (SLOs)

### Availability
- **Target**: 99.9% uptime
- **Downtime Budget**: 43 minutes/month
- **Measurement**: Health check success rate

### Performance
- **API Response Time**: P95 < 100ms
- **Task Processing**: P95 < 60 seconds
- **Database Queries**: P95 < 10ms

### Reliability
- **Error Rate**: < 0.1%
- **Recovery Time**: < 2 minutes
- **Data Loss**: Zero tolerance

---

## Incident Response

### Severity Levels
- **P0 (Critical)**: Complete system outage
- **P1 (High)**: Major feature broken
- **P2 (Medium)**: Minor feature degraded
- **P3 (Low)**: Cosmetic issue

### Response Times
- **P0**: Immediate response, 24/7
- **P1**: Response within 1 hour
- **P2**: Response within 4 hours
- **P3**: Response within 24 hours

### Incident Procedure
1. [ ] Acknowledge incident
2. [ ] Assess severity
3. [ ] Notify stakeholders
4. [ ] Investigate root cause
5. [ ] Implement fix
6. [ ] Verify resolution
7. [ ] Document incident
8. [ ] Conduct post-mortem

---

## Compliance

### Data Protection
- [ ] GDPR compliance reviewed (if applicable)
- [ ] Data retention policy defined
- [ ] User data encrypted at rest
- [ ] User data encrypted in transit
- [ ] Data deletion procedure documented

### Security
- [ ] Security audit completed
- [ ] Penetration testing done
- [ ] Vulnerability scanning enabled
- [ ] Security patches applied
- [ ] Access logs retained

### Legal
- [ ] Terms of service published
- [ ] Privacy policy published
- [ ] License compliance verified
- [ ] Third-party agreements signed

---

## Success Criteria

### Technical
- [ ] All services running
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Security requirements met
- [ ] Monitoring active

### Business
- [ ] Stakeholders notified
- [ ] Documentation complete
- [ ] Training provided
- [ ] Support ready
- [ ] Feedback mechanism in place

---

## Sign-Off

### Deployment Team
- [ ] Developer: _________________ Date: _______
- [ ] System Admin: _________________ Date: _______
- [ ] QA: _________________ Date: _______

### Stakeholders
- [ ] Product Owner: _________________ Date: _______
- [ ] Technical Lead: _________________ Date: _______
- [ ] Operations: _________________ Date: _______

---

**Deployment Date**: ______________  
**Version**: ______________  
**Environment**: Production  
**Status**: ☐ Ready ☐ In Progress ☐ Complete ☐ Rolled Back

---

**Remember**: Production is not a testing environment. Test thoroughly before deploying!
