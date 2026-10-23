import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")
st.title("🧬 SLC6A8 Mutation Predictor")
st.markdown("Structural Evaluation of SLC6A8 mutations with ClinVar cross-referencing.")
st.divider()

# Extended mapping to show readable full labels in dropdown selectors
AA_LABELS = {
    'A': 'A (Alanine)', 'R': 'R (Arginine)', 'N': 'N (Asparagine)', 'D': 'D (Aspartate)',
    'C': 'C (Cysteine)', 'E': 'E (Glutamate)', 'Q': 'Q (Glutamine)', 'G': 'G (Glycine)',
    'H': 'H (Histidine)', 'I': 'I (Isoleucine)', 'L': 'L (Leucine)', 'K': 'K (Lysine)',
    'M': 'M (Methionine)', 'F': 'F (Phenylalanine)', 'P': 'P (Proline)', 'S': 'S (Serine)',
    'T': 'T (Threonine)', 'W': 'W (Tryptophan)', 'Y': 'Y (Tyrosine)', 'V': 'V (Valine)',
    '*': '* (Stop Codon)'
}

CLINVAR_DB = {
    "p.G351R": ("2290132", "VUS", "Reviewed by ClinGen expert panel. High in-silico constraint but insufficient emperical data."),
    "p.P382L": ("533700", "Pathogenic", "Observed in multiple patients exhibiting classic X-linked Creatine Transporter Deficiency (CTD)."),
    "p.P390L": ("1361089", "Likely Pathogenic", "Disrupts the conserved loop transition flanking the functional transporter core."),
    "p.A495T": ("942968", "Likely Benign", "Frequently observed in standard healthy population cohorts; retains transport activity."),
    "p.R514*": ("11696", "Pathogenic", "Classic nonsense mutation resulting in severe protein truncation.")
}

with st.sidebar:
    st.header("🧬 Variant Editor")
    mut_type = st.selectbox("Mechanism", ["Missense", "Nonsense", "Frameshift", "Synonymous"])
    
    # Dual-input layout: User can type the number directly OR slide across the bar
    pos_input = st.number_input("Residue Position Box", min_value=1, max_value=635, value=351, step=1)
    pos = st.slider("Residue Position Slider", 1, 635, value=int(pos_input))
    
    wt, mut = "N/A", "N/A"
    if mut_type == "Missense":
        wt_key = st.selectbox("Wild-Type Amino Acid", list(AA_LABELS.keys()), index=7, format_func=lambda x: AA_LABELS[x])
        mut_key = st.selectbox("Substitute Amino Acid", list(AA_LABELS.keys()), index=1, format_func=lambda x: AA_LABELS[x])
        wt, mut = wt_key, mut_key
    elif mut_type == "Nonsense":
        wt_key = st.selectbox("Wild-Type Amino Acid", list(AA_LABELS.keys()), index=7, format_func=lambda x: AA_LABELS[x])
        wt, mut = wt_key, "*"

# 1. TOPOLOGY ARCHITECTURE DATA STRUCTURE
raw_topology = [
    ("N", "Intracellular N-Terminus", 1, 40, "terminus", 0),
    ("1", "Transmembrane Helix 1 (Core)", 41, 65, "helix", 0),
    ("ECL1", "Extracellular Loop 1", 66, 80, "loop", ("out", 0.2, "1", "2")),
    ("2", "Transmembrane Helix 2 (Scaffold)", 81, 105, "helix", 0),
    ("IL1", "Intracellular Loop 1", 106, 130, "loop", ("in", -0.2, "2", "3")),
    ("3", "Transmembrane Helix 3 (Core)", 131, 155, "helix", 0),
    ("ECL2", "Extracellular Loop 2", 156, 175, "loop", ("out", 0.3, "3", "4")),
    ("4", "Transmembrane Helix 4 (Scaffold)", 176, 200, "helix", 0),
    ("IL2", "Intracellular Loop 2", 201, 215, "loop", ("in", -0.2, "4", "5")),
    ("5", "Transmembrane Helix 5 (Scaffold)", 216, 240, "helix", 0),
    ("ECL3", "Extracellular Loop 3", 241, 275, "loop", ("out", 0.4, "5", "6")),
    ("6", "Transmembrane Helix 6 (Core)", 276, 300, "helix", 0),
    ("IL3", "Intracellular Loop 3", 301, 320, "loop", ("in", -0.3, "6", "7")),
    ("7", "Transmembrane Helix 7 (Core)", 321, 345, "helix", 0),
    ("ECL4", "Extracellular Loop 4", 346, 370, "loop", ("out", 0.2, "7", "8")),
    ("8", "Transmembrane Helix 8 (Core)", 371, 396, "helix", 0),
    ("IL4", "Intracellular Loop 4", 397, 420, "loop", ("in", -0.3, "8", "9")),
    ("9", "Transmembrane Helix 9 (Scaffold)", 421, 445, "helix", 0),
    ("ECL5", "Extracellular Loop 5", 446, 465, "loop", ("out", 0.2, "9", "10")),
    ("10", "Transmembrane Helix 10 (Scaffold)", 466, 490, "helix", 0),
    ("IL5", "Intracellular Loop 5", 491, 510, "loop", ("in", -0.2, "10", "11")),
    ("11", "Transmembrane Helix 11 (Scaffold)", 511, 535, "helix", 0),
    ("ECL6", "Extracellular Loop 6", 536, 545, "loop", ("out", 0.2, "11", "12")),
    ("12", "Transmembrane Helix 12 (Scaffold)", 546, 570, "helix", 0),
    ("C", "Intracellular C-Terminus", 571, 635, "terminus", 0)
]

