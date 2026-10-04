"""
Guardrails module for screening queries.
Screening covers:
1. Emergency Red Flags (chest pain, severe dyspnea, stroke signs, anaphylaxis, suicide/self-harm).
2. Out-of-Scope Requests (direct diagnosis, requests for prescriptions/dosage for a specific child/individual patient).
"""

import re
from typing import Dict, Any

# Emergency Red Flag Keywords & Symptoms
EMERGENCY_PATTERNS = [
    r"\bchest pain\b",
    r"\bleft arm (numb|pain|tingling)\b",
    r"\barm feels numb\b",
    r"\bshortness of breath\b",
    r"\bcan'?t breathe\b",
    r"\bcannot breathe\b",
    r"\bdifficulty breathing\b",
    r"face (is )?droop",
    r"\bslurred speech\b",
    r"\bsevere allergic reaction\b",
    r"\bswelling up\b",
    r"\banaphylaxis\b",
    r"\bsudden loss of vision\b",
    r"\bcoughing up blood\b",
    r"\bunconscious\b",
    r"\bpassed out\b",
    r"\bsuicide\b",
    r"\bkill myself\b"
]

# Diagnostic / Prescribing Out-of-Scope Patterns
DIAGNOSIS_PATTERNS = [
    r"\bdo i have\b",
    r"\bdiagnose me\b",
    r"\bwhat disease do i have\b",
    r"\bprescribe me\b",
    r"\bwrite me a prescription\b",
    r"\bcan you tell me if i have cancer\b"
]

def evaluate_guardrails(user_query: str) -> Dict[str, Any]:
    """
    Evaluates a user query against safety policies.
    Returns standard decision dict:
    - is_emergency: bool
    - is_out_of_scope: bool
    - category: "EMERGENCY" | "DIAGNOSIS_REJECT" | "SAFE_INFO"
    - trigger_reason: str
    """
    query_lower = user_query.lower()

    # 1. Check Emergency Red Flags
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, query_lower):
            return {
                "is_emergency": True,
                "is_out_of_scope": False,
                "category": "EMERGENCY",
                "trigger_reason": f"Matched emergency red flag symptom/pattern: '{re.search(pattern, query_lower).group(0)}'",
                "action": "ROUTE_TO_ESCALATION"
            }

    # 2. Check Diagnostic or Prescribing Requests
    for pattern in DIAGNOSIS_PATTERNS:
        if re.search(pattern, query_lower):
            return {
                "is_emergency": False,
                "is_out_of_scope": True,
                "category": "DIAGNOSIS_REJECT",
                "trigger_reason": "Medical diagnosis or prescription issuance requested",
                "action": "DECLINE_POLITELY"
            }

    # 3. Safe Informational Query
    return {
        "is_emergency": False,
        "is_out_of_scope": False,
        "category": "SAFE_INFO",
        "trigger_reason": "General medicine or health information request",
        "action": "ROUTE_TO_AGENT"
    }

if __name__ == "__main__":
    print(evaluate_guardrails("I have chest pain and my left arm feels numb."))
    print(evaluate_guardrails("Can you diagnose me if I have diabetes?"))
    print(evaluate_guardrails("What is paracetamol used for?"))
