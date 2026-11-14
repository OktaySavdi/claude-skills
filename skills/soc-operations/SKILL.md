---
name: soc-operations
description: >-
  SOC operations specialist covering alert triage, Azure Sentinel/Microsoft Defender,
  SIEM rule writing, playbook automation, and SOC metrics. Activate when managing
  security alerts, writing detection rules, building Sentinel workbooks, or improving
  SOC efficiency.
domain: cybersecurity
subdomain: soc-operations
tags:
  - soc
  - sentinel
  - defender
  - alert-triage
  - detection-rules
  - playbooks
  - siem
  - kql
nist_csf: [DE.AE-01, DE.AE-02, DE.AE-05, RS.AN-01, RS.CO-02]
mitre_attack: [T1078, T1190, T1486, T1059]
version: "1.0"
license: Apache-2.0
---

# SOC Operations Skill

## When to Use

- Writing Azure Sentinel analytics rules (KQL)
- Building Sentinel playbooks (Logic Apps) for auto-response
- Alert triage — determining P1/P2/P3 severity
- Creating SOC runbooks for top alert types
- Reporting SOC metrics (MTTD, MTTR)
- Tuning false positives in detection rules

## Prerequisites

- Azure Sentinel workspace with data connectors configured
- Logic Apps / Automation account for playbooks
- MITRE ATT&CK Navigator for coverage mapping

## Alert Triage Process

```
Alert Received
    │
    ▼
1. Validate — Is this a true positive?
   - Check alert context, entities, related events
   - Run enrichment queries (IP reputation, user history)
    │
    ▼
2. Severity — Assign P1/P2/P3
   P1: Active threat, data exfil, ransomware, compromised admin
   P2: Suspicious but not confirmed, high-risk user, lateral movement indicator
   P3: Policy violation, anomaly requiring investigation
    │
    ▼
3. Contain — Apply containment within SLA
   P1: 15 minutes  |  P2: 1 hour  |  P3: 4 hours
    │
    ▼
4. Investigate → Escalate → Close
```

## Sentinel Analytics Rule (KQL Template)

```kql
// Detection: Multiple failed logins followed by success
let threshold = 5;
let timeWindow = 1h;
SigninLogs
| where TimeGenerated > ago(timeWindow)
| summarize
    FailedAttempts=countif(ResultType != "0"),
    SuccessCount=countif(ResultType == "0"),
    IPAddresses=make_set(IPAddress)
  by UserPrincipalName, bin(TimeGenerated, timeWindow)
| where FailedAttempts >= threshold and SuccessCount > 0
| extend AlertSeverity="High"
| extend AlertName="Brute Force Success — " + UserPrincipalName
| project TimeGenerated, UserPrincipalName, FailedAttempts, SuccessCount, IPAddresses, AlertSeverity
```

## Playbook — Auto-Disable Compromised Account (Logic App)

```json
{
  "trigger": "When Azure Sentinel incident created",
  "actions": [
    {
      "name": "Get account entity",
      "type": "Get-AzureADUser"
    },
    {
      "name": "Disable account",
      "type": "Set-AzureADUser",
      "inputs": { "AccountEnabled": false }
    },
    {
      "name": "Revoke sessions",
      "type": "Revoke-AzureADUserAllRefreshToken"
    },
    {
      "name": "Post Teams notification",
      "type": "post-message-in-channel"
    }
  ]
}
```

## KQL Enrichment Queries

```kql
// IP enrichment — lookup in threat intelligence
let suspiciousIP = "1.2.3.4";
ThreatIntelligenceIndicator
| where NetworkIP == suspiciousIP
| project TimeGenerated, ThreatType, Confidence, Description

// User risk history
SigninLogs
| where UserPrincipalName == "user@domain.com"
| where TimeGenerated > ago(30d)
| summarize
    TotalLogins=count(),
    FailedLogins=countif(ResultType != "0"),
    Countries=make_set(Location),
    LastLogin=max(TimeGenerated)
```

## SOC Metrics Dashboard (KQL for Sentinel Workbook)

```kql
// MTTD — Mean Time to Detect
SecurityIncident
| where TimeGenerated > ago(30d)
| extend MTTD = datetime_diff('minute', CreatedTime, FirstActivityTime)
| summarize AvgMTTD=avg(MTTD), P95MTTD=percentile(MTTD, 95) by bin(TimeGenerated, 1d)

// MTTR — Mean Time to Respond
SecurityIncident
| where Status == "Closed"
| extend MTTR = datetime_diff('hour', ClosedTime, CreatedTime)
| summarize AvgMTTR=avg(MTTR), P95MTTR=percentile(MTTR, 95) by Severity
```

## Runbook: AKS Suspicious Pod Exec

```markdown
**Trigger:** `kube-audit` log shows `exec` into production pod by non-CI user

1. Identify the user: `kubectl get clusterrolebindings -o yaml | grep <username>`
2. Check what was executed: query `AzureDiagnostics | where log_s contains "exec"`
3. Review pod access since exec time: any file changes, network connections?
4. Containment: `kubectl delete pod <pod>` + apply deny NetworkPolicy
5. Rotate any secrets the pod had access to
6. Revoke user's `kubectl` access pending investigation
7. Escalate to P2 if production pod; P1 if data access confirmed
```
