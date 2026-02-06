# Deploy a Stateless Application to Kubernetes

## Overview

This guide walks through deploying a stateless web application to a Kubernetes cluster using a Deployment resource. You will create a Deployment manifest, apply it to the cluster, verify the rollout, expose the application via a Service, update the application image, and clean up resources.

## Prerequisites

- A running Kubernetes cluster (v1.24 or later). For local development, use minikube, kind, or Docker Desktop with Kubernetes enabled.
- `kubectl` command-line tool installed and configured to communicate with your cluster. Verify with:

  ```bash
  kubectl version --client
  kubectl cluster-info
  ```

- Container image available in a registry accessible to the cluster. This guide uses `nginx:1.25` as the example image.
- Basic familiarity with YAML syntax and Kubernetes resource types (Pods, Deployments, Services).

## Step 1: Create the Deployment Manifest

Create a file named `nginx-deployment.yaml` with the following content:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
```

Important: The `selector.matchLabels` field must match `template.metadata.labels`. If these do not match, the Deployment controller cannot identify which Pods belong to this Deployment.

Note: The `resources` block sets CPU and memory requests and limits. Requests guarantee minimum resources; limits cap maximum usage. Omitting resource limits is not recommended for production workloads because a single Pod can consume all available node resources.

## Step 2: Apply the Deployment

Run the following command to create the Deployment in your cluster:

```bash
kubectl apply -f nginx-deployment.yaml
```

Expected output:

```
deployment.apps/nginx-deployment created
```

## Step 3: Verify the Rollout

Check that the Deployment rolled out successfully:

```bash
kubectl rollout status deployment/nginx-deployment
```

Expected output when complete:

```
deployment "nginx-deployment" successfully rolled out
```

Inspect the Deployment details:

```bash
kubectl get deployments
```

Expected output:

```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           30s
```

If the `READY` column does not show `3/3` after 60 seconds, check Pod status:

```bash
kubectl get pods -l app=nginx
```

If any Pods show `ImagePullBackOff` or `ErrImagePull`, the container image name or tag is incorrect, or the registry is inaccessible from the cluster. Verify the image name and ensure your cluster has network access to the container registry.

If Pods show `CrashLoopBackOff`, inspect the Pod logs:

```bash
kubectl logs <pod-name>
```

Replace `<pod-name>` with the actual Pod name from the `kubectl get pods` output.

## Step 4: Expose the Application with a Service

Create a Service to make the application accessible outside the cluster:

```bash
kubectl expose deployment nginx-deployment --type=LoadBalancer --port=80 --target-port=80
```

Expected output:

```
service/nginx-deployment exposed
```

Check the Service and its external IP:

```bash
kubectl get services nginx-deployment
```

Expected output:

```
NAME               TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx-deployment   LoadBalancer   10.96.45.123   <pending>      80:31234/TCP   10s
```

Warning: On local clusters (minikube, kind), `EXTERNAL-IP` may remain `<pending>` indefinitely because no cloud load balancer is available. Use one of these alternatives:

- **minikube:** Run `minikube service nginx-deployment` to open the service in your browser.
- **kind:** Use port-forwarding instead: `kubectl port-forward service/nginx-deployment 8080:80`, then access `http://localhost:8080`.
- **Docker Desktop:** The LoadBalancer type works on Docker Desktop; wait 30 seconds for the external IP to appear.

## Step 5: Update the Application Image

To update the application to a newer image version, use `kubectl set image`:

```bash
kubectl set image deployment/nginx-deployment nginx=nginx:1.26
```

Monitor the rolling update:

```bash
kubectl rollout status deployment/nginx-deployment
```

The Deployment performs a rolling update by default, replacing Pods one at a time. During the update, at least 2 of the 3 replicas remain available (controlled by `maxUnavailable` and `maxSurge` settings).

If the new image causes failures, roll back to the previous version:

```bash
kubectl rollout undo deployment/nginx-deployment
```

Verify the rollback completed:

```bash
kubectl describe deployment nginx-deployment | grep Image
```

Expected output after rollback:

```
    Image: nginx:1.25
```

## Step 6: Scale the Deployment

Adjust the number of replicas based on load:

```bash
kubectl scale deployment/nginx-deployment --replicas=5
```

Verify the scaling:

```bash
kubectl get deployment nginx-deployment
```

Expected output:

```
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   5/5     5            5           5m
```

Note: For production workloads, configure a Horizontal Pod Autoscaler (HPA) instead of manual scaling. The HPA automatically adjusts replicas based on CPU or memory utilization metrics.

## Step 7: Clean Up Resources

When finished, delete the Deployment and Service to free cluster resources:

```bash
kubectl delete service nginx-deployment
kubectl delete deployment nginx-deployment
```

Verify all resources are removed:

```bash
kubectl get deployments
kubectl get services
kubectl get pods -l app=nginx
```

The output for each command should show no resources matching the `nginx-deployment` name or `app=nginx` label.

## Troubleshooting Reference

| Symptom | Possible Cause | Resolution |
|---------|---------------|------------|
| Pods stuck in `Pending` | Insufficient cluster resources (CPU or memory) | Check node capacity with `kubectl describe nodes`. Add nodes or reduce resource requests. |
| Pods in `ImagePullBackOff` | Image name or tag is incorrect, or registry is unreachable | Verify image exists: `docker pull nginx:1.25`. Check cluster network policies and registry credentials. |
| Pods in `CrashLoopBackOff` | Application crashes on startup | Check logs: `kubectl logs <pod-name>`. Verify the container command, environment variables, and configuration. |
| Service shows `<pending>` external IP | No cloud load balancer provisioner available | Use NodePort type instead, or use `kubectl port-forward` for local access. |
| Rolling update stuck | New image fails readiness probe | Check probe configuration and container health. Run `kubectl rollout undo` to revert. |
| Pods evicted after deployment | Node under memory pressure | Increase memory limits or add cluster capacity. Review resource requests and limits. |

## Cross-References

- Kubernetes Deployments documentation: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Kubernetes Services documentation: https://kubernetes.io/docs/concepts/services-networking/service/
- Horizontal Pod Autoscaler: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
