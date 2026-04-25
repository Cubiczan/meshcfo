#!/usr/bin/env bash
# Quick CLI examples for the Multi-Agent CFO OS.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Investment case ==="
PYTHONPATH=src python3 -m cme.cli cfo-os \
  --task investment_case \
  --title "Fund enterprise tier Q3" \
  --company "Acme" \
  --problem "Should we fund a dedicated enterprise tier this quarter?" \
  --amount 4000000 \
  --payback-months 14 \
  --min-runway 12 \
  --current-runway 18 \
  --upside "Higher ACV" --upside "Lower strategic-account churn" \
  --risk "Adoption lag" --risk "Implementation complexity" \
  --priority "Expand enterprise ARR" \
  --registry /tmp/cfo_registry.json

echo "=== Forecast pack ==="
PYTHONPATH=src python3 -m cme.cli cfo-os \
  --task forecast \
  --title "FY26 driver-based plan" \
  --company "Acme" \
  --problem "Build the FY26 driver-based operating plan with stress views." \
  --base-revenue 42000000 --base-opex 33000000 \
  --growth-pct 0.28 --churn-pct 0.09 \
  --min-runway 12 --current-runway 20 \
  --priority "Net dollar retention >= 115%" \
  --registry /tmp/cfo_registry.json

echo "=== Board output ==="
PYTHONPATH=src python3 -m cme.cli cfo-os \
  --task board_output \
  --title "Q3 board: enterprise expansion" \
  --company "Acme" \
  --problem "Approve the FY26 enterprise expansion plan with phased capital release." \
  --option "Approve phased capital release with milestone gates" \
  --option "Defer one quarter pending pipeline confirmation" \
  --option "Reject and reinvest in SMB retention" \
  --recommended-index 0 \
  --open-question "Is enterprise pipeline conversion confidence supported by recent cohorts?" \
  --open-question "Does compliance posture cover SOC2 + data residency at scale?" \
  --risk "Adoption ramp slope" --risk "Compliance scope creep" \
  --registry /tmp/cfo_registry.json
