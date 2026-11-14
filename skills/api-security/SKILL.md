---
name: api-security
description: >-
  API security specialist covering OWASP API Top 10, Azure API Management security,
  authentication (OAuth2, JWT, API keys), rate limiting, input validation, and API
  threat detection. Activate when reviewing API security, securing APIM policies,
  or investigating API abuse.
domain: cybersecurity
subdomain: api-security
tags:
  - api-security
  - owasp-api-top10
  - apim
  - oauth2
  - jwt
  - rate-limiting
  - azure
  - kubernetes
nist_csf: [PR.AC-03, PR.DS-02, DE.CM-01, ID.RA-01]
version: "1.0"
license: Apache-2.0
---

# API Security Skill

## When to Use

- Reviewing an API for OWASP API Security Top 10 vulnerabilities
- Securing Azure API Management policies
- JWT/OAuth2 implementation review
- Designing rate limiting and throttling
- Detecting API abuse patterns in logs
- Writing Kyverno or OPA policies to restrict API exposure in Kubernetes

## OWASP API Top 10 Checklist

- [ ] **API1 — Broken Object Level Auth**: Every request validates caller owns the resource
- [ ] **API2 — Broken Authentication**: JWT validated (signature, exp, iss, aud); no API keys in URLs
- [ ] **API3 — Broken Object Property Auth**: Response filtering — never return all fields
- [ ] **API4 — Unrestricted Resource Consumption**: Rate limiting + pagination limits enforced
- [ ] **API5 — Broken Function Level Auth**: Admin endpoints separate, not just hidden
- [ ] **API6 — Unrestricted Access to Sensitive Business Flows**: Bot detection, CAPTCHA for abuse-prone flows
- [ ] **API7 — Server Side Request Forgery**: URL parameters never passed to internal HTTP clients unvalidated
- [ ] **API8 — Security Misconfiguration**: No debug endpoints in prod; CORS locked down
- [ ] **API9 — Improper Inventory Management**: API versioning tracked; old versions retired
- [ ] **API10 — Unsafe Consumption of APIs**: Validate all upstream API responses; no trust by default

## Azure API Management Security Policies

```xml
<!-- Inbound policy: JWT validation + rate limiting -->
<policies>
  <inbound>
    <!-- Rate limiting: 100 req/min per subscription key -->
    <rate-limit calls="100" renewal-period="60" />

    <!-- JWT validation -->
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401"
                  failed-validation-error-message="Unauthorized">
      <openid-config url="https://login.microsoftonline.com/{tenant}/.well-known/openid-configuration" />
      <audiences>
        <audience>api://{app-id}</audience>
      </audiences>
      <required-claims>
        <claim name="roles" match="any">
          <value>API.Read</value>
          <value>API.Write</value>
        </claim>
      </required-claims>
    </validate-jwt>

    <!-- Remove internal headers before forwarding -->
    <set-header name="X-Internal-User" exists-action="delete" />
  </inbound>

  <outbound>
    <!-- Strip sensitive headers from response -->
    <set-header name="X-Powered-By" exists-action="delete" />
    <set-header name="Server" exists-action="delete" />
  </outbound>
</policies>
```

## JWT Security Review

```python
import jwt
from jwt import PyJWKClient

def validate_token(token: str, audience: str, issuer: str) -> dict:
    jwks_client = PyJWKClient(f"{issuer}/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],  # never allow "none" or "HS256" with public key
        audience=audience,
        issuer=issuer,
        options={
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "require": ["exp", "iss", "aud", "sub"],
        }
    )
```

## API Abuse Detection (KQL — APIM Logs)

```kql
// Detect rate limit violations (potential abuse)
ApiManagementGatewayLogs
| where ResponseCode == 429
| summarize Count=count() by CallerIpAddress, OperationId, bin(TimeGenerated, 5m)
| where Count > 50
| order by Count desc

// Detect authentication failures (credential stuffing)
ApiManagementGatewayLogs
| where ResponseCode in (401, 403)
| summarize FailCount=count(), Ops=make_set(OperationId) by CallerIpAddress, bin(TimeGenerated, 10m)
| where FailCount > 20

// Detect unusual data volumes (data exfiltration indicator)
ApiManagementGatewayLogs
| where ResponseCode == 200
| summarize TotalBytes=sum(ResponseSize) by CallerIpAddress, bin(TimeGenerated, 1h)
| where TotalBytes > 100000000  // 100MB threshold
```

## Kubernetes — Restrict API Exposure

```yaml
# Kyverno: Block services of type LoadBalancer without annotation
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-internal-lb-annotation
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-internal-annotation
      match:
        resources:
          kinds: [Service]
      preconditions:
        all:
          - key: "{{request.object.spec.type}}"
            operator: Equals
            value: LoadBalancer
      validate:
        cel:
          expressions:
            - expression: >
                has(object.metadata.annotations) &&
                "service.beta.kubernetes.io/azure-load-balancer-internal" in object.metadata.annotations &&
                object.metadata.annotations["service.beta.kubernetes.io/azure-load-balancer-internal"] == "true"
              message: "LoadBalancer services must be internal (annotate with azure-load-balancer-internal: true)"
```
