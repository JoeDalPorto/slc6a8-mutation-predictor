import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")

st.title("🧬 SLC6A8 Structural Mutation Predictor")
st.markdown("Evaluate mutation consequences mapped onto the experimental LeuT-fold membrane topology.")
st.divider()

AA_MAP = {
    'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartate',
    'C': 'Cysteine', 'E': 'Glutamate', 'Q': 'Glutamine', 'G': 'Glycine',
    'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
    'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
    'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine', '*': 'Stop'
}

with st.sidebar:
    st.header("🧬 Variant Editor")
    mutation_type = st.selectbox("Mutation Mechanism", ["Missense", "Nonsense", "Frameshift", "Synonymous"])
    position = st.slider("Amino Acid Residue Position", 1, 635, 351)
    wt_aa, mut_aa = "N/A", "N/A"
    if mutation_type == "Missense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)     
        mut_aa = st.selectbox("Target Substitute Amino Acid", list(AA_MAP.keys()), index=1) 
    elif mutation_type == "Nonsense":
        wt_aa = st.selectbox("Wild-Type Amino Acid", list(AA_MAP.keys()), index=7)
        mut_aa = "*"

# 1. TOPOLOGY LOGIC BOUNDARIES
helix_mapping = {"1": (41, 65), "2": (81, 105), "3": (131, 155), "4": (176, 200), "5": (216, 240), "6": (276, 300), "7": (321, 345), "8": (371, 395), "9": (421, 445), "10": (466, 490), "11": (511, 535), "12": (546, 570)}
active_id, domain_found = "Loops/Termini", "Loops or Terminal Tails"

for h_id, (start, end) in helix_mapping.items():
    if position in range(start, end + 1):
        active_id, domain_found = h_id, f"Transmembrane Helix {h_id}"
if position in range(1, 41): active_id, domain_found = "N", "Intracellular N-Terminus"
if position in range(571, 636): active_id, domain_found = "C", "Intracellular C-Terminus"

# 2. PATHOGENICITY PREDICTION
is_core = active_id in ["1", "3", "6", "7", "8"]
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction, alert, mechanism = "Pathogenic (High Risk)", st.error, "Triggers structural truncation or NMD, leading to total loss of transporter function."
elif mutation_type == 'Synonymous':
    prediction, alert, mechanism = "Benign / Low Risk", st.success, "Identical amino acid sequence preserved. No structural impact expected."
else:
    hgvs = f"p.{wt_aa}{position}{mut_aa}"
    if is_core:
        prediction, alert, mechanism = "Likely Pathogenic (High Risk)", st.error, f"Mutation {hgvs} alters the core transport machinery (TM{active_id}), directly disrupting creatine pocket binding kinetics."
    elif active_id in ["N", "C"]:
        prediction, alert, mechanism = "Likely Benign (Low Risk)", st.success, f"Mutation {hgvs} falls in flexible terminal regions and is usually well tolerated."
    else:
        prediction, alert, mechanism = "Variant of Uncertain Significance (VUS)", st.warning, f"Mutation {hgvs} affects the structural scaffolding. Empirical validation required."

# 3. INTERFACE DISPLAY
col1, col2 = st.columns(2)
col1.metric("Mapped Topology Location", domain_found)
col2.metric("Variant Identity", f"p.{wt_aa}{position}{mut_aa}" if mutation_type=="Missense" else mutation_type)

alert(f"### Prediction Outcome: {prediction}")
st.info(f"**Predicted Molecular Impact:** {mechanism}")

# 4. MATPLOTLIB VECTOR IMAGE GENERATION ( LeuT-Fold Structure Array )
st.subheader("🗺️ Live Structural Bundle Diagram")
fig, ax = plt.subplots(figsize=(7, 2.5), facecolor='#0f172a')
ax.set_facecolor('#0f172a')

# Layout sequence representing the exact image blueprint
helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
core_helices = ["1", "3", "6", "8"]

# Draw Membrane boundary lines
ax.axhline(y=0.4, color='#475569', linestyle='--', linewidth=1.5)
ax.axhline(y=-0.4, color='#475569', linestyle='--', linewidth=1.5)
ax.text(-0.8, 0.5, "OUT (Extracellular)", color='#38bdf8', fontsize=7, fontweight='bold')
ax.text(-0.8, -0.6, "IN (Intracellular)", color='#a855f7', fontsize=7, fontweight='bold')

for idx, h_id in enumerate(helix_order):
    x_pos = idx * 0.7
    # Determine color archetype
    if h_id == active_id: color = '#dc2626' # Red Glow target highlight
    elif h_id in core_helices: color = '#0284c7' # Core Teal
    else: color = '#a21caf' # Scaffold Purple
    
    # Draw cylinder representation
    rect = plt.Rectangle((x_pos-0.2, -0.4), 0.4, 0.8, color=color, alpha=0.9, rwidth=None)
    ax.add_patch(rect)
    ax.text(x_pos, 0, h_id, color='white', ha='center', va='center', fontsize=9, fontweight='bold')

# Draw Creatine molecule asset marker next to core bundle channels
ax.plot(3.15, 0, marker='o', markersize=14, color='#f8fafc', markeredgecolor='#0284c7', markeredgewidth=2)
ax.text(3.15, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7, fontweight='bold')

ax.set_xlim(-1, 8.5)
ax.set_ylim(-0.8, 0.8)
ax.axis('off')
st.pyplot(fig)
