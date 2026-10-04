"""
Curated knowledge base documents for RAG (WHO fact sheets, first aid, drug information).
"""

WHO_FACT_SHEETS = [
    {
        "title": "WHO Fact Sheet: Cardiovascular Diseases & Emergency Signs",
        "topic": "Cardiovascular / Emergency",
        "content": """
Cardiovascular diseases (CVDs) are the leading cause of death globally. 
Warning signs of a heart attack include:
- Severe chest pain or discomfort, squeezing feeling in the center of the chest.
- Pain or discomfort spreading to shoulders, left arm, neck, jaw, or back.
- Shortness of breath, dizziness, cold sweat, or nausea.
If any of these symptoms occur, immediate emergency medical intervention (calling 911 or local emergency services) is critical. Do not attempt self-medication.
        """
    },
    {
        "title": "WHO Fact Sheet: Hypertension and Blood Pressure Management",
        "topic": "Hypertension",
        "content": """
Hypertension (high blood pressure) is when pressure in your blood vessels is too high (140/90 mmHg or higher).
Common antihypertensive classes:
- ACE Inhibitors (e.g., Lisinopril, Enalapril)
- ARBs (e.g., Losartan, Valsartan)
- Beta-blockers (e.g., Metoprolol, Atenolol)
- Calcium Channel Blockers (e.g., Amlodipine)
- NSAIDs like ibuprofen or naproxen can reduce the effectiveness of antihypertensive medications and cause fluid retention, potentially elevating blood pressure. Always consult a physician before combining NSAIDs with blood pressure medications.
        """
    },
    {
        "title": "WHO Fact Sheet: Antimicrobial Resistance and Safe Antibiotic Use",
        "topic": "Antibiotics",
        "content": """
Antibiotics are medicines used to prevent and treat bacterial infections.
Key principles:
- Only use antibiotics when prescribed by a certified health professional.
- Always complete the full prescribed course, even if feeling better.
- Common antibiotics include Amoxicillin, Azithromycin, Ciprofloxacin.
- Antibiotics do not treat viral infections like flu or common colds.
        """
    },
    {
        "title": "First Aid Leaflet: Stroke & Neurological Emergencies",
        "topic": "Emergency First Aid",
        "content": """
Use FAST to identify stroke symptoms:
- Face dropping on one side.
- Arm weakness or numbness, especially on one side of the body.
- Speech difficulty or slurred speech.
- Time to call emergency services immediately!
Immediate hospital treatment within hours can dramatically reduce long-term disability.
        """
    },
    {
        "title": "Patient Guidance Leaflet: Pain Management & Analgesics",
        "topic": "Pain Relief",
        "content": """
Paracetamol (Acetaminophen): Used for mild-to-moderate pain and fever reduction. Safe when used at recommended doses (max 4,000 mg per day for adults). Overdose can lead to severe liver damage.
Ibuprofen: A Non-Steroidal Anti-Inflammatory Drug (NSAID) used for pain, inflammation, and fever. Side effects include stomach irritation, heartburn, and increased risk of gastrointestinal ulcers. Avoid taking on an empty stomach.
        """
    }
]

