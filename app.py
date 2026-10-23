import streamlit as st

# Application Title
st.title("🧬 SLC6A8 Mutation Predictor")
st.write("An interactive tool to evaluate variant pathogenicity risk across structural domains.")

# 1. Inputs
mutation_type = st.selectbox(
    "Select Mutation Type",
    ["Missense", "Nonsense", "Frameshift", "Synonymous"]
)
position = st.number_input("Amino Acid Position (1 - 635)", min_value=1, max_value=635, value=350)

# 2. Logic
domains = {
    "N-terminus": range(1, 41),
    "TM1-TM6": range(41, 300),
    "TM7-TM8 (Binding Pocket)": range(300, 420),
    "TM9-TM12": range(420, 570),
    "C-terminus": range(570, 636)
}

domain_found = "Unknown"
for name, pos_range in domains.items():
    if position in pos_range:
        domain_found = name
        break

# 3. Predictor Logic
if mutation_type in ['Nonsense', 'Frameshift']:
    prediction = "Pathogenic (High Risk)"
    color = "red"
    mechanism = "Causes major structural disruption or nonsense-mediated decay, leading to Creatine Transporter Deficiency (CTD)."
elif mutation_type == 'Synonymous':
    prediction = "Benign / Low Risk"
    color = "green"
    mechanism = "Does not alter the amino acid sequence."
else:  # Missense
    if domain_found == "TM7-TM8 (Binding Pocket)":
        prediction = "Likely Pathogenic (High Risk)"
        color = "red"
        mechanism = "Mutations in the highly conserved TM7/TM8 core directly impair substrate binding."
    elif domain_found in ["N-terminus", "C-terminus"]:
        prediction = "Likely Benign / Tolerated (Low Risk)"
        color = "green"
        mechanism = "Terminal domains are flexible; substitutions here are usually tolerated."
    else:
        prediction = "Variant of Uncertain Significance (VUS)"
        color = "orange"
        mechanism = "Located in a transmembrane/loop domain. Requires external verification metrics."

# 4. Display Results
st.subheader("Prediction Result")
st.metric(label="Assigned Domain", value=domain_found)
st.markdown(f"**Classification:** :{color}[{prediction}]")
st.write(f"**Mechanism:** {mechanism}")
