---
name: cloud-security
description: >-
  Cloud security specialist covering Azure, AKS, and multi-cloud threat detection,
  misconfiguration remediation, CSPM findings, identity abuse detection, and
  cloud-native security controls. Activate for any Azure/cloud security review,
  Defender for Cloud findings, or cloud threat hunting.
domain: cybersecurity
subdomain: cloud-security
tags:
  - azure
  - aks
  - cloud-security
  - cspm
  - defender-for-cloud
  - kql
  - threat-hunting
  - misconfiguration
  - identity
nist_csf: [DE.CM-01, PR.AC-01, PR.AC-03, RS.MA-01, ID.AM-03]
mitre_attack: [T1078, T1530, T1537, T1619, T1580]
version: "1.0"
license: Apache-2.0
---

# Cloud Security Skill

## When to Use

- Reviewing Azure security posture / Defender for Cloud alerts
- Investigating suspicious Azure activity logs or sign-in events
- AKS cluster security hardening or audit
- Remediating Wiz/CSPM findings in cloud environments
- Detecting privilege escalation, lateral movement, or data exfil in Azure
- Writing KQL threat-hunting queries for Azure Monitor / Sentinel
- Any `az`, `kubectl`, Azure Policy, or RBAC security question

## Prerequisites

- Access to Azure subscription or Log Analytics workspace
- `az` CLI authenticated, `kubectl` context set
- KQL familiarity for query-based detection

## Core Competencies

### Azure Identity & Access
- Detect overly permissive role assignments (`Owner`, `Contributor` at subscription scope)
- Identify service principal secret exposure vs. UAMI/workload identity
- Audit Conditional Access policy gaps
- Hunt impossible travel / anomalous sign-in patterns

### AKS Security
- Pod Security Standards enforcement (Restricted profile)
- Kyverno/OPA policy coverage gaps
- Workload identity (UAMI + federated credential) configuration
- Audit RBAC roles — `cluster-admin` bindings especially
- Network Policy coverage, egress lockdown
- Image provenance: registry restriction, digest pinning

### Azure Defender / Sentinel Detections
```kql
// Detect privilege escalation via role assignment
AzureActivity
| where OperationNameValue == "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE"
| where ActivityStatusValue == "Success"
| extend PrincipalId = tostring(parse_json(Properties).requestbody)
| project TimeGenerated, Caller, ResourceGroup, PrincipalId

// Impossible travel detection
SigninLogs
| where ResultType == "0"
| summarize Locations=make_set(Location), Count=count() by UserPrincipalName, bin(TimeGenerated, 1h)
| where array_length(Locations) > 1

// Key Vault access from new IP
AzureDiagnostics
| where ResourceType == "VAULTS"
| where OperationName == "SecretGet"
| summarize IPs=make_set(CallerIPAddress) by id_s
| where array_length(IPs) > 3
```

### CSPM / Misconfiguration Remediation
- Storage account public access — disable `allowBlobPublicAccess`
- NSG overly permissive rules (0.0.0.0/0 inbound)
- Missing diagnostic settings on Key Vault, AKS, Storage
- Unencrypted disks, CMK vs. PMK decisions
- Defender for Servers / Containers not enabled on subscriptions

## Workflow

1. **Scope** — Identify affected subscription, resource group, or cluster
2. **Enumerate** — `az resource list`, `kubectl get all -A`, check RBAC assignments
3. **Detect** — Run KQL queries or Wiz policy checks
4. **Prioritise** — CVSS + blast radius + exploitability
5. **Remediate** — Terraform IaC fix preferred over portal click
6. **Verify** — Re-run detection query; confirm finding closed in CSPM

## Verification

```bash
# Verify AKS RBAC audit
kubectl get clusterrolebindings -o json | jq '.items[] | select(.roleRef.name=="cluster-admin") | .subjects'

# Verify no public storage
az storage account list --query "[?allowBlobPublicAccess==true].name" -o tsv

# Verify Defender enabled
az security pricing list --query "[?pricingTier=='Standard'].name" -o tsv
```
