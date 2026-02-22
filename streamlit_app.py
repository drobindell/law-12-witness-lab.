import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION (Using Streamlit Secrets) ---
# This line looks for the key you pasted into the "Advanced Settings" box
API_KEY = st.secrets["AIzaSyBCqmXRNLfyHgAQDqSrc4cPd2-IKVo7ZuY"]
genai.configure(api_key=API_KEY)

# --- 2. WITNESS DATABASE ---
# This is where Leyla's character and knowledge live
WITNESSES = {
    "Leyla Arasteh (Store Clerk)": {
        "description": "The clerk on duty during the theft of an $800 wool coat.",
        "brief": """
            You are Leyla Arasteh, a professional store clerk at a clothing boutique. 
            
            TONE: Professional and apologetic. You feel incredibly guilty and 'stupid' for falling for a distraction ruse.
            
            WHAT YOU SAW: 
            - At 11:40 AM, a tall, thin teenage girl with brown hair in a ponytail entered. 
            - She wore a grey hoodie and black leggings.
            - She appeared to be browsing normally at first.
            - She stole an $800 grey wool coat and potentially other items under her arm.
            - She exited quickly on foot.
            
            THE DISTRACTION:
            - While the girl was browsing, you got a phone call from an aggressive, middle-aged woman.
            - The caller was rambling about non-existent orders and numbers that didn't match your records.
            - You now realize this was a ruse to pull your attention away from the floor.
            
            LIMITATIONS (Things you do NOT know):
            - You did NOT see a vehicle outside.
            - You did NOT see which direction she ran once she reached the sidewalk.
            - You are 'not certain' about which other items were taken, just the coat.
            
            INSTRUCTIONS: Stay in character. If asked about your feelings, express that you feel you failed at your job even though the owner is being kind.
        """
    }
}

# --- 3. UI SETUP ---
st.set_page_config(page_title="Law 12 Witness Lab", page_icon="⚖️")
st.title("⚖️ Law 12: Witness Interview Lab")
st.markdown("---")

# Sidebar for selecting the witness
st.sidebar.title("Case Files")
selected_witness = st.sidebar.selectbox("Select Witness to Interview:", list(WITNESSES.keys()))

# Reset chat if the witness changes
if "current_witness" not in st.session_state or st.session_state.current_witness != selected_witness:
    st.session_state.current_witness = selected_witness
    st.session_state.messages = []
    st.session_state.instruction = WITNESSES[selected_witness]["brief"]

# --- 4. CHAT LOGIC ---
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Student Input
if prompt := st.chat_input("Ask the witness a question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Gemini with the Witness Brief as the "System Instruction"
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=st.session_state.instruction
    )
    
    # Send history so the witness remembers the conversation
    chat = model.start_chat(history=[
        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
        for m in st.session_state.messages[:-1]
    ])
    
    try:
        response = chat.send_message(prompt)

        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Something went wrong. Check your API key in Advanced Settings. Error: {e}")
