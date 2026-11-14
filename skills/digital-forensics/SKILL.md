---
name: digital-forensics
description: >-
  Digital forensics specialist for cloud and container environments. Covers evidence
  collection, disk/memory acquisition, container forensics, Azure log preservation,
  and chain-of-custody. Activate for post-incident forensic investigation, evidence
  collection, or timeline reconstruction.
domain: cybersecurity
subdomain: digital-forensics
tags:
  - digital-forensics
  - dfir
  - memory-forensics
  - container-forensics
  - evidence-collection
  - chain-of-custody
  - azure
  - kubernetes
nist_csf: [RS.AN-01, RS.AN-03, RS.AN-04, RS.CO-03]
mitre_attack: [T1005, T1560, T1074]
version: "1.0"
license: Apache-2.0
---

# Digital Forensics Skill

## When to Use

- Post-incident evidence collection from AKS pods or Azure VMs
- Preserving Azure logs for legal hold or compliance investigation
- Container forensics — analysing a suspicious or terminated pod
- Memory dump acquisition and analysis
- Building forensic timelines from multiple log sources
- Chain-of-custody documentation for IR evidence

## Prerequisites

- `kubectl` access with exec permissions (read-only if possible)
- Azure Storage account for evidence preservation
- `volatility3`, `dd`/`dcfldd` for memory/disk forensics
- Log Analytics workspace with retention ≥ 90 days

## Container Forensics (Kubernetes)

```bash
# 1. Snapshot the suspicious pod (do NOT delete yet)
kubectl get pod <pod> -n <ns> -o yaml > pod-snapshot.yaml

# 2. Collect pod logs (current + previous)
kubectl logs <pod> -n <ns> --all-containers > pod-logs.txt
kubectl logs <pod> -n <ns> --previous --all-containers > pod-logs-prev.txt 2>/dev/null || true

# 3. Exec to collect filesystem artifacts (if safe to do so)
kubectl exec <pod> -n <ns> -- tar czf - /tmp /var/log /etc 2>/dev/null | \
  gzip > pod-fs-snapshot.tar.gz

# 4. Capture network connections at time of incident
kubectl exec <pod> -n <ns> -- ss -tulpn 2>/dev/null > pod-network-state.txt
kubectl exec <pod> -n <ns> -- ps aux 2>/dev/null > pod-process-list.txt

# 5. Hash all collected evidence
sha256sum pod-snapshot.yaml pod-logs.txt pod-fs-snapshot.tar.gz > evidence-hashes.txt
```

## Azure Log Preservation

```bash
# Set diagnostic log retention to 365 days
az monitor diagnostic-settings create \
  --resource <resource-id> \
  --name forensic-retention \
  --logs '[{"category": "AuditEvent","enabled": true,"retentionPolicy":{"days":365,"enabled":true}}]' \
  --storage-account <storage-id>

# Export activity logs to immutable storage
az monitor activity-log list \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-16T00:00:00Z \
  --output json > azure-activity-logs-20240115.json

# Legal hold on storage container
az storage container legal-hold set \
  --account-name <account> \
  --container-name forensic-evidence \
  --tags "incident-2024-001"
```

## Memory Acquisition (Linux VM)

```bash
# Using LiME kernel module
sudo insmod lime-$(uname -r).ko "path=/tmp/memory.lime format=lime"

# Compress and hash immediately
sha256sum /tmp/memory.lime > /tmp/memory.lime.sha256
gzip /tmp/memory.lime

# Upload to immutable evidence storage
az storage blob upload \
  --account-name <forensic-account> \
  --container-name incident-2024-001 \
  --file /tmp/memory.lime.gz \
  --name "$(hostname)-memory-$(date +%Y%m%dT%H%M%S).lime.gz"
```

## Memory Analysis (Volatility3)

```bash
# Process list
python3 vol.py -f memory.lime linux.pslist

# Network connections
python3 vol.py -f memory.lime linux.netstat

# Detect injected code
python3 vol.py -f memory.lime linux.malfind

# Bash history from memory
python3 vol.py -f memory.lime linux.bash
```

## Forensic Timeline (KQL)

```kql
// Multi-source timeline reconstruction
let incident_window = (datetime(2024-01-15T10:00:00Z), datetime(2024-01-15T14:00:00Z));
union withsource=LogSource
  (AzureActivity | project TimeGenerated, Actor=Caller, Action=OperationNameValue, Result=ActivityStatusValue, Details=tostring(Properties)),
  (AuditLogs | project TimeGenerated, Actor=tostring(InitiatedBy.user.userPrincipalName), Action=OperationName, Result=Result, Details=tostring(TargetResources)),
  (AzureDiagnostics | where Category == "kube-audit" | project TimeGenerated, Actor=extract('"username":"([^"]+)"',1,log_s), Action=extract('"verb":"([^"]+)"',1,log_s), Result="", Details=log_s)
| where TimeGenerated between (incident_window)
| order by TimeGenerated asc
| project TimeGenerated, LogSource, Actor, Action, Result, Details
```

## Chain of Custody Template

```markdown
## Evidence Chain of Custody

**Case:** Incident-2024-001
**Evidence Item:** pod-fs-snapshot.tar.gz
**SHA256:** <hash>

| Date/Time (UTC) | Action | By | Notes |
|---|---|---|---|
| 2024-01-15 11:30 | Collected | analyst@domain.com | kubectl exec snapshot |
| 2024-01-15 11:35 | Uploaded | analyst@domain.com | Azure immutable storage |
| 2024-01-15 14:00 | Accessed | ir-lead@domain.com | Read-only analysis |

**Storage Location:** `<storage-account>/forensic-evidence/incident-2024-001/`
**Legal Hold:** Active — tag: incident-2024-001
```
