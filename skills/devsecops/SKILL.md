---
name: devsecops
description: >-
  DevSecOps specialist integrating security into CI/CD pipelines (Azure DevOps, GitHub Actions).
  Covers SAST, DAST, SCA, image scanning, secret detection, IaC security scanning, and
  pipeline hardening. Activate when securing pipelines, adding security gates, or shifting
  security left in the SDLC.
domain: cybersecurity
subdomain: devsecops
tags:
  - devsecops
  - azure-devops
  - github-actions
  - sast
  - sca
  - trivy
  - secret-scanning
  - pipeline-security
  - shift-left
nist_csf: [ID.AM-02, PR.DS-01, DE.CM-01, PR.IP-01]
version: "1.0"
license: Apache-2.0
---

# DevSecOps Skill

## When to Use

- Adding security scanning stages to Azure DevOps or GitHub Actions pipelines
- Reviewing pipeline YAML for secret exposure or insecure practices
- Integrating Trivy, Semgrep, Checkov, or Gitleaks into CI
- Setting up branch protection and pipeline approval gates
- Hardening service connections and pipeline permissions
- Ensuring IaC (Terraform) passes security checks before apply

## Prerequisites

- Azure DevOps project or GitHub repo with pipeline access
- Image registry (ACR) for image scan results
- Secret store (Azure Key Vault) for pipeline credentials

## Security Gates in Azure DevOps

### Stage: Secret Detection
```yaml
- stage: SecurityScan
  jobs:
    - job: SecretScan
      steps:
        - task: Bash@3
          displayName: Gitleaks secret scan
          inputs:
            targetType: inline
            script: |
              docker run --rm -v $(Build.SourcesDirectory):/path \
                zricethezav/gitleaks:latest detect \
                --source /path --exit-code 1 --report-format json \
                --report-path /path/gitleaks-report.json
        - task: PublishBuildArtifacts@1
          condition: always()
          inputs:
            PathtoPublish: gitleaks-report.json
            ArtifactName: security-reports
```

### Stage: Container Image Scan
```yaml
    - job: ImageScan
      steps:
        - task: Bash@3
          displayName: Trivy image scan
          inputs:
            targetType: inline
            script: |
              trivy image \
                --exit-code 1 \
                --severity HIGH,CRITICAL \
                --ignore-unfixed \
                --format table \
                $(imageRepository):$(Build.BuildId)
```

### Stage: IaC Security (Terraform)
```yaml
    - job: TerraformScan
      steps:
        - task: Bash@3
          displayName: Checkov IaC scan
          inputs:
            targetType: inline
            script: |
              checkov -d $(Build.SourcesDirectory)/Terraform \
                --framework terraform \
                --output junitxml > checkov-results.xml || true
        - task: PublishTestResults@2
          inputs:
            testResultsFormat: JUnit
            testResultsFiles: checkov-results.xml
```

### Stage: SAST (Semgrep)
```yaml
    - job: SAST
      steps:
        - task: Bash@3
          displayName: Semgrep SAST scan
          inputs:
            targetType: inline
            script: |
              semgrep ci --config=auto \
                --junit-xml --output semgrep.xml
```

## Pipeline Hardening Checklist

- [ ] No plain-text secrets in YAML — use Variable Groups (secret type) or Key Vault
- [ ] `failOnStandardError: true` on all AzureCLI tasks
- [ ] Service connections use Workload Identity Federation (not SP client secrets)
- [ ] Approval gate before any `prod` stage
- [ ] Pipeline YAML in source control — no UI-only pipelines
- [ ] Branch protection: require PR + at least 1 review before merge to `main`
- [ ] Disable fork PRs from triggering internal pipelines with secrets access
- [ ] `AZURE_DEVOPS_EXT_PAT` rotated quarterly minimum

## Shift-Left Policy

| Gate | Tool | Failure Action |
|------|------|----------------|
| Secret detection | Gitleaks | Block merge |
| Dependency CVE | `pip-audit` / `npm audit` | Block if CRITICAL |
| Container CVE | Trivy | Block if CRITICAL |
| IaC misconfiguration | Checkov | Warn (configurable to block) |
| SAST | Semgrep | Warn on HIGH |
| Policy compliance | OPA/Conftest | Block |

## Verification

```bash
# Test pipeline locally with act (GitHub Actions)
act push --secret-file .env.test

# Validate ADO pipeline
az pipelines run --name <pipeline> --branch feature/devsecops-test
```
