# B-Search Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying B-Search in a production environment with full DevOps capabilities, monitoring, and automated error detection.

## 🚀 Production Startup Script

### Features

The `startup-prod.sh` script provides:

- **Pre-flight Checks**: System requirements, dependencies, configuration validation
- **Health Monitoring**: Real-time service health checks during startup
- **Error Detection**: Comprehensive error handling and reporting
- **Rollback Capabilities**: Automatic cleanup on failure
- **Production Optimizations**: Resource limits, security hardening
- **Detailed Logging**: Structured logging with timestamps and severity levels

### Usage

```bash
# Basic startup
./startup-prod.sh

# Show help
./startup-prod.sh --help

# Dry run (show what would be done)
./startup-prod.sh --dry-run

# Skip health checks (faster startup)
./startup-prod.sh --skip-health-checks

# Force startup even if some checks fail
./startup-prod.sh --force
```

### What It Does

1. **System Validation**
   - Checks OS, memory (8GB+), disk space (20GB+), CPU cores
   - Validates Docker and Docker Compose installation
   - Verifies network connectivity and DNS resolution

2. **Dependency Checks**
   - Validates Python 3.x, pip, virtualenv
   - Checks for required system packages (curl, jq, etc.)
   - Verifies Docker daemon status

3. **Configuration Validation**
   - Checks for required environment variables
   - Validates database connection parameters
   - Ensures API keys are properly configured (when provided)

4. **Infrastructure Startup**
   - Starts PostgreSQL, Redis, MinIO in correct order
   - Waits for services to become healthy
   - Configures monitoring stack (Prometheus, Grafana)

5. **Database Setup**
   - Runs database migrations
   - Initializes required schemas and tables
   - Validates database connectivity

6. **Application Deployment**
   - Sets up Python virtual environment
   - Installs all dependencies
   - Starts Celery workers and API service
   - Enables Label Studio (if configured)

7. **Health Checks**
   - Comprehensive API endpoint testing
   - Database connectivity verification
   - Service dependency validation
   - Performance baseline measurement

8. **Monitoring Setup**
   - Configures log rotation and retention
   - Sets up alerting channels
   - Initializes monitoring dashboards

## 📊 Production Monitoring Script

### Features

The `monitor-prod.sh` script provides:

- **Continuous Health Monitoring**: 24/7 service health checks
- **Multi-Channel Alerting**: Email, Slack, webhook notifications
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Error Rate Analysis**: Log analysis and error pattern detection
- **Performance Metrics**: API response times, throughput monitoring
- **Automated Reporting**: Daily/weekly health reports
- **Rate Limiting**: Prevents alert spam during incidents

### Usage

```bash
# Start continuous monitoring
./monitor-prod.sh

# Run one-time health check
./monitor-prod.sh --once

# Generate current status report
./monitor-prod.sh --report

# Send test alert
./monitor-prod.sh --alert-test

# Show help
./monitor-prod.sh --help
```

### Configuration

Set these environment variables for alerting:

```bash
# Email alerts
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_SERVER=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=alerts@yourdomain.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_RECIPIENTS=admin@yourdomain.com,devops@yourdomain.com

# Slack alerts
ALERT_SLACK_ENABLED=true
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Webhook alerts
ALERT_WEBHOOK_ENABLED=true
ALERT_WEBHOOK_URL=https://your-monitoring-service.com/webhook

# Monitoring settings
MONITOR_INTERVAL=60          # Check every 60 seconds
ALERT_THRESHOLD=3           # Rate limiting threshold
API_URL=http://localhost:8080  # API base URL
```

### Monitored Components

- **Docker Services**: All containers health and status
- **API Endpoints**: Response times, error rates, availability
- **Database**: Connection health, query performance
- **Cache**: Redis connectivity and performance
- **Storage**: MinIO/S3 connectivity and operations
- **System Resources**: CPU, memory, disk usage
- **Network**: Connectivity and DNS resolution
- **Application Logs**: Error patterns and rates

## 🔧 Systemd Service Integration

### Installation

