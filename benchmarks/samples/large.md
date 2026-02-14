# Production Operations Runbook

This runbook covers deployment, monitoring, incident response, and maintenance
procedures for the CloudScale platform. All on-call engineers should review
this document before starting their rotation.

## Deployment

### Pre-Deployment Checklist

Before deploying to production, verify:

1. All CI/CD pipeline stages are green
2. Staging environment smoke tests pass
3. Database migration scripts have been reviewed
4. Rollback plan documented and tested
5. On-call engineer notified

### Standard Deployment Procedure

Deploy using the release management CLI:

```bash
release-cli deploy \
  --environment production \
  --version v2.4.1 \
  --strategy canary \
  --canary-percentage 10
```

Monitor the canary for 15 minutes before proceeding:

```bash
release-cli canary-status --watch
```

If metrics are healthy, promote to full deployment:

```bash
release-cli promote --version v2.4.1
```

### Canary Deployment

Canary deployments route a percentage of traffic to the new version.
Key metrics to monitor during canary:

| Metric       | Threshold | Action if Exceeded |
| ------------ | --------- | ------------------ |
| Error rate   | > 1%      | Auto-rollback      |
| P99 latency  | > 500ms   | Alert on-call      |
| CPU usage    | > 80%     | Scale horizontally |
| Memory usage | > 85%     | Investigate leaks  |

### Blue-Green Deployment

For major releases, use blue-green deployment:

```bash
release-cli deploy \
  --environment production \
  --strategy blue-green \
  --version v3.0.0
```

This creates an identical environment (green) alongside the current one (blue).
Traffic is switched atomically after validation.

### Rollback Procedure

If issues are detected, initiate immediate rollback:

```bash
release-cli rollback --to-version v2.4.0 --reason "elevated error rate"
```

Rollback completes within 60 seconds. Verify with:

```bash
release-cli status --environment production
```

## Monitoring

### Dashboard Overview

The primary monitoring dashboard is available at:
`https://monitoring.internal/dashboards/production`

Key panels to monitor:

1. **Request Rate** — Total requests per second across all services
2. **Error Rate** — Percentage of 5xx responses
3. **Latency Percentiles** — P50, P95, P99 response times
4. **Resource Utilization** — CPU, memory, disk across the fleet

### Alerting Rules

Active alerting rules and their escalation paths:

| Alert            | Condition             | Severity | Escalation   |
| ---------------- | --------------------- | -------- | ------------ |
| HighErrorRate    | > 2% 5xx for 5min     | P1       | Page on-call |
| HighLatency      | P99 > 1s for 10min    | P2       | Slack alert  |
| DiskPressure     | > 90% usage           | P2       | Slack alert  |
| PodCrashLoop     | > 3 restarts in 10min | P1       | Page on-call |
| CertExpiry       | < 14 days remaining   | P3       | Email team   |
| DBConnectionPool | > 90% utilized        | P2       | Slack alert  |

### Custom Metrics

Add custom metrics using the instrumentation library:

```python
from cloudscale.metrics import counter, histogram, gauge

request_count = counter(
    "http_requests_total",
    description="Total HTTP requests",
    labels=["method", "endpoint", "status"],
)

request_duration = histogram(
    "http_request_duration_seconds",
    description="Request duration in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 5.0],
)

active_connections = gauge(
    "active_connections",
    description="Currently active connections",
)
```

### Log Aggregation

Centralized logging is handled by the ELK stack. Query logs using:

```bash
log-query --service api-gateway --level ERROR --since 1h
```

Common log query patterns:

```bash
# Find all 500 errors for a specific endpoint
log-query --service api-gateway --level ERROR --filter "path=/api/v2/users"

# Trace a specific request across services
log-query --trace-id abc123def456 --all-services

# Count errors by type in the last hour
log-query --service api-gateway --level ERROR --since 1h --aggregate type
```

## Incident Response

### Severity Classification

| Severity      | Definition              | Response Time | Examples                     |
| ------------- | ----------------------- | ------------- | ---------------------------- |
| P1 — Critical | Complete service outage | 5 minutes     | API down, data loss          |
| P2 — Major    | Degraded service        | 30 minutes    | High latency, partial outage |
| P3 — Minor    | Limited impact          | 4 hours       | Non-critical feature broken  |
| P4 — Low      | Cosmetic                | Next sprint   | UI glitch, docs error        |

### Incident Commander Checklist

When paged for a P1/P2 incident:

1. **Acknowledge** the page within 5 minutes
2. **Open an incident channel** in Slack: `/incident create`
3. **Assess** the blast radius and customer impact
4. **Communicate** initial status to stakeholders
5. **Mitigate** — Apply immediate fix or rollback
6. **Monitor** — Verify recovery metrics
7. **Document** — Write post-incident review within 48 hours

### Communication Templates

**Initial Status Update:**

```
INCIDENT: [Brief description]
SEVERITY: P1/P2
STATUS: Investigating
IMPACT: [Customer-facing impact]
NEXT UPDATE: [Time]
```

**Resolution Update:**

```
INCIDENT: [Brief description]
SEVERITY: P1/P2
STATUS: Resolved
ROOT CAUSE: [Brief explanation]
DURATION: [Start to resolution]
FOLLOW-UP: Post-incident review scheduled for [date]
```

### Runbook: Database Failover

If the primary database becomes unresponsive:

