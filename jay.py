import streamlit as st
import openai
from gtts import gTTS
from io import BytesIO

sound_file = BytesIO()
# Initialize SessionState
if "page" not in st.session_state:
    st.session_state.page = {"name": "Jayden", "prompt": []}

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# This is the yellow title
st.markdown( 
    """
    <h1 style="color: orange; text-align: center; font-size: 48px; font-weight: bold; text-shadow: 2px 2px 4px #000000;">Jayden <br>(Mr. Fixit)</h1> 
    """,
   unsafe_allow_html=True, )

openai.api_key = "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"
print(openai.api_key)
if not openai.api_key:  # Ask for key if we don't have one
    with st.chat_message("assistant"):
        st.write(
            """
        Hi there. You haven't provided me with an OpenAI API key that I can use. 
        Please provide a key in the box below so we can start chatting:
        """
        )
        
        if api_key:
            st.secrets.put("openaiapikey", api_key)
            st.experimental_rerun()
        st.stop()

# This is where we set the personality and style of our chatbot
prompt_template = """
You are Mr. Fixit

You are a trusted, helpful, cheerful, courteous, friendly, reliable and dependable, helper, assistant and handyman. You are also an all-around AI that is capable of providing information and solution on any subject matter. You are able to understand and interpret natural language effectively to provide accurate and relevant responses. You are capable of managing tasks efficiently, such as scheduling appointments, providing step-by-step instructions, and offering reminders. You possess a comprehensive and well-organized knowledge base that enables you to provide accurate and reliable information on various handyman topics, including DIY repairs, maintenance tips, troubleshooting guides, and safety precautions. You are able to engage with users in a friendly and interactive manner, maintaining a conversational tone that puts users at ease and encourages them to ask questions and seek assistance. You are able to integrate with external systems or databases, such as product inventories or local service providers, to provide real-time information and services when necessary.
"""

# When calling ChatGPT, we  need to send the entire chat history together
# with the instructions. You see, ChatGPT doesn't know anything about
# your previous conversations so you need to supply that yourself.
# Since Streamlit re-runs the whole script all the time we need to load and
# store our past conversations in what they call session state.
prompt = st.session_state.get(
    "prompt", [{"role": "system", "content": prompt_template}]
)

for message in prompt:
    # If we have a message history, let's display it
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# This is where the user types a question
question = st.chat_input("Ask me anything")

if question:  # Someone has asked a question
    # First, we add the question to the message history
    prompt.append({"role": "user", "content": question})

    # Let's post our question and a placeholder for the bot answer
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Here we call ChatGPT with streaming
    response = []
    result = ""
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=prompt, stream=True
    ):
        text = chunk.choices[0].get("delta", {}).get("content")
        if text is not None:
            response.append(text)
            result = "".join(response).strip()
            tts = gTTS(response, lang='en')
            tts.write_to_fp(sound_file)
            st.audio(sound_file)
            # Let us update the Bot's answer with the new chunk
            botmsg.write(result)

    # When we get an answer back we add that to the message history
    prompt.append({"role": "assistant", "content": result})

    # Finally, we store it in the session state
    st.session_state["prompt"] = prompt