1. **Copy service files**:
```bash
sudo cp bsearch.service /etc/systemd/system/
sudo cp bsearch-monitor.service /etc/systemd/system/
```

2. **Create bsearch user**:
```bash
sudo useradd -r -s /bin/false bsearch
sudo mkdir -p /opt/bsearch
sudo chown bsearch:bsearch /opt/bsearch
```

3. **Copy application files**:
```bash
sudo cp -r /path/to/bsearch/server /opt/bsearch/
sudo chown -R bsearch:bsearch /opt/bsearch/server
```

4. **Create log directories**:
```bash
sudo mkdir -p /var/log/bsearch /var/run/bsearch
sudo chown bsearch:bsearch /var/log/bsearch /var/run/bsearch
```

5. **Configure environment**:
```bash
sudo cp .env.production.template /opt/bsearch/server/.env
sudo nano /opt/bsearch/server/.env  # Edit with production values
sudo chown bsearch:bsearch /opt/bsearch/server/.env
sudo chmod 600 /opt/bsearch/server/.env
```

6. **Reload systemd and enable services**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bsearch.service
sudo systemctl enable bsearch-monitor.service
```

### Service Management

```bash
# Start services
sudo systemctl start bsearch.service
sudo systemctl start bsearch-monitor.service

# Check status
sudo systemctl status bsearch.service
sudo systemctl status bsearch-monitor.service

# View logs
sudo journalctl -u bsearch.service -f
sudo journalctl -u bsearch-monitor.service -f

# Restart services
sudo systemctl restart bsearch.service
sudo systemctl restart bsearch-monitor.service

# Stop services
sudo systemctl stop bsearch.service
sudo systemctl stop bsearch-monitor.service
```

## 📋 Production Checklist

### Pre-Deployment

- [ ] Review and customize `.env.production.template`
- [ ] Set strong passwords for all services
- [ ] Configure SSL/TLS certificates
- [ ] Set up DNS records for your domain
- [ ] Configure firewall rules
- [ ] Set up log aggregation (ELK stack, etc.)
- [ ] Configure backup storage
- [ ] Set up monitoring alerts

### Security Hardening

- [ ] Change default service passwords
- [ ] Enable SSL/TLS for all services
- [ ] Configure firewall rules
- [ ] Set up intrusion detection
- [ ] Enable audit logging
- [ ] Configure log rotation
- [ ] Set up regular security updates

### Monitoring Setup

- [ ] Configure alerting channels (email, Slack, webhook)
- [ ] Set up log aggregation
- [ ] Configure monitoring dashboards
- [ ] Set up backup monitoring
- [ ] Configure performance monitoring
- [ ] Set up error tracking (Sentry)

### Backup Strategy

- [ ] Configure automated database backups
- [ ] Set up file system backups
- [ ] Configure backup retention policies
- [ ] Test backup restoration
- [ ] Set up offsite backup storage
- [ ] Document backup procedures

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check Docker status
sudo systemctl status docker

# Check service logs
sudo journalctl -u bsearch.service -n 50

# Check Docker Compose logs
cd /opt/bsearch/server
sudo -u bsearch docker compose logs

# Check resource usage
docker system df
docker stats
```

#### Database Connection Issues

```bash
# Check PostgreSQL container
docker ps | grep postgres

# Check database logs
docker logs $(docker ps -q -f name=postgres)

# Test database connection
docker exec -it $(docker ps -q -f name=postgres) psql -U bsearch_prod -d bsearch_db -c "SELECT version();"
```

#### API Not Responding

```bash
# Check API container
docker ps | grep api

# Check API logs
docker logs $(docker ps -q -f name=api)

# Test API health
curl -v http://localhost:8080/healthz

# Check network connectivity
docker exec $(docker ps -q -f name=api) curl -v http://localhost:5432
```

#### High Resource Usage

```bash
# Check system resources
top
htop
free -h
df -h

# Check Docker resource usage
docker stats

# Check application resource usage
docker exec $(docker ps -q -f name=api) ps aux
```

