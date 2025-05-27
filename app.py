from flask import Flask, render_template, request, jsonify
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Add the project root to the sys.path to allow importing cyber_agent_core
# This is often needed when running Flask apps from a sub-directory or if imports aren't clean
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

# Import your core analysis function from cyber_agent_core.py
# This will also initialize the LLM (gemini-1.5-flash) when app.py starts
from cyber_agent_core import analyze_threat_intelligence

app = Flask(__name__)

# !!! IMPORTANT: Flask requires a secret key for sessions, even if we don't use them directly in this app
# Generate one using: import os; print(os.urandom(24).hex())
app.secret_key = 'your_super_secret_key_for_flask_app_replace_me' 

# Disable reloader during development to prevent WinError 32 PermissionError
# (Especially if your cyber_agent_core.py does file operations like ChromaDB in __init__)
app.config['DEBUG'] = True
app.config['USE_RELOADER'] = False # Prevents file locking issues on Windows

analysis_history = []

@app.route('/')
def index():
    """Renders the main page for threat analysis input."""
    return render_template('index.html')

def extract_severity_from_report(report):
    """Extracts the severity level from the AI report text."""
    import re
    match = re.search(r"Severity Assessment:\s*(?:`)?(Informational|Low|Medium|High|Critical)(?:`)?", report, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    # Fallback: try to find severity in the text
    for sev in ["Critical", "High", "Medium", "Low", "Informational"]:
        if sev.lower() in report.lower():
            return sev
    return "Unknown"

@app.route('/analyze_threat', methods=['POST'])
def analyze_threat():
    """Receives threat text, calls AI agent, and returns analysis report and mitigation."""
    data = request.get_json()
    input_text = data.get('text', '').strip()

    if not input_text:
        return jsonify({'success': False, 'message': 'No input text provided for analysis.'}), 400

    print(f"\n--- Web App: Analyzing input text (length: {len(input_text)}): ---")
    print(input_text[:200] + "..." if len(input_text) > 200 else input_text)

    try:
        report = analyze_threat_intelligence(input_text)
        severity = extract_severity_from_report(report)
        # Simple mitigation suggestion logic (replace with your own or use LLM)
        mitigation = []
        if "phishing" in report.lower():
            mitigation.append("Warn users not to click suspicious links or provide credentials.")
        if "malware" in report.lower():
            mitigation.append("Run a full antivirus scan and isolate affected systems.")
        if "ransomware" in report.lower():
            mitigation.append("Disconnect infected machines and restore from backups.")
        if not mitigation:
            mitigation.append("No specific mitigation required. Monitor for unusual activity.")

        analysis_history.append({
            'input': input_text,
            'report': report,
            'mitigation': mitigation,
            'severity': severity
        })

        print("\n--- Web App: Analysis complete. Returning report and mitigation. ---")
        return jsonify({'success': True, 'report': report, 'mitigation': mitigation, 'severity': severity})
    except Exception as e:
        print(f"ERROR: Analysis failed in Flask route: {e}")
        return jsonify({'success': False, 'message': f'Analysis failed due to an internal error: {e}'}), 500

@app.route('/history')
def history():
    return jsonify({'success': True, 'history': analysis_history})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get('message', '').strip().lower()
    if not user_message:
        return jsonify({'success': False, 'message': 'No message provided.'}), 400
    try:
        # Simple keyword-based responses
        if "ai" in user_message or "artificial intelligence" in user_message:
            answer = "AI (Artificial Intelligence) refers to computer systems that can perform tasks that typically require human intelligence, such as learning, reasoning, and problem-solving."
        elif "risk" in user_message:
            answer = "A risk is the potential for loss or damage when a threat exploits a vulnerability."
        elif "threat" in user_message:
            answer = "A threat is any circumstance or event with the potential to adversely impact organizational operations, assets, or individuals."
        elif "phishing" in user_message:
            answer = "Phishing is a cyber attack where attackers impersonate legitimate organizations via email, text, or other means to steal sensitive information."
        elif "malware" in user_message:
            answer = "Malware is malicious software designed to disrupt, damage, or gain unauthorized access to computer systems."
        elif "ransomware" in user_message:
            answer = "Ransomware is a type of malware that encrypts your files and demands payment for the decryption key."
        elif "mitigation" in user_message or "prevent" in user_message:
            answer = "Mitigation steps include keeping software updated, using strong passwords, enabling multi-factor authentication, and educating users about threats."
        elif "history" in user_message:
            answer = "You can view your analysis history by clicking the 'View Analysis History' button below the main panel."
        elif "how to use" in user_message or "help" in user_message:
            answer = "Paste suspicious text (like emails, logs, or URLs) in the input box and click 'Analyze Threat' to get an AI-powered analysis."
        elif "cybersecurity" in user_message:
            answer = "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks."
        elif "ioc" in user_message or "indicator of compromise" in user_message:
            answer = "An Indicator of Compromise (IOC) is evidence that a system has been breached, such as unusual network traffic, file changes, or log entries."
        else:
            answer = "I'm your CyberGuard Assistant. Ask me about AI, threats, phishing, malware, risk, mitigation, or how to use this tool!"
        return jsonify({'success': True, 'response': answer})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # !!! IMPORTANT: Change the host and port as needed, or use 0.0.0.0:5000 to listen on all interfaces
    app.run(host='0.0.0.0', port=5000) # Listen on all interfaces, default port
    print("Starting Flask app...")