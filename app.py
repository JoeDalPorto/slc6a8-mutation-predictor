import streamlit as st
import streamlit.components.v1 as html

st.set_page_config(
    page_title="SLC6A8 Mutation Predictor",
    page_icon="🧬",
    layout="centered"
)

st.title("🧬 SLC6A8 Computational Mutation Effect Predictor")
st.markdown("Predict how structural domain variations across the SLC6A8 protein impact variant pathogenicity risks.")
st.divider()

AA_MAP = {
    'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartate',
    'C': 'Cysteine', 'E': 'Glutamate', 'Q': 'Glutamine', 'G': 'Glycine',
    'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
    'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
    'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine',
    '*': 'Stop Codon'
}

# 1. SIDEBAR CONFIGURATION CONTROLS
with st.sidebar:
    st.header("🧬 Mutation Configuration")
    st.write("Adjust parameters to dynamically calculate the phenotypic impact.")
    st.divider()
    
    mutation_type = st.selectbox(
        "Mutation Type / Mechanism",
        ["Missense", "Nonsense", "Frameshift", "Synonymous"],
        index=0
    )
    
    position = st.slider(
        "Amino Acid Site of Interest",
        min_value=1,
        max_value=635,
        value=351,
        step=1
    )
    
    st.divider()
    
    wt_aa, mut_aa = "N/A", "N/A"
    if mutation_type == "Missense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)     
        mut_aa = st.selectbox("Target Substitute Amino Acid", list(AA_MAP.keys()), index=1) 
    elif mutation_type == "Nonsense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)
        mut_aa = "*"

# 2. SECTOR SPECIFIC TOPOLOGY LOGIC 
# Mapping the 12 TM domains systematically
if position in range(1, 41):
    active_segment = "N-term"
    domain_found = "N-terminus (Intracellular)"
elif position in range(41, 300):
    active_segment = "TM1-6"
    domain_found = "TM1 - TM6 Transport Spans"
elif position in range(300, 420):
    active_segment = "TM7-8"
    domain_found = "TM7 - TM8 (Creatine Binding Core)"
elif position in range(420, 570):
    active_segment = "TM9-12"
    domain_found = "TM9 - TM12 Channel Spans"
else:
    active_segment = "C-term"
    domain_found = "C-terminus (Intracellular)"

# 3. CONSTRUCTING PATHOGENICITY ALGORITHM
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction = "Pathogenic (High Risk)"
    alert_box = st.error
    hgvs = f"p.{(wt_aa if wt_aa != 'N/A' else 'X')}{position}fs" if mutation_type == "Frameshift" else f"p.{wt_aa}{position}*"
    mechanism = f"Variant **{hgvs}** causes structural truncation, leading to absolute loss of functional Creatine Transporter 1 (CT1)."
elif mutation_type == 'Synonymous':
    prediction = "Benign / Low Risk"
    alert_box = st.success
    mechanism = "The codon yields the identical residue. Structural transport kinetics remain unaffected."
else:  # Missense
    hgvs = f"p.{wt_aa}{position}{mut_aa}"
    if active_segment == "TM7-8":
        prediction = "Likely Pathogenic (High Risk)"
        alert_box = st.error
        mechanism = f"The shift **{hgvs}** disrupts spatial kinetics in the core binding cluster, entirely breaking substrate accessibility."
    elif active_segment in ["N-term", "C-term"]:
        prediction = "Likely Benign / Tolerated (Low Risk)"
        alert_box = st.success
        mechanism = f"The swap **{hgvs}** alters a highly variable terminal loop. Structurally tolerated."
    else:
        prediction = "Variant of Uncertain Significance (VUS)"
        alert_box = st.warning
        mechanism = f"The mutation **{hgvs}** falls inside a baseline core structural channel helix. Requires cell essays."