### Emergency Procedures

#### Service Restart

```bash
# Graceful restart
sudo systemctl restart bsearch.service

# Force restart
sudo systemctl stop bsearch.service
sudo systemctl start bsearch.service

# Full system restart
sudo systemctl stop bsearch-monitor.service
sudo systemctl stop bsearch.service
sudo systemctl start bsearch.service
sudo systemctl start bsearch-monitor.service
```

#### Data Recovery

```bash
# Restore from backup
cd /opt/bsearch/server
docker compose down
# Copy backup files to appropriate locations
docker compose up -d postgres
# Restore database from backup
docker compose up -d
```

## 📊 Monitoring Dashboards

### Grafana Setup

1. **Access Grafana**: http://localhost:3000 (admin/admin)
2. **Import Dashboards**:
   - Docker monitoring dashboard
   - Application performance dashboard
   - System resources dashboard
   - API metrics dashboard

### Prometheus Metrics

Available metrics:
- `api_requests_total`: Total API requests by endpoint
- `api_request_duration_seconds`: Request duration histograms
- `database_connections_active`: Active database connections
- `redis_memory_used_bytes`: Redis memory usage
- `system_cpu_usage_percent`: System CPU usage
- `system_memory_usage_percent`: System memory usage

### Alert Rules

Pre-configured alerts:
- API response time > 5 seconds
- Error rate > 5% in 5 minutes
- Database connection pool exhausted
- Disk usage > 90%
- Memory usage > 90%
- Service down/unhealthy

## 🔄 Backup and Recovery

### Automated Backups

```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/opt/bsearch/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker exec $(docker ps -q -f name=postgres) pg_dump -U bsearch_prod bsearch_db > "$BACKUP_DIR/db_backup_$DATE.sql"
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +30 -delete
```

### Recovery Procedures

1. **Database Recovery**:
```bash
docker compose down
docker compose up -d postgres
docker exec -i $(docker ps -q -f name=postgres) psql -U bsearch_prod -d bsearch_db < backup.sql
docker compose up -d
```

2. **Full System Recovery**:
```bash
# Stop all services
sudo systemctl stop bsearch-monitor.service
sudo systemctl stop bsearch.service

# Restore from backups
# ... restore procedures ...

# Restart services
sudo systemctl start bsearch.service
sudo systemctl start bsearch-monitor.service
```

## 📈 Scaling and Performance

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.9'
services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  workers:
    deploy:
      replicas: 5
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Vertical Scaling

```yaml
# Increase resource limits
services:
  api:
    environment:
      - WORKER_CONCURRENCY=16
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_items_created_at ON items(created_at);
CREATE INDEX CONCURRENTLY idx_items_project_id ON items(project_id);
CREATE INDEX CONCURRENTLY idx_items_content_gin ON items USING gin(to_tsvector('english', content));
```

## 🔐 Security Best Practices

### Network Security

```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### SSL/TLS Configuration

```nginx
# nginx.conf for SSL termination
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Access Control

```bash
# Create restricted user
sudo useradd -m -s /bin/bash bsearch_ops
sudo usermod -aG docker bsearch_ops

# Set up SSH key authentication
ssh-keygen -t ed25519
ssh-copy-id bsearch_ops@server

# Disable password authentication
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks

- [ ] Monitor system resources weekly
- [ ] Review and rotate logs monthly
- [ ] Update dependencies quarterly
- [ ] Test backup restoration monthly
- [ ] Review security configurations quarterly
- [ ] Update SSL certificates before expiration

### Emergency Contacts

- **Primary**: admin@yourdomain.com
- **Secondary**: devops@yourdomain.com
- **On-call**: +1234567890

### Documentation Updates

Keep these documents updated:
- [ ] Incident response procedures
- [ ] Backup and recovery procedures
- [ ] Security policies and procedures
- [ ] System architecture diagrams
- [ ] Network topology documentation

---

**Production Deployment Complete!** 🎉

Your B-Search system is now running in production with comprehensive monitoring, alerting, and automated error detection capabilities.