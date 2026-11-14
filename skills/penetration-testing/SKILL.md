---
name: penetration-testing
description: >-
  Penetration testing specialist for Azure and Kubernetes environments. Covers reconnaissance,
  privilege escalation paths, lateral movement, AKS attack vectors, and reporting.
  For AUTHORIZED engagements only. Activate when performing a sanctioned pentest,
  purple team exercise, or attack path review.
domain: cybersecurity
subdomain: penetration-testing
tags:
  - penetration-testing
  - azure-pentest
  - kubernetes-pentest
  - purple-team
  - attack-simulation
  - mitre-attack
  - authorized-only
nist_csf: [ID.RA-05, PR.IP-09, RS.MI-01]
mitre_attack: [T1078, T1190, T1611, T1613, T1548]
version: "1.0"
license: Apache-2.0
---

# Penetration Testing Skill

> **AUTHORIZATION REQUIRED**: This skill is for use only during authorized security
> testing engagements, CTF competitions, purple team exercises, or security research
> with explicit written permission. Never use against systems you do not own or have
> explicit authorization to test.

## When to Use

- Conducting authorized Azure or AKS penetration tests
- Purple team exercises simulating adversary TTPs
- Attack path analysis for security architecture review
- CTF challenges involving cloud or container environments
- Validating Kyverno/OPA policies block specific attack vectors

## Azure Attack Surface — Common Pentest Targets

### Reconnaissance
```bash
# Enumerate Azure tenant (unauthenticated)
curl https://login.microsoftonline.com/<domain>.onmicrosoft.com/.well-known/openid-configuration

# Enumerate storage accounts (check public blobs)
az storage account list --query "[].name" -o tsv | while read acct; do
  az storage container list --account-name "$acct" --auth-mode login \
    --query "[?properties.publicAccess!='None'].name" -o tsv 2>/dev/null
done

# Check for exposed management ports
az network nsg list --query "[].securityRules[?destinationPortRange=='3389' || destinationPortRange=='22' && sourceAddressPrefix=='*']"
```

### Privilege Escalation — Azure
Common paths to enumerate:
1. Reader → Key Vault reader → secret access → SP creds → Contributor
2. Automation Account RunAs certificate export
3. VM metadata service → MSI token → scoped permissions
4. Logic App managed identity with excessive scope

```bash
# Check MSI token scope (from inside VM)
curl -H "Metadata:true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" \
  | python3 -c "import sys,json; t=json.load(sys.stdin)['access_token']; import base64; print(json.loads(base64.b64decode(t.split('.')[1]+'==').decode()))"
```

### AKS Attack Vectors
```bash
# Container escape check — verify privileged pod is blocked by policy
# (This should be DENIED by Kyverno — use to validate policies)
cat <<EOF | kubectl apply --dry-run=server -f -
apiVersion: v1
kind: Pod
metadata: {name: test-priv, namespace: default}
spec:
  containers:
  - name: test
    image: busybox
    securityContext: {privileged: true}
EOF
# Expected: admission webhook denies this

# Check for overly permissive ServiceAccount
kubectl get serviceaccounts -A -o json | \
  jq '.items[] | select(.automountServiceAccountToken != false) | {ns: .metadata.namespace, sa: .metadata.name}'

# Check for default SA with roles
kubectl get rolebindings,clusterrolebindings -A -o json | \
  jq '.items[] | select(.subjects[]?.name=="default" and .subjects[]?.kind=="ServiceAccount")'
```

## MITRE ATT&CK — AKS Technique Coverage

| Technique | ID | Test Method | Expected Control |
|---|---|---|---|
| Deploy Container | T1610 | Create pod with `privileged: true` | Kyverno deny |
| Container Escape | T1611 | Mount host path `/` | Kyverno deny hostPath |
| Credentials from APIs | T1528 | Read service account token | Disable automount |
| Lateral Movement via Exec | T1021 | `kubectl exec` into pod | Audit log + alert |
| Resource Hijack | T1496 | GPU/CPU intensive pod | ResourceQuota limit |

## Purple Team Exercise Template

```markdown
## Purple Team Exercise — AKS Privilege Escalation

**Date:** YYYY-MM-DD
**Scope:** AKS cluster <name> in <subscription>
**Authorization:** Signed by CISO — <reference>

### Attack Scenario
Attacker has compromised a developer workstation with `kubectl` access
to the `staging` namespace. Goal: reach `production` namespace secrets.

### Steps
1. [ ] Enumerate staging namespace: `kubectl get all -n staging`
2. [ ] Check SA permissions: `kubectl auth can-i --list -n staging`
3. [ ] Attempt cross-namespace exec (should fail)
4. [ ] Attempt secrets read in production (should fail)

### Expected Controls
- NetworkPolicy: no cross-namespace traffic
- RBAC: staging SA cannot read production
- Kyverno: no hostPath/privileged pods

### Findings
| Finding | Severity | Control Gap | Remediation |
|---|---|---|---|
| | | | |
```

## Reporting Template

```markdown
## Penetration Test Report — <Scope>

**Engagement:** <client/project>
**Period:** <dates>
**Tester:** <name>
**Authorization:** <reference>

### Executive Summary
<3-5 sentences: scope, critical findings, overall risk rating>

### Critical Findings
| ID | Title | CVSS | Affected Resource | Status |
|---|---|---|---|---|

### Detailed Findings
#### FIND-001: <Title>
**Severity:** Critical/High/Medium/Low
**CVSS:** X.X
**Description:** ...
**Evidence:** ...
**Recommendation:** ...
**References:** CVE-XXXX / MITRE TXXXX
```
