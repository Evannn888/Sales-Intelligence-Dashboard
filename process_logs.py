import re
import requests
import json
from collections import defaultdict
from datetime import datetime

def parse_log_line(line):
    """
    Parse a line in Apache Common Log Format and extract IP, URL path, and timestamp as datetime object.
    Returns a dict: {'ip': '...', 'path': '...', 'timestamp': datetime}
    """
    # Example: 192.168.1.100 - - [15/Dec/2024:14:30:25 +0000] "GET /forms-request-demo/ HTTP/1.1" 200 15000
    pattern = r'^(\S+)\s+-\s+-\s+\[(.*?)\]\s+"\S+\s+(\S+)\s+HTTP/\d\.\d"'
    match = re.match(pattern, line)
    if match:
        ip = match.group(1)
        timestamp_str = match.group(2)
        path = match.group(3)
        # Parse timestamp to datetime object
        try:
            timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
        except Exception:
            timestamp = None
        return {'ip': ip, 'path': path, 'timestamp': timestamp}
    return None

def is_private_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    a, b = int(parts[0]), int(parts[1])
    if a == 10:
        return True
    if a == 192 and b == 168:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    return False

def get_company_from_ip(ip, cache):
    if is_private_ip(ip):
        label = f'Internal User ({ip})'
        cache[ip] = label
        return label
    if ip in cache:
        return cache[ip]
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,org"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success' and 'org' in data:
                cache[ip] = data['org']
                return data['org']
            else:
                cache[ip] = ''
                return ''
        else:
            cache[ip] = ''
            return ''
    except Exception:
        cache[ip] = ''
        return ''

def calculate_lead_score(visited_pages):
    # Define scoring by tier
    tier1 = {"/forms-request-demo/", "/try-ai-agent/", "/try-ai-knowledge-hub/", "/contact-us/"}
    tier2 = {"/roi-calculator/", "/ai-agent/", "/ai-knowledge-hub/", "/conversation-hub/", "/products/analytics/"}
    tier3 = {
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
    }
    tier4 = {
        "/company/about-us/", "/careers/", "/podcasts/", "/resources/egain-innovation-best-practices-webinars/", "/resources/case-studies/", "/company/news/", "/company/events/"
    }
    score_map = {}
    for path in visited_pages:
        if path in tier1:
            score_map[path] = 25
        elif path in tier2:
            score_map[path] = 15
        elif path in tier3:
            score_map[path] = 5
        elif path in tier4:
            score_map[path] = 1
        else:
            score_map[path] = 0
    return sum(score_map.values())

def summarize_interests(visited_pages):
    # Map paths to human-readable tags
    interest_map = {
        "/forms-request-demo/": "Requested Demo",
        "/try-ai-agent/": "AI Agent Trial",
        "/try-ai-knowledge-hub/": "Knowledge Hub Trial",
        "/contact-us/": "Contacted Sales",
        "/roi-calculator/": "ROI/Justification",
        "/ai-agent/": "AI Agent Research",
        "/ai-knowledge-hub/": "Knowledge Hub Research",
        "/conversation-hub/": "Conversation Hub",
        "/products/analytics/": "Analytics Product",
        "/whats-in-knowledge-management-in-banking/": "Banking Industry",
        "/whats-in-knowledge-management-in-financial-services/": "Financial Services Industry",
        "/whats-in-knowledge-management-in-government/": "Government Sector",
        "/whats-in-knowledge-management-in-healthcare-providers/": "Healthcare Providers",
        "/whats-in-knowledge-management-in-health-insurance/": "Health Insurance",
        "/whats-in-knowledge-management-in-healthcare/": "Healthcare Industry",
        "/whats-in-knowledge-management-in-insurance/": "Insurance Industry",
        "/whats-in-knowledge-management-in-manufacturing/": "Manufacturing Industry",
        "/whats-in-knowledge-management-in-retail/": "Retail Industry",
        "/whats-in-knowledge-management-in-technology-sector/": "Technology Sector",
        "/whats-in-knowledge-management-in-telecommunications/": "Telecommunications",
        "/whats-in-knowledge-management-in-the-public-sector/": "Public Sector",
        "/whats-in-knowledge-management-in-travel-hospitality-airlines/": "Travel/Hospitality/Airlines",
        "/whats-in-knowledge-management-in-utilities/": "Utilities Industry",
        "/company/about-us/": "About Us",
        "/careers/": "Careers",
        "/podcasts/": "Podcasts",
        "/resources/egain-innovation-best-practices-webinars/": "Webinars",
        "/resources/case-studies/": "Case Studies",
        "/company/news/": "Company News",
        "/company/events/": "Company Events"
    }
    tags = set()
    for path in visited_pages:
        if path in interest_map:
            tags.add(interest_map[path])
    return list(tags)

if __name__ == "__main__":
    ip_company_cache = {}
    company_visits = defaultdict(list)
    with open("access.log", "r") as f:
        for line in f:
            parsed = parse_log_line(line)
            if not parsed:
                continue
            ip = parsed['ip']
            path = parsed['path']
            timestamp = parsed['timestamp']
            company = get_company_from_ip(ip, ip_company_cache)
            if company:
                company_visits[company].append((path, timestamp))
    # Prepare output data
    output_data = []
    for company, visits in company_visits.items():
        paths = [p for p, t in visits]
        timestamps = [t for p, t in visits if t is not None]
        lead_score = calculate_lead_score(paths)
        key_interests = summarize_interests(paths)
        last_visit = max(timestamps).astimezone().isoformat() if timestamps else None
        visit_count = len(visits)
        output_data.append({
            "companyName": company,
            "leadScore": lead_score,
            "keyInterests": key_interests,
            "lastVisit": last_visit,
            "visitCount": visit_count
        })
    # Write to visitorData.json
    with open("visitorData.json", "w") as out_f:
        json.dump(output_data, out_f, indent=2)
    print("Wrote visitorData.json with lead scoring and interests.") 