MEDICINE_DATABASE = {
    "paracetamol": {
        "generic_name": "Paracetamol (Acetaminophen)",
        "brand_names": ["Tylenol", "Panadol", "Calpol", "Crocin"],
        "class": "Analgesic & Antipyretic",
        "uses": ["Mild to moderate pain relief", "Fever reduction", "Headaches", "Muscle aches"],
        "side_effects": ["Nausea (mild)", "Allergic rash (rare)", "Liver damage (at high doses or with alcohol)"],
        "warnings": ["Maximum daily dose for adults is 4000 mg (4g).", "Do not consume with heavy alcohol.", "Check other cold medications to avoid duplicate acetaminophen dosing."],
        "common_dosage_form": "500 mg tablets, liquid syrup"
    },
    "ibuprofen": {
        "generic_name": "Ibuprofen",
        "brand_names": ["Advil", "Motrin", "Nurofen", "Brufen"],
        "class": "NSAID (Nonsteroidal Anti-inflammatory Drug)",
        "uses": ["Pain relief", "Inflammation reduction", "Fever reduction", "Arthritis", "Menstrual cramps"],
        "side_effects": ["Stomach upset", "Heartburn", "Dizziness", "GI ulcer risk with prolonged use"],
        "warnings": ["Take with food or milk to minimize stomach upset.", "May decrease efficacy of blood pressure medicines (e.g. Lisinopril, Amlodipine).", "Avoid in severe kidney disease or active stomach ulcers."],
        "common_dosage_form": "200 mg, 400 mg tablets"
    },
    "lisinopril": {
        "generic_name": "Lisinopril",
        "brand_names": ["Zestril", "Prinivil"],
        "class": "ACE Inhibitor",
        "uses": ["Hypertension (high blood pressure)", "Heart failure management", "Post-myocardial infarction care"],
        "side_effects": ["Dry persistent cough", "Dizziness/lightheadedness", "Elevated potassium levels"],
        "warnings": ["Do not use during pregnancy.", "Interacts with NSAIDs like ibuprofen (may impair kidney function and reduce blood pressure control).", "Seek immediate help if facial or throat swelling (angioedema) occurs."],
        "common_dosage_form": "5 mg, 10 mg, 20 mg tablets"
    },
    "amlodipine": {
        "generic_name": "Amlodipine",
        "brand_names": ["Norvasc"],
        "class": "Calcium Channel Blocker",
        "uses": ["Hypertension", "Angina (chest pain) prevention"],
        "side_effects": ["Swelling in ankles/feet (edema)", "Dizziness", "Flushing"],
        "warnings": ["Avoid grapefruit juice in large quantities.", "Report sudden swelling or rapid weight gain to doctor."],
        "common_dosage_form": "5 mg, 10 mg tablets"
    },
    "amoxicillin": {
        "generic_name": "Amoxicillin",
        "brand_names": ["Amoxil", "Moxatag", "Novamox"],
        "class": "Penicillin Antibiotic",
        "uses": ["Bacterial infections (ear, nose, throat, skin, urinary tract)"],
        "side_effects": ["Diarrhea", "Nausea", "Mild skin rash"],
        "warnings": ["Do not take if allergic to penicillin.", "Complete full course as prescribed to prevent antibiotic resistance."],
        "common_dosage_form": "250 mg, 500 mg capsules"
    },
    "metformin": {
        "generic_name": "Metformin",
        "brand_names": ["Glucophage", "Fortamet"],
        "class": "Biguanide Antidiabetic",
        "uses": ["Type 2 Diabetes Mellitus management"],
        "side_effects": ["Nausea", "Diarrhea", "Abdominal discomfort", "Metallic taste"],
        "warnings": ["Take with meals.", "Rare risk of lactic acidosis.", "Avoid heavy alcohol consumption."],
        "common_dosage_form": "500 mg, 850 mg, 1000 mg tablets"
    },
    "atorvastatin": {
        "generic_name": "Atorvastatin",
        "brand_names": ["Lipitor"],
        "class": "Statin (HMG-CoA Reductase Inhibitor)",
        "uses": ["High cholesterol management", "Cardiovascular disease prevention"],
        "side_effects": ["Muscle pain/weakness", "Digestive issues", "Mild elevation in liver enzymes"],
        "warnings": ["Report unexplained muscle soreness or weakness promptly.", "Avoid excessive grapefruit intake."],
        "common_dosage_form": "10 mg, 20 mg, 40 mg tablets"
    }
}

INTERACTION_RULES = [
    {
        "pair": ["ibuprofen", "lisinopril"],
        "severity": "Moderate to High",
        "summary": "NSAIDs like Ibuprofen can diminish the blood pressure-lowering effect of ACE inhibitors like Lisinopril and increase the risk of kidney impairment.",
        "recommendation": "Consult a healthcare provider before combining. Paracetamol may be a safer pain relief alternative for patients taking blood pressure medication."
    },
    {
        "pair": ["ibuprofen", "amlodipine"],
        "severity": "Moderate",
        "summary": "Ibuprofen may cause fluid retention and slightly offset blood pressure reduction from Amlodipine.",
        "recommendation": "Monitor blood pressure if taken together short-term, or ask a doctor for alternative pain relief."
    },
    {
        "pair": ["paracetamol", "alcohol"],
        "severity": "High",
        "summary": "Combining Paracetamol with heavy alcohol intake significantly increases the risk of acute liver toxicity.",
        "recommendation": "Avoid heavy alcohol consumption while taking paracetamol."
    },
    {
        "pair": ["atorvastatin", "grapefruit"],
        "severity": "Moderate",
        "summary": "Large amounts of grapefruit juice inhibit enzymes that break down Atorvastatin, increasing drug levels and side effect risks.",
        "recommendation": "Limit or avoid grapefruit consumption while taking Atorvastatin."
    }
]
