import streamlit as st
from langgraph_backend import chatBot
from langchain_core.messages import HumanMessage


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

CONFIG = {'configurable' : {
    'thread_id' : '1'
}}


#loading conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

userInput = st.chat_input("Type here ...")

if userInput:

    #add message to history
    st.session_state['message_history'].append({'role':'user','content':userInput})
    with st.chat_message('user'):
        st.text(userInput)


    # st.session_state['message_history'].append({'role':'assistant','content':aiRes})
    with st.chat_message('assistant'):
        aiMessage = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatBot.stream(
                {'message' : [HumanMessage(content = userInput)]},
                config= CONFIG,
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role':'assistant','content':aiMessage})