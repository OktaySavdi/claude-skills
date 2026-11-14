---
name: identity-access-management
description: >-
  Azure IAM specialist covering RBAC, Managed Identity, Entra ID, PIM, Conditional
  Access, Workload Identity Federation, and Kubernetes RBAC. Detects privilege escalation
  paths, audits access assignments, and designs least-privilege architectures. Activate
  for any identity, access, or authentication security question.
domain: cybersecurity
subdomain: identity-access-management
tags:
  - iam
  - azure-ad
  - entra-id
  - rbac
  - managed-identity
  - pim
  - conditional-access
  - workload-identity
  - kubernetes-rbac
nist_csf: [PR.AC-01, PR.AC-03, PR.AC-04, PR.AC-06, DE.CM-03]
mitre_attack: [T1078, T1098, T1528, T1548]
version: "1.0"
license: Apache-2.0
---

# Identity & Access Management Skill

## When to Use

- Auditing Azure RBAC assignments for over-privilege
- Designing Workload Identity (UAMI + federated credentials) for AKS pods
- Writing Kubernetes RBAC Role/ClusterRole manifests
- Reviewing Conditional Access policies for gaps
- Detecting privilege escalation paths in Azure
- PIM activation policy design
- Service principal vs. Managed Identity decision

## Prerequisites

- `az` CLI authenticated with appropriate read permissions
- `kubectl` context set for Kubernetes RBAC work
- Entra ID read permissions (or Global Reader role)

## Azure RBAC Audit

```bash
# List all role assignments at subscription scope
az role assignment list --all --include-inherited \
  --query "[].{Principal:principalName,Role:roleDefinitionName,Scope:scope}" \
  -o table

# Find Owners and Contributors at subscription level (highest risk)
az role assignment list --all \
  --query "[?roleDefinitionName=='Owner' || roleDefinitionName=='Contributor'] | [?contains(scope, '/subscriptions/') && !contains(scope, '/resourceGroups/')]" \
  -o table

# Find service principals with direct role assignments (prefer Managed Identity)
az role assignment list --all \
  --query "[?principalType=='ServicePrincipal'].{SP:principalName,Role:roleDefinitionName,Scope:scope}" \
  -o table
```

## Workload Identity (UAMI) Pattern

```bash
# 1. Create UAMI
az identity create -n <name> -g <rg> -l <location>

# 2. Get OIDC issuer URL
az aks show -n <cluster> -g <rg> --query oidcIssuerProfile.issuerUrl -o tsv

# 3. Create federated credential
az identity federated-credential create \
  --identity-name <name> \
  --resource-group <rg> \
  --name <fc-name> \
  --issuer <oidc-issuer> \
  --subject system:serviceaccount:<namespace>:<sa-name> \
  --audience api://AzureADTokenExchange

# 4. Kubernetes ServiceAccount annotation
kubectl annotate serviceaccount <sa-name> \
  azure.workload.identity/client-id=<uami-client-id> \
  -n <namespace>
```

```yaml
# Pod spec for workload identity
metadata:
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: <sa-name>
```

## Kubernetes RBAC — Least Privilege

```yaml
# Namespace-scoped read-only role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: readonly
  namespace: production
rules:
  - apiGroups: [""]
    resources: [pods, services, configmaps]
    verbs: [get, list, watch]
---
# Audit cluster-admin bindings (should be near-zero)
# kubectl get clusterrolebindings -o json | jq '.items[] | select(.roleRef.name=="cluster-admin")'
```

## Privilege Escalation Detection (KQL)

```kql
// Detect new Owner assignments
AzureActivity
| where OperationNameValue == "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE"
| where ActivityStatusValue == "Success"
| extend RoleId = tostring(parse_json(tostring(parse_json(Properties).requestbody)).properties.roleDefinitionId)
| where RoleId endswith "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"  // Owner role GUID
| project TimeGenerated, Caller, ResourceGroup

// Detect PIM activation for high-privilege roles
AuditLogs
| where Category == "RoleManagement"
| where OperationName == "Activate eligible role assignment request (PIM activation)"
| extend Role = tostring(TargetResources[0].displayName)
| where Role in ("Global Administrator", "Privileged Role Administrator", "Security Administrator")
```

## IAM Checklist

- [ ] No direct user assignments to subscription-level Owner/Contributor
- [ ] Service principals replaced by Managed Identity where possible
- [ ] Workload Identity used for AKS pods (not `automountServiceAccountToken: true`)
- [ ] PIM enabled for all privileged roles (Contributor+)
- [ ] Conditional Access: MFA required for all users, block legacy auth
- [ ] No permanent Guest accounts with resource access
- [ ] Service principal secrets: 90-day rotation, or use certificate auth
- [ ] `kubectl` admin access via Just-In-Time (PIM/Bastion) not always-on

## Verification

```bash
# No wildcards in K8s RBAC
kubectl get clusterroles -o json | jq '.items[] | select(.rules[].verbs[]=="*") | .metadata.name'

# Verify UAMI federated credential
az identity federated-credential list --identity-name <name> -g <rg> -o table
```
