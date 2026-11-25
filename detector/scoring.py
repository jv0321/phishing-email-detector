from . import checks
from .parser import get_attachments, get_body, get_headers


def score_email(msg):
    headers, body, attachments = get_headers(msg), get_body(msg), get_attachments(msg)
    results = [
        checks.check_reply_to(headers),
        checks.check_auth(headers),
        checks.check_lookalike(headers),
        checks.check_urgency(body),
        checks.check_links(body),
        checks.check_attachments(attachments),
    ]
    total = min(sum(points for points, _ in results), 100)
    reasons = [r for _, rs in results for r in rs]
    if total >= 60:
        label = 'HIGH'
    elif total >= 30:
        label = 'MEDIUM'
    else:
        label = 'LOW'
    return {'score': total, 'label': label, 'reasons': reasons, 'subject': headers['subject']}
