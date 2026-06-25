import streamlit as st
import PyPDF2
import google.generativeai as genai

# --- UI Setup ---
st.title("The Ultimate Custom Resume Bot 🤖")
st.write("Upload a resume and tell the AI exactly how you want it to behave!")

# --- 1. YOUR API KEY IS HARDCODED HERE ---
GOOGLE_API_KEY = "AQ.Ab8RN6Ij_g4zDyWomqDRku4bBCixj46kKngCyZH5hE9jMs88QQ"

# Wake up the Gemini Brain
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
# Set up a memory bank
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. The Custom Prompt Box ---
custom_prompt = st.text_area(
    "How should the AI act?", 
    placeholder="Example: Act as a strict tech interviewer and grill me on my skills based on this resume.",
    height=100
)

# --- 3. The File Uploader ---
uploaded_file = st.file_uploader("Drop a Resume (PDF) here to start!", type="pdf")

# The bot only starts if they provide BOTH a prompt AND a resume
if uploaded_file is not None and custom_prompt:
    
    # --- 4. Extract Text ---
    if "resume_text" not in st.session_state:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.session_state.resume_text = text

        # --- 5. The DYNAMIC System Prompt ---
        system_prompt = f"""
        Here are your specific instructions for how to act: 
        {custom_prompt}
        
        Here is the candidate's extracted resume text to base your answers on: 
        {text}
        """

        # Feed the prompt to the AI invisibly
        st.session_state.messages.append({"role": "user", "content": system_prompt})
        
        # Get the AI's first response
        response = model.generate_content(st.session_state.messages[0]["content"])
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    # --- 6. Display the Chat ---
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- 7. The Chat Input Box ---
    if prompt := st.chat_input("Chat with the bot here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Remind the AI of the whole conversation
        conversation_history = ""
        for msg in st.session_state.messages:
            conversation_history += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        with st.chat_message("assistant"):
            response = model.generate_content(conversation_history)
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
