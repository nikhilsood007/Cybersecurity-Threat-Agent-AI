"""
Test red (threat/critical) scenarios for CyberGuard AI Analyst.
These should all be classified as 'High' or 'Critical' severity (red alert).
"""
import requests

BASE_URL = "http://localhost:5000/analyze_threat"

red_cases = [
    {
        "desc": "Phishing email with password reset link",
        "text": "Subject: Urgent Password Reset\n\nDear user, your account has been compromised. Click here to reset your password: http://malicious-link.com/"
    },
    {
        "desc": "Malware attachment double extension",
        "text": "Suspicious attachment detected: invoice.pdf.exe"
    },
    {
        "desc": "Fake account verification with link",
        "text": "Subject: Account Verification Required\n\nPlease verify your account immediately: http://phishingsite.com/verify"
    },
    {
        "desc": "Ransomware threat",
        "text": "Your files have been encrypted! Pay 1 BTC to the following address or lose your data forever."
    },
    {
        "desc": "Fake security alert with urgent action",
        "text": "Security Alert: Your account will be locked. Click here to avoid suspension: http://scam-alert.com/"
    },
    {
        "desc": "Social engineering with suspicious sender",
        "text": "From: ceo@company.com\nTo: finance@company.com\nSubject: Urgent Payment\n\nPlease transfer $10,000 to the following account immediately."
    }
]

def test_red_cases():
    for case in red_cases:
        try:
            resp = requests.post(BASE_URL, json={"text": case["text"]})
            data = resp.json()
            print(f"Test: {case['desc']}")
            if data.get("success") and data.get("severity", "").lower() in ["high", "critical"]:
                print("  ✅ PASSED (Red)")
            else:
                print(f"  ❌ FAILED: Severity={data.get('severity')} | Message={data.get('message')}")
            print()
        except Exception as e:
            print(f"  ❌ ERROR: {e}\n")

if __name__ == "__main__":
    test_red_cases()
