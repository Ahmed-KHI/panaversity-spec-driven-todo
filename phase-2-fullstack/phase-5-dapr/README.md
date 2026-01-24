# Dapr Integration Guide

**[Task]**: T-D-008 (Document Dapr Setup Instructions)  
**[From]**: specs/005-phase-v-cloud/phase5-cloud.specify.md §3, §6,  
           specs/005-phase-v-cloud/phase5-cloud.tasks.md §D.8

## Overview

This guide explains how to run the Todo Management application with Dapr for event-driven architecture and microservices orchestration.

**Dapr Version**: 1.12+  
**Components**:
- Kafka Pub/Sub (via Redpanda)
- PostgreSQL State Store
- Kubernetes Secrets Store
- Jobs API (for reminders)

---

## Prerequisites

### 1. Install Dapr CLI

**Linux/Mac**:
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Windows (PowerShell)**:
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

Verify installation:
```bash
dapr --version
```

### 2. Initialize Dapr

**Local Development (Docker)**:
```bash
dapr init
```

This installs:
- Dapr sidecar
- Dapr placement service
- Redis (default state store)
- Zipkin (distributed tracing)

Verify:
```bash
dapr --version
docker ps  # Should show dapr_redis, dapr_placement, dapr_zipkin
```

**Kubernetes**:
```bash
dapr init --kubernetes --wait
```

---

## Component Configuration

### Kafka Pub/Sub (`kafka-pubsub.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "todo-service"
```

**Local Development**: Uses `kafka:9092` (via Docker Compose)  
**Production**: Update `brokers` to Redpanda Cloud URL with SASL authentication

### PostgreSQL State Store (`statestore.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secrets
      key: connection-string
```

### Kubernetes Secrets (`kubernetes-secrets.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
```

---

## Running Locally with Dapr

### Option 1: Backend Only

```bash
cd phase-2-fullstack/backend

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/tododb"
export BETTER_AUTH_SECRET="your-secret-32-chars"
export OPENAI_API_KEY="sk-proj-..."
export DAPR_HTTP_ENDPOINT="http://localhost:3500"
export KAFKA_ENABLED="true"

# Run with Dapr
dapr run \
  --app-id backend-service \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --resources-path ../phase-5-dapr/components \
  --log-level debug \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Explanation**:
- `--app-id`: Unique service identifier
- `--app-port`: Your app's HTTP port
- `--dapr-http-port`: Dapr sidecar HTTP API port
- `--resources-path`: Path to Dapr component YAML files
- `-- uvicorn ...`: Command to run your app

### Option 2: Multi-Service with Docker Compose

Create `docker-compose.dapr.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: todo_pass
      POSTGRES_DB: tododb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Kafka (Redpanda)
  kafka:
    image: vectorized/redpanda:latest
    command:
      - redpanda start
      - --smp 1
      - --overprovisioned
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
      - --advertise-kafka-addr PLAINTEXT://kafka:9092
    ports:
      - "9092:9092"

  # Backend with Dapr
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://todo_user:todo_pass@postgres:5432/tododb
      - BETTER_AUTH_SECRET=change-me-32-chars
      - OPENAI_API_KEY=sk-proj-xxx
      - DAPR_HTTP_ENDPOINT=http://localhost:3500
      - KAFKA_ENABLED=true
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - kafka
  
  backend-dapr:
    image: "daprio/daprd:1.12.0"
    command:
      - "./daprd"
      - "--app-id"
      - "backend-service"
      - "--app-port"
      - "8000"
      - "--dapr-http-port"
      - "3500"
      - "--resources-path"
      - "/components"
    volumes:
      - ./phase-5-dapr/components:/components
    network_mode: "service:backend"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Run:
```bash
docker-compose -f docker-compose.dapr.yml up
```

---

## Testing Event Publishing

### 1. Create a Task (Triggers `task.created` Event)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing Dapr events",
    "priority": "high",
    "due_date": "2026-01-25T10:00:00Z"
  }'
```

### 2. Check Dapr Logs

```bash
dapr logs --app-id backend-service
```

You should see:
```
✅ Event published via Dapr: task-events
```

### 3. Verify Event in Kafka

If you have `kafkacat` or `rpk` installed:

```bash
# Using rpk (Redpanda CLI)
rpk topic consume task-events --brokers localhost:9092

# Using kafkacat
kafkacat -b localhost:9092 -t task-events -C
```

---

## Kubernetes Deployment with Dapr

### 1. Create Namespace and Secrets

```bash
kubectl create namespace todo-app

# Apply secrets (update values first!)
kubectl apply -f phase-5-kubernetes/secrets.yaml
```

### 2. Apply Dapr Components

```bash
kubectl apply -f phase-5-dapr/components/
```

Verify:
```bash
kubectl get components -n todo-app
```

Expected output:
```
NAME                  AGE
kafka-pubsub          10s
kubernetes-secrets    10s
statestore            10s
```

### 3. Deploy Backend

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: backend
        image: your-registry/todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: connection-string
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: KAFKA_ENABLED
          value: "true"
