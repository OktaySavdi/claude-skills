---
name: container-security
description: >-
  Container and Kubernetes security specialist. Hardens container images, audits
  Dockerfiles, enforces Pod Security Standards, detects runtime threats, and reviews
  supply-chain integrity. Activate for any Docker, OCI image, or Kubernetes workload
  security question.
domain: cybersecurity
subdomain: container-security
tags:
  - docker
  - kubernetes
  - aks
  - container-hardening
  - image-scanning
  - pod-security
  - supply-chain
  - trivy
  - distroless
nist_csf: [PR.DS-01, PR.AC-03, DE.CM-01, ID.AM-02]
mitre_attack: [T1610, T1611, T1613, T1525]
version: "1.0"
license: Apache-2.0
---

# Container Security Skill

## When to Use

- Reviewing a Dockerfile or container image for vulnerabilities
- Hardening Kubernetes workload manifests (securityContext)
- Trivy scan findings remediation
- Supply chain security — image signing, SBOM, provenance
- Detecting container escape or privilege escalation attempts
- Writing Kyverno policies to enforce container security controls
- Any question about distroless images, Pod Security Standards, or OCI security

## Prerequisites

- `trivy`, `docker`, `kubectl` available
- Access to image registry (ACR, Docker Hub, etc.)
- Kyverno or OPA/Gatekeeper installed for policy enforcement

## Core Competencies

### Dockerfile Hardening Checklist
- [ ] Use minimal base: `distroless`, `alpine`, or `scratch`
- [ ] Pin to digest: `FROM gcr.io/distroless/static-debian12@sha256:<digest>`
- [ ] Never run as root — set `USER nonroot` or `USER 65532`
- [ ] Multi-stage build — no build tools in final image
- [ ] No secrets in `ENV`, `ARG`, or `COPY`
- [ ] Read-only filesystem where possible
- [ ] `HEALTHCHECK` defined

### Pod Security Context (Restricted Profile)
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65532
  runAsGroup: 65532
  fsGroup: 65532
  seccompProfile:
    type: RuntimeDefault
containers:
  - securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: [ALL]
```

### Kyverno Policy — Enforce Restricted Profile
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-pod-security-restricted
spec:
  validationFailureAction: Enforce
  rules:
    - name: restrict-privilege-escalation
      match:
        resources: {kinds: [Pod]}
      validate:
        cel:
          expressions:
            - expression: >
                object.spec.containers.all(c,
                  has(c.securityContext) &&
                  c.securityContext.allowPrivilegeEscalation == false)
              message: "allowPrivilegeEscalation must be false"
```

### Image Scanning
```bash
# Full image scan
trivy image --severity HIGH,CRITICAL <image>:<tag>

# Scan Dockerfile
trivy config Dockerfile

# Generate SBOM
trivy image --format spdx-json -o sbom.json <image>

# Scan K8s manifests
trivy k8s --report summary cluster
```

### Supply Chain Security
- Sign images with Cosign: `cosign sign --key cosign.key <image>@<digest>`
- Verify in Kyverno: use `verifyImages` rule with Cosign/Notation
- SBOM attestation: attach SPDX/CycloneDX to image
- ACR image policy: geo-restrictions, trust policies

## Workflow

1. **Scan** — `trivy image` on every image pre-deployment
2. **Review** — Dockerfile multi-stage, USER, pinned digest
3. **Manifest audit** — securityContext fields present and correct
4. **Policy check** — Kyverno `kyverno test` passes
5. **Runtime** — Falco rules for anomalous syscalls
6. **Verify** — Re-scan post-fix; policy dry-run passes

## Verification

```bash
# Confirm no critical CVEs
trivy image --exit-code 1 --severity CRITICAL <image>

# Confirm non-root
docker inspect --format='{{.Config.User}}' <image>

# Kyverno dry-run
kubectl apply --dry-run=server -f deployment.yaml
```
