import streamlit as st

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

# 1. SIDEBAR CONTROLS
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

# 3. PATHOGENICITY ALGORITHM
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

# 5. HIGH-FIDELITY 12-PASS TRANS-MEMBRANE CELLULAR GRAPHIC
st.subheader("🗺️ Live Molecular Topology Visualization")

# Setup color styles for each domain segment
bg_colors = {"N-term": "#3f3f46", "TM1-6": "#2563eb", "TM7-8": "#ea580c", "TM9-12": "#16a34a", "C-term": "#3f3f46"}
glows = {"N-term": "", "TM1-6": "", "TM7-8": "", "TM9-12": "", "C-term": ""}

# Highlight active element
bg_colors[active_segment] = "#dc2626"
glows[active_segment] = "box-shadow: 0 0 25px 8px #dc2626; transform: scale(1.08); border: 2px solid white; z-index: 10;"

# Structure HTML Canvas
html_membrane = f"""
<div style="font-family: Arial, sans-serif; background-color: #0f172a; padding: 20px; border-radius: 12px; color: white; min-width: 600px; overflow-x: auto; box-sizing: border-box;">
    
    <!-- Compartment: Extracellular Space -->
    <div style="height: 60px; background: rgba(56, 189, 248, 0.05); border-radius: 8px; position: relative; display: flex; align-items: center; padding-left: 15px;">
        <span style="color: #38bdf8; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase;">Extracellular Space (Outside Cell)</span>
    </div>
    
    <!-- Compartment: Lipid Bilayer Membrane -->
    <div style="margin: 15px 0; height: 120px; background: linear-gradient(180deg, rgba(244,63,94,0.1) 0%, rgba(244,63,94,0.02) 50%, rgba(244,63,94,0.1) 100%); border-top: 3px solid #f43f5e; border-bottom: 3px solid #f43f5e; position: relative; display: flex; justify-content: center; align-items: center; gap: 4px; padding: 0 50px;">
        
        <div style="position: absolute; left: 15px; top: 43%; color: #f43f5e; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; transform: rotate(-90deg); transform-origin: left center; width: 100px;">Cell Membrane</div>
        
        <!-- Helix Group 1-6 -->
        <div style="display: flex; gap: 4px; transition: all 0.3s; {glows['TM1-6']}">
            {"".join(f'<div style="width: 14px; height: 110px; background: {bg_colors["TM1-6"]}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: bold; color: white;">{i}</div>' for i in range(1, 7))}
            <div style="position: absolute; top: -12px; width: 104px; text-align: center; font-size: 10px; color: #60a5fa; font-weight: bold; background: #0f172a; padding: 1px 4px; border-radius: 4px; left: 65px;">TM 1 - 6 Spans</div>
        </div>

        <!-- Binding Pocket Helix Group 7-8 -->
        <div style="display: flex; gap: 5px; margin: 0 15px; transition: all 0.3s; position: relative; {glows['TM7-8']}">
            <div style="width: 16px; height: 110px; background: {bg_colors['TM7-8']}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; color: white;">7</div>
            <div style="width: 16px; height: 110px; background: {bg_colors['TM7-8']}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; color: white;">8</div>
            <div style="position: absolute; top: -12px; width: 60px; text-align: center; font-size: 9px; color: #fb923c; font-weight: bold; background: #0f172a; padding: 1px 4px; border-radius: 4px; left: -12px; border: 1px solid #ea580c;">CORE RECEPTOR</div>
        </div>

        <!-- Helix Group 9-12 -->
        <div style="display: flex; gap: 4px; transition: all 0.3s; {glows['TM9-12']}">
            {"".join(f'<div style="width: 14px; height: 110px; background: {bg_colors["TM9-12"]}; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 8px; font-weight: bold; color: white;">{i}</div>' for i in range(9, 13))}
            <div style="position: absolute; top: -12px; width: 70px; text-align: center; font-size: 10px; color: #4ade80; font-weight: bold; background: #0f172a; padding: 1px 4px; border-radius: 4px; right: 65px;">TM 9 - 12 Spans</div>
        </div>
    </div>
    
    <!-- Compartment: Intracellular Space -->
    <div style="height: 75px; background: rgba(168, 85, 247, 0.05); border-radius: 8px; position: relative; display: flex; align-items: flex-start; padding-left: 15px; padding-top: 10px; gap: 80px;">
        <span style="color: #a855f7; font-size: 11px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-right: -40px;">Intracellular Space (Inside Cell)</span>
        
        <!-- N-Terminus Tail Tail -->
        <div style="display: flex; flex-direction: column; align-items: center; margin-left: 20px; transition: all 0.3s; {glows['N-term']}">
            <div style="width: 5px; height: 20px; background: #64748b;"></div>
            <div style="background: {bg_colors['N-term']}; padding: 4px 10px; border-radius: 12px; font-size: 10px; font-weight: bold; color: #e2e8f0; white-space: nowrap;">N-Terminus (1-40)</div>
        </div>
        
        <!-- C-Terminus Tail -->
        <div style="display: flex; flex-direction: column; align-items: center; margin-left: auto; margin-right: 60px; transition: all 0.3s; {glows['C-term']}">
            <div style="width: 5px; height: 20px; background: #64748b;"></div>
            <div style="background: {bg_colors['C-term']}; padding: 4px 10px; border-radius: 12px; font-size: 10px; font-weight: bold; color: #e2e8f0; white-space: nowrap;">C-Terminus (570-635)</div>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 12px; font-size: 11px; color: #94a3b8; font-weight: bold;">
        CURRENT VARIANT TARGET RESIDUE: <span style="color: #dc2626; font-size: 13px;">Residue {position} ({active_segment})</span>
    </div>
</div>
"""

# Render full diagram box cleanly using core components
st.components.v1.html(html_membrane, height=340)
