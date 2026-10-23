import streamlit as st

st.set_page_config(
    page_title="SLC6A8 Mutation Predictor",
    page_icon="🧬",
    layout="centered"
)

st.title("🧬 SLC6A8 Structural Mutation Predictor")
st.markdown("Evaluate mutation consequences mapped onto the experimental LeuT-fold membrane topology of the creatine transporter.")
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
    st.header("🧬 Variant Editor")
    mutation_type = st.selectbox(
        "Mutation Mechanism",
        ["Missense", "Nonsense", "Frameshift", "Synonymous"],
        index=0
    )
    
    position = st.slider(
        "Amino Acid Residue Position",
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
    active_id, domain_found = "N", "Intracellular N-Terminus"
elif position in range(41, 66):
    active_id, domain_found = "1", "Transmembrane Helix 1 (Core Binding)"
elif position in range(66, 81):
    active_id, domain_found = "IL1", "Intracellular Loop 1"
elif position in range(81, 106):
    active_id, domain_found = "2", "Transmembrane Helix 2 (Scaffold)"
elif position in range(106, 131):
    active_id, domain_found = "ECL2", "Extracellular Loop 2"
elif position in range(131, 156):
    active_id, domain_found = "3", "Transmembrane Helix 3 (Core Gating)"
elif position in range(156, 176):
    active_id, domain_found = "IL2", "Intracellular Loop 2"
elif position in range(176, 201):
    active_id, domain_found = "4", "Transmembrane Helix 4 (Scaffold)"
elif position in range(201, 216):
    active_id, domain_found = "ECL3", "Extracellular Loop 3"
elif position in range(216, 241):
    active_id, domain_found = "5", "Transmembrane Helix 5 (Scaffold)"
elif position in range(241, 276):
    active_id, domain_found = "IL3", "Intracellular Loop 3"
elif position in range(276, 301):
    active_id, domain_found = "6", "Transmembrane Helix 6 (Core Binding)"
elif position in range(301, 321):
    active_id, domain_found = "ECL4", "Extracellular Loop 4"
elif position in range(321, 346):
    active_id, domain_found = "7", "Transmembrane Helix 7 (Binding Pocket Core)"
elif position in range(346, 371):
    active_id, domain_found = "IL4", "Intracellular Loop 4"
elif position in range(371, 396):
    active_id, domain_found = "8", "Transmembrane Helix 8 (Binding Pocket Core)"
elif position in range(396, 421):
    active_id, domain_found = "ECL5", "Extracellular Loop 5"
elif position in range(421, 446):
    active_id, domain_found = "9", "Transmembrane Helix 9 (Scaffold)"
elif position in range(446, 466):
    active_id, domain_found = "IL5", "Intracellular Loop 5"
elif position in range(466, 491):
    active_id, domain_found = "10", "Transmembrane Helix 10 (Scaffold)"
elif position in range(491, 511):
    active_id, domain_found = "ECL6", "Extracellular Loop 6"
elif position in range(511, 536):
    active_id, domain_found = "11", "Transmembrane Helix 11 (Outer Support)"
elif position in range(536, 546):
    active_id, domain_found = "IL6", "Intracellular Loop 6"
elif position in range(546, 571):
    active_id, domain_found = "12", "Transmembrane Helix 12 (Outer Support)"
else:
    active_id, domain_found = "C", "Intracellular C-Terminus"

# 3. PATHOGENICITY ALGORITHM
is_core = active_id in ["1", "3", "6", "7", "8"]
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction = "Pathogenic (High Risk)"
    alert_box = st.error
    hgvs = f"p.{(wt_aa if wt_aa != 'N/A' else 'X')}{position}fs" if mutation_type == "Frameshift" else f"p.{wt_aa}{position}*"
    mechanism = f"Variant **{hgvs}** causes structural truncation, destroying vital downstream transmembrane helices and inducing complete loss of transporter function."
elif mutation_type == 'Synonymous':
    prediction = "Benign / Low Risk"
    alert_box = st.success
    mechanism = "The nucleotide swap retains the identical amino acid. Transporter fold and binding parameters are unaffected."
else:  # Missense
    hgvs = f"p.{wt_aa}{position}{mut_aa}"
    if is_core:
        prediction = "Likely Pathogenic (High Risk)"
        alert_box = st.error
        mechanism = f"The mutation **{hgvs}** disrupts the specialized LeuT-fold transport core (TM{active_id}). Alterations here directly block structural transitions or destabilize the central creatine (Cr) binding coordination pocket."
    elif active_id in ["N", "C"]:
        prediction = "Likely Benign / Tolerated (Low Risk)"
        alert_box = st.success
        mechanism = f"The residue variation **{hgvs}** is located within a flexible, non-conserved intracellular terminal tail, preserving transport function."
    else:
        prediction = "Variant of Uncertain Significance (VUS)"
        alert_box = st.warning
        mechanism = f"The change **{hgvs}** is located within an outer scaffold structural domain segment. Requires testing to determine if it impacts folding efficiency or stability."

# 4. DATA PRESENTATION PANEL
st.subheader("📊 Pathogenicity Summary")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Target Topology Domain", value=domain_found)
with col2:
    st.metric(label="HGVS Mutation Identity", value=hgvs if mutation_type in ["Missense", "Nonsense"] else mutation_type)

alert_box(f"### **Prediction Outcome:** {prediction}")
st.info(f"**Predicted Molecular Impact:** {mechanism}")

# 5. DYNAMIC LEUT-FOLD ARCHITECTURE SCHEMATIC (TRIPLE-QUOTE FREE IMPLEMENTATION)
st.subheader("🗺️ Live Structural Bundle Diagram")

colors = {"1":"#0284c7","2":"#a21caf","3":"#0284c7","4":"#a21caf","5":"#a21caf","6":"#0284c7","7":"#a21caf","8":"#0284c7","9":"#a21caf","10":"#a21caf","11":"#a21caf","12":"#a21caf"}
styles = {k: f"background-color: {colors[k]}; color: white;" for k in colors.keys()}
loop_styles = {"ECL2":"", "ECL3":"", "ECL4":"", "N":"", "C":""}

highlight_css = "background-color: #dc2626 !important; color: white !important; box-shadow: 0 0 25px 8px #dc2626; transform: scale(1.1); z-index: 10; border: 2px solid #fff;"
if active_id in styles:
    styles[active_id] = highlight_css
elif active_id in loop_styles:
    loop_styles[active_id] = "background-color: #dc2626 !important; color: white !important; box-shadow: 0 0 15px 5px #dc2626; border: 1px solid white;"

display_id = active_id + "-Terminus" if active_id in ['N','C'] else "Helix " + active_id

# Assembling HTML segment by segment via list concatenation to guarantee no syntax splitting
html_lines = [
    '<div style="font-family: Arial, sans-serif; background-color: #0f172a; padding: 25px; border-radius: 12px; min-width: 650px; overflow-x: auto; box-sizing: border-box; color: white; position: relative;">',
    f'    <div style="font-size: 11px; color: #94a3b8; font-weight: bold; text-align: center; margin-bottom: 25px; letter-spacing: 1px;">🔴 HIGHLIGHTING TARGET SITE: RESIDUE {position} ({display_id})</div>',
    '    <div style="height: 100px; border-top: 3px solid #cbd5e1; border-bottom: 3px solid #cbd5e1; background: rgba(203, 213, 225, 0.05); display: flex; justify-content: space-around; align-items: center; position: relative; padding: 0 30px; margin: 40px 0;">',
    '        <div style="position: absolute; top: -25px; left: 10px; font-size: 11px; font-weight: bold; color: #38bdf8; text-transform: uppercase;">Out (Extracellular)</div>',
    '        <div style="position: absolute; bottom: -25px; left: 10px; font-size: 11px; font-weight: bold; color: #a855f7; text-transform: uppercase;">In (Intracellular)</div>',
    f'        <div style="width: 24px; height: 130px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; transition: all 0.3s; {styles["5"]}">5</div>',
    f'        <div style="width: 24px; height: 130px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; transition: all 0.3s; {styles["4"]}">4</div>',
    f'        <div style="width: 24px; height: 130px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; transition: all 0.3s; {styles["2"]}">2</div>',
    f'        <div style="width: 24px; height: 130px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; transform: rotate(12deg); transition: all 0.3s; {styles["3"]}">3</div>',
    '        <div style="display: flex; flex-direction: column; gap: 24px; position: relative; align-items: center;">',
    f'            <div style="width: 24px; height: 50px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; transition: all 0.3s; {styles["1"]}">1</div>',
    f'            <div style="width: 24px; height: 50px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; transition: all 0.3s; {styles["1"]}">1</div>',
