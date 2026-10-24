import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Import backend cleanly from our custom file
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")

# PREMIUM CSS DESIGN - Enforcing clean white sidebar text
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* Make all sidebar text labels and captions bright white */
    section[data-testid='stSidebar'] { 
        background-color: #111827 !important; 
        border-right: 1px solid #1f2937; 
    }
    section[data-testid='stSidebar'] .stWidgetLabel p, 
    section[data-testid='stSidebar'] p,
    section[data-testid='stSidebar'] h2,
    section[data-testid='stSidebar'] label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    div[data-testid='stMetricValue'] { font-family: monospace !important; font-weight: 700 !important; color: #38bdf8 !important; font-size: 22px !important; }
    div[data-testid='metric-container'] { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 12px; padding: 15px !important; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🧬 SLC6A8 Computational Predictor</h1><p style='text-align: center; color: #94a3b8; font-size: 14px;'>Advanced LeuT-Fold Molecular Mutation Mapping Engine</p>", unsafe_allow_html=True)
st.divider()

# ─── STATE MANAGEMENT SINGLE SLIDER SOURCE WITH STEP TUNING ────────────────
if "pos" not in st.session_state: 
    st.session_state.pos = 351

# Handler to catch direct slider movements safely
def handle_slider_change():
    st.session_state.pos = st.session_state.pos_slider

with st.sidebar:
    st.markdown("<h2 style='font-size: 18px; margin-bottom: 0;'>🛠️ Variant Editor</h2>", unsafe_allow_html=True)
    st.write("")
    
    mut_type = st.selectbox("Mechanism Type", ["Missense", "Nonsense", "Frameshift", "Synonymous"])
    
    # 1. Standard Slider tied directly to state
    st.slider("Residue Position", 1, 635, key="pos_slider", on_change=handle_slider_change, value=st.session_state.pos)
    
    # 2. Stepper Fine-Tuning Layout Buttons modifying state directly
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("⬅️ Step -1", use_container_width=True):
            if st.session_state.pos > 1:
                st.session_state.pos -= 1
                st.rerun()
    with btn_col2:
        if st.button("Step +1 ➡️", use_container_width=True):
            if st.session_state.pos < 635:
                st.session_state.pos += 1
                st.rerun()
                
    current_pos = st.session_state.pos
    wt_letter = REF_SEQ[current_pos - 1] if current_pos <= len(REF_SEQ) else "G"
    
    # Display wild-type using full nomenclature
    st.markdown(f"**Wild-Type Residue:**  \n`{AA_MAP.get(wt_letter, 'Unknown')}`")
    st.write("")
    
    # Substitute dropdown matching exact same nomenclature style as wild-type box
    if mut_type == "Nonsense":
        mut = "*"
        st.markdown(f"**Substitute Residue:**  \n`{AA_MAP.get('*')}`")
    elif mut_type == "Missense":
        mut = st.selectbox("Substitute Amino Acid", list(AA_MAP.keys()), index=10, format_func=lambda x: AA_MAP[x])
    else:
        mut = "N/A"
        st.markdown("**Substitute Residue:**  \n`Not Applicable`")

# ─── MAP STRUCTURAL LOCATIONS ───────────────────────────────────────────────
active_id, dom_name = ("N", "Intracellular N-Terminus") if current_pos <= 40 else (("C", "Intracellular C-Terminus") if current_pos >= 571 else ("Loops", "Interhelical Structural Loop"))

for h_id, (s, e) in HELIX_MAP.items():
    if s <= current_pos <= e: active_id, dom_name = h_id, f"Transmembrane Helix {h_id}"
for l_id, (s, e, side, curve, f_h, t_h) in LOOP_MAP.items():
    if s <= current_pos <= e: active_id, dom_name = l_id, f"{l_id} Domain Region"

# ─── CALCULATE PREDICTIONS AND METRICS ──────────────────────────────────────
is_core = active_id in ["1","3","6","7","8"] or active_id in ["ECL1","IL1","ECL2","IL2","ECL3","IL3","ECL4","IL4"]

if mut_type in ['Nonsense', 'Frameshift']:
    risk_score, trans_yield, pred, alert, mech = 100, 0, "Pathogenic (High Risk)", st.error, "Triggers structural protein truncation or NMD; complete loss of functional transport operations."
elif mut_type == 'Synonymous':
    risk_score, trans_yield, pred, alert, mech = 5, 98, "Benign / Low Risk", st.success, "Silent nucleotide substitution preserves original sequence fold parameters completely."
else:
    if is_core: risk_score, trans_yield, pred, alert, mech = 85, 12, "Likely Pathogenic (High Risk)", st.error, f"Alters critical transport core segments ({active_id}), directly stalling creatine binding pocket coordination."
    elif active_id in ["N", "C"]: risk_score, trans_yield, pred, alert, mech = 15, 88, "Likely Benign (Low Risk)", st.success, "Alters flexible terminal tail residues outside vital functional structural wraps."
    else: risk_score, trans_yield, pred, alert, mech = 45, 55, "Variant of Uncertain Significance (VUS)", st.warning, "Modifies general peripheral scaffold wraps. Empirical tracking assays required."

# Generate clean HGVS code for database lookups (e.g., p.P382L)
hgvs = f"p.{wt_letter}{current_pos}{mut}" if mut_type == "Missense" else (f"p.{wt_letter}{current_pos}*" if mut_type == "Nonsense" else (f"p.X{current_pos}fs" if mut_type == "Frameshift" else "Synonymous"))

# Engine Diagnostic Variant Readout Label
st.write(f"⚙️ **System Engine Variant String Generated:** `{hgvs}`")

# ─── RENDER READOUT INTERFACE ───────────────────────────────────────────────
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Mapped Domain", active_id if active_id in ["N","C"] else f"TM {active_id}" if active_id.isdigit() else active_id)
col_b.metric("Variant Identity", hgvs)
col_c.metric("Calculated Risk", f"{risk_score}%")
col_d.metric("Transporter Yield", f"{trans_yield}%")

# Clean, safe database cross-reference verification
cm = CLINVAR_DB.get(hgvs)
if cm:
    st.warning(f"**ClinVar Database Record Match Found**\n\n* **Clinical Status:** {cm[1]}\n* **Evidence Track:** {cm[2]}\n* **Formal Variant Reference:** {cm[3]}")
    st.link_button(f"Open Official NCBI Archive #{cm[0]} ➔", f"https://nih.gov{cm[0]}")

alert(f"### Predictor Model Output: {pred}")
st.info(f"**Predicted Molecular Impact:**\n\n{mech}")

# ─── VECTOR IMAGING BLUEPRINT ───────────────────────────────────────────────
st.markdown("### Experimental LeuT-Fold Blueprint Mapping")
fig, ax = plt.subplots(figsize=(7.5, 3.1), facecolor='#0b0f19')
ax.set_facecolor('#0b0f19')

helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
x_coords = {h: i * 0.65 for i, h in enumerate(helix_order)}

ax.axhline(0.5, color='#1f2937', linestyle='-'), ax.axhline(-0.5, color='#1f2937', linestyle='-')
ax.text(-0.8, 0.65, "OUT (Extracellular)", color='#38bdf8', fontsize=7.5, fontweight='bold')
ax.text(-0.8, -0.75, "IN (Intracellular)", color='#a855f7', fontsize=7.5, fontweight='bold')

for l, (s, e, side, curve, f_h, t_h) in LOOP_MAP.items():
    x1, x2 = x_coords[f_h], x_coords[t_h]
    yb = 0.5 if side == "out" else -0.5
    path = patches.Path([(x1, yb), ((x1+x2)/2, yb+curve), (x2, yb)], [patches.Path.MOVETO, patches.Path.CURVE3, patches.Path.CURVE3])
    if active_id == l: ax.add_patch(patches.PathPatch(path, edgecolor='#f59e0b', facecolor='none', linewidth=6.0, alpha=0.8, zorder=1))
    ax.add_patch(patches.PathPatch(path, edgecolor='#4b5563', facecolor='none', linewidth=2.0, zorder=2))

if active_id == "N": ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#f59e0b', linewidth=6.5, zorder=1)
if active_id == "C": ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#f59e0b', linewidth=6.5, zorder=1)
ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#4b5563', linewidth=2.5), ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#4b5563', linewidth=2.5)
ax.text(x_coords["1"]-0.3, -0.87, "N-term", color='#f59e0b' if active_id=="N" else '#6b7280', fontsize=7.5, ha='center', fontweight='bold')
ax.text(x_coords["12"]+0.3, -0.87, "C-term", color='#f59e0b' if active_id=="C" else '#6b7280', fontsize=7.5, ha='center', fontweight='bold')

for h, x in x_coords.items():
    if h == active_id: ax.add_patch(patches.Rectangle((x-0.24, -0.56), 0.48, 1.12, color='#f59e0b', alpha=0.9, zorder=2))
    rect = patches.FancyBboxPatch((x-0.16, -0.5), 0.32, 1.0, boxstyle="round,pad=0.02", color='#0284c7' if h in ["1","3","6","8"] else '#7c3aed', alpha=0.95, zorder=3)
    ax.add_patch(rect)
    ax.text(x, 0, h, color='white', ha='center', va='center', fontsize=9.5, fontweight='bold', zorder=4)

ax.plot(2.92, 0, marker='o', markersize=14, color='#ffffff', markeredgecolor='#0284c7', markeredgewidth=2, zorder=5)
ax.text(2.92, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7.5, fontweight='bold', zorder=6)
ax.set_xlim(-1, 7.8), ax.set_ylim(-1.0, 1.0), ax.axis('off')
st.pyplot(fig)
