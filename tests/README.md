# Phishing Email Detector

A Python command-line triage tool that parses raw `.eml` email files, inspects authentication headers, URLs, attachments, and social-engineering indicators, and outputs a **0–100 phishing risk score** (`LOW`, `MEDIUM`, `HIGH`) with plain-English explanations.

Built as a hands-on security engineering and SOC triage portfolio project aligned with **CompTIA Security+ Domain 2** concepts (email authentication and social-engineering / malicious indicator analysis), complete with modular Python code and automated `pytest` tests.

---

## Features & Detection Rules

Each check evaluates a distinct phishing signal and returns weighted points (capped at `100` overall) plus human-readable reasons:

| Check | What It Inspects | Max Points | Security & SOC Rationale |
| :--- | :--- | :---: | :--- |
| **Email Authentication** | `Authentication-Results` and `Received-SPF` for `spf=fail`, `spf=softfail`, `dkim=fail`, `dmarc=fail` | 25 | Flags messages that fail sender authorization, cryptographic signature checks, or domain alignment policies. |
| **Lookalike Domain** | Domain name similarity (`SequenceMatcher >= 0.8`) against common brands while allowing the real brand and its subdomains | 25 | Catches typosquatting/lookalike domains (such as `paypa1.com`) while reducing false positives on legitimate brand infrastructure. |
| **Risky Attachments** | Attachment filenames ending in `.exe`, `.js`, `.vbs`, `.scr`, `.iso`, `.docm`, `.xlsm`, `.bat`, `.zip`, `.html` | 25 | Highlights executables, scripts, archives, HTML lures, and macro-enabled Office files commonly used in phishing payloads. |
| **Reply-To Mismatch** | Compares the domain in `From` against the domain in `Reply-To` | 20 | Detects spoofing or redirection where replies are routed to an external or attacker-controlled address. |
| **Pressure Language** | Urgency and fear phrases (`urgent`, `immediately`, `verify your account`, `suspended`, `act now`, `final notice`, `password expires`, `confirm your identity`, `unusual activity`, `click here`) | 20 | Identifies social-engineering pressure tactics designed to rush recipients into acting before verifying. |
| **Suspicious Links** | HTML `<a>` tags using raw IP addresses, URL shorteners (`bit.ly`, `tinyurl.com`, `t.co`, `goo.gl`, `ow.ly`, `is.gd`), punycode (`xn--`), or visible URL text that differs from the destination `href` host | 40 | Exposes credential-harvesting links disguised behind deceptive anchor text, obfuscated domains, or direct IP hosts. |

### Risk Thresholds & Assumptions

* **`0–29` (`LOW`):** Minimal or no phishing indicators detected.
* **`30–59` (`MEDIUM`):** One or more anomalies detected; warrants closer analyst review.
* **`60–100` (`HIGH`):** Multiple high-signal phishing indicators detected; strong candidate for quarantine and investigation.

> **Tuning Note:** The `30` and `60` score thresholds and individual point weights are baseline heuristics designed for clarity and explainability. In production, they should be tuned against real mail flow and false-positive/false-negative metrics.

---

## Project Structure

```text
phishing-email-detector/
├── detector/
│   ├── __init__.py      # Marks detector as a Python package
│   ├── parser.py        # Loads .eml files and extracts headers, body content, and attachments
│   ├── checks.py        # Individual heuristic checks returning (points, reasons)
│   └── scoring.py       # Aggregates check scores, applies LOW/MEDIUM/HIGH labels, and formats output
├── samples/
│   ├── legit1.eml       # Sample legitimate email for baseline testing
│   └── phish1.eml       # Sample phishing email with multiple red flags
├── tests/
│   └── test_checks.py   # Automated unit and integration tests using pytest
├── main.py              # CLI entry point supporting files, folders, and --json output
├── requirements.txt     # Pinned project dependencies (beautifulsoup4, pytest, etc.)
├── .gitignore           # Excludes .venv/, __pycache__/, *.pyc, and .env
└── README.md
```

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/](https://github.com/)<your-username>/phishing-email-detector.git
cd phishing-email-detector
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Git Bash):**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage & Commands

Make sure your virtual environment is activated (`(.venv)` visible in your prompt) before running commands.

### Scan a Folder of `.eml` Files

```bash
python main.py samples
```

### Scan a Single `.eml` File

```bash
python main.py samples/phish1.eml
```

### Scan Multiple Paths at Once

```bash
python main.py samples/legit1.eml samples/phish1.eml
```

### Output Structured JSON (Useful for Scripting, SIEM, or SOAR Pipelines)

```bash
python main.py samples --json
```

### Run Automated Tests with `pytest`

```bash
pytest -v
```

---

## Example Output

### Text Output (`python main.py samples`)

```text
samples\legit1.eml
  Subject: Lunch on Friday?
  Risk: LOW (0/100)

samples\phish1.eml
  Subject: URGENT: verify your account
  Risk: HIGH (100/100)
   - Reply-To domain (mail-recovery.example) differs from From domain (paypa1.com)
   - Email authentication problems: spf=fail, dmarc=fail
   - Sender domain paypa1.com looks like paypal.com
   - Pressure language: suspended, act now, confirm your identity
   - Link uses a raw IP address: [http://192.0.2.10/login](http://192.0.2.10/login)
   - Link text shows [www.paypal.com](https://www.paypal.com) but goes to 192.0.2.10
```

### JSON Output (`python main.py samples --json`)

```json
{
  "samples\\legit1.eml": {
    "score": 0,
    "label": "LOW",
    "reasons": [],
    "subject": "Lunch on Friday?"
  },
  "samples\\phish1.eml": {
    "score": 100,
    "label": "HIGH",
    "reasons": [
      "Reply-To domain (mail-recovery.example) differs from From domain (paypa1.com)",
      "Email authentication problems: spf=fail, dmarc=fail",
      "Sender domain paypa1.com looks like paypal.com",
      "Pressure language: suspended, act now, confirm your identity",
      "Link uses a raw IP address: [http://192.0.2.10/login](http://192.0.2.10/login)",
      "Link text shows [www.paypal.com](https://www.paypal.com) but goes to 192.0.2.10"
    ],
    "subject": "URGENT: verify your account"
  }
}
```
## Visual Proof

### CLI Phishing Triage Output
![CLI output scoring legit1.eml as LOW and phish1.eml as HIGH]
### Automated Pytest Suite
![pytest verbose output showing unit tests passing]
(assets\pytest-output-results.png)

---

## Git & GitHub Workflow Commands

When updating the project locally and publishing changes to GitHub:

```bash
git status
git add .
git commit -m "Update phishing email detector"
git push
```

If creating and pushing a new public GitHub repository from the local folder for the first time using GitHub CLI (`gh`):

```bash
gh repo create phishing-email-detector --public --source=. --remote=origin --push
```

---

## Limitations & Security Hygiene

* **Heuristic Scoring Only:** Rule-based scoring catches common spoofing, lookalike domains, urgency lures, and link/attachment red flags, but cannot replace full sandbox detonation, threat intelligence feeds, or organizational mail gateway telemetry.
* **Safe Handling:** Never commit sensitive credentials, API keys, personal emails, or live malware samples to version control. Keep local secrets in `.env` (already ignored via `.gitignore`).