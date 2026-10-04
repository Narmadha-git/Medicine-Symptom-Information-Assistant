"""
Orchestration workflow / Agent design using state-based graph logic (LangGraph architecture concept).

Nodes:
1. Guardrail Node: Screens input for red flags / out-of-scope.
2. Escalation Node: Emits red emergency alert guidance.
3. Out-Of-Scope Node: Returns polite declination.
4. Interaction Agent Node: Executes check_interaction tool.
5. Info Agent Node: Executes drug_info tool + generic_finder tool + RAG search + Tavily search fallback.
6. Formatter Node: Adds standardized mandatory medical disclaimer and source attributions.
"""

from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from guardrails import evaluate_guardrails
from mcp_server import get_drug_info, check_drug_interaction, find_generic_equivalent
from rag_store import rag_store

MANDATORY_DISCLAIMER = (
    "\n\n---"
    "\n⚠️ **Standard Medical Disclaimer**: *This information is strictly for general educational purposes "
    "and does NOT constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider, "
    "physician, or licensed pharmacist before making any medical decisions or changing any treatment plan.*"
)

def run_agent_workflow(user_query: str) -> Dict[str, Any]:
    """
    Main orchestration pipeline that models the LangGraph flow:
    Query -> Guardrail Node -> [Escalation | Out-of-Scope | Info/Interaction Agent] -> Output Formatter
    """
    state = {
        "query": user_query,
        "guardrail_status": None,
        "node_executed": None,
        "response_text": "",
        "sources": [],
        "is_emergency": False
    }

    # Step 1: Guardrail Agent Node
    guardrail_result = evaluate_guardrails(user_query)
    state["guardrail_status"] = guardrail_result

    # Step 2: Route based on Guardrail decision
    if guardrail_result["is_emergency"]:
        # Escalation Node
        state["node_executed"] = "Escalation Node (LangGraph Interrupt)"
        state["is_emergency"] = True
        state["response_text"] = (
            "🚨 **RED-FLAG EMERGENCY DETECTED**\n\n"
            "Your query indicates potential medical emergency symptoms (e.g. chest pain, numbness, respiratory distress, or severe allergic reaction).\n\n"
            "**IMMEDIATE ACTION REQUIRED:**\n"
            "- Call **911** (or your local emergency medical service) immediately.\n"
            "- Go to the nearest emergency room (ER).\n"
            "- Do NOT wait for online replies or self-medicate."
        ) + MANDATORY_DISCLAIMER
        return state

    if guardrail_result["is_out_of_scope"]:
        # Out-of-Scope Node
        state["node_executed"] = "Declination Node"
        state["response_text"] = (
            "ℹ️ **Out of Scope Request**\n\n"
            "I am an informational AI health assistant and cannot provide medical diagnoses or write prescriptions. "
            "Please consult a certified medical doctor or healthcare professional for diagnosis or personalized medical prescriptions."
        ) + MANDATORY_DISCLAIMER
        return state

    # Step 3: Determine if Interaction query vs General Info / Generic query
    query_lower = user_query.lower()
    
    # Interaction Query Detection
    if any(k in query_lower for k in ["take with", "together", "interaction", "interact", "combine", "mixing"]):
        state["node_executed"] = "Interaction Agent Node"
        
        # Extract medicine names mentioned in query
        medicines = []
        for drug in ["paracetamol", "ibuprofen", "lisinopril", "amlodipine", "amoxicillin", "metformin", "atorvastatin", "alcohol", "grapefruit", "blood pressure"]:
            if drug in query_lower:
                medicines.append(drug)
        
        # Default fallback list if ambiguous
        if len(medicines) < 2:
            if "ibuprofen" in query_lower:
                medicines = ["ibuprofen", "lisinopril"]
            elif "paracetamol" in query_lower:
                medicines = ["paracetamol", "alcohol"]

        interaction_res = check_drug_interaction(medicines if medicines else ["ibuprofen", "blood pressure medicine"])
        rag_docs = rag_store.search(user_query)

        res_msg = f"### Drug Interaction Analysis\n\n"
        if interaction_res["has_interaction"]:
            res_msg += f"⚠️ **Interaction Warning**: Potential interactions detected between **{', '.join(interaction_res['medicines_checked'])}**.\n\n"
            for inter in interaction_res["interactions"]:
                res_msg += f"- **Severity**: `{inter['severity']}`\n"
                res_msg += f"- **Summary**: {inter['summary']}\n"
                res_msg += f"- **Recommendation**: {inter['recommendation']}\n\n"
        else:
            res_msg += f"✅ {interaction_res.get('message')}\n\n"

        if rag_docs:
            res_msg += "### 📚 Verified Knowledge Base Context\n"
            for doc in rag_docs:
                res_msg += f"**[{doc['title']}]**\n_{doc['content'].strip()}_\n\n"
                state["sources"].append(doc["title"])

        state["response_text"] = res_msg + MANDATORY_DISCLAIMER
        return state

    # Generic Finder Query Detection
    if any(k in query_lower for k in ["cheaper", "generic", "brand", "alternative"]):
        state["node_executed"] = "Info Agent Node (Generic Finder)"
        
        # find drug name
        drug_target = "tylenol"
        for d in ["tylenol", "panadol", "advil", "motrin", "zestril", "norvasc", "glucophage", "lipitor", "paracetamol", "ibuprofen"]:
            if d in query_lower:
                drug_target = d
                break

        generic_res = find_generic_equivalent(drug_target)
        res_msg = f"### Generic Equivalent Search\n\n"
        if generic_res["found"]:
            res_msg += f"- **Branded Name**: {generic_res['input_name'].capitalize()}\n"
            res_msg += f"- **Generic Active Ingredient**: **{generic_res['generic_active_ingredient']}**\n"
            res_msg += f"- **Drug Class**: {generic_res['drug_class']}\n"
            res_msg += f"- **Equivalent Brands**: {', '.join(generic_res['equivalent_brand_names'])}\n\n"
            res_msg += f"💰 **Cost Saving Note**: {generic_res['cost_saving_note']}\n"
            state["sources"].append("OpenFDA / Curated Generic Mapping Database")
        else:
            res_msg += f"{generic_res['message']}\n"

        state["response_text"] = res_msg + MANDATORY_DISCLAIMER
        return state

    # Default General Info Query Node
    state["node_executed"] = "Info Agent Node (Drug Info & RAG)"
    
    # Identify target drug
    target_drug = "paracetamol"
    for d in ["paracetamol", "ibuprofen", "lisinopril", "amlodipine", "amoxicillin", "metformin", "atorvastatin"]:
        if d in query_lower:
            target_drug = d
            break

    drug_res = get_drug_info(target_drug)
    rag_docs = rag_store.search(user_query)

    res_msg = f"### 💊 Medicine Information: {drug_res.get('medicine_name', target_drug.capitalize())}\n\n"
    if drug_res.get("found"):
        res_msg += f"**Data Source**: _{drug_res['source']}_\n\n"
        res_msg += f"- **Therapeutic Class**: {drug_res['class']}\n"
        res_msg += f"- **Brand Names**: {', '.join(drug_res['brand_names'])}\n"
        res_msg += f"- **Primary Uses**: {', '.join(drug_res['uses'])}\n"
        res_msg += f"- **Common Side Effects**: {', '.join(drug_res['side_effects'])}\n"
        res_msg += f"- **Key Warnings**: {', '.join(drug_res['warnings'])}\n"
        state["sources"].append(drug_res['source'])
    
    if rag_docs:
        res_msg += "\n### 📖 WHO Fact Sheet & Leaflet Excerpts\n"
        for doc in rag_docs:
            res_msg += f"**{doc['title']}**\n{doc['content'].strip()}\n\n"
            state["sources"].append(doc["title"])

    state["response_text"] = res_msg + MANDATORY_DISCLAIMER
    return state

if __name__ == "__main__":
    print("Testing Agent Graph...")
    res = run_agent_workflow("What is paracetamol used for?")
    print(res["response_text"][:300])
