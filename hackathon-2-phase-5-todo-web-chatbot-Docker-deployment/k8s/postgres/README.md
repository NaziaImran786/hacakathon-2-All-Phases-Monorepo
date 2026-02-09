# PostgreSQL Database Deployment Guide

This directory contains Kubernetes manifests for deploying PostgreSQL with persistent storage.

## Files

- `statefulset.yaml` - PostgreSQL StatefulSet with PersistentVolumeClaim
- `service.yaml` - Kubernetes Service for database access
- `../secrets/postgres-secret.yaml.example` - Secret template for database password

## Quick Start

### 1. Create PostgreSQL Secret

**Option A: Imperative (Recommended)**
```bash
# Create secret with your password
kubectl create secret generic postgres-secret \
  --from-literal=password='YOUR_SECURE_PASSWORD_HERE'

# Verify secret created
kubectl get secret postgres-secret
```

**Option B: Declarative (from YAML)**
```bash
# Copy example file
cp ../secrets/postgres-secret.yaml.example ../secrets/postgres-secret.yaml

# Edit postgres-secret.yaml and update password (base64 encoded)
# Generate base64: echo -n 'your-password' | base64

# Apply secret
kubectl apply -f ../secrets/postgres-secret.yaml

# IMPORTANT: Never commit postgres-secret.yaml to git!
```

### 2. Deploy PostgreSQL

```bash
# Apply StatefulSet (includes PVC template)
kubectl apply -f statefulset.yaml

# Apply Service
kubectl apply -f service.yaml
```

### 3. Verify Deployment

```bash
# Check StatefulSet status
kubectl get statefulset postgres

# Check pod status (should be Running)
kubectl get pods -l app=postgres

# Check PersistentVolumeClaim (should be Bound)
kubectl get pvc

# Check Service endpoints
kubectl get endpoints postgres-service

# View pod logs
kubectl logs postgres-0

# Describe for detailed status
kubectl describe statefulset postgres
```

## Configuration Details

### Database Credentials

- **User**: `todouser`
- **Database**: `tododb`
- **Password**: From `postgres-secret` Secret (key: `password`)
- **Port**: 5432

### Connection String

From backend pods:
```
postgresql://todouser:PASSWORD@postgres-service:5432/tododb
```

Replace `PASSWORD` with the actual password from the secret.

### Persistent Storage

- **Storage Class**: `standard` (default in Minikube)
- **Size**: 10Gi
- **Access Mode**: ReadWriteOnce (RWO)
- **PVC Name**: `postgres-storage-postgres-0`
- **Mount Path**: `/var/lib/postgresql/data`

### Resource Limits

- **Requests**: 250m CPU, 256Mi memory
- **Limits**: 500m CPU, 512Mi memory

## Testing

### Test Database Connection

**From within cluster:**
```bash
# Run psql client
kubectl run -it --rm psql-client \
  --image=postgres:15-alpine \
  --restart=Never \
  -- psql -h postgres-service -U todouser -d tododb

# Enter password when prompted
# Exit with \q
```

**From postgres pod directly:**
```bash
kubectl exec -it postgres-0 -- psql -U todouser -d tododb
```

### Test from Backend Pod

```bash
# Get backend pod name
kubectl get pods -l app=backend

# Exec into backend pod
kubectl exec -it <backend-pod-name> -- bash

# Test connection with Python
python -c "from sqlmodel import create_engine; engine = create_engine('postgresql://todouser:PASSWORD@postgres-service:5432/tododb'); engine.connect(); print('Connection successful!')"
```

### Test DNS Resolution

```bash
# From any pod in the cluster
kubectl exec -it <any-pod> -- nslookup postgres-service

# Should resolve to ClusterIP address
```

## Data Persistence Testing

### Verify Data Survives Pod Restart

```bash
# 1. Create test data
kubectl exec -it postgres-0 -- psql -U todouser -d tododb -c \
  "CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT); INSERT INTO test (name) VALUES ('Test Data');"

# 2. Delete pod (StatefulSet will recreate it)
kubectl delete pod postgres-0

# 3. Wait for pod to be Running again
kubectl get pods -l app=postgres -w

# 4. Verify data still exists
kubectl exec -it postgres-0 -- psql -U todouser -d tododb -c \
  "SELECT * FROM test;"

# Expected output: id | name
#                  1  | Test Data
```

### Check PVC Status

```bash
# List PVCs
kubectl get pvc

# Describe PVC
kubectl describe pvc postgres-storage-postgres-0

# Check PVC size
kubectl get pvc postgres-storage-postgres-0 -o jsonpath='{.status.capacity.storage}'
```

## Monitoring

### Check Logs

```bash
# Tail logs
kubectl logs -f postgres-0

# Last 100 lines
kubectl logs postgres-0 --tail=100

# Logs since 1 hour ago
kubectl logs postgres-0 --since=1h
```

### Check Resource Usage

```bash
# CPU and memory usage
kubectl top pod postgres-0

# Detailed resource allocation
kubectl describe pod postgres-0 | grep -A 5 "Requests\|Limits"
```

### Check Health Probes

