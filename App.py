import streamlit as st
import os
import time
import PIL.Image

# App title
st.set_page_config(
    page_title = "Chatbot", 
    layout = "wide", 
    initial_sidebar_state = "auto", 
    menu_items = None
)

# OpenAI Credentials
with st.sidebar:
    api_key = st.text_input('Enter your API key:', type = 'password')
    if not (api_key.startswith('AI') and len(api_key) == 39):
        st.warning('Please enter your credentials!', icon = '⚠️')
    else:
        st.success("Proceed to entering your prompt message!", icon = '✅')
        st.toast('Refreshed')
        time.sleep(0.5)

    st.subheader('Models and Parameters')

    selected_model = st.sidebar.selectbox(
        ':blue[Choose a Model]',
        ['gemini-pro', 'gemini-pro-vision'], 
        index = None, 
        key = 'selected_model', 
        placeholder='select a model', 
        disabled=not api_key)
    
    if api_key and not selected_model:
        st.warning("Please select a model.")
    
    stream = st.sidebar.toggle(label=':blue[Stream Output]', help = 'Return partial results as they become available, instead of waiting until the computation is done.', disabled=not api_key)

    file_uploader = st.sidebar.file_uploader(
        label = ':blue[Upload an Image]',
        type = ['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files = False,
        key = None,
        help = 'Only for gemini pro vision model',
        disabled=not selected_model or selected_model[-1] != 'n'
    )

# Store LLM generated responses
if "message" not in st.session_state.keys():
    st.session_state.history = [{
        "text": "Hi there! I'm Gemini Pro. How may I assist you today?",
        "role": "model"
    }]

# Display or clear chat messages 
for message in st.session_state.history:
    with st.chat_message(message["role"], avatar='🤖'):
        st.write(message['text'])

def clear_chat_history():
    st.session_state.history = [{
        "text": "Hi there! I'm Gemini Pro. How may I assist you today?",
        "role": "model"
    }]

st.sidebar.button('Clear Chat History', on_click = clear_chat_history)

# function for generating responses
def generate_response_gemini_pro(message):
    if stream:
        response = chat.send_message(message, stream=True)
        responses = ""
        for chunk in response:
            responses += chunk.text or ""
        return responses
    else:
        response = chat.send_message(message)
        return response.text
    

def generate_response_gemini_pro_vision(message, imgs):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro-vision')
    if stream:
        response = model.generate_content([message, imgs], stream=True)
        responses = ""
        for chunk in response:
            responses += chunk.text or ""
        return responses
    else:
        response = model.generate_content([message, imgs])
        return response.text

# user-provided prompt message
if prompt := st.chat_input(disabled = not api_key):
    st.session_state.history.append({
        "text": prompt,
        "role": "user"
    })
    with st.chat_message('user'):
        st.write(prompt)

global chat

# generate a new response if last message is not from model
if st.session_state.history[-1]["role"] != "model":
    with st.chat_message('model', avatar='🤖'):
        with st.spinner("Thinking..."):
            if selected_model[-1] == 'o':
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                chat = model.start_chat(history=[])
                assistant_response = generate_response_gemini_pro(prompt)
            elif selected_model[-1] == 'n':
                if file_uploader is not None:
                    imgs = PIL.Image.open(file_uploader)
                    assistant_response = generate_response_gemini_pro_vision(prompt, imgs)
            placeholder = st.empty()
            full_response = ''
            if stream:
                # Simulate stream of response with milliseconds delay
                for item in assistant_response.split():
                    full_response += item + " "
                    time.sleep(0.05)
                    # Blinking cursor to simulate typing
                    placeholder.markdown(full_response + "| ")
            else:
                for item in assistant_response:
                    full_response  += item
            placeholder.markdown(full_response)

    message = {
        "text": full_response,
        "role": 'model'
    }
    st.session_state.history.append(message)