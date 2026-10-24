import streamlit as st
import pandas as pd
import numpy as np

# Import backend variables securely from topology.py
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP

# 1. Page Configuration
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

# 2. Force Bright White High-Contrast Typography for Sidebar Labels
st.markdown(
    """
    <style>
        /* Force high-contrast text rendering on all sidebar components */
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        /* Ensure drop-down selections are dark and clear on expansion */
        div[data-baseweb="select"] * {
            color: #111827 !important;
        }
        /* Custom High-Contrast Metric Cards for Main Page Layout */
        .metric-box {
            padding: 1.5rem;
            border-radius: 0.75rem;
            border-left: 5px solid;
            background-color: #1e293b;
            margin-bottom: 1rem;
        }
        .metric-lbl {
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            color: #9ca3af;
            letter-spacing: 0.05em;
        }
        .metric-val {
            font-size: 1.4rem;
            font-weight: 900;
            margin-top: 0.5rem;
            color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. State Management Setup (Single Source of Truth)
if "pos" not in st.session_state:
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 4. Sidebar Configuration Panels
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

# Active locus processing values
current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

aa_options = [f"{aa}" for aa in AA_MAP.keys() if aa != wt_residue]
alt_residue = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)

# 5. Core Dashboard Framework Rendering
st.title("⚡ SLC6A8 Creatine Transporter Variant Explorer")
st.subheader(f"Current Target Locus: {wt_residue}{current_pos}{alt_residue}")

# Resolve Domain types and map to color blocks
if current_pos in HELIX_MAP:
    domain_type = f"Transmembrane Helix {HELIX_MAP[current_pos]}"
    domain_border = "#ef4444"  # High-contrast red border for transmembrane domains
else:
    domain_type = f"{LOOP_MAP.get(current_pos, 'Unmapped Terminal Segment')}"
    domain_border = "#3b82f6"  # High-contrast blue border for loop regions

# Resolve database classifications and colors
variant_key = f"{wt_residue}{current_pos}{alt_residue}"
clinvar_status = CLINVAR_DB.get(variant_key, "Not Documented / Novel Variant")

if "Pathogenic" in clinvar_status:
    clinvar_border = "#f43f5e"  # Rose
elif "Benign" in clinvar_status:
    clinvar_border = "#10b981"  # Emerald
else:
    clinvar_border = "#f59e0b"  # Amber

# Render Custom Metrics Rows using HTML Markdown to bypass standard layout margins
metrics_col1, metrics_col2 = st.columns(2)
with metrics_col1:
    st.markdown(
        f"""<div class="metric-box" style="border-color: {domain_border};">
            <div class="metric-lbl">Structural Domain Map</div>
            <div class="metric-val">📍 {domain_type}</div>
        </div>""",
        unsafe_allow_html=True
    )
with metrics_col2:
    st.markdown(
        f"""<div class="metric-box" style="border-color: {clinvar_border};">
            <div class="metric-lbl">ClinVar Database Classification</div>
            <div class="metric-val">🔍 {clinvar_status}</div>
        </div>""",
        unsafe_allow_html=True
    )

st.write("") 

# 6. High-Contrast Interactive 2D LeuT-Fold Topology Grid Map
st.markdown("### LeuT-Fold Grid Configuration Map")

# Build data grid vectors mapping out structural types cleanly
plot_data = []
for x in range(1, MAX_RESIDUE + 1):
    # Sinusoidal wave mapping cross-membrane loop-helix coordinates precisely like our dashboard template
    y_val = Math.sin(x / 10) * 5 + Math.cos(x / 35) * 2 if hasattr(np, 'sin') else 0
    y_val = np.sin(x / 10) * 5 + np.cos(x / 35) * 2
    
    if x == current_pos:
        region = "Active Target Locus"
    elif x in HELIX_MAP:
        region = "Transmembrane Helix (Core)"
    else:
        region = "Loops & Terminal Tails"
        
    plot_data.append({"Residue Position": x, "Structural Shift Vector": y_val, "Domain Region": region})

df = pd.DataFrame(plot_data)

# Render interactive scatter configuration mapping layout natively
st.scatter_chart(
    data=df,
    x="Residue Position",
    y="Structural Shift Vector",
    color="Domain Region",
    color_config={
        "Transmembrane Helix (Core)": "#ef4444",
        "Loops & Terminal Tails": "#3b82f6",
        "Active Target Locus": "#10b981"
    },
    use_container_width=True,
    height=320
)
