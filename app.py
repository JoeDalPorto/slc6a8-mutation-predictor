import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")

st.title("🧬 SLC6A8 Structural Mutation Predictor")
st.markdown("Evaluate mutation consequences mapped onto the experimental LeuT-fold membrane topology with loop connectivity.")
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

# 4. ADVANCED MATPLOTLIB DRAWING WITH LOOP CONNECTIVITY
st.subheader("🗺️ Live Structural Bundle Diagram")
fig, ax = plt.subplots(figsize=(7.5, 3.5), facecolor='#0f172a')
ax.set_facecolor('#0f172a')

# Structural layout sequence
helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
core_helices = ["1", "3", "6", "8"]

# Map helix names to their direct X coordinates on the graph canvas
x_coords = {h_id: idx * 0.65 for idx, h_id in enumerate(helix_order)}

# Draw Membrane boundary lines
ax.axhline(y=0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.axhline(y=-0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.text(-0.8, 0.65, "OUT (Extracellular Space)", color='#38bdf8', fontsize=7, fontweight='bold')
ax.text(-0.8, -0.75, "IN (Intracellular Space)", color='#a855f7', fontsize=7, fontweight='bold')

# Sequential connectivity routing rules for the loops (Helix N -> Helix M)
# Format: (From_Helix, To_Helix, Space['out' or 'in'], Curvature_Height)
loop_routes = [
    ("1", "2", "out", 0.2), ("2", "3", "in", -0.2), ("3", "4", "out", 0.3),
    ("4", "5", "in", -0.2), ("5", "6", "out", 0.4), ("6", "7", "in", -0.3),
    ("7", "8", "out", 0.2), ("8", "9", "in", -0.3), ("9", "10", "out", 0.2),
    ("10", "11", "in", -0.2), ("11", "12", "out", 0.2)
]

# Draw the protein loop wires
for h_from, h_to, space, curve in loop_routes:
    x1, x2 = x_coords[h_from], x_coords[h_to]
    y_base = 0.5 if space == "out" else -0.5
    
    # Calculate control path points for bezier curves
    x_mid = (x1 + x2) / 2
    y_mid = y_base + curve
    
    # Draw path line
    path_data = [
        (patches.Path.MOVETO, (x1, y_base)),
        (patches.Path.CURVE3, (x_mid, y_mid)),
        (patches.Path.CURVE3, (x2, y_base))
    ]
    codes, verts = zip(*path_data)
    path = patches.Path(verts, codes)
    patch = patches.PathPatch(path, edgecolor='#64748b', facecolor='none', linewidth=1.5, alpha=0.7, zorder=1)
    ax.add_patch(patch)

# Draw N-Terminus and C-Terminus tails dangling into intracellular space
ax.plot([x_coords["1"], x_coords["1"] - 0.3], [-0.5, -0.8], color='#dc2626' if active_id == "N" else '#64748b', linewidth=2, zorder=1)
ax.text(x_coords["1"] - 0.3, -0.85, "N-term", color='#dc2626' if active_id == "N" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')

ax.plot([x_coords["12"], x_coords["12"] + 0.3], [-0.5, -0.8], color='#dc2626' if active_id == "C" else '#64748b', linewidth=2, zorder=1)
ax.text(x_coords["12"] + 0.3, -0.85, "C-term", color='#dc2626' if active_id == "C" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')

# Draw the Cylinder blocks
for h_id, x_pos in x_coords.items():
    if h_id == active_id:
        color = '#dc2626'
        z_ord = 4
        # Add a subtle bounding highlight box for the active mutation target
        box = patches.Rectangle((x_pos-0.22, -0.52), 0.44, 1.04, color='white', fill=False, linewidth=1, zorder=3)
        ax.add_patch(box)
    elif h_id in core_helices:
        color = '#0284c7'
        z_ord = 3
    else:
        color = '#a21caf'
        z_ord = 2
        
    rect = patches.Rectangle((x_pos-0.18, -0.5), 0.36, 1.0, color=color, alpha=0.95, zorder=z_ord)
    ax.add_patch(rect)
    ax.text(x_pos, 0, h_id, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=z_ord+1)

# Draw Creatine molecule core asset marker
ax.plot(2.92, 0, marker='o', markersize=14, color='#f8fafc', markeredgecolor='#0284c7', markeredgewidth=2, zorder=5)
ax.text(2.92, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7, fontweight='bold', zorder=6)

ax.set_xlim(-1, 7.8)
ax.set_ylim(-1.0, 1.0)
ax.axis('off')
st.pyplot(fig)