```

Apply:
```bash
kubectl apply -f backend-deployment.yaml
```

### 4. Verify Dapr Injection

```bash
kubectl get pods -n todo-app

# Each pod should have 2/2 containers (app + dapr sidecar)
# Example output:
# NAME                       READY   STATUS    RESTARTS   AGE
# backend-5b8c7d8f9-abcde    2/2     Running   0          30s
```

Check logs:
```bash
# Application logs
kubectl logs -n todo-app backend-5b8c7d8f9-abcde -c backend

# Dapr sidecar logs
kubectl logs -n todo-app backend-5b8c7d8f9-abcde -c daprd
```

---

## Dapr API Reference

### Publish Event

**Endpoint**: `POST /v1.0/publish/{pubsubname}/{topic}`

**Example**:
```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "123e4567-e89b-12d3-a456-426614174000",
    "event_type": "task.created",
    "timestamp": "2026-01-21T10:00:00Z",
    "data": {
      "task_id": 1,
      "title": "Test Task"
    }
  }'
```

### State Management

**Save State**:
```bash
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{
    "key": "notification-1",
    "value": {
      "task_id": 1,
      "message": "Task due soon"
    }
  }]'
```

**Get State**:
```bash
curl http://localhost:3500/v1.0/state/statestore/notification-1
```

### Jobs API (Alpha)

**Schedule Job**:
```bash
curl -X POST http://localhost:3500/v1.0-alpha1/jobs/reminder-job-123 \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "@daily",
    "data": {
      "task_id": 1,
      "reminder_time": "2026-01-22T09:00:00Z"
    }
  }'
```

---

## Troubleshooting

### Issue: Dapr Sidecar Not Starting

**Solution**:
```bash
# Check Dapr system services
dapr status

# Reinstall Dapr
dapr uninstall
dapr init
```

### Issue: Events Not Publishing to Kafka

**Check**:
1. Kafka is running: `docker ps | grep kafka`
2. Component config: `kubectl describe component kafka-pubsub -n todo-app`
3. Dapr logs: `dapr logs --app-id backend-service`

**Common Causes**:
- Incorrect broker address
- Kafka not reachable (network/firewall)
- SASL credentials incorrect (production)

### Issue: 401 Unauthorized from Dapr

**Solution**: Ensure `dapr.io/app-id` annotation matches component scopes.

### Issue: State Store Connection Failed

**Check**:
1. PostgreSQL is running
2. Connection string is correct in secret
3. `dapr_state` table exists (Dapr creates automatically)

**Manual Table Creation** (if needed):
```sql
CREATE TABLE dapr_state (
  key TEXT PRIMARY KEY,
  value JSONB,
  etag TEXT,
  creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expiration_time TIMESTAMP
);
```

---

## Performance Tuning

### Kafka Producer Settings

In `kafka-pubsub.yaml`:

```yaml
metadata:
  # Increase throughput
  - name: maxMessageBytes
    value: "1024000"  # 1MB
  
  # Reduce latency
  - name: initialOffset
    value: "newest"
```

### Connection Pooling

In `statestore.yaml`:

```yaml
metadata:
  - name: maxConns
    value: "20"  # Increase for high load
  
  - name: connectionMaxIdleTime
    value: "300"  # 5 minutes
```

---

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.gitignore` for `secrets.yaml`
   - Use sealed-secrets or external-secrets operator

2. **Use TLS for Kafka in production**
   ```yaml
   - name: skipVerify
     value: "false"
   ```

3. **Enable mTLS between services**
   ```bash
   dapr run --enable-mtls ...
   ```

4. **Restrict component scopes**
   ```yaml
   scopes:
   - backend-service  # Only backend can access
   ```

5. **Use RBAC for secrets**
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: secret-reader
   rules:
   - apiGroups: [""]
     resources: ["secrets"]
     verbs: ["get"]
   ```

---

## Monitoring and Observability

### Dapr Dashboard

```bash
dapr dashboard -p 9999
```

Open: http://localhost:9999

### Distributed Tracing (Zipkin)

```bash
# Already running if you did `dapr init`
open http://localhost:9411
```

### Prometheus Metrics

Dapr exposes metrics at:
- `http://localhost:9090/metrics` (sidecar)
- `http://localhost:8000/metrics` (app, if configured)

---

## Next Steps

1. ✅ Run backend with Dapr locally (T-D-007)
2. 🔄 Create recurring task consumer microservice (T-C-005)
3. 🔄 Create notification service microservice (T-C-008)
4. 🔄 Deploy to Kubernetes with Helm (Section E)
5. 🔄 Deploy to cloud (AKS/GKE/OKE) (Section E)

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Kafka Pub/Sub Component](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [PostgreSQL State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
- [Dapr Jobs API (Alpha)](https://docs.dapr.io/developing-applications/building-blocks/jobs/jobs-overview/)
- [Redpanda (Kafka-compatible)](https://redpanda.com/)

---

**Version**: 1.0  
**Last Updated**: January 21, 2026  
**Maintained By**: Phase V Implementation Team
