import tempfile
from xml.dom.minidom import Document
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader, YoutubeLoader, CSVLoader, PyPDFLoader,TextLoader

def carrega_site(url):
    loader = WebBaseLoader(url)
    documentos = loader.load()
    documento_final = '\n\n'.join([doc.page_content for doc in documentos ])
    return documento_final

def carrega_youtube(url):
    loader = YoutubeLoader(url,add_video_info=False,language=['pt'])
    documentos = loader.load()
    documento_final = '\n\n'.join([doc.page_content for doc in documentos ])
    return documento_final

def carrega_csv(caminho):
    loader = CSVLoader(caminho)
    documentos = loader.load()
    documento_final = '\n\n'.join([doc.page_content for doc in documentos ])
    return documento_final

def carrega_pdf(caminho):
    loader = PyPDFLoader(caminho)
    documentos = loader.load()
    documento_final = '\n\n'.join([doc.page_content for doc in documentos ])
    return documento_final


def carrega_txt(caminho):
    loader = TextLoader(caminho)
    documentos = loader.load()
    documento_final = '\n\n'.join([doc.page_content for doc in documentos ])
    return documento_final

###################################################################
TIPOS_ARQUIVOS_VALIDOS = ['Site','Video Youtube','PDF','CSV','TXT']


CONFIG_MODELOS ={
                'Groq':
                        {'modelos':['gemma2-9b-it','llama-3.1-70b-versatile'],
                         'chat':ChatGroq},
                 'OpenAI':{'modelos':['gpt-4o-mini','gpt-4o','o1-preview'],
                           'chat':ChatOpenAI}
                 }

MEMORIA = ConversationBufferMemory()

def carrega_documentos(tipo_arquivo,arquivo):
    
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    if tipo_arquivo == 'Youtube':
        documento = carrega_youtube(arquivo)
    if tipo_arquivo == 'PDF':
        with tempfile.NamedTemporaryFile(suffix='.pdf',delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_pdf(nome_temp)
    if tipo_arquivo == 'CSV':
        with tempfile.NamedTemporaryFile(suffix='.csv',delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_csv(nome_temp)
    if tipo_arquivo == 'TXT':
        with tempfile.NamedTemporaryFile(suffix='.txt',delete=False) as temp:
            temp.write(arquivo.read())
            nome_temp = temp.name
        documento = carrega_txt(nome_temp)
    return documento


def carrega_modelo(provedor, modelo, api_key,tipo_arquivo, arquivo):
    if 'chat' not in st.session_state:
        st.session_state['chat'] = None

    documento = carrega_documentos(tipo_arquivo,arquivo)

    system_message ='''Você é um assistente amigável chamado Oráculo.
                        Você possui acesso às seguintes informações vindas 
                        de um documento {}: 

                        ####
                        {}
                        ####

                        Utilize as informações fornecidas para basear as suas respostas.

                        Sempre que houver $ na sua saída, substita por S.

                        Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
                        sugira ao usuário carregar novamente o Oráculo!'''.format(tipo_arquivo, documento)
    
    template  = ChatPromptTemplate.from_messages([
        ('system',system_message),
        ('placeholder','{chat_history}'),
        ('user','{input}')
        ])


    chat = CONFIG_MODELOS[provedor]['chat'](model=modelo, api_key=api_key)

    chain = template | chat
    st.session_state['chain'] = chain
    return



def pagina_chat():
    st.header('Bem-Vindo ao Oraculo 🤖') 

    chain = st.session_state.get('chain')
    if chain is None:
        st.error("Carregue o Oraculo")
        st.stop()


    memoria = st.session_state.get('memoria',MEMORIA)
    for mensagem in memoria.buffer_as_messages:
        chat = st.chat_message(mensagem.type) 
        chat.markdown(mensagem.content)
    

    input_usuario = st.chat_input('Fale com o Oraculo: ')
    if input_usuario:
        chat = st.chat_message('human')
        chat.markdown(input_usuario)

        chat = st.chat_message("ai")        
        resposta = chat.write_stream(chain.stream({
            'input': input_usuario,
            'chat_history': memoria.buffer_as_messages
            }))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        st.rerun()


def side_bar():
    tabs = st.tabs(['Upload de arquivos','Seleção de Modelos'])
    with tabs[0]:
        tipo_arquivo = st.selectbox('Selecione o tipo de arquivo',TIPOS_ARQUIVOS_VALIDOS)
        if tipo_arquivo == "Site":
            arquivo = st.text_input("Digite a URL do Site")
        if tipo_arquivo == "Video Youtube":
            arquivo = st.text_input("Digite a URL do Video")
        if tipo_arquivo == "PDF":
            arquivo = st.file_uploader("Faça o Upload do arquivo PDF", type=['.pdf'])
        if tipo_arquivo == "CSV":
            arquivo = st.file_uploader("Faça o Upload do arquivo PDF", type=['.csv'])
        if tipo_arquivo == "TXT":
            arquivo = st.file_uploader("Faça o Upload do arquivo PDF", type=['.txt'])
    with tabs[1]:
        provedor = st.selectbox('selecione o provedor dos modelos',CONFIG_MODELOS)
        modelo = st.selectbox('selecione o modelo',CONFIG_MODELOS[provedor]['modelos'])
        api_key = st.text_input(
            f'adcione a api key para o provedor {provedor}',
              value = st.session_state.get(f'api_key_{provedor}'))

        st.session_state[f'api_key_{provedor}'] = api_key

    if st.button('inicializar Oraculo',use_container_width=True):
        carrega_modelo(provedor,modelo,api_key,tipo_arquivo,arquivo)
    if st.button('Apagar historico',use_container_width=True):
        st.session_state['memoria'] = MEMORIA



def main():
    with st.sidebar:
        side_bar()
    pagina_chat()

    

if __name__ == '__main__':
    main()
