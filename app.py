import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Import backend variables and structures
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP

# 1. Page Configuration & Layout Customization
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

# Custom CSS to force bright white sidebar text labels & slider metrics
st.markdown(
    """
    <style>
        /* Force bright white for sidebar widget text */
        [data-testid="stSidebar"] .stWidgetLabel p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        /* Target slider specific tick marks and numerical labels */
        [data-testid="stSidebar"] span[data-testid="stWidgetLabel"] ~ div div {
            color: #FFFFFF !important;
        }
        /* Fallback for general markdown blocks in sidebar */
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. State Management (Single Source of Truth)
if "pos" not in st.session_state:
    st.session_state.pos = 1  # 1-indexed representation for biological notation

MAX_RESIDUE = len(REF_SEQ)

# Stepper adjustment callbacks with strict boundary clamping
def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 3. Sidebar Configuration (Controls)
st.sidebar.header("Navigation & Variant Setup")

# Fine-tuning UI column layout
col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    st.button("⬅️ Step -1", on_click=step_down, use_container_width=True)
with col_next:
    st.button("Step +1 ➡️", on_click=step_up, use_container_width=True)

# Main positional slider (Synced via state value)
st.slider(
    "Select Residue Position",
    min_value=1,
    max_value=MAX_RESIDUE,
    key="pos"
)

# Extract properties for current selection
current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]  # Safely convert to 0-index string offset
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

# Display unified nomenclature header within the control board
st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

# Mutation Target Dropdown (Unified format matching the WT display)
aa_options = [f"{aa} ({name})" for aa, name in AA_MAP.items() if aa != wt_residue]
selected_alt_raw = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)
alt_residue = selected_alt_raw.split(" ")[0]

# 4. Core Visualizations & Data Processing (Main Window)
st.title("⚡ SLC6A8 Creatine Transporter Variant Explorer")
st.subheader(f"Current Target: {wt_residue}{current_pos}{alt_residue}")

# Context Layout Columns
metrics_col, plot_col = st.columns([1, 2])

with metrics_col:
    st.markdown("### Topology & ClinVar Status")
    
    # Domain Mapping Lookup
    if current_pos in HELIX_MAP:
        domain_type = f"Transmembrane Helix {HELIX_MAP[current_pos]}"
        bg_color = "#ffe6e6"
    elif current_pos in LOOP_MAP:
        domain_type = f"Loop Region ({LOOP_MAP[current_pos]})"
        bg_color = "#e6f2ff"
    else:
        domain_type = "Unmapped / Terminal Tail"
        bg_color = "#f0f0f0"
        
    st.info(f"**Structural Domain:** {domain_type}")
    
    # Variant Specific Database Check
    variant_key = f"{wt_residue}{current_pos}{alt_residue}"
    clinvar_status = CLINVAR_DB.get(variant_key, "Not Documented / Novel Variant")
    
    if "Pathogenic" in clinvar_status:
        st.error(f"**ClinVar Classification:** {clinvar_status}")
    elif "Benign" in clinvar_status:
        st.success(f"**ClinVar Classification:** {clinvar_status}")
    else:
        st.warning(f"**ClinVar Classification:** {clinvar_status}")

with plot_col:
    st.markdown("### LeuT-Fold Topology Plot")
    
    # Generate structural plot dynamically
    fig, ax = plt.subplots(figsize=(7, 4))
    
    # Synthesize layout representation across a 12-TM standard grid
    x_coords = np.arange(1, MAX_RESIDUE + 1)
    # Simple simulated spatial wave tracking Transmembrane (TM) transitions
    y_coords = np.sin(x_coords / 10) * 5 + np.cos(x_coords / 35) * 2
    
    # Plot complete backbone trajectory
    ax.plot(x_coords, y_coords, color="#cccccc", label="Backbone", zorder=1, linewidth=1.5)
    
    # Highlight current functional groupings
    helix_positions = [p for p in x_coords if p in HELIX_MAP]
    loop_positions = [p for p in x_coords if p in LOOP_MAP]
    
    ax.scatter(helix_positions, [y_coords[p-1] for p in helix_positions], color="#ff4b4b", s=3, label="TM Helices", alpha=0.5)
    ax.scatter(loop_positions, [y_coords[p-1] for p in loop_positions], color="#1f77b4", s=3, label="Loops", alpha=0.5)
    
    # Accentuate currently evaluated locus
    ax.scatter([current_pos], [y_coords[current_pos-1]], color="#2ca02c", s=130, edgecolor="black", linewidth=1.5, label=f"Active Site ({wt_residue}{current_pos})", zorder=5)
    
    # Plot design adjustments
    ax.set_title("LeuT-Structural Configuration Map", fontsize=10, fontweight="bold")
    ax.set_xlabel("Residue Position Sequence", fontsize=8)
    ax.set_ylabel("Membrane Vector Coordinate", fontsize=8)
    ax.legend(loc="upper right", fontsize=7)
    ax.grid(True, linestyle="--", alpha=0.3)
    
    st.pyplot(fig)
