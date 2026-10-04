"""
Streamlit Web UI for Task 5: Medicine & Symptom Information Assistant.
Features:
- Responsive, clean medical-themed UI layout with CSS styling
- Interactive AI Assistant Chat with red-flag emergency alert popups & LangGraph execution step view
- Dedicated Quick Tools: Drug Info Lookup, Drug Interaction Checker, Generic Finder
- Verified RAG Knowledge Base Browser (WHO Fact Sheets & Leaflets)
- Guardrail Agent Detection Accuracy & Evaluation Benchmark Report
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_graph import run_agent_workflow
from mcp_server import get_drug_info, check_drug_interaction, find_generic_equivalent
from rag_store import rag_store
from evaluation import run_evaluation, EVALUATION_DATASET

# Page Config
st.set_page_config(
    page_title="MedInfo Guard - Medicine & Symptom Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look and emergency styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1e3d59;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #43505c;
        margin-bottom: 1.5rem;
    }
    .emergency-box {
        background-color: #ffeded;
        border-left: 6px solid #e53935;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #900c3f;
    }
    .disclaimer-box {
        background-color: #f7f9fa;
        border: 1px solid #dcdfe3;
        padding: 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #55606d;
        margin-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .metric-card {
        background: #f0f7ff;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/medical-heart.png", width=70)
st.sidebar.title("MedInfo Guard 🩺")
st.sidebar.caption("Safe, Informational Healthcare Assistant")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Emergency Guidance")
st.sidebar.warning(
    "If you or someone else is experiencing severe chest pain, left arm numbness, sudden breathing difficulty, or signs of stroke, **call emergency services (911) immediately!**"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Sample Queries")
sample_queries = [
    "What is paracetamol used for and what are its side effects?",
    "Can I take ibuprofen with my blood pressure medication?",
    "Is there a cheaper generic for Tylenol?",
    "I have chest pain and my left arm feels numb.",
    "Can you diagnose if I have diabetes?"
]

selected_sample = st.sidebar.selectbox("Try a sample prompt:", ["Select a prompt..."] + sample_queries)

st.sidebar.markdown("---")
st.sidebar.info("Built with LangGraph Architecture, MCP Tools, OpenFDA API & RAG Knowledge Base.")

# Main Title Header
st.markdown('<div class="main-header">🩺 Medicine & Symptom Information Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Verified medicine explanations, drug-drug interaction screening, generic equivalents, and emergency guardrails.</div>', unsafe_allow_html=True)

# Application Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Assistant Chat", 
    "💊 Medicine Lookup", 
    "⚡ Interaction Checker", 
    "🏷️ Generic Finder", 
    "📚 RAG Knowledge Base", 
    "📊 Guardrail Benchmarks"
])

# ----------------------------------------------------
# TAB 1: ASSISTANT CHAT
# ----------------------------------------------------
with tab1:
    st.subheader("Interactive Safe Health Assistant")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your informational healthcare assistant. You can ask me about medicine uses, side effects, drug interactions, or generic alternatives.\n\n*Note: I do not provide medical diagnoses or prescriptions.*"}
        ]

    # Handle sample query insertion
    query_input_value = ""
    if selected_sample != "Select a prompt...":
        query_input_value = selected_sample

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask about medicines, interactions, or generics...", key="chat_input_field")
    
    # If user selected a sample from sidebar, auto submit if chat input empty
    if not user_query and query_input_value and ("last_sample" not in st.session_state or st.session_state.last_sample != query_input_value):
        user_query = query_input_value
        st.session_state.last_sample = query_input_value

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Screening query via Guardrails & processing response..."):
                agent_res = run_agent_workflow(user_query)
                
                # Show execution metadata expander
                with st.expander(f"⚙️ LangGraph Flow Details ({agent_res['node_executed']})", expanded=False):
                    st.json({
                        "node_executed": agent_res["node_executed"],
                        "guardrail_category": agent_res["guardrail_status"]["category"],
                        "trigger_reason": agent_res["guardrail_status"]["trigger_reason"],
                        "is_emergency": agent_res["is_emergency"],
                        "sources_consulted": agent_res["sources"]
                    })

                if agent_res["is_emergency"]:
                    st.error("🚨 EMERGENCY RED FLAG DETECTED")
                
                st.markdown(agent_res["response_text"])
                st.session_state.messages.append({"role": "assistant", "content": agent_res["response_text"]})


# ----------------------------------------------------
# TAB 2: MEDICINE LOOKUP TOOL
# ----------------------------------------------------
with tab2:
    st.subheader("💊 Monograph & Drug Info Lookup")
    st.write("Retrieve structured usage, side effects, and warning monographs for any drug.")
    
    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
        med_search_term = st.text_input("Enter medicine name (e.g. Paracetamol, Ibuprofen, Lisinopril, Metformin):", value="Paracetamol")
    with col_m2:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_lookup = st.button("Lookup Drug Info", use_container_width=True)
        
    if med_search_term or btn_lookup:
        info_data = get_drug_info(med_search_term)
        if info_data.get("found"):
            st.success(f"Monograph for **{info_data['medicine_name']}** (Source: {info_data['source']})")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Therapeutic Class:** {info_data['class']}")
                st.markdown(f"**Common Brand Names:** {', '.join(info_data['brand_names'])}")
                st.markdown(f"**Typical Dosage Form:** {info_data['dosage']}")
            with c2:
                st.markdown("**Primary Indications / Uses:**")
                for u in info_data['uses']:
                    st.markdown(f"- {u}")
                    
            st.markdown("---")
            st.warning("**Key Warnings & Precautions:**")
            for w in info_data['warnings']:
                st.markdown(f"- {w}")

            st.info("**Common Side Effects:**")
            for s in info_data['side_effects']:
                st.markdown(f"- {s}")
        else:
            st.error(info_data.get("message"))


# ----------------------------------------------------
# TAB 3: INTERACTION CHECKER
# ----------------------------------------------------
with tab3:
    st.subheader("⚡ Drug-Drug Interaction Checker")
    st.write("Check documented interactions between multiple medications or dietary substances.")

    ic1, ic2 = st.columns(2)
    with ic1:
        drug_a = st.text_input("First Medication / Substance:", value="Ibuprofen")
    with ic2:
        drug_b = st.text_input("Second Medication / Substance:", value="Lisinopril")

    if st.button("Check Interactions", type="primary"):
        with st.spinner("Checking interaction database & OpenFDA rules..."):
            res_inter = check_drug_interaction([drug_a, drug_b])
            
            if res_inter["has_interaction"]:
                st.error("⚠️ Potential Interaction Detected!")
                for rule in res_inter["interactions"]:
                    st.markdown(f"### Severity: `{rule['severity']}`")
                    st.markdown(f"**Summary:** {rule['summary']}")
                    st.markdown(f"**Clinical Recommendation:** {rule['recommendation']}")
            else:
                st.success("✅ No Severe Interactions Documented in Primary Database")
                st.write(res_inter["message"])


# ----------------------------------------------------
# TAB 4: GENERIC FINDER
# ----------------------------------------------------
with tab4:
    st.subheader("🏷️ Generic Equivalent Finder")
    st.write("Find cost-effective generic alternatives for commercial brand-name medications.")

    brand_input = st.text_input("Enter Brand Name (e.g. Tylenol, Advil, Zestril, Lipitor, Norvasc):", value="Tylenol")
    if st.button("Find Generic Equivalent"):
        gen_res = find_generic_equivalent(brand_input)
        if gen_res["found"]:
            st.success(f"Generic Match Found for **{gen_res['input_name']}**!")
            st.markdown(f"- **Generic Active Chemical**: `{gen_res['generic_active_ingredient']}`")
            st.markdown(f"- **Drug Class**: {gen_res['drug_class']}")
            st.markdown(f"- **Equivalent Commercial Brands**: {', '.join(gen_res['equivalent_brand_names'])}")
            st.info(f"💡 **Cost Savings**: {gen_res['cost_saving_note']}")
        else:
            st.warning(gen_res["message"])


# ----------------------------------------------------
# TAB 5: RAG KNOWLEDGE BASE BROWSER
# ----------------------------------------------------
with tab5:
    st.subheader("📚 Verified RAG Knowledge Base")
    st.write("Explore verified WHO fact sheets, emergency first aid guides, and patient information leaflets.")

    search_rag = st.text_input("Search knowledge base documents:", value="cardiovascular emergency")
    if search_rag:
        docs = rag_store.search(search_rag, top_k=5)
        st.write(f"Found {len(docs)} matching documents:")
        for doc in docs:
            with st.expander(f"📄 {doc['title']} ({doc['topic']})"):
                st.markdown(doc["content"])


# ----------------------------------------------------
# TAB 6: GUARDRAIL BENCHMARKS & EVALUATION REPORT
# ----------------------------------------------------
with tab6:
    st.subheader("📊 Guardrail Agent Benchmark & Accuracy Report")
    st.write("Evaluation metrics testing the Guardrail Agent's ability to detect emergency red flags and reject diagnostic requests.")

    if st.button("Run Full Evaluation Suite"):
        with st.spinner("Running evaluation benchmark suite across test dataset..."):
            metrics = run_evaluation()
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Overall Accuracy", f"{metrics['accuracy_percentage']}%")
            with m2:
                st.metric("Emergency Precision", f"{metrics['emergency_precision']}%")
            with m3:
                st.metric("Emergency Recall", f"{metrics['emergency_recall']}%")

            st.markdown("### Detailed Benchmark Test Results")
            st.dataframe(metrics["detailed_results"], use_container_width=True)

# Footer Disclaimer
st.markdown("---")
st.markdown('<div class="disclaimer-box"><b>Standard Medical Disclaimer:</b> This application is strictly an educational tool powered by AI. It does not replace professional medical judgment, diagnosis, or treatment. In case of medical emergency, contact your local emergency services immediately.</div>', unsafe_allow_html=True)
