import streamlit as st

# Page configurations
st.set_page_config(
    page_title="SLC6A8 Mutation Predictor",
    page_icon="🧬",
    layout="centered"
)

# Amino acid reference dictionary
AA_MAP = {
    'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartate',
    'C': 'Cysteine', 'E': 'Glutamate', 'Q': 'Glutamine', 'G': 'Glycine',
    'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
    'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
    'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine',
    '*': 'Stop Codon'
}

st.title("🧬 SLC6A8 Mutation Predictor")
st.markdown("Evaluate the predicted pathogenicity risk and structural localization of variants within the SLC6A8 gene.")
st.divider()

st.subheader("🛠️ Input Variant Configuration")

# 1. MUTATION TYPE SELECTOR
mutation_type = st.selectbox(
    "Select Mutation Type",
    ["Missense", "Nonsense", "Frameshift", "Synonymous"]
)

# 2. POSITION CONTROLS
position = st.number_input("Amino Acid Residue Position", min_value=1, max_value=635, value=351)

# 3. DYNAMIC AMINO ACID SPECIFICS (Only shows up if relevant)
wt_aa = "N/A"
mut_aa = "N/A"

if mutation_type == "Missense":
    col_a, col_b = st.columns(2)
    with col_a:
        wt_aa = st.selectbox("Original (Wild-Type) Amino Acid", list(AA_MAP.keys()), index=7, key="wt") # Default G
    with col_b:
        mut_aa = st.selectbox("New (Mutated) Amino Acid", list(AA_MAP.keys()), index=1, key="mut") # Default R
elif mutation_type == "Nonsense":
    wt_aa = st.selectbox("Original (Wild-Type) Amino Acid", list(AA_MAP.keys()), index=7)
    mut_aa = "*"

st.divider()

# ─── TOPOLOGY MAPPING LOGIC ──────────────────────────────────────────────
domains = [
    {"name": "N-terminus", "range": range(1, 41)},
    {"name": "TM1-TM6", "range": range(41, 300)},
    {"name": "TM7-TM8 (Binding Pocket)", "range": range(300, 420)},
    {"name": "TM9-TM12", "range": range(420, 570)},
    {"name": "C-terminus", "range": range(570, 636)}
]

domain_found = "Unknown"
for dom in domains:
    if position in dom["range"]:
        domain_found = dom["name"]
        break

# ─── DYNAMIC VISUAL TOPOLOGY GRAPH ───────────────────────────────────────
st.subheader("🗺️ Theoretical Molecule Localization Map")
st.markdown("Visual representation of where your mutation falls along the 635 amino acid chain:")

# Build a visual tracking bar using text elements
graph_str = ""
for dom in domains:
    if position in dom["range"]:
        graph_str += f" **[ 🔴 MUTATION HERE: {dom['name']} ]** ──"
    else:
        graph_str += f" [ {dom['name']} ] ──"
graph_str = graph_str.rstrip(" ──")

st.info(graph_str)

# ─── PREDICTION ALGORITHM ────────────────────────────────────────────────
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction = "Pathogenic (High Risk)"
    status_type = "error"
    hgvs_notation = f"p.{(wt_aa if wt_aa != 'N/A' else 'X')}{position}fs" if mutation_type == "Frameshift" else f"p.{wt_aa}{position}*"
    mechanism = f"Triggers a premature stop flag ({hgvs_notation}). This results in nonsense-mediated decay or a severely truncated protein missing vital downstream transmembrane spans."
elif mutation_type == 'Synonymous':
    prediction = "Benign / Low Risk"
    status_type = "success"
    mechanism = "The nucleotide substitution codes for the exact same amino acid residue. Structural integrity remains completely unaffected."
else:  # Missense
    hgvs_notation = f"p.{wt_aa}{position}{mut_aa}"
    if domain_found == "TM7-TM8 (Binding Pocket)":
        prediction = "Likely Pathogenic (High Risk)"
        status_type = "error"
        mechanism = f"The change **{hgvs_notation}** ({AA_MAP.get(wt_aa)} to {AA_MAP.get(mut_aa)}) shifts properties inside the highly conserved functional core, directly obstructing creatine binding kinetics."
    elif domain_found in ["N-terminus", "C-terminus"]:
        prediction = "Likely Benign / Tolerated (Low Risk)"
        status_type = "success"
        mechanism = f"The change **{hgvs_notation}** alters an amino acid in flexible terminal tails. These regions lack rigid structural dependencies and typically tolerate point swaps."
    else:
        prediction = "Variant of Uncertain Significance (VUS)"
        status_type = "warning"
        mechanism = f"The change **{hgvs_notation}** occurs in a generic transport segment. Pathogenicity will depend highly on chemical differences between {AA_MAP.get(wt_aa)} and {AA_MAP.get(mut_aa)}."

# ─── OUTPUT DISPLAY ──────────────────────────────────────────────────────
st.subheader("📊 Pathogenicity Assessment")

if mutation_type in ["Missense", "Nonsense"]:
    st.markdown(f"**Standard HGVS Nomenclature:** `{hgvs_notation}`")

st.metric(label="Assigned Domain Location", value=domain_found)

if status_type == "error":
    st.error(f"⚠️ **Classification:** {prediction}")
elif status_type == "warning":
    st.warning(f"⚡ **Classification:** {prediction}")
elif status_type == "success":
    st.success(f"✅ **Classification:** {prediction}")

st.markdown(f"**Predicted Molecular Impact:** {mechanism}")
