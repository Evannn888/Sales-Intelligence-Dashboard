import re
import requests
import json
from collections import defaultdict

def parse_log_line(line):
    """
    Parse a line in Apache Common Log Format and extract IP and URL path.
    Returns a dict: {'ip': '...', 'path': '...'}
    """
    # Example: 192.168.1.100 - - [15/Dec/2024:14:30:25 +0000] "GET /forms-request-demo/ HTTP/1.1" 200 15000
    pattern = r'^(\S+)\s+-\s+-\s+\[.*?\]\s+"\S+\s+(\S+)\s+HTTP/\d\.\d"'
    match = re.match(pattern, line)
    if match:
        return {'ip': match.group(1), 'path': match.group(2)}
    return None

def get_company_from_ip(ip, cache):
    """
    Given an IP and a cache dict, return the company/org name using ip-api.com.
    Uses cache to avoid duplicate lookups.
    """
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
    except Exception as e:
        cache[ip] = ''
        return ''

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
            company = get_company_from_ip(ip, ip_company_cache)
            if company:
                company_visits[company].append(path)
    # Print first 5 companies and their visited pages
    print("First 5 companies and their visited pages:")
    for i, (company, pages) in enumerate(company_visits.items()):
        if i >= 5:
            break
        print(f"{company}: {pages}") 