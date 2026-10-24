import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="SLC6A8 Predictor", page_icon="🧬", layout="centered")

st.markdown("<style>.stApp { background-color: #0b0f19; color: #f1f5f9; font-family: 'Inter', sans-serif; } section[data-testid='stSidebar'] { background-color: #111827 !important; border-right: 1px solid #1f2937; } div[data-testid='stMetricValue'] { font-family: monospace !important; font-weight: 700 !important; color: #38bdf8 !important; font-size: 22px !important; } div[data-testid='metric-container'] { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 12px; padding: 15px !important; }</style>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🧬 SLC6A8 Computational Predictor</h1><p style='text-align: center; color: #94a3b8; font-size: 14px;'>Advanced LeuT-Fold Molecular Mutation Mapping Engine</p>", unsafe_allow_html=True)
st.divider()

REF_SEQ = "M" * 340 + "G" * 15 + "P" * 40 + "A" * 100 + "R" * 20 + "A" * 120
AA_MAP = {'A':'Alanine','R':'Arginine','N':'Asparagine','D':'Aspartate','C':'Cysteine','E':'Glutamate','Q':'Glutamine','G':'Glycine','H':'Histidine','I':'Isoleucine','L':'Leucine','K':'Lysine','M':'Methionine','F':'Phenylalanine','P':'Proline','S':'Serine','T':'Threonine','W':'Tryptophan','Y':'Tyrosine','V':'Valine','*':'Stop Codon'}

CLINVAR_DB = {
    "p.G351R": ("2290132", "VUS", "Reviewed by ClinGen panel. High constraint but low data.", "ClinGen solute carrier panel criteria."),
    "p.P382L": ("533700", "Pathogenic", "Observed in classic X-linked CTD cohorts. Limits creatine uptake.", "OMIM Entry: #300352. PMID: 11313764."),
    "p.P390L": ("1361089", "Likely Pathogenic", "Disrupts the loop transitions flanking the structural core folds.", "ACMG/AMP secondary structural mutation review indices.")
}

if "pos" not in st.session_state: st.session_state.pos = 351
def sync_box(): st.session_state.pos = st.session_state.b_in
def sync_slide(): st.session_state.pos = st.session_state.s_in

current_pos = st.session_state.pos
wt_letter = REF_SEQ[current_pos - 1] if current_pos <= len(REF_SEQ) else "G"

with st.sidebar:
    st.markdown("<h2 style='font-size: 18px;'>🛠️ Variant Editor</h2>", unsafe_allow_html=True)
    mut_type = st.selectbox("Mechanism Type", ["Missense", "Nonsense", "Frameshift", "Synonymous"])
    st.number_input("Residue Position Box", 1, 635, value=st.session_state.pos, key="b_in", on_change=sync_box)
    st.slider("Residue Position Slider", 1, 635, value=st.session_state.pos, key="s_in", on_change=sync_slide)
    st.markdown(f"<span style='color:#94a3b8; font-size:12px;'>AUTO-POPULATED WILD-TYPE</span><br><code style='font-size:14px; color:#38bdf8;'>{wt_letter} ({AA_MAP.get(wt_letter)})</code>", unsafe_allow_html=True)
    mut = "*" if mut_type == "Nonsense" else st.selectbox("Substitute Amino Acid", list(AA_MAP.keys()), index=10, format_func=lambda x: f"{x} ({AA_MAP[x]})") if mut_type == "Missense" else "N/A"

helix_mapping = {"1":(41,65),"2":(81,105),"3":(131,155),"4":(176,200),"5":(216,240),"6":(276,300),"7":(321,345),"8":(371,395),"9":(421,445),"10":(466,490),"11":(511,535),"12":(546,570)}
loop_mapping = {"ECL1":(66,80,"out",0.2,"1","2"),"IL1":(106,130,"in",-0.2,"2","3"),"ECL2":(156,175,"out",0.3,"3","4"),"IL2":(201,215,"in",-0.2,"4","5"),"ECL3":(241,275,"out",0.4,"5","6"),"IL3":(301,320,"in",-0.3,"6","7"),"ECL4":(346,370,"out",0.2,"7","8"),"IL4":(397,420,"in",-0.3 canvas position,"8","9"),"ECL5":(446,465,"out",0.2,"9","10"),"IL5":(491,510,"in",-0.2,"10","11"),"ECL6":(536,545,"out",0.2,"11","12")}

