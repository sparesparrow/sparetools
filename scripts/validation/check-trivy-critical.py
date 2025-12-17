#!/usr/bin/env python3
"""Count CRITICAL vulnerabilities in Trivy JSON results."""
import json
import sys

try:
    with open("trivy-results.json", "r") as f:
        data = json.load(f)
        
    critical_count = 0
    critical_vulns = []
    
    for result in data.get("Results", []):
        if "Vulnerabilities" in result:
            for vuln in result["Vulnerabilities"]:
                if vuln.get("Severity") == "CRITICAL":
                    critical_count += 1
                    critical_vulns.append({
                        "pkg": vuln.get("PkgName", "unknown"),
                        "id": vuln.get("VulnerabilityID", "unknown"),
                        "title": vuln.get("Title", "No title")
                    })
    
    if critical_count > 0:
        print("\n🔴 CRITICAL Vulnerabilities Found:", file=sys.stderr)
        for v in critical_vulns[:10]:
            print(f"  - {v['pkg']}: {v['id']} - {v['title']}", file=sys.stderr)
    
    print(critical_count)
                  
except Exception as e:
    print(f"Error parsing Trivy results: {e}", file=sys.stderr)
    print("0")