```bash
# Check replication lag
db-admin replication-status --cluster production

# Initiate failover to standby
db-admin failover \
  --cluster production \
  --target standby-01 \
  --reason "primary unresponsive"

# Verify application connectivity
db-admin connection-test --cluster production --all-services
```

### Runbook: Cache Invalidation

When stale cache causes data inconsistency:

```bash
# Flush specific cache keys
cache-admin flush --pattern "user:*" --cluster redis-prod

# Flush entire cache (use with caution)
cache-admin flush --all --cluster redis-prod --confirm

# Verify cache is rebuilding
cache-admin stats --cluster redis-prod --watch
```

## Database Operations

### Backup Schedule

| Type        | Frequency          | Retention | Storage     |
| ----------- | ------------------ | --------- | ----------- |
| Full backup | Daily at 02:00 UTC | 30 days   | S3 Glacier  |
| Incremental | Every 6 hours      | 7 days    | S3 Standard |
| WAL archive | Continuous         | 7 days    | S3 Standard |
| Snapshot    | Weekly             | 90 days   | S3 Glacier  |

### Manual Backup

Trigger an on-demand backup:

```bash
db-admin backup \
  --cluster production \
  --type full \
  --label "pre-migration-v2.5"
```

### Restore Procedure

Restore from a backup to a staging environment:

```bash
db-admin restore \
  --backup-id bk-20260210-020000 \
  --target staging \
  --point-in-time "2026-02-10T03:00:00Z"
```

### Schema Migrations

Run migrations in a transaction with automatic rollback:

```bash
db-admin migrate \
  --cluster production \
  --migration-dir ./migrations \
  --dry-run  # Preview changes first

db-admin migrate \
  --cluster production \
  --migration-dir ./migrations \
  --execute
```

## Security

### Access Control

Access to production systems follows the principle of least privilege:

| Role            | Permissions               | Approval Required      |
| --------------- | ------------------------- | ---------------------- |
| Engineer        | Read logs, read metrics   | None                   |
| Senior Engineer | Deploy, read database     | Team lead              |
| On-call         | Deploy, restart, failover | None (during incident) |
| DBA             | Full database access      | Manager + security     |
| Admin           | Full infrastructure       | VP + security          |

### Secret Management

Secrets are stored in HashiCorp Vault:

```bash
# Read a secret
vault kv get secret/production/api-keys

# Rotate a secret
vault kv put secret/production/api-keys \
  stripe_key="sk_live_new_key_value"

# List available secrets
vault kv list secret/production/
```

### Security Audit Checklist

Monthly security review items:

- [ ] Review access control changes
- [ ] Rotate service account credentials
- [ ] Check SSL certificate expiry dates
- [ ] Review firewall rules for stale entries
- [ ] Audit API key usage patterns
- [ ] Verify backup encryption status

## Maintenance

### Scheduled Maintenance Windows

| Day      | Time (UTC)  | Duration | Type           |
| -------- | ----------- | -------- | -------------- |
| Tuesday  | 06:00–08:00 | 2 hours  | Infrastructure |
| Thursday | 06:00–07:00 | 1 hour   | Database       |
| Saturday | 04:00–08:00 | 4 hours  | Major upgrades |

### Node Drain and Replacement

To replace a node in the cluster:

```bash
# Drain workloads from the node
cluster-admin drain node-prod-07 --grace-period 300

# Verify all pods have been rescheduled
cluster-admin node-status node-prod-07

# Terminate the old node
cluster-admin terminate node-prod-07

# Launch replacement
cluster-admin provision --type worker --count 1
```

### Certificate Renewal

TLS certificates are managed by cert-manager. Manual renewal:

```bash
cert-admin renew --domain api.cloudscale.io --force
cert-admin verify --domain api.cloudscale.io
```

### Capacity Planning

Review capacity metrics quarterly:

| Resource | Current       | Projected (90d) | Action          |
| -------- | ------------- | --------------- | --------------- |
| CPU      | 45% avg       | 52% avg         | Monitor         |
| Memory   | 62% avg       | 68% avg         | Plan upgrade    |
| Disk     | 55% used      | 70% used        | Order expansion |
| Network  | 30% bandwidth | 35% bandwidth   | No action       |

## Appendix

### Useful Commands

Quick reference for commonly used CLI commands:

```bash
# Service status
service-admin status --all

# Recent deployments
release-cli history --last 10

# Current on-call
oncall-cli who --team platform

# Resource usage summary
cluster-admin resource-report --format table
```

### Contact Information

| Role           | Contact                   | Backup                      |
| -------------- | ------------------------- | --------------------------- |
| Platform Lead  | platform-lead@example.com | platform-team@example.com   |
| DBA Team       | dba@example.com           | dba-oncall@example.com      |
| Security       | security@example.com      | security-urgent@example.com |
| VP Engineering | vp-eng@example.com        | cto@example.com             |

### Glossary

| Term       | Definition                                                               |
| ---------- | ------------------------------------------------------------------------ |
| Canary     | Deployment strategy routing a small percentage of traffic to new version |
| Blue-Green | Deployment strategy maintaining two identical environments               |
| WAL        | Write-Ahead Log — PostgreSQL transaction log for point-in-time recovery  |
| P1         | Priority 1 — Critical incident requiring immediate response              |
| SLO        | Service Level Objective — Target reliability metric                      |
