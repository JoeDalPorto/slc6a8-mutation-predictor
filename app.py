import streamlit as st

# 1. Page Configuration & Title Styling
st.set_page_config(
    page_title="SLC6A8 Mutation Predictor",
    page_icon="🧬",
    layout="centered"
)

st.title("🧬 SLC6A8 Computational Mutation Effect Predictor")
st.markdown("Predict how structural domain variations across the SLC6A8 protein impact variant pathogenicity risks.")
st.divider()

# Dictionary to decode single letter amino acids to full names
AA_MAP = {
    'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartate',
    'C': 'Cysteine', 'E': 'Glutamate', 'Q': 'Glutamine', 'G': 'Glycine',
    'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
    'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
    'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine',
    '*': 'Stop Codon'
}

# 2. Left Sidebar Control Panel (The Interactive Configuration Panel)
with st.sidebar:
    st.header("🧬 Mutation Configuration")
    st.write("Adjust parameters to dynamically calculate the phenotypic impact.")
    st.divider()
    
    # Mutational Mechanism Dropdown
    mutation_type = st.selectbox(
        "Mutation Type / Mechanism",
        ["Missense", "Nonsense", "Frameshift", "Synonymous"],
        index=0
    )
    
    # Interactive Amino Acid Slider (1 to 635)
    position = st.slider(
        "Amino Acid Site of Interest",
        min_value=1,
        max_value=635,
        value=351,
        step=1,
        help="Slide across the 635 amino acid sequence of the SLC6A8 transporter."
    )
    
    st.divider()
    
    # Conditional target substitute controls (only shows when relevant to clean up space)
    wt_aa = "N/A"
    mut_aa = "N/A"
    if mutation_type == "Missense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)     # Default G
        mut_aa = st.selectbox("Target Substitute Amino Acid", list(AA_MAP.keys()), index=1) # Default R
    elif mutation_type == "Nonsense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)
        mut_aa = "*"

# 3. Structural Topology Mapping Logic
domains = [
    {"name": "N-terminus (Intracellular)", "range": range(1, 41)},
    {"name": "TM1 - TM6 Domains", "range": range(41, 300)},
    {"name": "TM7 - TM8 (Creatine Binding Pocket)", "range": range(300, 420)},
    {"name": "TM9 - TM12 Domains", "range": range(420, 570)},
    {"name": "C-terminus (Intracellular)", "range": range(570, 636)}
]

domain_found = "Unknown"
for dom in domains:
    if position in dom["range"]:
        domain_found = dom["name"]
        break

# 4. Pathogenicity Algorithm
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction = "Pathogenic (High Risk)"
    status_color = "red"
    alert_box = st.error
    hgvs = f"p.{(wt_aa if wt_aa != 'N/A' else 'X')}{position}fs" if mutation_type == "Frameshift" else f"p.{wt_aa}{position}*"
    mechanism = f"Variant **{hgvs}** causes a major structural truncation or nonsense-mediated decay, leading to an absolute loss of functional Creatine Transporter 1 (CT1)."
elif mutation_type == 'Synonymous':
    prediction = "Benign / Low Risk"
    status_color = "green"
    alert_box = st.success
    mechanism = "The alternative codon yields the identical amino acid residue. The primary protein structure and transport kinetics remain completely normal."
else:  # Missense
    hgvs = f"p.{wt_aa}{position}{mut_aa}"
    if "TM7 - TM8" in domain_found:
        prediction = "Likely Pathogenic (High Risk)"
        status_color = "red"
        alert_box = st.error
        mechanism = f"The change **{hgvs}** ({AA_MAP.get(wt_aa)} → {AA_MAP.get(mut_aa)}) shifts spatial characteristics inside the critical substrate core, breaking creatine binding."
    elif "terminus" in domain_found:
        prediction = "Likely Benign / Tolerated (Low Risk)"
        status_color = "green"
        alert_box = st.success
        mechanism = f"The change **{hgvs}** shifts an amino acid in a flexible, variable terminal tail. Point substitutions outside membrane boundaries are structurally tolerated."
    else:
        prediction = "Variant of Uncertain Significance (VUS - Moderate Risk)"
        status_color = "orange"
        alert_box = st.warning
        mechanism = f"The change **{hgvs}** changes properties inside a general transmembrane support helical channel. Requires empirical uptake tracking to confirm disruption profile."

# 5. Dashboard Output Layout (Main Interface Panel)
st.subheader("📊 Algorithmic Consequence Assessment")

# Display Domain Location & Standardized Name Side-by-Side
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Target Topology Mapping", value=domain_found)
with col2:
    if mutation_type in ["Missense", "Nonsense"]:
        st.metric(label="HGVS Standard Variant Name", value=hgvs)
    else:
        st.metric(label="Variant Structural Profile", value=mutation_type)

# Display the main classification container color code
alert_box(f"### **Prediction Outcome:** {prediction}")

# Display Explanatory Mechanism Card
st.info(f"**Predicted Molecular Mechanism Impact:**\n\n{mechanism}")

# 6. Interactive Localization Graphic Map
st.subheader("🗺️ Structural Chain Mapping Visualization")
graph_str = ""
for dom in domains:
    if position in dom["range"]:
        graph_str += f" 👉 **[🔴 {dom['name']}]** ──"
    else:
        graph_str += f" [ {dom['name'].split(' (')[0]} ] ──"
graph_str = graph_str.rstrip(" ──")

st.markdown(f"<div style='background-color:#1e1e24; padding:15px; border-radius:8px; border-left:5px solid #ff4b4b; color: white;'>{graph_str}</div>", unsafe_allow_html=True)