active = next((item for item in raw_topology if pos in range(item[2], item[3] + 1)), None)
dom_name, active_id = (active[1], active[0]) if active else ("Unknown", "")

# 2. EVALUATE CONSEQUENCE PREDICTION
hgvs = f"p.{wt}{pos}{mut}" if mut_type == "Missense" else (f"p.{wt}{pos}*" if mut_type == "Nonsense" else (f"p.X{pos}fs" if mut_type == "Frameshift" else "Synonymous"))
is_core = active_id in ["1", "3", "6", "7", "8"] or (active and active[4] == "loop" and active[5][2] in ["1","3","6","7","8"])

if mut_type in ['Nonsense', 'Frameshift']:
    pred, alert, mech = "Pathogenic (High Risk)", st.error, "Triggers structural protein truncation or NMD pathways; total loss of transporter function."
elif mut_type == 'Synonymous':
    pred, alert, mech = "Benign / Low Risk", st.success, "Silent nucleotide mutation leaves the original amino acid string completely normal."
else:
    if is_core: pred, alert, mech = "Likely Pathogenic (High Risk)", st.error, f"Alters core machinery (TM{active_id}), directly stalling substrate binding coordinates."
    elif active and active[4] == "terminus": pred, alert, mech = "Likely Benign (Low Risk)", st.success, "Rests inside a flexible terminal tail outside active structural folds."
    else: pred, alert, mech = "Variant of Uncertain Significance (VUS)", st.warning, "Alters an outer structural loop or non-core span. functional impact unknown."

# 3. INTERFACE DISPLAY PANELS
col1, col2 = st.columns(2)
col1.metric("Mapped Domain", dom_name)
col2.metric("Variant Identity", hgvs)

c_match = CLINVAR_DB.get(hgvs)
if c_match:
    st.subheader("📚 ClinVar Database Cross-Reference")
    st.markdown(f"**Clinical Status:** `{c_match[1]}` (ID: [{c_match[0]}](https://nih.gov{c_match[0]}))")
    st.caption(f"**Curated Evidence:** {c_match[2]}")
    st.divider()

alert(f"### Predictor Model Output: {pred}")
st.info(f"**Predicted Impact:** {mech}")

# 4. MAP HELIX POSITIONS AND DRAW VECTOR BLUEPRINT WITH HALO OUTLINES
st.subheader("Topological Blueprint of Mutation Location")
fig, ax = plt.subplots(figsize=(7.5, 3.3), facecolor='#0f172a')
ax.set_facecolor('#0f172a')

helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
x_coords = {h: i * 0.65 for i, h in enumerate(helix_order)}

ax.axhline(0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.axhline(-0.5, color='#475569', linestyle='--', linewidth=1.2)
ax.text(-0.8, 0.65, "OUT (Extracellular)", color='#38bdf8', fontsize=7, fontweight='bold')
ax.text(-0.8, -0.75, "IN (Intracellular)", color='#a855f7', fontsize=7, fontweight='bold')

# A. Draw Loop Connections
for item in raw_topology:
    if item[4] != "loop": continue
    x1, x2 = x_coords[item[5][2]], x_coords[item[5][3]]
    yb = 0.5 if item[5][0] == "out" else -0.5
    path = patches.Path([(x1, yb), ((x1+x2)/2, yb+item[5][1]), (x2, yb)], [patches.Path.MOVETO, patches.Path.CURVE3, patches.Path.CURVE3])
    
    if active_id == item[0]:
        ax.add_patch(patches.PathPatch(path, edgecolor='#eab308', facecolor='none', linewidth=5.5, alpha=0.9, zorder=1))
    ax.add_patch(patches.PathPatch(path, edgecolor='#64748b', facecolor='none', linewidth=1.5, zorder=2))

# B. Draw Terminal Lines
if active_id == "N": ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#eab308', linewidth=6, zorder=1)
if active_id == "C": ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#eab308', linewidth=6, zorder=1)
ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#64748b', linewidth=2, zorder=2)
ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#64748b', linewidth=2, zorder=2)
ax.text(x_coords["1"]-0.3, -0.85, "N-term", color='#eab308' if active_id=="N" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')
ax.text(x_coords["12"]+0.3, -0.85, "C-term", color='#eab308' if active_id=="C" else '#94a3b8', fontsize=7, ha='center', fontweight='bold')

# C. Draw Cylinder Blocks
for h, x in x_coords.items():
    if h == active_id:
        ax.add_patch(patches.Rectangle((x-0.23, -0.55), 0.46, 1.1, color='#eab308', zorder=2))
    rect = patches.Rectangle((x-0.18, -0.5), 0.36, 1.0, color='#0284c7' if h in ["1","3","6","8"] else '#a21caf', alpha=0.95, zorder=3)
    ax.add_patch(rect)
    ax.text(x, 0, h, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=4)

# Cargo Pellet
ax.plot(2.92, 0, marker='o', markersize=14, color='#f8fafc', markeredgecolor='#0284c7', markeredgewidth=2, zorder=5)
ax.text(2.92, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7, fontweight='bold', zorder=6)

ax.set_xlim(-1, 7.8); ax.set_ylim(-1.0, 1.0); ax.axis('off')
st.pyplot(fig)
