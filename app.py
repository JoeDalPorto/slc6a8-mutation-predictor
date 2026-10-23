import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")

st.title("🧬 SLC6A8 Structural Mutation Predictor")
st.markdown("Evaluate mutation consequences mapped onto the experimental LeuT-fold membrane topology with targeted loop highlighting.")
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

# 1. PRECISE RESIDUE MAPPING (All 12 Helices + All Connecting Loops)
topology_db = [
    {"id": "N", "name": "Intracellular N-Terminus", "start": 1, "end": 40, "type": "terminus"},
    {"id": "1", "name": "Transmembrane Helix 1 (Core)", "start": 41, "end": 65, "type": "helix"},
    {"id": "ECL1", "name": "Extracellular Loop 1", "start": 66, "end": 80, "type": "loop", "side": "out", "from": "1", "to": "2", "curve": 0.2},
    {"id": "2", "name": "Transmembrane Helix 2 (Scaffold)", "start": 81, "end": 105, "type": "helix"},
    {"id": "IL1", "name": "Intracellular Loop 1", "start": 106, "end": 130, "type": "loop", "side": "in", "from": "2", "to": "3", "curve": -0.2},
    {"id": "3", "name": "Transmembrane Helix 3 (Core)", "start": 131, "end": 155, "type": "helix"},
    {"id": "ECL2", "name": "Extracellular Loop 2", "start": 156, "end": 175, "type": "loop", "side": "out", "from": "3", "to": "4", "curve": 0.3},
    {"id": "4", "name": "Transmembrane Helix 4 (Scaffold)", "start": 176, "end": 200, "type": "helix"},
    {"id": "IL2", "name": "Intracellular Loop 2", "start": 201, "end": 215, "type": "loop", "side": "in", "from": "4", "to": "5", "curve": -0.2},
    {"id": "5", "name": "Transmembrane Helix 5 (Scaffold)", "start": 216, "end": 240, "type": "helix"},
    {"id": "ECL3", "name": "Extracellular Loop 3", "start": 241, "end": 275, "type": "loop", "side": "out", "from": "5", "to": "6", "curve": 0.4},
    {"id": "6", "name": "Transmembrane Helix 6 (Core)", "start": 276, "end": 300, "type": "helix"},
    {"id": "IL3", "name": "Intracellular Loop 3", "start": 301, "end": 320, "type": "loop", "side": "in", "from": "6", "to": "7", "curve": -0.3},
    {"id": "7", "name": "Transmembrane Helix 7 (Core)", "start": 321, "end": 345, "type": "helix"},
    {"id": "ECL4", "name": "Extracellular Loop 4", "start": 346, "end": 370, "type": "loop", "side": "out", "from": "7", "to": "8", "curve": 0.2},
    {"id": "8", "name": "Transmembrane Helix 8 (Core)", "start": 371, "end": 396, "type": "helix"},
    {"id": "IL4", "name": "Intracellular Loop 4", "start": 397, "end": 420, "type": "loop", "side": "in", "from": "8", "to": "9", "curve": -0.3},
    {"id": "9", "name": "Transmembrane Helix 9 (Scaffold)", "start": 421, "end": 445, "type": "helix"},
    {"id": "ECL5", "name": "Extracellular Loop 5", "start": 446, "end": 465, "type": "loop", "side": "out", "from": "9", "to": "10", "curve": 0.2},
    {"id": "10", "name": "Transmembrane Helix 10 (Scaffold)", "start": 466, "end": 490, "type": "helix"},
    {"id": "IL5", "name": "Intracellular Loop 5", "start": 491, "end": 510, "type": "loop", "side": "in", "from": "10", "to": "11", "curve": -0.2},
    {"id": "11", "name": "Transmembrane Helix 11 (Scaffold)", "start": 511, "end": 535, "type": "helix"},
    {"id": "ECL6", "name": "Extracellular Loop 6", "start": 536, "end": 545, "type": "loop", "side": "out", "from": "11", "to": "12", "curve": 0.2},
    {"id": "12", "name": "Transmembrane Helix 12 (Scaffold)", "start": 546, "end": 570, "type": "helix"},
    {"id": "C", "name": "Intracellular C-Terminus", "start": 571, "end": 635, "type": "terminus"}
]

active_item = None
for item in topology_db:
    if position in range(item["start"], item["end"] + 1):
        active_item = item
        break

domain_found = active_item["name"] if active_item else "Unknown Domain"
active_id = active_item["id"] if active_item else ""

# 2. ALGOCONSEQUENCE ASSIGNMENTS
is_core = active_id in ["1", "3", "6", "7", "8"] or (active_item and active_item["type"] == "loop" and active_item["from"] in ["1","3","6","7","8"] and active_item["to"] in ["1","3","6","7","8"])

if mutation_type in ['Nonsense', 'Frameshift']:
    prediction, alert, mechanism = "Pathogenic (High Risk)", st.error, "Induces structural translation failure or mRNA decay, leading to functional loss."
elif mutation_type == 'Synonymous':
    prediction, alert, mechanism = "Benign / Low Risk", st.success, "Identical amino acid sequence sustained. Structural operations continue normally."
