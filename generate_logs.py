#!/usr/bin/env python3
"""
Generate fake weblog entries in classic Apache Common Log Format for eGain sales motion analysis.
Creates access.log with 500 entries distributed across 4 tiers of user interest.
Features:
- Pool of 80 unique IP addresses for returning visitors
- Classic Apache Common Log Format (no user-agent or referrer)
- Tiered URL structure using only the provided eGain.com links
"""

import random
import datetime
from pathlib import Path

def generate_ip_pool():
    """Generate a pool of 80 unique, realistic IP addresses, including public company IPs and private IPs."""
    # Well-known public company IPs
    company_ips = [
        # Google
        "8.8.8.8", "8.8.4.4", "142.250.74.78", "142.250.191.78",
        # Microsoft
        "40.76.4.15", "40.77.226.250", "40.112.72.205",
        # Amazon
        "52.95.110.1", "54.239.28.85", "52.94.225.248",
        # Apple
        "17.172.224.47", "17.142.160.59",
        # Facebook (Meta)
        "31.13.71.36", "157.240.1.35"
    ]
    # Add 20 private IPs (mix of 10.x.x.x, 192.168.x.x, 172.16-31.x.x)
    private_ips = set()
    while len(private_ips) < 7:
        private_ips.add(f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
    while len(private_ips) < 14:
        private_ips.add(f"192.168.{random.randint(0,255)}.{random.randint(1,254)}")
    while len(private_ips) < 20:
        private_ips.add(f"172.{random.randint(16,31)}.{random.randint(0,255)}.{random.randint(1,254)}")
    ip_pool = set(company_ips) | private_ips
    # Fill the rest with random public IPs (avoid private/reserved ranges)
    while len(ip_pool) < 80:
        a = random.choice([8, 17, 31, 40, 52, 54, 142, 157, 185, 199, 205, 216])
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(1, 254)
        ip = f"{a}.{b}.{c}.{d}"
        # Avoid private/reserved ranges
        if ip.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.")):
            continue
        ip_pool.add(ip)
    return list(ip_pool)

def generate_timestamp():
    """Generate timestamp from the last 30 days."""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    random_date = start_date + datetime.timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
    )
    return random_date.strftime("%d/%b/%Y:%H:%M:%S +0000")

def generate_url_path():
    # URLs from the image, grouped by tier, with duplicates removed
    tier1_urls = [
        "/forms-request-demo/",
        "/try-ai-agent/",
        "/try-ai-knowledge-hub/",
        "/contact-us/"
    ]
    tier2_urls = [
        "/roi-calculator/",
        "/ai-agent/",
        "/ai-knowledge-hub/",
        "/conversation-hub/",
        "/products/analytics/"
    ]
    tier3_urls = [
        "/whats-in-knowledge-management-in-banking/",
        "/whats-in-knowledge-management-in-financial-services/",
        "/whats-in-knowledge-management-in-government/",
        "/whats-in-knowledge-management-in-healthcare-providers/",
        "/whats-in-knowledge-management-in-health-insurance/",
        "/whats-in-knowledge-management-in-healthcare/",
        "/whats-in-knowledge-management-in-insurance/",
        "/whats-in-knowledge-management-in-manufacturing/",
        "/whats-in-knowledge-management-in-retail/",
        "/whats-in-knowledge-management-in-technology-sector/",
        "/whats-in-knowledge-management-in-telecommunications/",
        "/whats-in-knowledge-management-in-the-public-sector/",
        "/whats-in-knowledge-management-in-travel-hospitality-airlines/",
        "/whats-in-knowledge-management-in-utilities/"
    ]
    tier4_urls = [
        "/company/about-us/",
        "/careers/",
        "/podcasts/",
        "/resources/egain-innovation-best-practices-webinars/",
        "/resources/case-studies/",
        "/company/news/",
        "/company/events/"
    ]
    # Weighted distribution
    tiers = [
        (tier1_urls, 10),   # 10%
        (tier2_urls, 20),   # 20%
        (tier3_urls, 45),   # 45%
        (tier4_urls, 25)    # 25%
    ]
    weighted_paths = []
    for url_list, weight in tiers:
        for url in url_list:
            weighted_paths.extend([url] * weight)
    return random.choice(weighted_paths)