# 4. MAIN INTERFACE OUTPUT GENERATION
st.subheader("📊 Algorithmic Consequence Assessment")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Target Topology Mapping", value=domain_found)
with col2:
    if mutation_type in ["Missense", "Nonsense"]:
        st.metric(label="HGVS Standard Variant Name", value=hgvs)
    else:
        st.metric(label="Variant Structural Profile", value=mutation_type)

alert_box(f"### **Prediction Outcome:** {prediction}")
st.info(f"**Predicted Molecular Mechanism Impact:**\n\n{mechanism}")

# 5. DYNAMIC ANIMATED TOPOLOGY MAP COMPONENT (HTML/CSS CANVAS)
st.subheader("🗺️ Live Molecular Topology Visualization")

# Classes dynamically highlight matching domain blocks using CSS animations
css_highlights = {
    "N-term": "animation: pulse 1.2s infinite alternate; background-color: #ff4b4b; color: white;",
    "TM1-6": "animation: pulse 1.2s infinite alternate; background-color: #ff4b4b; color: white;",
    "TM7-8": "animation: pulse 1.2s infinite alternate; background-color: #ff4b4b; color: white;",
    "TM9-12": "animation: pulse 1.2s infinite alternate; background-color: #ff4b4b; color: white;",
    "C-term": "animation: pulse 1.2s infinite alternate; background-color: #ff4b4b; color: white;",
}
# Default background settings for idle segments
for k in css_highlights.keys():
    if k != active_segment:
        css_highlights[k] = "background-color: #2b2b36; color: #a1a1aa;"

html_canvas = f"""
<div style="font-family: sans-serif; background-color: #111116; padding: 25px; border-radius: 12px; border: 1px solid #3b3b4f; text-align: center;">
    <style>
        @keyframes pulse {{
            0% {{ transform: scale(1.0); box-shadow: 0 0 5px #ff4b4b; }}
            100% {{ transform: scale(1.05); box-shadow: 0 0 20px #ff4b4b; }}
        }}
        .bilayer {{
            border-top: 6px dashed #4b5563; border-bottom: 6px dashed #4b5563;
            background: rgba(75, 85, 99, 0.1); padding: 20px 10px; margin: 20px 0;
            display: flex; justify-content: space-around; align-items: center; position: relative;
        }}
        .membrane-label {{
            position: absolute; left: 10px; top: 38%; color: #6b7280; font-size: 11px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;
        }}
        .node {{
            border-radius: 8px; padding: 12px 8px; font-size: 13px; font-weight: bold; transition: all 0.3s; min-width: 90px;
        }}
        .tail {{
            display: inline-block; padding: 8px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; transition: all 0.3s;
        }}
    </style>
    
    <div style="color: #9ca3af; font-size: 12px; margin-bottom: 10px;">🔴 INDICATES ACTIVE MUTATION RESIDUE LOCATION (SITE: {position})</div>
    
    <!-- Intracellular Top Loop -->
    <div class="tail" style="{css_highlights['N-term']}">N-Terminus<br>(1-40)</div>
    
    <!-- Membrane Segment Row -->
    <div class="bilayer">
        <div class="membrane-label">Lipid Bilayer</div>
        <div class="node" style="{css_highlights['TM1-6']}">🩻 TM1 - TM6<br>Helices<br>(41-299)</div>
        <div style="font-size: 24px; color: #4b5563;">➔</div>
        <div class="node" style="{css_highlights['TM7-8']}">🎯 TM7 - TM8<br>Binding Core<br>(300-419)</div>
        <div style="font-size: 24px; color: #4b5563;">➔</div>
        <div class="node" style="{css_highlights['TM9-12']}">🩻 TM9 - TM12<br>Helices<br>(420-569)</div>
    </div>
    
    <!-- Extracellular Bottom Loop -->
    <div class="tail" style="{css_highlights['C-term']}">C-Terminus<br>(570-635)</div>
</div>
"""

# Render container
html(html_canvas, height=260)


