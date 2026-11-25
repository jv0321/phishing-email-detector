import argparse
import json
from pathlib import Path

from detector.parser import load_email
from detector.scoring import score_email


def main():
    ap = argparse.ArgumentParser(description='Score .eml files for phishing risk')
    ap.add_argument('paths', nargs='+', help='.eml files or folders')
    ap.add_argument('--json', action='store_true', help='print JSON instead of text')
    args = ap.parse_args()

    files = []
    for p in args.paths:
        path = Path(p)
        files += sorted(path.glob('*.eml')) if path.is_dir() else [path]

    results = {str(f): score_email(load_email(f)) for f in files}

    if args.json:
        print(json.dumps(results, indent=2))
        return
    for name, r in results.items():
        print(f"\n{name}\n  Subject: {r['subject']}\n  Risk: {r['label']} ({r['score']}/100)")
        for reason in r['reasons']:
            print(f'   - {reason}')


if __name__ == '__main__':
    main()