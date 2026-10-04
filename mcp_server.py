"""
MCP Tools Implementation for Medicine & Symptom Assistant.
Provides drug_info, check_interaction, and find_generic tools with OpenFDA API integration + local dataset fallback.
"""

import requests
from typing import Dict, List, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.health_data import MEDICINE_DATABASE, INTERACTION_RULES

OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json"

def get_drug_info(medicine_name: str) -> Dict[str, Any]:
    """
    Retrieves uses, common side effects, warnings, and class for a given medicine.
    Checks OpenFDA API first; falls back to local curated database if offline or not found.
    """
    clean_name = medicine_name.strip().lower()
    
    # 1. Try local dataset first for high accuracy & speed on common terms
    for key, data in MEDICINE_DATABASE.items():
        if clean_name in key or key in clean_name or any(clean_name in b.lower() for b in data["brand_names"]):
            return {
                "found": True,
                "source": "Curated Medical Knowledge Base",
                "medicine_name": data["generic_name"],
                "brand_names": data["brand_names"],
                "class": data["class"],
                "uses": data["uses"],
                "side_effects": data["side_effects"],
                "warnings": data["warnings"],
                "dosage": data["common_dosage_form"]
            }
            
    # 2. Try OpenFDA Drug Label API
    try:
        response = requests.get(
            OPENFDA_LABEL_URL,
            params={"search": f'openfda.generic_name:"{clean_name}" OR openfda.brand_name:"{clean_name}"', "limit": 1},
            timeout=4
        )
        if response.status_code == 200:
            res_json = response.json()
            results = res_json.get("results", [])
            if results:
                item = results[0]
                openfda = item.get("openfda", {})
                generic_name = openfda.get("generic_name", [medicine_name.capitalize()])[0]
                brand_name = openfda.get("brand_name", [])
                
                indications = item.get("indications_and_usage", ["Information not specified in standard format."])[0][:300]
                adverse = item.get("adverse_reactions", ["Consult drug label for side effect profile."])[0][:300]
                warnings = item.get("warnings", ["Consult healthcare professional before use."])[0][:300]
                
                return {
                    "found": True,
                    "source": "US FDA (OpenFDA) Official Drug Label API",
                    "medicine_name": generic_name.title(),
                    "brand_names": brand_name[:5],
                    "class": openfda.get("pharm_class_cs", ["General Pharmacotherapy"])[0] if openfda.get("pharm_class_cs") else "Pharmaceutical",
                    "uses": [indications],
                    "side_effects": [adverse],
                    "warnings": [warnings],
                    "dosage": "Refer to product packaging or physician advice"
                }
    except Exception as e:
        pass
        
    return {
        "found": False,
        "query": medicine_name,
        "message": f"Could not find detailed monograph for '{medicine_name}'. Please verify the spelling or check with a licensed pharmacist."
    }

def check_drug_interaction(medicines: List[str]) -> Dict[str, Any]:
    """
    Checks known interactions between two or more medicines or substance keywords.
    """
    cleaned = [m.strip().lower() for m in medicines]
    found_interactions = []
    
    for rule in INTERACTION_RULES:
        pair = rule["pair"]
        # check if all items in pair match anything in cleaned
        match_count = 0
        for p in pair:
            if any(p in c or c in p for c in cleaned):
                match_count += 1
        if match_count >= 2:
            found_interactions.append(rule)
            
    if found_interactions:
        return {
            "has_interaction": True,
            "medicines_checked": medicines,
            "interactions": found_interactions,
            "summary_warning": "Potential interactions detected. Consult your physician or pharmacist before taking these medications together."
        }
        
    return {
        "has_interaction": False,
        "medicines_checked": medicines,
        "message": f"No severe documented interactions found between {', '.join(medicines)} in our primary database. Note: Always consult a doctor or pharmacist for a complete clinical review."
    }

def find_generic_equivalent(branded_name: str) -> Dict[str, Any]:
    """
    Returns generic active ingredient equivalents and typical brand alternatives for a given drug name.
    """
    clean_name = branded_name.strip().lower()
    
    for key, data in MEDICINE_DATABASE.items():
        if clean_name in key or any(clean_name in b.lower() for b in data["brand_names"]):
            return {
                "found": True,
                "input_name": branded_name,
                "generic_active_ingredient": data["generic_name"],
                "equivalent_brand_names": data["brand_names"],
                "drug_class": data["class"],
                "cost_saving_note": f"Generic '{data['generic_name']}' contains the exact same active pharmaceutical ingredient as branded versions ({', '.join(data['brand_names'])}) and is typically 50%-80% less expensive."
            }
            
    # OpenFDA fallback lookup
    try:
        response = requests.get(
            OPENFDA_LABEL_URL,
            params={"search": f'openfda.brand_name:"{clean_name}"', "limit": 1},
            timeout=4
        )
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                openfda = results[0].get("openfda", {})
                generic = openfda.get("generic_name", [])
                if generic:
                    return {
                        "found": True,
                        "input_name": branded_name,
                        "generic_active_ingredient": generic[0].title(),
                        "equivalent_brand_names": openfda.get("brand_name", [])[:5],
                        "drug_class": "Therapeutic Agent",
                        "cost_saving_note": f"Generic '{generic[0].title()}' offers identical therapeutic activity as brand '{branded_name}' at a significantly lower retail cost."
                    }
    except Exception:
        pass

    return {
        "found": False,
        "input_name": branded_name,
        "message": f"Generic mapping for '{branded_name}' was not found. Ask your local pharmacist to verify the generic chemical name."
    }

if __name__ == "__main__":
    print("Testing MCP Tools...")
    print(get_drug_info("paracetamol"))
    print(check_drug_interaction(["ibuprofen", "lisinopril"]))
    print(find_generic_equivalent("Tylenol"))
