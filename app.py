import streamlit as st
import json
from topology import REF_SEQ, AA_MAP, CLINVAR_DB, HELIX_MAP, LOOP_MAP
import streamlit.components.v1 as components

# Force full viewport expansion
st.set_page_config(page_title="SLC6A8 Mutation Predictor", layout="wide")

# Inject global CSS to force ultra-high contrast bright white text on sidebar controls
st.markdown(
    """
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0f172a !important;
        }
        [data-testid="stMainBlockContainer"] {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        header { visibility: hidden !important; height: 0px !important; }
        div[data-testid="stToolbar"] { display: none !important; }
        
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        div[data-baseweb="select"] * {
            color: #111827 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# State Management Initialization
if "pos" not in st.session_state:
    st.session_state.pos = 1

MAX_RESIDUE = len(REF_SEQ)

def step_down():
    if st.session_state.pos > 1:
        st.session_state.pos -= 1

def step_up():
    if st.session_state.pos < MAX_RESIDUE:
        st.session_state.pos += 1

# Sidebar Controls Layout
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

current_pos = st.session_state.pos
wt_residue = REF_SEQ[current_pos - 1]
wt_full_name = AA_MAP.get(wt_residue, "Unknown Residue")

st.sidebar.markdown(f"**Wild-Type Residue:** `{wt_residue}{current_pos}` ({wt_full_name})")

aa_options = [f"{aa}" for aa in AA_MAP.keys() if aa != wt_residue]
alt_residue = st.sidebar.selectbox("Select Variant Allele (MUT)", aa_options)

# Serialize Python items to clean JSON parameters
helix_json = json.dumps(HELIX_MAP)
loop_json = json.dumps(LOOP_MAP)
clinvar_json = json.dumps(CLINVAR_DB)
# Build Dashboard UI Framework inside variable block string
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://tailwindcss.com"></script>
    <script src="https://jsdelivr.net"></script>
    <style>
        body {{ 
            background-color: #0f172a; 
            margin: 0; 
            padding: 32px; 
            font-family: ui-sans-serif, system-ui, sans-serif;
            overflow-x: hidden; 
        }}
        ::-webkit-scrollbar {{ display: none; }}
    </style>
</head>
<body class="text-white">
    <div class="space-y-6 max-w-7xl mx-auto">
        <div>
            <h1 class="text-3xl font-black text-white tracking-tight">⚡ SLC6A8 Variant Explorer</h1>
            <p class="text-gray-400 text-sm font-medium mt-1">Dynamic LeuT-Fold configuration and validation sandbox.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-gray-800/90 p-6 rounded-xl border border-gray-700 shadow-2xl">
                <h3 class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Structural Domain Map</h3>
                <div id="domain-card" class="p-4 rounded-lg flex flex-col justify-center min-h-[90px] border">
                    <span id="domain-title" class="text-xl font-extrabold tracking-tight">Loading...</span>
                </div>
            </div>

            <div class="bg-gray-800/90 p-6 rounded-xl border border-gray-700 shadow-2xl">
                <h3 class="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">ClinVar Database Classification</h3>
                <div id="clinvar-card" class="p-4 rounded-lg flex flex-col justify-center min-h-[90px] border">
                    <span id="clinvar-title" class="text-xl font-extrabold tracking-tight">Checking...</span>
                </div>
            </div>
        </div>

        <div class="bg-gray-800/90 p-6 rounded-xl border border-gray-700 shadow-2xl">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xs font-bold uppercase tracking-widest text-gray-400">LeuT-Structural Configuration Map</h3>
                <span class="text-xs text-gray-500 font-mono font-bold uppercase tracking-wider bg-gray-900/50 px-2 py-1 rounded">Interactive Viewport</span>
            </div>
            <div class="relative w-full h-[320px]"><canvas id="topologyChart"></canvas></div>
        </div>
    </div>
"""
# Append runtime processing logic and render the final dashboard engine component window
html_code += f"""
    <script>
        const REF_SEQ = "{REF_SEQ}";
        const currentPos = {current_pos};
        const wtAA = "{wt_residue}";
        const altAA = "{alt_residue}";
        const helixMap = {helix_json};
        const loopMap = {loop_json};
        const clinvarDb = {clinvar_json};

        const domainCard = document.getElementById('domain-card');
        const domainTitle = document.getElementById('domain-title');
        const clinvarCard = document.getElementById('clinvar-card');
        const clinvarTitle = document.getElementById('clinvar-title');

        if (helixMap[currentPos]) {{
            domainTitle.textContent = "Transmembrane Helix " + helixMap[currentPos];
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-red-950/60 text-red-200 border-red-500 shadow-lg";
        }} else if (loopMap[currentPos]) {{
            domainTitle.textContent = loopMap[currentPos];
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-blue-950/60 text-blue-200 border-blue-500 shadow-lg";
        }} else {{
            domainTitle.textContent = "Unmapped Terminal Segment";
            domainCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-gray-900/60 text-gray-300 border-gray-600 shadow-lg";
        }}

        const variantKey = wtAA + currentPos + altAA;
        const statusStr = clinvarDb[variantKey] || "Not Documented / Novel Variant";
        clinvarTitle.textContent = statusStr;

        if (statusStr.includes("Pathogenic")) {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-rose-950/60 text-rose-200 border-rose-500 shadow-lg";
        }} else if (statusStr.includes("Benign")) {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-emerald-950/60 text-emerald-200 border-emerald-500 shadow-lg";
        }} else {{
            clinvarCard.className = "p-4 rounded-lg flex flex-col justify-center min-h-[90px] bg-amber-950/60 text-amber-200 border-amber-500 shadow-lg";
        }}

        const xCoords = Array.from({{length: REF_SEQ.length}}, (_, i) => i + 1);
        const backboneTrace = xCoords.map(x => Math.sin(x / 10) * 5 + Math.cos(x / 35) * 2);

        const helixData = xCoords.filter(x => helixMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));
        const loopData = xCoords.filter(x => loopMap[x]).map(x => ({{ x: x, y: backboneTrace[x-1] }}));

        const ctx = document.getElementById('topologyChart').getContext('2d');
        new Chart(ctx, {{
            type: 'scatter',
            data: {{
                datasets: [
                    {{ label: 'Backbone Trace', data: xCoords.map((x, i) => ({{ x: x, y: backboneTrace[i] }})), showLine: true, borderColor: '#4b5563', borderWidth: 2.5, pointRadius: 0, order: 2 }},
                    {{ label: 'TM Helices', data: helixData, backgroundColor: '#f87171', pointRadius: 5, order: 3 }},
                    {{ label: 'Loops / Tails', data: loopData, backgroundColor: '#60a5fa', pointRadius: 5, order: 4 }},
                    {{ label: `Active Site (${wtAA}${{currentPos}}${{altAA}})`, data: [{{ x: currentPos, y: backboneTrace[currentPos - 1] }}], backgroundColor: '#10b981', pointRadius: 11, borderColor: '#ffffff', borderWidth: 2.5, order: 1 }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ type: 'linear', title: {{ display: true, text: 'Residue Position Sequence', color: '#9ca3af', font: {{ size: 12, weight: 'bold' }} }}, grid: {{ color: '#374151' }}, ticks: {{ color: '#9ca3af', font: {{ weight: 'bold' }} }}, min: 1, max: REF_SEQ.length }},
                    y: {{ display: false }}
                }},
                plugins: {{ legend: {{ position: 'top', labels: {{ color: '#f3f4f6', font: {{ size: 12, weight: '600' }} }} }} }}
            }}
        }});
    </script>
</body>
</html>
"""

components.html(html_code, height=660, scrolling=False)
