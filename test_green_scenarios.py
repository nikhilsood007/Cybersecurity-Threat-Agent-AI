"""
Test green (benign/safe) scenarios for CyberGuard AI Analyst.
These should all be classified as 'Informational' or 'Low' severity (green alert).
"""
import requests

BASE_URL = "http://localhost:5000/analyze_threat"

green_cases = [
    {
        "desc": "Normal business email",
        "text": "Subject: Meeting Reminder\n\nHi team,\n\nJust a reminder about our project meeting scheduled for tomorrow at 10 AM. Please let me know if you have any questions.\n\nBest,\nPriya"
    },
    {
        "desc": "Routine system log",
        "text": "2025-05-27 09:00:01 INFO System backup completed successfully.\n2025-05-27 09:05:12 INFO User 'admin' logged in from IP 192.168.1.5."
    },
    {
        "desc": "Internal file transfer notification",
        "text": "User 'john.smith' uploaded 'Q2_report.xlsx' to the shared drive.\nNo errors detected during the transfer."
    },
    {
        "desc": "Newsletter subscription confirmation",
        "text": "Thank you for subscribing to our monthly newsletter!\nYou will receive updates at your registered email address."
    },
    {
        "desc": "Password change confirmation (user-initiated)",
        "text": "Your password was changed successfully.\nIf you did not request this change, please contact support."
    },
    {
        "desc": "Calendar event notification",
        "text": "Event: Team Lunch\nDate: 2025-06-01\nLocation: Cafeteria\nThis is an automated reminder for your upcoming event."
    }
]

def test_green_cases():
    for case in green_cases:
        resp = requests.post(BASE_URL, json={"text": case["text"]})
        data = resp.json()
        print(f"Test: {case['desc']}")
        if data.get("success") and data.get("severity", "").lower() in ["informational", "low"]:
            print("  ✅ PASSED (Green)")
        else:
            print(f"  ❌ FAILED: Severity={data.get('severity')} | Message={data.get('message')}")
        print()

if __name__ == "__main__":
    test_green_cases()
