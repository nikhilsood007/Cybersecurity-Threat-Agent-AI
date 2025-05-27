import google.generativeai as genai
import os
import re # For regular expressions to extract IoCs
import random # For simulating varying lookup results
import requests
from dotenv import load_dotenv


# --- Configuration ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please set it up.")
genai.configure(api_key=api_key)

# Initialize the LLM (Gemini 1.5 Flash) for analysis
llm_model = genai.GenerativeModel('gemini-1.5-flash')

# --- Simulated Agent Tools (Python Functions) ---

def extract_iocs_from_text(text: str) -> dict:
    """
    Simulates an IoC extraction tool. Extracts URLs, IP addresses, and Email addresses.
    This function represents a 'tool' the AI agent can conceptually 'use'.
    """
    iocs = {
        "urls": [],
        "ips": [],
        "emails": []
    }
    # Regex for URLs (simplified, captures http/https links)
    urls = re.findall(r'https?://[^\s/$.?#].[^\s]*', text)
    for url in urls:
        if url.endswith('.'): # Remove trailing period if it's from sentence end
            url = url[:-1]
        iocs["urls"].append(url)

    # Regex for IP addresses (IPv4 only, simplified)
    ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
    iocs["ips"].extend(ips)

    # Regex for email addresses
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    iocs["emails"].extend(emails)

    return iocs

def simulate_threat_lookup(ioc_type: str, ioc_value: str) -> str:
    """
    Simulates looking up an IoC's reputation (e.g., via VirusTotal, URLscan.io).
    This is another 'tool' the AI agent uses.
    """
    if ioc_type == "url":
        if "malicious" in ioc_value.lower() or "scam" in ioc_value.lower() or "phish" in ioc_value.lower():
            return f"Simulated Threat Intel for URL '{ioc_value}': Known MALICIOUS URL, categorized as phishing/malware distribution."
        elif "update" in ioc_value.lower() and random.random() < 0.7: # 70% chance to flag update domains as suspicious
            return f"Simulated Threat Intel for URL '{ioc_value}': SUSPICIOUS. Domain patterns suggest potential phishing or fake updates."
        else:
            return f"Simulated Threat Intel for URL '{ioc_value}': No immediate threat data found in simulated database."
    elif ioc_type == "ip":
        if ioc_value.startswith("192.168.") or ioc_value.startswith("10.") or ioc_value.startswith("172.16."):
            return f"Simulated Threat Intel for IP '{ioc_value}': INTERNAL/PRIVATE IP. Cannot be externally looked up."
        elif random.random() < 0.5: # 50% chance of being flagged as malicious
            return f"Simulated Threat Intel for IP '{ioc_value}': MALICIOUS. Associated with botnets or attack campaigns."
        else:
            return f"Simulated Threat Intel for IP '{ioc_value}': No threat data found in simulated database."
    elif ioc_type == "email":
        if "nigerianprince" in ioc_value.lower() or "urgentdelivery" in ioc_value.lower() or "amazonsupport" in ioc_value.lower():
            return f"Simulated Threat Intel for Email '{ioc_value}': KNOWN SPAM/SCAM SENDER."
        else:
            return f"Simulated Threat Intel for Email '{ioc_value}': No threat data found in simulated database."
    return f"Simulated Threat Intel for {ioc_type} '{ioc_value}': Type not recognized or no data."

