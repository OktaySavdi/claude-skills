---
name: threat-hunting
description: >-
  Proactive threat hunting across Azure, AKS, and on-prem environments using KQL,
  Elastic, and Prometheus. Builds hypothesis-driven hunt playbooks, detects living-off-the-land
  techniques, lateral movement, and persistence. Activate when hunting for adversary
  activity, writing detection rules, or investigating anomalies.
domain: cybersecurity
subdomain: threat-hunting
tags:
  - threat-hunting
  - kql
  - sentinel
  - elastic
  - mitre-attack
  - detection
  - lateral-movement
  - persistence
nist_csf: [DE.AE-01, DE.AE-02, DE.CM-01, RS.AN-01]
mitre_attack: [T1078, T1059, T1021, T1053, T1547, T1105]
version: "1.0"
license: Apache-2.0
---

# Threat Hunting Skill

## When to Use

- Writing KQL queries for Azure Sentinel / Log Analytics
- Building Elastic detection rules (EQL, KQL)
- Investigating alerts or anomalies in AKS/Azure logs
- Creating hunt playbooks mapped to MITRE ATT&CK
- Detecting living-off-the-land (LOLBins), lateral movement, or C2 beaconing
- Analysing Prometheus/Grafana metrics for operational anomalies

## Prerequisites

- Log Analytics workspace or Elastic cluster with data ingested
- MITRE ATT&CK Navigator access
- Hypothesis about adversary TTP

## Hunt Methodology (PEAK Framework)

1. **Purpose** — Define hypothesis: "Attacker may have compromised a service principal and is querying Key Vault secrets"
2. **Execute** — Run queries across relevant log sources
3. **Analyse** — Pivot on IOCs; correlate with ATT&CK techniques
4. **Knowledge** — Document findings; create detection rule if hunt confirms activity

## Azure Sentinel KQL Hunts

```kql
// Hunt: Suspicious Azure CLI from new ASN
AzureActivity
| where OperationNameValue startswith "MICROSOFT.KEYVAULT"
| join kind=leftouter (SigninLogs | project UserPrincipalName, ASN=AutonomousSystemNumber, IPAddress) on $left.Caller == $right.UserPrincipalName
| summarize OpsCount=count(), ASNs=make_set(ASN) by Caller, bin(TimeGenerated, 1h)
| where array_length(ASNs) > 2

// Hunt: New service principal role assignment
AuditLogs
| where Category == "RoleManagement"
| where OperationName == "Add member to role"
| where Result == "success"
| extend TargetUser = tostring(TargetResources[0].userPrincipalName)
| where TargetUser !in (known_service_principals)

// Hunt: Lateral movement via AKS exec
AzureDiagnostics
| where Category == "kube-audit"
| where log_s contains "exec"
| extend User = extract('"username":"([^"]+)"', 1, log_s)
| summarize ExecCount=count() by User, PodName=extract('"name":"([^"]+)"', 1, log_s)
| where ExecCount > 5
```

## Elastic (EQL) Hunts

```eql
// Detect reverse shell pattern
process where process.name in ("bash", "sh", "zsh") and
  process.args : ("/dev/tcp/*", "nc", "ncat") and
  process.parent.name : ("python*", "ruby", "perl")

// Detect credential dumping
process where event.type == "start" and
  process.name in ("mimikatz.exe", "procdump.exe") or
  (process.name == "lsass.exe" and process.parent.name != "wininit.exe")
```

## MITRE ATT&CK Mapping Template

| Hypothesis | Technique | Log Source | KQL/Query |
|---|---|---|---|
| SP secret theft | T1528 | AuditLogs | `AuditLogs | where OperationName == "Retrieve application"` |
| Container escape | T1611 | kube-audit | `AzureDiagnostics | where log_s contains "privileged"` |
| Scheduled task persistence | T1053.005 | SecurityEvent | `SecurityEvent | where EventID == 4698` |

## Verification

- Document true positive rate per hunt hypothesis
- Convert confirmed hunts to automated detection rules
- Update MITRE ATT&CK Navigator heatmap with covered techniques
