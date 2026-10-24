import streamlit as st
import json
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP
import streamlit.components.v1 as components

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
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 3. Sidebar Configuration (Controls)
st.sidebar.header("Navigation & Variant Setup")

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

current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

aa_options = [f"{aa} ({name})" for aa, name in AA_MAP.items() if aa != wt_residue]
selected_alt_raw = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)
alt_residue = selected_alt_raw.split(" ")

# 4. Streamlit Python Metric Lookups
if current_pos in HELIX_MAP:
    domain_type = f"Transmembrane Helix {HELIX_MAP[current_pos]}"
    domain_css = "background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; border-color: #ef4444;"
elif current_pos in LOOP_MAP:
    domain_type = f"{LOOP_MAP[current_pos]}"
    domain_css = "background-color: rgba(59, 130, 246, 0.15); color: #93c5fd; border-color: #3b82f6;"
else:
    domain_type = "Unmapped / Terminal Tail"
    domain_css = "background-color: rgba(107, 114, 128, 0.15); color: #d1d5db; border-color: #6b7280;"

variant_key = f"{wt_residue}{current_pos}{alt_residue}"
clinvar_status = CLINVAR_DB.get(variant_key, "Not Documented / Novel Variant")

if "Pathogenic" in clinvar_status:
    clinvar_css = "background-color: rgba(244, 63, 94, 0.15); color: #fda4af; border-color: #f43f5e;"
elif "Benign" in clinvar_status:
    clinvar_css = "background-color: rgba(16, 185, 129, 0.15); color: #6ee7b7; border-color: #10b981;"
else:
    clinvar_css = "background-color: rgba(245, 158, 11, 0.15); color: #fde047; border-color: #f55e0b;"

# 5. Core Layout Structure (Main Window)
st.title("⚡ SLC6A8 Creatine Transporter Variant Explorer")
st.subheader(f"Current Target: {wt_residue}{current_pos}{alt_residue}")

# Render metrics using clean HTML layout to match the dashboard style
metrics_col1, metrics_col2 = st.columns(2)
with metrics_col1:
    st.markdown(
        f"""<div style="padding: 1.25rem; border-radius: 0.75rem; border-left-width: 4px; border-style: solid; min-height: 90px; {domain_css}">
            <span style="font-size: 0.75rem; font-weight: bold; text-transform: uppercase; color: #9ca3af; display: block; tracking-ratio: 0.05em;">Structural Domain Map</span>
            <span style="font-size: 1.125rem; font-weight: 800; margin-top: 0.25rem; display: block;">{domain_type}</span>
        </div>""", 
        unsafe_allow_html=True
    )

with metrics_col2:
    st.markdown(
        f"""<div style="padding: 1.25rem; border-radius: 0.75rem; border-left-width: 4px; border-style: solid; min-height: 90px; {clinvar_css}">
            <span style="font-size: 0.75rem; font-weight: bold; text-transform: uppercase; color: #9ca3af; display: block; tracking-ratio: 0.05em;">ClinVar Database Classification</span>
            <span style="font-size: 1.125rem; font-weight: 800; margin-top: 0.25rem; display: block;">{clinvar_status}</span>
        </div>""", 
        unsafe_allow_html=True
    )

st.write("") # Tiny spacer

# 6. Injecting the Interactive Chart Template (Chart.js Engine)
st.markdown("### LeuT-Structural Configuration Map")

# Convert Python map structures to JSON safe parameters for browser processing
helix_json = json.dumps(HELIX_MAP)
loop_json = json.dumps(LOOP_MAP)

# Generate raw interactive HTML frame responsive component block
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://jsdelivr.net"></script>
    <style>
        body {{ 
            background-color: #0e1117; 
            margin: 0; 
            padding: 10px; 
            overflow: hidden; 
            font-family: sans-serif; 
        }}
        .chart-wrapper {{
            background-color: #1f2937;
            border: 1px solid #374151;
            border-radius: 0.75rem;
            padding: 1.25rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        .chart-container {{ 
            position: relative; 
            width: 100%; 
            height: 300px; 
        }}
    </style>
</head>
<body>
    <div class="chart-wrapper">
        <div class="chart-container">
            <canvas id="canvasChart"></canvas>
        </div>
    </div>

    <script>
        const refSeqLength = {MAX_RESIDUE};
        const currentPos = {current_pos};
        const helixMap = {helix_json};
        const loopMap = {loop_json};

        const xCoords = Array.from({{length: refSeqLength}}, (_, i) => i + 1);
        const backboneTrace = xCoords.map(x => Math.sin(x / 10) * 5 + Math.cos(x / 35) * 2);

        const helixData = xCoords.filter(x => helixMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));
        const loopData = xCoords.filter(x => loopMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));

        const ctx = document.getElementById('canvasChart').getContext('2d');
        new Chart(ctx, {{
            type: 'scatter',
            data: {{
                datasets: [
                    {{ label: 'Backbone', data: xCoords.map((x, i) => ({{ x: x, y: backboneTrace[i] }})), showLine: true, borderColor: '#4b5563', borderWidth: 2, pointRadius: 0, order: 2 }},
                    {{ label: 'TM Helices', data: helixData, backgroundColor: '#ef4444', pointRadius: 4, order: 3 }},
                    {{ label: 'Loops', data: loopData, backgroundColor: '#3b82f6', pointRadius: 4, order: 4 }},
                    {{ label: 'Active Locus', data: [{{ x: currentPos, y: backboneTrace[currentPos - 1] }}], backgroundColor: '#10b981', pointRadius: 10, borderColor: '#ffffff', borderWidth: 2, order: 1 }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ type: 'linear', title: {{ display: true, text: 'Residue Position Sequence', color: '#9ca3af' }}, grid: {{ color: '#374151' }}, ticks: {{ color: '#9ca3af' }}, min: 1, max: refSeqLength }},
                    y: {{ title: {{ display: true, text: 'Membrane Vector Coordinate', color: '#9ca3af' }}, grid: {{ color: '#374151' }}, ticks: '#374151', display: false }}
                }},
                plugins: {{ 
                    legend: {{ 
                        labels: {{ color: '#f3f4f6', boxWidth: 12, font: {{ size: 11 }} }} 
                    }} 
                }}
            }}
        }});
    </script>
</body>
</html>
"""

# Render custom component window
components.html(html_code, height=370)
