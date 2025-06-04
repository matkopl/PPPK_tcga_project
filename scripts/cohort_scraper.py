import xenaPython as xena
import re

hub = "https://tcga.xenahubs.net"
cohorts_full = xena.all_cohorts(hub, [])

cohorts = []
for name in cohorts_full:
    match = re.search(r'\((\w+)\)$', name)
    if match:
        cohorts.append(match.group(1))

cohorts = sorted(set(cohorts))

cohorts = [c for c in cohorts if c.lower() != "unassigned"]

print("COHORTS =", cohorts)
