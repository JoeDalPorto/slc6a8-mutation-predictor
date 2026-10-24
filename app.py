import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Import backend variables securely
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP

# 1. Page Configuration
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

# 2. Strict High-Contrast Typography Styles (Guarantees White Labels)
st.markdown(
    """
    <style>
        /* Force ultra-high contrast bright white on all sidebar text */
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        /* Ensure drop-down menu items remain dark and readable on expansion */
        div[data-baseweb="select"] * {
            color: #111827 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. State Management (Single Source of Truth)
if "pos" not in st.session_state:
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 4. Sidebar Configuration Controls
st.sidebar.header("🧬 Configuration Controls")

col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    st.button("⬅️ Step -1", on_click=step_down, use_container_width=True)
with col_next:
    st.button("Step +1 ➡️", on_click=step_up, use_container_width=True)

st.sidebar.slider(
    "Select Residue Position",
    min_value=1,
    max_value=MAX_RESIDUE,
    key="pos"
)

# Current selection state calculations
current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

# Unified dropdown selection matching the wild-type residue parameters
aa_options = [f"{aa}" for aa in AA_MAP.keys() if aa != wt_residue]
alt_residue = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)

# 5. Native Dashboard Structural & ClinVar Metric Cards
st.title("⚡ SLC6A8 Creatine Transporter Variant Explorer")
st.subheader(f"Current Target Locus: {wt_residue}{current_pos}{alt_residue}")

# Evaluate Structural Mappings
if current_pos in HELIX_MAP:
    domain_type = f"Transmembrane Helix {HELIX_MAP[current_pos]}"
    domain_box = st.error
else:
    domain_type = f"{LOOP_MAP.get(current_pos, 'Unmapped Terminal Segment')}"
    domain_box = st.info

# Evaluate Database Mappings
variant_key = f"{wt_residue}{current_pos}{alt_residue}"
clinvar_status = CLINVAR_DB.get(variant_key, "Not Documented / Novel Variant")

if "Pathogenic" in clinvar_status:
    clinvar_box = st.error
elif "Benign" in clinvar_status:
    clinvar_box = st.success
else:
    clinvar_box = st.warning

# Render Dashboard Metrics with absolute text contrast layout
metrics_col1, metrics_col2 = st.columns(2)
with metrics_col1:
    st.markdown("**Structural Domain Map**")
    domain_box(f"📍 {domain_type}")

with metrics_col2:
    st.markdown("**ClinVar Database Classification**")
    clinvar_box(f"🔍 {clinvar_status}")

st.write("") 

# 6. Intuitive 2D LeuT-Fold Topology Grid Viewport Plot
st.markdown("### LeuT-Fold Topology Position Map")

# Set up clean dark-theme container plotting parameters matching your interface
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(11, 2.5))
fig.patch.set_facecolor('#0f172a') # Hex colors matching your theme canvas layers
ax.set_facecolor('#1e293b')

# Construct true linear representation layout grid coordinates
x_coords = np.arange(1, MAX_RESIDUE + 1)
y_coords = np.zeros(MAX_RESIDUE) # Strictly linear grid row layout

# Segregate structural clusters into concrete mapping rows
helix_indices = [p for p in x_coords if p in HELIX_MAP]
loop_indices = [p for p in x_coords if p in LOOP_MAP]

# Plot Backbone Matrix Connections
ax.plot(x_coords, y_coords, color="#4b5563", linewidth=3, zorder=1, label="Protein Backbone")

# Plot Structural Regions as Distinct Blocks
ax.scatter(helix_indices, [0]*len(helix_indices), color="#ef4444", s=50, marker="s", label="TM Helices (Core)", zorder=2)
ax.scatter(loop_indices, [0]*len(loop_indices), color="#3b82f6", s=50, marker="o", label="Loops / Tails", zorder=2)

# Highlight Current Target Amino Acid with high-contrast accent ring
ax.scatter([current_pos], [0], color="#10b981", s=250, edgecolor="#ffffff", linewidth=3, zorder=5, label=f"Active Site ({wt_residue}{current_pos}{alt_residue})")

# Remove plot borders for an intuitive dashboard style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#374151')
ax.get_yaxis().set_visible(False)

# Configure grids and display text sizes
ax.set_xlabel("Amino Acid Sequence Index", fontsize=10, color="#9ca3af", fontweight='bold')
ax.tick_params(colors='#9ca3af', labelsize=9)
ax.set_xlim(0, MAX_RESIDUE + 1)
ax.set_ylim(-1, 1)
ax.grid(True, axis='x', linestyle=":", alpha=0.3, color="#9ca3af")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=4, framealpha=0.9, facecolor="#1e293b", edgecolor="#374151", fontsize=9)

st.pyplot(fig)
