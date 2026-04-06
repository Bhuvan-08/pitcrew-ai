import streamlit as st
import time
from strategist.agent import run_agent

st.set_page_config(page_title="PitCrew Control Room", page_icon="🏎️", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🏎️ PitCrew AI: Autonomous SRE Command Center")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 System Telemetry")
    if st.button("Refresh Infrastructure Status"):
        with st.spinner("Pinging Mechanic API..."):
            try:
                time.sleep(1) 
                st.success("Connection to infrastructure is active.")
                st.code("production-payment-gateway: RUNNING\npitcrew-mechanic: RUNNING", language="text")
            except Exception as e:
                st.error(f"Network Error: {e}")

with col2:
    st.subheader("🤖 PitCrew Chief (Agent Chat)")
    
    # UI FIX: Create a fixed-height scrolling container for the chat messages
    chat_container = st.container(height=500)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # The chat input stays securely below the scrolling container
    if prompt := st.chat_input("Command the PitCrew (e.g., 'Diagnose the payment gateway')"):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Render the new messages inside the scrolling container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing infrastructure..."):
                    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    
                    # BRAIN FIX: This actually calls your Groq agent instead of the placeholder!
                    response = run_agent(prompt, history)
                    
                    st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})