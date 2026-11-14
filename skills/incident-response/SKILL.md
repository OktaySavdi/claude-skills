---
name: incident-response
description: >-
  Structured incident response for cloud, Kubernetes, and Azure environments.
  Covers triage, containment, eradication, and recovery. Builds runbooks, coordinates
  timeline reconstruction, and produces post-incident reports. Activate when
  responding to a security incident, breach, or suspicious alert.
domain: cybersecurity
subdomain: incident-response
tags:
  - incident-response
  - dfir
  - triage
  - containment
  - azure
  - kubernetes
  - forensics
  - timeline
nist_csf: [RS.MA-01, RS.AN-01, RS.CO-01, RC.RP-01, DE.AE-05]
mitre_attack: [T1078, T1190, T1486, T1537]
version: "1.0"
license: Apache-2.0
---

# Incident Response Skill

## When to Use

- Active security incident or suspected breach in Azure/AKS
- Alert triage — determining if an event is a true positive
- Building incident response runbooks
- Post-incident timeline reconstruction
- Writing incident reports or post-mortems
- Coordinating containment actions (isolate pod, revoke SP, lock account)

## Prerequisites

- Access to affected Azure subscription and/or cluster
- Log Analytics / Sentinel access with appropriate permissions
- Incident tracking system (Jira, ServiceNow)

## PICERL Phases

### 1. Preparation
- Runbooks pre-authored for top 5 scenarios
- Contact tree documented (Azure support, CISO, legal)
- Sentinel playbooks (Logic Apps) ready for auto-containment

### 2. Identification
```bash
# AKS — check for anomalous pods
kubectl get pods -A --field-selector=status.phase=Running | grep -v kube-system

# Azure — check recent role assignments (last 24h)
az monitor activity-log list \
  --offset 24h \
  --query "[?operationName.value=='Microsoft.Authorization/roleAssignments/write']" \
  --output table

# Check for new service principals
az ad sp list --query "[?createdDateTime>'2024-01-01'].[displayName,appId,createdDateTime]" -o table
```

### 3. Containment

**Azure — Revoke compromised SP:**
```bash
az ad sp credential reset --id <appId> --append false
az role assignment delete --assignee <appId> --role Contributor --scope /subscriptions/<id>
```

**AKS — Isolate compromised pod:**
```bash
# Apply deny-all NetworkPolicy to pod
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: isolate-compromised-pod
  namespace: <ns>
spec:
  podSelector:
    matchLabels:
      app: <compromised-app>
  policyTypes: [Ingress, Egress]
EOF

# Cordon node if container escape suspected
kubectl cordon <node-name>
```

**Azure — Lock storage account:**
```bash
az storage account update --name <account> --resource-group <rg> \
  --public-network-access Disabled
```

### 4. Eradication
- Rotate all credentials for affected service principals
- Re-deploy affected workloads from clean image digest
- Remove unauthorised role assignments
- Patch exploited vulnerability

### 5. Recovery
- Restore from known-good state (Terraform re-apply, GitOps sync)
- Enable enhanced logging temporarily
- Monitor for reinfection (24h watch)

### 6. Lessons Learned
- Timeline reconstruction in KQL
- Root cause documented
- Detection gap identified → new Sentinel rule created
- MITRE technique documented → Kyverno/policy gap closed

## Timeline Reconstruction (KQL)

```kql
let incident_start = datetime(2024-01-15T10:00:00Z);
let incident_end = datetime(2024-01-15T14:00:00Z);
union AzureActivity, AuditLogs, SigninLogs
| where TimeGenerated between (incident_start .. incident_end)
| extend Actor = coalesce(Caller, InitiatedBy.user.userPrincipalName, UserPrincipalName)
| project TimeGenerated, Actor, OperationName, Result=ActivityStatus, Details=Properties
| order by TimeGenerated asc
```

## Incident Report Template

```markdown
## Incident Report — <TITLE>

**Severity:** P1/P2/P3
**Timeline:** YYYY-MM-DD HH:MM — HH:MM UTC
**Affected:** <resources>
**Impact:** <business impact>

### Root Cause
<concise description>

### Timeline
| Time | Event |
|------|-------|
| HH:MM | Initial alert triggered |
| HH:MM | Containment applied |

### Remediation
- [ ] Action 1
- [ ] Action 2

### Prevention
- Detection rule added: <rule name>
- Policy updated: <Kyverno/Azure Policy>
```