```bash
# View probe configuration
kubectl describe pod postgres-0 | grep -A 10 "Liveness\|Readiness"

# Manual probe test
kubectl exec -it postgres-0 -- pg_isready -U todouser -d tododb
```

## Troubleshooting

### Pod Stuck in Pending

**Symptoms**: Pod status remains `Pending`

**Possible Causes**:
- PVC cannot be bound
- Insufficient cluster resources
- Storage class not available

**Solutions**:
```bash
# Check PVC status
kubectl get pvc
kubectl describe pvc postgres-storage-postgres-0

# Check storage class
kubectl get storageclass

# Check cluster resources
kubectl describe nodes

# Check pod events
kubectl describe pod postgres-0
```

### Pod CrashLoopBackOff

**Symptoms**: Pod repeatedly crashes and restarts

**Possible Causes**:
- Wrong password in secret
- PGDATA directory conflict
- Insufficient memory

**Solutions**:
```bash
# Check logs for errors
kubectl logs postgres-0
kubectl logs postgres-0 --previous  # Previous container logs

# Verify secret exists and is correct
kubectl get secret postgres-secret
kubectl get secret postgres-secret -o jsonpath='{.data.password}' | base64 -d

# Check PGDATA setting (must use /pgdata suffix)
kubectl get statefulset postgres -o yaml | grep PGDATA
```

### Connection Refused

**Symptoms**: Backend cannot connect to database

**Possible Causes**:
- Service not created
- Pod not ready
- Wrong connection string

**Solutions**:
```bash
# Check service exists
kubectl get service postgres-service

# Check service endpoints
kubectl get endpoints postgres-service

# Verify pod is Ready
kubectl get pods -l app=postgres

# Test DNS resolution
kubectl exec -it <backend-pod> -- nslookup postgres-service

# Test connection
kubectl exec -it <backend-pod> -- nc -zv postgres-service 5432
```

### PVC Not Binding

**Symptoms**: PVC status remains `Pending`

**Possible Causes**:
- Storage class doesn't exist
- No available PersistentVolumes
- Insufficient storage space

**Solutions**:
```bash
# Check PVC status
kubectl describe pvc postgres-storage-postgres-0

# Check storage class
kubectl get storageclass

# For Minikube: Ensure Minikube is running with enough disk space
minikube ssh df -h

# Check available PVs
kubectl get pv
```

## Backup and Restore

### Backup Database

**Method 1: pg_dump (Logical Backup)**
```bash
# Backup to local file
kubectl exec postgres-0 -- pg_dump -U todouser tododb > backup.sql

# Backup with compression
kubectl exec postgres-0 -- pg_dump -U todouser tododb | gzip > backup.sql.gz

# Backup specific tables
kubectl exec postgres-0 -- pg_dump -U todouser -t users -t tasks tododb > backup.sql
```

**Method 2: PVC Snapshot (Physical Backup)**
```bash
# Create VolumeSnapshot (requires VolumeSnapshot CRD)
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot-$(date +%Y%m%d)
spec:
  source:
    persistentVolumeClaimName: postgres-storage-postgres-0
EOF
```

### Restore Database

**From pg_dump file:**
```bash
# Copy backup into pod
kubectl cp backup.sql postgres-0:/tmp/backup.sql

# Restore
kubectl exec -it postgres-0 -- psql -U todouser tododb < /tmp/backup.sql

# Or pipe directly
cat backup.sql | kubectl exec -i postgres-0 -- psql -U todouser tododb
```

## Cleanup

### Delete Everything (Data Will Be Lost!)

```bash
# Delete StatefulSet (pods will be deleted)
kubectl delete -f statefulset.yaml

# Delete Service
kubectl delete -f service.yaml

# Delete PVC (THIS DELETES DATA!)
kubectl delete pvc postgres-storage-postgres-0

# Delete Secret
kubectl delete secret postgres-secret
```

### Delete Only Pods (Keep Data)

```bash
# Delete StatefulSet (keeps PVC)
kubectl delete statefulset postgres

# PVC remains bound
kubectl get pvc postgres-storage-postgres-0

# Reapply StatefulSet to recreate pods
kubectl apply -f statefulset.yaml

# Data is preserved!
```

## Production Considerations

### High Availability

For production, consider:
- PostgreSQL streaming replication (primary + replicas)
- Patroni for automatic failover
- Managed database services (AWS RDS, Google Cloud SQL, Azure Database)

### Security

- Enable SSL/TLS for connections
- Implement Network Policies to restrict access
- Use Kubernetes RBAC for secret access
- Rotate passwords regularly
- Enable PostgreSQL audit logging

### Performance

- Tune PostgreSQL configuration (postgresql.conf)
- Adjust `shared_buffers`, `work_mem`, `maintenance_work_mem`
- Monitor query performance with `pg_stat_statements`
- Use connection pooling (PgBouncer)

### Backup Strategy

- Automated daily backups with pg_dump
- Point-in-time recovery (PITR) with WAL archiving
- Test restore procedures regularly
- Store backups outside cluster (S3, GCS, etc.)

## Additional Resources

- [PostgreSQL Docker Documentation](https://hub.docker.com/_/postgres)
- [Kubernetes StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
