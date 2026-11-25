from email import policy
from email.parser import BytesParser


def load_email(path):
    with open(path, 'rb') as f:
        return BytesParser(policy=policy.default).parse(f)


def get_headers(msg):
    return {
        'from': str(msg.get('From', '')),
        'reply_to': str(msg.get('Reply-To', '')),
        'subject': str(msg.get('Subject', '')),
        'auth_results': str(msg.get('Authentication-Results', '')),
        'received_spf': str(msg.get('Received-SPF', '')),
    }


def get_body(msg):
    part = msg.get_body(preferencelist=('html', 'plain'))
    return part.get_content() if part else ''


def get_attachments(msg):
    return [p.get_filename() for p in msg.iter_attachments() if p.get_filename()]
