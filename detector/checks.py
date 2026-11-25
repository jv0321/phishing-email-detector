import re
from difflib import SequenceMatcher
from urllib.parse import urlparse

from bs4 import BeautifulSoup

URGENCY_WORDS = [
    'urgent', 'immediately', 'verify your account', 'suspended', 'act now',
    'final notice', 'password expires', 'confirm your identity',
    'unusual activity', 'click here',
]
RISKY_EXTENSIONS = ('.exe', '.js', '.vbs', '.scr', '.iso', '.docm', '.xlsm', '.bat', '.zip', '.html')
SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd'}
KNOWN_BRANDS = ['paypal.com', 'microsoft.com', 'google.com', 'apple.com', 'amazon.com', 'netflix.com']
IP_RE = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')


def domain_of(address):
    m = re.search(r'@([\w.-]+)', address)
    return m.group(1).lower() if m else ''


def check_reply_to(headers):
    f, r = domain_of(headers['from']), domain_of(headers['reply_to'])
    if f and r and f != r:
        return 20, [f'Reply-To domain ({r}) differs from From domain ({f})']
    return 0, []


def check_auth(headers):
    text = (headers['auth_results'] + ' ' + headers['received_spf']).lower()
    fails = [k for k in ('spf=fail', 'spf=softfail', 'dkim=fail', 'dmarc=fail') if k in text]
    if fails:
        return 25, ['Email authentication problems: ' + ', '.join(fails)]
    return 0, []


def name_part(domain):
    """'mail.paypa1.com' -> 'paypa1' (the registered name without the TLD)."""
    parts = domain.split('.')
    return parts[-2] if len(parts) >= 2 else domain


def check_lookalike(headers):
    d = domain_of(headers['from'])
    if not d:
        return 0, []
    for brand in KNOWN_BRANDS:
        if d == brand or d.endswith('.' + brand):
            continue  # the real brand or one of its subdomains
        if SequenceMatcher(None, name_part(d), name_part(brand)).ratio() >= 0.8:
            return 25, [f'Sender domain {d} looks like {brand}']
    return 0, []


def check_urgency(body):
    text = body.lower()
    hits = [w for w in URGENCY_WORDS if w in text]
    if hits:
        return min(5 * len(hits), 20), ['Pressure language: ' + ', '.join(hits)]
    return 0, []


def check_links(body):
    soup = BeautifulSoup(body, 'html.parser')
    reasons, points = [], 0
    for a in soup.find_all('a', href=True):
        href = a['href']
        host = (urlparse(href).hostname or '').lower()
        text = a.get_text(strip=True).lower()
        if IP_RE.match(host):
            points += 20
            reasons.append(f'Link uses a raw IP address: {href}')
        if host in SHORTENERS:
            points += 10
            reasons.append(f'Link uses a URL shortener: {host}')
        if host.startswith('xn--') or '.xn--' in host:
            points += 15
            reasons.append(f'Link uses punycode (possible lookalike): {host}')
        if text.startswith(('http', 'www.')):
            shown = urlparse(text if text.startswith('http') else 'http://' + text).hostname or ''
            if shown and host and shown != host:
                points += 25
                reasons.append(f'Link text shows {shown} but goes to {host}')
    return min(points, 40), reasons


def check_attachments(names):
    bad = [n for n in names if n.lower().endswith(RISKY_EXTENSIONS)]
    if bad:
        return 25, ['Risky attachment type: ' + ', '.join(bad)]
    return 0, []
