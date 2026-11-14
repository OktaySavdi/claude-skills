---
name: threat-intelligence
description: >-
  Threat intelligence specialist covering IOC analysis, MITRE ATT&CK mapping, threat
  actor profiling, STIX/TAXII feeds, and intelligence-driven defence. Activate when
  analysing threat intel reports, building detection rules from TTPs, or researching
  adversary groups targeting cloud and Kubernetes environments.
domain: cybersecurity
subdomain: threat-intelligence
tags:
  - threat-intelligence
  - mitre-attack
  - ioc
  - stix
  - taxii
  - ttp
  - adversary-profiling
  - sentinel
nist_csf: [ID.RA-02, ID.RA-03, DE.AE-02, RS.AN-02]
mitre_attack: [T1589, T1590, T1591, T1592, T1593]
version: "1.0"
license: Apache-2.0
---

# Threat Intelligence Skill

## When to Use

- Analysing a threat intelligence report or ISAC advisory
- Mapping adversary TTPs to MITRE ATT&CK techniques
- Building detection rules from IOC feeds in Azure Sentinel
- Researching threat actors targeting Azure or Kubernetes environments
- Creating threat intel-driven Kyverno/Sentinel detection rules
- Evaluating if a Wiz or Defender alert matches known threat actor behaviour

## Prerequisites

- Azure Sentinel with Threat Intelligence data connector
- MITRE ATT&CK Navigator access
- Access to STIX/TAXII feeds or MSTIC advisories

## IOC Ingestion — Azure Sentinel

```kql
// Query ingested threat intelligence IOCs
ThreatIntelligenceIndicator
| where TimeGenerated > ago(7d)
| where Active == true
| summarize Count=count() by ThreatType, IndicatorType=IndicatorTypes
| order by Count desc

// Correlate IOCs with sign-in logs
let MaliciousIPs = ThreatIntelligenceIndicator
  | where Active == true and IndicatorTypes has "ip-addr"
  | distinct NetworkIP;
SigninLogs
| where IPAddress in (MaliciousIPs)
| project TimeGenerated, UserPrincipalName, IPAddress, Location, ResultType

// Correlate IOCs with DNS queries
let MaliciousDomains = ThreatIntelligenceIndicator
  | where Active == true and IndicatorTypes has "domain-name"
  | distinct DomainName;
DnsEvents
| where Name in (MaliciousDomains)
| project TimeGenerated, ClientIP, Name, QueryType
```

## MITRE ATT&CK Mapping Template

```markdown
## Threat Actor TTP Mapping — <Group Name>

**Actor:** <name> (aliases: ...)
**Motivation:** Financial / Espionage / Hacktivism
**Targeting:** Azure tenants, AKS clusters, SaaS applications

### Observed TTPs

| Phase | Technique | ID | Detection | Kyverno/Sentinel Rule |
|---|---|---|---|---|
| Initial Access | Valid Accounts: Cloud | T1078.004 | Sentinel: impossible travel rule | — |
| Execution | Cloud Administration Command | T1651 | AuditLogs: RunCommand op | — |
| Persistence | Account Manipulation | T1098 | AuditLogs: role assignment | — |
| Lateral Movement | Remote Services | T1021 | AzureActivity: VM access | — |
| Exfiltration | Transfer to Cloud Account | T1537 | Storage: unusual egress | — |
```

## IOC Enrichment Workflow

```bash
# Enrich IP against OSINT (requires ipinfo.io token)
IP="1.2.3.4"
curl -s "https://ipinfo.io/${IP}?token=${IPINFO_TOKEN}" | \
  jq '{ip, org, country, hostname, abuse: .abuse.email}'

# Check domain in VirusTotal (requires API key)
DOMAIN="evil.example.com"
curl -s "https://www.virustotal.com/api/v3/domains/${DOMAIN}" \
  -H "x-apikey: ${VT_API_KEY}" | \
  jq '{malicious: .data.attributes.last_analysis_stats.malicious, categories: .data.attributes.categories}'
```

## Threat Intel → Detection Rule Pipeline

1. **Receive** intel report (ISAC, MSTIC, vendor advisory)
2. **Extract** IOCs: IPs, domains, hashes, TTPs
3. **Validate** IOCs: age, confidence, false-positive risk
4. **Ingest** into Sentinel TI data connector or watchlist
5. **Create** analytics rule correlated against log sources
6. **Test** rule against historical data (no FPs in last 30 days)
7. **Deploy** rule with appropriate alert severity
8. **Track** via MITRE Navigator — mark technique as covered

## Sentinel Watchlist — IOC Management

```bash
# Upload IOC watchlist to Sentinel
az sentinel watchlist create \
  --workspace-name <workspace> \
  --resource-group <rg> \
  --watchlist-alias "MaliciousIPs" \
  --display-name "Threat Intel - Malicious IPs" \
  --items-search-key "IPAddress" \
  --source-type "Local file" \
  --raw-content @iocs.csv

# Query watchlist in KQL
_GetWatchlist('MaliciousIPs')
| join kind=inner (SigninLogs | where TimeGenerated > ago(1d)) on $left.IPAddress == $right.IPAddress
| project TimeGenerated, UserPrincipalName, IPAddress, ThreatType
```

## STIX 2.1 Indicator Creation

```python
from stix2 import Indicator, Bundle

indicator = Indicator(
    name="Malicious IP - APT Example",
    pattern="[ipv4-addr:value = '1.2.3.4']",
    pattern_type="stix",
    valid_from="2024-01-15T00:00:00Z",
    labels=["malicious-activity"],
    confidence=85,
    external_references=[
        {"source_name": "internal-ir", "external_id": "IR-2024-001"}
    ]
)

bundle = Bundle(objects=[indicator])
print(bundle.serialize(pretty=True))
```
