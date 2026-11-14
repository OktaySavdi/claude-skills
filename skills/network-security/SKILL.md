---
name: network-security
description: >-
  Network security specialist for Azure and Kubernetes environments. Covers NSG design,
  Kubernetes NetworkPolicy, Private Endpoints, Azure Firewall, DNS security, and traffic
  inspection. Activate for any network security design, firewall rule review, or egress
  control question.
domain: cybersecurity
subdomain: network-security
tags:
  - network-security
  - nsg
  - networkpolicy
  - azure-firewall
  - private-endpoint
  - egress-control
  - dns-security
  - aks
nist_csf: [PR.AC-05, PR.DS-02, DE.CM-01, ID.AM-03]
mitre_attack: [T1046, T1571, T1090, T1048]
version: "1.0"
license: Apache-2.0
---

# Network Security Skill

## When to Use

- Designing NSG rules for Azure resources
- Writing Kubernetes NetworkPolicy for namespace isolation
- Reviewing Azure Firewall rules or Private Endpoint configurations
- Implementing egress lockdown for AKS workloads
- DNS security — Private DNS zones, DoH, DNS filtering
- Hub-spoke network topology security review
- Detecting unauthorized network connections or port scans

## Prerequisites

- `az` CLI and `kubectl` access
- Network topology diagram (hub-spoke or flat)
- Understanding of workload communication requirements

## Kubernetes NetworkPolicy — Default Deny + Allow

```yaml
# Step 1: Default deny all in namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# Step 2: Allow only what's needed
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - port: 5432
  policyTypes: [Ingress]
---
# Step 3: Allow egress to Azure DNS only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: production
spec:
  podSelector: {}
  egress:
    - ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
  policyTypes: [Egress]
```

## Azure NSG — Principle of Least Access

```bash
# Audit overly permissive rules (0.0.0.0/0 inbound)
az network nsg list --query \
  "[].{NSG:name,RG:resourceGroup}" -o tsv | while read nsg rg; do
  az network nsg rule list -n "$nsg" -g "$rg" \
    --query "[?sourceAddressPrefix=='*' && direction=='Inbound' && access=='Allow'].{Name:name,Priority:priority,Port:destinationPortRange}" \
    -o table
done

# Create deny-all inbound with exceptions
az network nsg rule create \
  --nsg-name <nsg> --resource-group <rg> \
  --name DenyAllInbound --priority 4096 \
  --direction Inbound --access Deny \
  --protocol '*' --source-address-prefixes '*' \
  --destination-port-ranges '*'
```

## AKS Egress Lockdown (Azure Firewall)

```bash
# Required AKS egress FQDNs
REQUIRED_FQDNS=(
  "*.hcp.<region>.azmk8s.io"
  "mcr.microsoft.com"
  "*.data.mcr.microsoft.com"
  "management.azure.com"
  "login.microsoftonline.com"
)

# Add to Azure Firewall application rule collection
for fqdn in "${REQUIRED_FQDNS[@]}"; do
  az network firewall application-rule create \
    --firewall-name <fw> --resource-group <rg> \
    --collection-name AKS-Required --priority 200 --action Allow \
    --name "allow-${fqdn//\*/wildcard}" \
    --target-fqdns "$fqdn" \
    --protocols https=443
done
```

## Private Endpoint Pattern

```bash
# Create Private Endpoint for AKV
az network private-endpoint create \
  --name akv-pe \
  --resource-group <rg> \
  --vnet-name <vnet> \
  --subnet <subnet> \
  --private-connection-resource-id $(az keyvault show -n <akv> --query id -o tsv) \
  --group-id vault \
  --connection-name akv-connection

# Create Private DNS Zone + link
az network private-dns zone create -g <rg> -n "privatelink.vaultcore.azure.net"
az network private-dns link vnet create -g <rg> \
  --zone-name "privatelink.vaultcore.azure.net" \
  --name akv-dns-link --virtual-network <vnet> --registration-enabled false
```

## Security Checklist

- [ ] All AKS subnets have NSG attached
- [ ] No `0.0.0.0/0` inbound except load balancer on 443
- [ ] Kubernetes NetworkPolicy: default-deny per namespace
- [ ] AKS API server accessible only from jump host / private endpoint
- [ ] Key Vault, ACR, Storage accessed via Private Endpoint
- [ ] Egress routed through Azure Firewall (UDR `0.0.0.0/0 → FW`)
- [ ] DNS: Private DNS Resolver for split-horizon, no public DNS leakage

## Verification

```bash
# Verify NetworkPolicy enforcement
kubectl run test-pod --image=busybox --rm -it -- sh
# Inside pod: wget http://other-service:8080  # should fail

# Verify no public IP on AKS API
az aks show -n <cluster> -g <rg> --query apiServerAccessProfile.enablePrivateCluster
```
