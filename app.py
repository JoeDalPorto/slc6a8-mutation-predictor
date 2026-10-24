import streamlit as st
import json
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP
import streamlit.components.v1 as components

# 1. Force Streamlit to hide its default wrappers, margins, and headers globally
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

st.markdown(
    """
    <style>
        /* Eliminate native Streamlit body padding to let the template expand fully */
        [data-testid="stAppViewContainer"] {
            background-color: #0f172a !important;
        }
        [data-testid="stMainBlockContainer"] {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        /* Completely hide standard header anchors */
        header { visibility: hidden !important; height: 0px !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        
        /* Force Bright White text labels inside native Sidebar frame */
        [data-testid="stSidebar"] .stWidgetLabel p, 
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] span[data-testid="stWidgetLabel"] ~ div div {
            color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Python State Synchronization
if "pos" not in st.session_state:
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# 3. Sidebar Construction
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

# Active coordinate metrics extraction
current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

# Clean Variant Options Lookup mapping
aa_options = [f"{aa} ({name})" for aa, name in AA_MAP.items() if aa != wt_residue]
selected_alt_raw = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)
alt_residue = selected_alt_raw.split(" ")[0]

# 4. Preparing variables for JavaScript ingestion
helix_json = json.dumps(HELIX_MAP)
loop_json = json.dumps(LOOP_MAP)
clinvar_json = json.dumps(CLINVAR_DB)

# 5. The Monolithic App Component Template (Compiled into an integrated presentation frame)
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://tailwindcss.com"></script>
    <script src="https://jsdelivr.net"></script>
    <style>
        body {{ background-color: #0f172a; margin: 0; padding: 24px; font-family: sans-serif; overflow-x: hidden; }}
        /* Hide scrollbars for an explicit dashboard appearance */
        ::-webkit-scrollbar {{ display: none; }}
    </style>
</head>
<body class="text-gray-100">

    <div class="space-y-6">
        <!-- Title Workspace -->
        <div>
            <h1 class="text-3xl font-extrabold text-white tracking-tight">
                ⚡ SLC6A8 Creatine Transporter Variant Explorer
            </h1>
            <p class="text-gray-400 text-sm mt-1">
                Dynamic LeuT-Fold configuration and validation sandbox.
            </p>
        </div>

        <!-- Status Display Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Structural Information Card -->
            <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-xl">
                <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Structural Domain Map</h3>
                <div id="domain-card" class="p-4 rounded-lg flex flex-col justify-center min-h-[90px] transition-colors duration-200">
                    <span id="domain-title" class="text-lg font-bold text-gray-900">Determining...</span>
                </div>
            </div>

            <!-- ClinVar Database Card -->
            <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-xl">
                <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">ClinVar Database Classification</h3>
                <div id="clinvar-card" class="p-4 rounded-lg flex flex-col justify-center min-h-[90px] transition-colors duration-200">
                    <span id="clinvar-title" class="text-lg font-bold text-gray-900">Checking DB...</span>
                </div>
            </div>
        </div>

        <!-- Interactive Topology Plot Container -->
        <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-xl">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xs font-bold uppercase tracking-wider text-gray-400">LeuT-Structural Configuration Map</h3>
                <span class="text-xs text-gray-500 font-mono">Interactive Vector Workspace</span>
            </div>
            <div class="relative w-full h-[320px]">
                <canvas id="topologyChart"></canvas>
            </div>
        </div>
    </div>

    <!-- PIPELINE SCRIPT INTERFACES -->
    <script>
        // Synchronized constants injected from python state boundaries
        const REF_SEQ = "{REF_SEQ}";
        const currentPos = {current_pos};
        const altAA = "{alt_residue}";
        const wtAA = "{wt_residue}";

        const helixMap = {helix_json};
        const loopMap = {loop_json};
        const clinvarDb = {clinvar_json};

        // Trace Math Generation
        const xCoords = Array.from({{length: REF_SEQ.length}}, (_, i) => i + 1);
        const backboneTrace = xCoords.map(x => Math.sin(x / 10) * 5 + Math.cos(x / 35) * 2);

        // DOM nodes setup
        const domainCard = document.getElementById('domain-card');
        const domainTitle = document.getElementById('domain-title');
        const clinvarCard = document.getElementById('clinvar-card');
        const clinvarTitle = document.getElementById('clinvar-title');

        // Process Topology Card Styles
        if (helixMap[currentPos]) {{
            domainTitle.textContent = "Transmembrane Helix " + helixMap[currentPos];
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-red-900/40 text-red-200 border-l-4 border-red-500 shadow-inner";
        }} else if (loopMap[currentPos]) {{
            domainTitle.textContent = loopMap[currentPos];
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-blue-900/40 text-blue-200 border-l-4 border-blue-500 shadow-inner";
        }} else {{
            domainTitle.textContent = "Unmapped Region";
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-gray-700/50 text-gray-300 border-l-4 border-gray-500 shadow-inner";
        }}

        // Process Variant Mapping Evaluation
        const variantKey = wtAA + currentPos + altAA;
        const statusStr = clinvarDb[variantKey] || "Not Documented / Novel Variant";
        clinvarTitle.textContent = statusStr;

        if (statusStr.includes("Pathogenic")) {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-rose-900/40 text-rose-200 border-l-4 border-rose-500 shadow-inner";
        }} else if (statusStr.includes("Benign")) {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-emerald-900/40 text-emerald-200 border-l-4 border-emerald-500 shadow-inner";
        }} else {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-amber-900/40 text-amber-200 border-l-4 border-amber-500 shadow-inner";
        }}

        // Initialize Chart Data Filters
        const helixData = xCoords.filter(x => helixMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));
        const loopData = xCoords.filter(x => loopMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));

        const ctx = document.getElementById('topologyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'scatter',
            data: {{
                datasets: [
                    {{ label: 'Backbone', data: xCoords.map((x, i) => ({{ x: x, y: backboneTrace[i] }})), showLine: true, borderColor: '#4b5563', borderWidth: 2, pointRadius: 0, order: 2 }},
                    {{ label: 'TM Helices', data: helixData, backgroundColor: '#ef4444', pointRadius: 4, order: 3 }},
                    {{ label: 'Loops', data: loopData, backgroundColor: '#3b82f6', pointRadius: 4, order: 4 }},
                    {{ label: 'Active Locus', data: [{{ x: currentPos, y: backboneTrace[currentPos - 1] }}], backgroundColor: '#10b981', pointRadius: 10, borderColor: '#ffffff', borderWidth: 3, order: 1 }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ type: 'linear', title: {{ display: true, text: 'Residue Position Sequence', color: '#9ca3af', font: {{ size: 12, weight: 'bold' }} }}, grid: {{ color: '#374151' }}, ticks: {{ color: '#9ca3af' }}, min: 1, max: REF_SEQ.length }},
                    y: {{ display: false }}
                }},
                plugins: {{ 
                    legend: {{ labels: {{ color: '#f3f4f6', boxWidth: 12, font: {{ size: 12 }} }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

# 6. Render as a unified layout dashboard viewport panel
components.html(html_code, height=650, scrolling=False)
