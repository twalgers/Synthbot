import streamlit as st
import openai
from typing import List

# ---- Config ----
openai.api_key = st.secrets["OPENAI_API_KEY"]  # You can set this in Streamlit Cloud

# ---- Session State ----
if "outputs" not in st.session_state:
    st.session_state.outputs = {"Customer": [], "Competition": [], "Brand": []}
if "final_output" not in st.session_state:
    st.session_state.final_output = ""
if "prompts" not in st.session_state:
    st.session_state.prompts = {
        "Customer": "Summarise key desires and unmet needs.",
        "Competition": "What are the recurring brand messages across competitors?",
        "Brand": "Extract key brand values and positioning themes.",
        "Final": "Synthesize the Customer, Competition and Brand insights into one cohesive brand strategy summary."
    }

# ---- Functions ----
def generate_response(prompt: str, input_text: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a brand strategist assistant."},
            {"role": "user", "content": f"{prompt}\n\nInput:\n{input_text}"}
        ]
    )
    return response.choices[0].message.content.strip()

# ---- Layout ----
st.title("🧠 Brand Strategy Synthesiser")
tabs = st.tabs(["Customer", "Competition", "Brand", "Final Synthesis"])

for i, section in enumerate(["Customer", "Competition", "Brand"]):
    with tabs[i]:
        st.subheader(f"{section} Inputs")
        input_text = st.text_area(f"Paste {section} text or notes:", key=f"{section}_input")
        uploaded_file = st.file_uploader("Or upload a file (PDFs not yet parsed):", key=f"{section}_file")

        st.subheader("Prompt")
        prompt = st.text_area("Edit prompt:", value=st.session_state.prompts[section], key=f"{section}_prompt")

        if st.button(f"Generate {section} Synthesis", key=f"{section}_run"):
            combined_input = input_text  # For now only text, PDF parsing not yet supported
            if combined_input.strip():
                output = generate_response(prompt, combined_input)
                st.session_state.outputs[section].append(output)
            else:
                st.warning("Please provide input text before generating.")

        if st.session_state.outputs[section]:
            st.subheader("Previous Syntheses")
            idx = st.slider(f"Browse iterations:", 0, len(st.session_state.outputs[section])-1, key=f"{section}_slider")
            st.text_area("Synthesis Output:", st.session_state.outputs[section][idx], height=200, key=f"{section}_output")

# ---- Final Synthesis ----
with tabs[3]:
    st.subheader("Final Synthesis Prompt")
    final_prompt = st.text_area("Edit final synthesis prompt:", value=st.session_state.prompts["Final"], key="Final_prompt")

    if all(st.session_state.outputs[sec] for sec in ["Customer", "Competition", "Brand"]):
        if st.button("Generate Final Synthesis"):
            combined_sections = "\n\n".join([
                f"{sec} Insight:\n{st.session_state.outputs[sec][-1]}" for sec in ["Customer", "Competition", "Brand"]
            ])
            final_output = generate_response(final_prompt, combined_sections)
            st.session_state.final_output = final_output

        if st.session_state.final_output:
            st.subheader("Final Synthesis Output")
            st.text_area("Final Output:", st.session_state.final_output, height=300)
    else:
        st.info("All three sections must have at least one synthesis before generating final output.")