def generate_log_entry(ip_pool):
    """Generate a single log entry in classic Apache Common Log Format."""
    ip = random.choice(ip_pool)
    timestamp = generate_timestamp()
    method = "GET"
    path = generate_url_path()
    status_code = random.choices([200, 200, 200, 200, 200, 404, 500], weights=[85, 85, 85, 85, 85, 10, 5])[0]
    bytes_sent = random.randint(1000, 50000)
    
    # Classic Apache Common Log Format: host ident authuser [timestamp] "request" status bytes
    # Note: ident and authuser are typically "-" in most configurations
    log_entry = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} {bytes_sent}'
    return log_entry

def main():
    """Generate 500 log entries and write to access.log."""
    print("Generating IP pool of 80 unique addresses...")
    ip_pool = generate_ip_pool()
    print(f"Created IP pool with {len(ip_pool)} unique addresses")
    
    print("\nGenerating 500 weblog entries in classic Apache Common Log Format...")
    
    log_entries = []
    for i in range(500):
        log_entries.append(generate_log_entry(ip_pool))
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} entries...")
    
    # Write to access.log
    with open("access.log", "w") as f:
        for entry in log_entries:
            f.write(entry + "\n")
    
    print(f"\nSuccessfully generated access.log with {len(log_entries)} entries")
    
    # Print distribution summary
    print("\nDistribution Summary:")
    path_counts = {}
    for entry in log_entries:
        # Extract path from log entry
        path = entry.split('"')[1].split()[1]
        path_counts[path] = path_counts.get(path, 0) + 1
    
    # Group by tiers for summary
    tier_summary = {
        "Tier 1 (Highest Intent)": 0,
        "Tier 2 (Research)": 0,
        "Tier 3 (Industry Interest)": 0,
        "Tier 4 (Low Interest)": 0
    }
    
    for path, count in path_counts.items():
        percentage = (count / 500) * 100
        print(f"  {path}: {count} entries ({percentage:.1f}%)")
        
        # Categorize by tier
        if path in [
            "/forms-request-demo/", "/try-ai-agent/", "/try-ai-knowledge-hub/", "/contact-us/"
        ]:
            tier_summary["Tier 1 (Highest Intent)"] += count
        elif path in [
            "/roi-calculator/", "/ai-agent/", "/ai-knowledge-hub/", "/conversation-hub/", "/products/analytics/"
        ]:
            tier_summary["Tier 2 (Research)"] += count
        elif path in [
            "/whats-in-knowledge-management-in-banking/",
            "/whats-in-knowledge-management-in-financial-services/",
            "/whats-in-knowledge-management-in-government/",
            "/whats-in-knowledge-management-in-healthcare-providers/",
            "/whats-in-knowledge-management-in-health-insurance/",
            "/whats-in-knowledge-management-in-healthcare/",
            "/whats-in-knowledge-management-in-insurance/",
            "/whats-in-knowledge-management-in-manufacturing/",
            "/whats-in-knowledge-management-in-retail/",
            "/whats-in-knowledge-management-in-technology-sector/",
            "/whats-in-knowledge-management-in-telecommunications/",
            "/whats-in-knowledge-management-in-the-public-sector/",
            "/whats-in-knowledge-management-in-travel-hospitality-airlines/",
            "/whats-in-knowledge-management-in-utilities/"
        ]:
            tier_summary["Tier 3 (Industry Interest)"] += count
        else:
            tier_summary["Tier 4 (Low Interest)"] += count
    
    print("\nTier Distribution:")
    for tier, count in tier_summary.items():
        percentage = (count / 500) * 100
        print(f"  {tier}: {count} entries ({percentage:.1f}%)")
    
    # Show IP reuse statistics
    ip_counts = {}
    for entry in log_entries:
        ip = entry.split()[0]
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    print(f"\nIP Address Usage:")
    print(f"  Unique IPs used: {len(ip_counts)}")
    print(f"  Most frequent IP: {max(ip_counts, key=ip_counts.get)} ({max(ip_counts.values())} times)")
    print(f"  Average visits per IP: {500/len(ip_counts):.1f}")

if __name__ == "__main__":
    main() 