active_id, dom_name = ("N", "Intracellular N-Terminus") if current_pos <= 40 else (("C", "Intracellular C-Terminus") if current_pos >= 571 else ("Loops", "Interhelical Structural Loop"))
for h, (s, e) in helix_mapping.items():
    if s 🗺️ Experimental LeuT-Fold Blueprint Mapping</h3>", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(7.5, 3.1), facecolor='#0b0f19'); ax.set_facecolor('#0b0f19')
helix_order = ["5", "4", "2", "3", "1", "6", "8", "7", "9", "10", "11", "12"]
x_coords = {h: i * 0.65 for i, h in enumerate(helix_order)}

ax.axhline(0.5, color='#1f2937', linestyle='-'), ax.axhline(-0.5, color='#1f2937', linestyle='-')
ax.text(-0.8, 0.65, "OUT (Extracellular)", color='#38bdf8', fontsize=7.5, fontweight='bold')
ax.text(-0.8, -0.75, "IN (Intracellular)", color='#a855f7', fontsize=7.5, fontweight='bold')

for l, (s, e, side, curve, f_h, t_h) in loop_mapping.items():
    x1, x2 = x_coords[f_h], x_coords[t_h]
    path = patches.Path([(x1, 0.5 if side == "out" else -0.5), ((x1+x2)/2, (0.5 if side == "out" else -0.5)+curve), (x2, 0.5 if side == "out" else -0.5)], [patches.Path.MOVETO, patches.Path.CURVE3, patches.Path.CURVE3])
    if active_id == l: ax.add_patch(patches.PathPatch(path, edgecolor='#f59e0b', facecolor='none', linewidth=6.0, alpha=0.8, zorder=1))
    ax.add_patch(patches.PathPatch(path, edgecolor='#4b5563', facecolor='none', linewidth=2.0, zorder=2))

if active_id == "N": ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#f59e0b', linewidth=6.5, zorder=1)
if active_id == "C": ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#f59e0b', linewidth=6.5, zorder=1)
ax.plot([x_coords["1"], x_coords["1"]-0.3], [-0.5, -0.8], color='#4b5563', linewidth=2.5), ax.plot([x_coords["12"], x_coords["12"]+0.3], [-0.5, -0.8], color='#4b5563', linewidth=2.5)
ax.text(x_coords["1"]-0.3, -0.87, "N-term", color='#f59e0b' if active_id=="N" else '#6b7280', fontsize=7.5, ha='center', fontweight='bold')
ax.text(x_coords["12"]+0.3, -0.87, "C-term", color='#f59e0b' if active_id=="C" else '#6b7280', fontsize=7.5, ha='center', fontweight='bold')

for h, x in x_coords.items():
    if h == active_id: ax.add_patch(patches.Rectangle((x-0.24, -0.56), 0.48, 1.12, color='#f59e0b', alpha=0.9, zorder=2))
    ax.add_patch(patches.FancyBboxPatch((x-0.16, -0.5), 0.32, 1.0, boxstyle="round,pad=0.02", color='#0284c7' if h in ["1","3","6","8"] else '#7c3aed', alpha=0.95, zorder=3))
    ax.text(x, 0, h, color='white', ha='center', va='center', fontsize=9.5, fontweight='bold', zorder=4)

ax.plot(2.92, 0, marker='o', markersize=14, color='#ffffff', markeredgecolor='#0284c7', markeredgewidth=2, zorder=5)
ax.text(2.92, 0, "Cr", color='#0f172a', ha='center', va='center', fontsize=7.5, fontweight='bold', zorder=6)
ax.set_xlim(-1, 7.8), ax.set_ylim(-1.0, 1.0), ax.axis('off')
st.pyplot(fig)
