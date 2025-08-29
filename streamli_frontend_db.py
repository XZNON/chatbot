import streamlit as st
from langgraph_db_backend import chatBot,findThreads,deleteDb,createName
from langchain_core.messages import HumanMessage
import uuid

#******************UTILS********************

def generateThreadId():
    threadId = uuid.uuid4()
    return threadId

def resetChat():
    threadId = generateThreadId()
    st.session_state['threadId'] = threadId
    addThread(st.session_state['threadId'])
    st.session_state['message_history'] = []

def addThread(threadId):
    if threadId not in st.session_state['chatThreads']:
        st.session_state['chatThreads'].append(threadId)

def loadConversation(threadId):
    config = {'configurable' : {
    'thread_id' : threadId
    }}
    state = chatBot.get_state(config=config)

    return state.values.get('message',[])

# *************************************SESSION SETUP***********************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'threadId' not in st.session_state:
    st.session_state['threadId'] = generateThreadId()

if 'chatThreads' not in st.session_state:
    st.session_state['chatThreads'] = findThreads()

if 'chatTitles' not in st.session_state:
    st.session_state['chatTitles'] = {}

addThread(st.session_state['threadId'])

# ************************SIDEBAR UI******************************

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    resetChat()


st.sidebar.header('My conversations')

if st.sidebar.button('delete history'):
    deleteDb('chatbot.db')
    resetChat()
    st.session_state['chatThreads'] = []
    st.session_state['chatTitles'] = {}


for threadId in st.session_state['chatThreads'][::-1]:
    chatName = st.session_state['chatTitles'].get(threadId,str(threadId))
    if st.sidebar.button(chatName):
        st.session_state['threadId'] = threadId
        messages = loadConversation(threadId)

        tempMessage = []
        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            tempMessage.append({'role':role,'content':message.content})
        
        st.session_state['message_history'] = tempMessage



#******************************** MAIN UI *****************************************

CONFIG = {'configurable' : {
    'thread_id' : st.session_state['threadId']
}}


#************************** loading conversation history *****************************
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

userInput = st.chat_input("Type here ...")

if userInput:

    #add message to history
    st.session_state['message_history'].append({'role':'user','content':userInput})
    threadId = st.session_state['threadId']
    if threadId not in st.session_state['chatTitles']:
        st.session_state['chatTitles'][threadId] = createName(userInput)

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