# --- Core Agent Analysis Function (Orchestrates Tool Use and LLM Reasoning) ---
def analyze_threat_intelligence(input_text: str) -> str:
    """
    Orchestrates IoC extraction (tool use) and simulated lookups (tool use),
    then uses the LLM (brain) to provide a structured threat analysis report.
    """
    # Step 1: Agent uses "extract IoCs" tool
    iocs = extract_iocs_from_text(input_text)

    tool_outputs_list = []
    tool_outputs_list.append("--- IoC Extraction Tool Output ---")
    if any(iocs.values()): # Check if any IoCs were actually found
        for ioc_type, values in iocs.items():
            if values: # Only process if there are values for this type
                tool_outputs_list.append(f"Extracted {ioc_type.upper()}: {', '.join(values)}")
                # Step 2: Agent uses "threat lookup" tool for each found IoC
                for value in values:
                    # Call simulate_threat_lookup with singular ioc_type (e.g., 'url' not 'urls')
                    tool_outputs_list.append(simulate_threat_lookup(ioc_type.rstrip('s'), value))
    else:
        tool_outputs_list.append("No Indicators of Compromise (IoCs) extracted by tool.")
    tool_outputs_list.append("--------------------------------")

    tool_output_string = "\n".join(tool_outputs_list)

    # Step 3: Agent's "brain" (LLM) analyzes original text AND tool outputs
    prompt = f"""
    You are a highly skilled and diligent Cybersecurity Threat Intelligence Analyst AI. Your primary mission is to identify, assess, and report on potential cyber threats. Your analysis must be comprehensive, actionable, and based solely on the provided information.

    **IMPORTANT:**
    - If you see a filename with a double extension (e.g., .pdf.exe, .docx.exe, .jpg.exe, .txt.exe, etc.), or a file that looks like a document but ends with .exe, .scr, .bat, .cmd, .js, or other executable extensions, you MUST treat it as a HIGH or CRITICAL threat. This is a classic malware and social engineering tactic. Clearly state this in your summary and severity.
    - If the input text contains phrases like "password reset", "account compromised", "urgent action required", or similar, and includes a suspicious link (especially an external URL), you MUST treat this as a HIGH or CRITICAL threat. This is a classic phishing tactic. Clearly state this in your summary and severity, even if the link does not look obviously malicious.
    - Any email or message that urges the user to click a link to reset a password, verify an account, or respond urgently, especially if it contains a link or asks for credentials, should be considered a likely phishing attempt and assigned HIGH or CRITICAL severity.
    - However, a standard password change confirmation (e.g., "Your password was changed successfully. If you did not request this change, please contact support.") with NO suspicious links or urgent action requests should be considered safe and assigned LOW or INFORMATIONAL severity.

    **Input Text (e.g., suspicious email, log snippet, URL to analyze):**
    ```
    {input_text}
    ```

    **Tool Outputs (from automated IoC extraction and threat lookups):**
    ```
    {tool_output_string}
    ```

    **Based on your comprehensive analysis of BOTH the Input Text AND the Tool Outputs, provide a clear, structured, and actionable threat intelligence report in the following format:**

    1.  **Threat Summary:** A concise, high-level overview of the detected threat type (e.g., "Likely Phishing Attempt," "Potential Malware Distribution," "Suspicious Network Activity," "No Immediate Threat Detected").
    2.  **Identified IoCs & Findings:**
        * List all relevant IoCs (URLs, IPs, Emails) explicitly identified in the Input Text or Tool Outputs.
        * For each IoC, summarize its nature (e.g., "Mismatched URL," "Known malicious IP," "Suspicious sender email").
        * Mention any other key findings from the Input Text (e.g., social engineering tactics, unusual phrasing, unusual login patterns, or suspicious filenames/extensions).
    3.  **Severity Assessment:** Assign an overall severity (e.g., `Informational`, `Low`, `Medium`, `High`, `Critical`) for this specific threat. Justify your reasoning, referencing both the input text and tool outputs.
    4.  **Recommended Immediate Actions:** Provide concrete, prioritized steps for a user or IT security team to respond to this threat. Be specific and actionable.
    5.  **Disclaimer:** Always include a disclaimer stating this is an AI-generated initial analysis and full human security assessment is required.

    Generate the threat intelligence report now:
    """
    try:
        response = llm_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing threat intelligence: {e}. Please check API key and input."

# --- Test the Function (for direct execution during development) ---
if __name__ == "__main__":
    print("--- Cybersecurity Threat Intelligence Analyst Agent (Core Logic Test) ---")

    sample_input_1 = """
    Subject: Urgent Account Verification!

    Dear Valued Customer,

    We have detected unusual activity on your account. Click here to verify your details immediately: http://malicious-bank-update.info/login.html

    Failure to comply within 24 hours will result in account suspension.

    Sincerely,
    The Security Team <support@some-unusual-domain.biz>
    """
    print("\n--- Analyzing Sample 1 (Phishing Email) ---")
    analysis_1 = analyze_threat_intelligence(sample_input_1)
    print(analysis_1)

    print("-" * 70)

    sample_input_2 = """
    Alert: Failed login attempts for user 'admin' from 185.123.45.67 (GB) over last 5 minutes.
    Source: Firewall log. User tried 15 times with invalid password.
    """
    print("\n--- Analyzing Sample 2 (Login Log Anomaly) ---")
    analysis_2 = analyze_threat_intelligence(sample_input_2)
    print(analysis_2)

    print("-" * 70)

    sample_input_3 = "This is a regular email about project updates. No suspicious links or attachments."
    print("\n--- Analyzing Sample 3 (Benign Text) ---")
    analysis_3 = analyze_threat_intelligence(sample_input_3)
    print(analysis_3)

    print("\n--- Hour 1 Complete: IoC Tools & Core Analysis Confirmed ---")