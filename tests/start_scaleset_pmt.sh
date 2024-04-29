#!/bin/bash
INSTALLATION_NAME="pmt-runner"
NAMESPACE="arc-runner-pmt"
GITHUB_CONFIG_URL="https://github.com/markmac99/pi-meteortools"
GITHUB_PAT=$(cat ~/.ssh/gh_pat_containers)
helm upgrade --install "${INSTALLATION_NAME}" \
    --namespace "${NAMESPACE}" \
    --create-namespace \
    -f ./pmt_values.yaml \
    --set githubConfigUrl="${GITHUB_CONFIG_URL}" \
    --set githubConfigSecret.github_token="${GITHUB_PAT}" \
    oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set

