import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Import backend elements securely
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP

# 1. Initialize Layout and Custom Clean Styles
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

# Inject explicit dark theme parameters across all core containers
st.markdown(
    """
    <style>
        /* Force explicit white typography styling on sidebar control components */
        [data-testid="stSidebar"] .stWidgetLabel p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] span[data-testid="stWidgetLabel"] ~ div div {
            color: #FFFFFF !important;
        }
        /* Custom Metric Style Overrides */
        .metric-card {
            padding: 1.25rem;
            border-radius: 0.75rem;
            border-left-width: 4px;
            border-style: solid;
            background-color: #1e293b;
            min-height: 100px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .metric-label {
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            color: #9ca3af;
            letter-spacing: 0.05em;
            display: block;
        }
        .metric-value {
            font-size: 1.15rem;
            font-weight: 800;
            margin-top: 0.25rem;
            display: block;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. State Management Framework
if "pos" not in st.session_state:
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 3. Sidebar Setup Configuration
st.sidebar.header("🧬 Configuration Controls")

col_prev, col_next = st.sidebar.columns(2)
with col_prev:
    st.button("⬅️ Step -1", on_click=step_down, use_container_width=True)
with col_next:
    st.button("Step +1 ➡️", on_click=step_up, use_container_width=True)

st.slider(
    "Select Residue Position",
    min_value=1,
    max_value=MAX_RESIDUE,
    key="pos"
)

# Core feature lookups
current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

# Extract the isolated alternative amino acid key safely without array fragmentation
aa_options = [f"{aa}" for aa in AA_MAP.keys() if aa != wt_residue]
alt_residue = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)

# 4. Process Structural Card Variables
if current_pos in HELIX_MAP:
    domain_type = f"Transmembrane Helix {HELIX_MAP[current_pos]}"
    domain_style = "border-color: #ef4444; color: #fca5a5;"
elif current_pos in LOOP_MAP:
    domain_type = f"{LOOP_MAP[current_pos]}"
    domain_style = "border-color: #3b82f6; color: #93c5fd;"
else:
    domain_type = "Unmapped Terminal Segment"
    domain_style = "border-color: #6b7280; color: #d1d5db;"

# Process Variant Mapping Database Lookup
variant_key = f"{wt_residue}{current_pos}{alt_residue}"
clinvar_status = CLINVAR_DB.get(variant_key, "Not Documented / Novel Variant")

if "Pathogenic" in clinvar_status:
    clinvar_style = "border-color: #f43f5e; color: #fda4af;"
elif "Benign" in clinvar_status:
    clinvar_style = "border-color: #10b981; color: #6ee7b7;"
else:
    clinvar_style = "border-color: #f59e0b; color: #fde047;"

# 5. Core Interface Display Assembly
st.title("⚡ SLC6A8 Creatine Transporter Variant Explorer")
st.subheader(f"Current Target Locus: {wt_residue}{current_pos}{alt_residue}")

# Render metrics columns natively using our custom style definitions
metrics_col1, metrics_col2 = st.columns(2)
with metrics_col1:
    st.markdown(
        f"""<div class="metric-card" style="{domain_style}">
            <span class="metric-label">Structural Domain Map</span>
            <span class="metric-value">{domain_type}</span>
        </div>""", 
        unsafe_allow_html=True
    )

with metrics_col2:
    st.markdown(
        f"""<div class="metric-card" style="{clinvar_style}">
            <span class="metric-label">ClinVar Database Classification</span>
            <span class="metric-value">{clinvar_status}</span>
        </div>""", 
        unsafe_allow_html=True
    )

st.write("") # Spacer

# 6. Advanced Matplotlib Native Configuration (Engineered to match Dark Mode Dashboard layout)
st.markdown("### LeuT-Structural Configuration Map")

# Set up clean dark theme properties manually for the figure layout
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor('#0f172a') # Matches Streamlit's canvas layer background
ax.set_facecolor('#1e293b')        # Matches internal card frames

# Plot Backbone Matrix Coordinates
x_coords = np.arange(1, MAX_RESIDUE + 1)
y_coords = np.sin(x_coords / 10) * 5 + np.cos(x_coords / 35) * 2
ax.plot(x_coords, y_coords, color="#4b5563", label="Protein Backbone", zorder=1, linewidth=2)

# Filter out specific groupings for multi-scatter passes
helix_x = [p for p in x_coords if p in HELIX_MAP]
helix_y = [y_coords[p-1] for p in helix_x]
loop_x = [p for p in x_coords if p in LOOP_MAP]
loop_y = [y_coords[p-1] for p in loop_x]

ax.scatter(helix_x, helix_y, color="#ef4444", s=25, label="TM Helices", zorder=2, alpha=0.85)
ax.scatter(loop_x, loop_y, color="#3b82f6", s=25, label="Loops / Tails", zorder=2, alpha=0.85)

# Accentuate our dynamic targeted index variant dot
ax.scatter([current_pos], [y_coords[current_pos-1]], color="#10b981", s=180, edgecolor="#ffffff", linewidth=2.5, label=f"Active Site ({wt_residue}{current_pos})", zorder=5)

# Styling clean-ups
ax.set_xlabel("Residue Position Sequence", fontsize=9, color="#9ca3af", fontweight='bold')
ax.grid(True, linestyle=":", alpha=0.2, color="#9ca3af")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#374151')
ax.spines['bottom'].set_color('#374151')
ax.tick_params(colors='#9ca3af', labelsize=8)
ax.get_yaxis().set_visible(False) # Clean look mapping like vector template
ax.legend(loc="upper right", framealpha=0.6, facecolor="#1e293b", edgecolor="#374151", fontsize=8)

# Output clean frame
st.pyplot(fig)