else:
    hgvs = f"p.{wt_aa}{position}{mut_aa}"
    if is_core:
        prediction, alert, mechanism = "Likely Pathogenic (High Risk)", st.error, f"Mutation {hgvs} hits a functional transport core segment ({active_id}), directly stalling substrate binding coordinates."
    elif active_item and active_item["type"] == "terminus":
        prediction, alert, mechanism = "Likely Benign (Low Risk)", st.success, f"Mutation {hgvs} rests inside a flexible terminal tail, yielding normal transport mechanics."
    else:
        prediction, alert, mechanism = "Variant of Uncertain Significance (VUS)", st.warning, f"Mutation {hgvs} changes a baseline auxiliary support domain loop/span. Further evaluation needed."

# 3. INTERFACE VISUALS
col1, col2 = st.columns(2)
col1.metric("Target Variant Domain", domain_found)
col2.metric("Nomenclature Tag", f"p.{wt_aa}{position}{mut_aa}" if mutation_type=="Missense" else mutation_type)

alert(f"### Prediction Outcome: {prediction}")
st.info(f"**Predicted Molecular Impact:** {mechanism}")

# 4. STRUCTURE IMAGE ASSEMBLY WITH GLOW OUTLINES
st.subheader("🗺️ Experimental LeuT-Fold Structural Blueprint")
fig, ax = plt.subplots(figsize=(7.5, 3.5), facecolor='#0f172a')
ax.set_facecolor('#0f172a')

helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
core_helices = ["1", "3", "6", "8"]
x_coords = {h_id: idx * 0.65 for idx, h_id in enumerate(helix_order)}

# Boundaries
ax.axhline(y=0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.axhline(y=-0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.text(-0.8, 0.65, "OUT (Extracellular)", color='#38bdf8', fontsize=7, fontweight='bold')
ax.text(-0.8, -0.75, "IN (Intracellular)", color='#a855f7', fontsize=7, fontweight='bold')

# ─── PART A: LOOP RENDERING WITH YELLOW HALO CHECKS ───
for item in topology_db:
    if item["type"] != "loop": continue
    
    x1, x2 = x_coords[item["from"]], x_coords[item["to"]]
    y_base = 0.5 if item["side"] == "out" else -0.5
    x_mid, y_mid = (x1 + x2) / 2, y_base + item["curve"]
    
    path_data = [(patches.Path.MOVETO, (x1, y_base)), (patches.Path.CURVE3, (x_mid, y_mid)), (patches.Path.CURVE3, (x2, y_base))]
    codes, verts = zip(*path_data)
    path = patches.Path(verts, codes)
    
    # IF LOOP IS ACTIVE: Draw a thick yellow halo outline right behind the wire path
    if active_id == item["id"]:
        halo = patches.PathPatch(path, edgecolor='#eab308', facecolor='none', linewidth=5.5, alpha=0.9, zorder=1)
        ax.add_patch(halo)
        
    wire = patches.PathPatch(path, edgecolor='#64748b', facecolor='none', linewidth=1.5, zorder=2)
    ax.add_patch(wire)

# ─── PART B: TERMINAL TAIL RENDERING WITH YELLOW HALOS ───
n_halo_z, c_halo_z = 1, 1
if active_id == "N":
    ax.plot([x_coords["1"], x_coords["1"] - 0.3], [-0.5, -0.8], color='#eab308', linewidth=6.0, zorder=1)
if active_id == "C":
    ax.plot([x_coords["12"], x_coords["12"] + 0.3], [-0.5, -0.8], color='#eab308', linewidth=6.0, zorder=1)

ax.plot([x_coords["1"], x_coords["1"] - 0.3], [-0.5, -0.8], color='#64748b', linewidth=2, zorder=2)
ax.text(x_coords["1"] - 0.3, -0.85, "N-term", color='#eab308' if active_id == "N" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')

ax.plot([x_coords["12"], x_coords["12"] + 0.3], [-0.5, -0.8], color='#64748b', linewidth=2, zorder=2)
ax.text(x_coords["12"] + 0.3, -0.85, "C-term", color='#eab308' if active_id == "C" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')

# ─── PART C: HELIX CYLINDER RENDERING WITH HALO BACKGROUNDS ───
for h_id, x_pos in x_coords.items():
    # Base natural background colors (Teal for Core, Purple for Scaffold)
    base_color = '#0284c7' if h_id in core_helices else '#a21caf'
    
    # IF HELIX IS ACTIVE: Generate a yellow backdrop halo shield outline
    if h_id == active_id:
        halo_rect = patches.Rectangle((x_pos-0.23, -0.55), 0.46, 1.1, color='#eab308', alpha=0.9, zorder=2)
        ax.add_patch(halo_rect)
        
    rect = patches.Rectangle((x_pos-0.18, -0.5), 0.36, 1.0, color=base_color, alpha=0.95, zorder=3)
    ax.add_patch(rect)
    ax.text(x_pos, 0, h_id, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)

# Cargo Marker
ax.plot(2.92, 0, marker='o', markersize=14, color='#f8fafc', markeredgecolor='#0284c7', markeredgewidth=2, zorder=5)
ax.text(2.92, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7, fontweight='bold', zorder=6)

ax.set_xlim(-1, 7.8)
ax.set_ylim(-1.0, 1.0)
ax.axis('off')
st.pyplot(fig)
