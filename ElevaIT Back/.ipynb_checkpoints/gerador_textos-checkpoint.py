import streamlit as st
import boto3
import requests
from bs4 import BeautifulSoup
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do cliente da IA
client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def chamada_api(prompt):
    logging.info("Chamando a API de IA para gerar texto.")
    response = client.converse(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=prompt,
        inferenceConfig={"maxTokens":2048, "stopSequences":["\n\nHuman:"], "temperature":1, "topP":1},
        additionalModelRequestFields={"top_k":250}
    )
    response_text = response["output"]["message"]["content"][0]["text"]
    logging.info("Resposta recebida da API.")
    return response_text

def coletar_dados(tema):
    logging.info(f"Iniciando coleta de dados para o tema: {tema}")
    url = f"https://www.google.com/search?q={tema.replace(' ', '+')}&hl=pt-BR"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    textos = []
    for element in soup.find_all(['h3', 'p', 'span']):
        if element.text.strip():
            textos.append(element.text.strip())
    
    logging.info(f"Número de textos coletados: {len(textos)}")
    logging.info(f"Textos coletados: {textos[:10]}...")  # Loga os primeiros 10 textos
    
    return textos

def gerar_textos(mensagem):
    st.session_state.mensagem = ""
    st.session_state.imagem = ""

    with text_spinner_placeholder:
        with st.spinner("Por favor aguarde enquanto sua mensagem está sendo gerada..."):
            system_prompt = """
            Você é uma IA assistente que ajuda funcionários a escrever legendas para publicações em redes sociais, emails para a rede corporativa e mensagem de newsletter da empresa.
 
            Você é especialista em comunicação corporativa e é muito criativa.

            Você receberá uma solicitação de um usuário e deverá responder a essa solicitação.

            Você estará auxiliando funcionários da instituição Inova Lopez. Uma instituição do governo focada na promoção de tecnologias emergentes e inovação digital. Seu objetivo é facilitar a transformação digital de órgãos públicos e oferecer suporte para startups e pequenas empresas de tecnologia.
 
            A solicitação do usuário estará dentro das tags <text></text>.
 
            Você deve seguir padrões de ética da sociedade, evitando assuntos como política, raça e qualquer outro que seja muito pessoal.
 
            Nas suas respostas, siga como exemplo os padrões de boas práticas ESG.

            Se não conseguir encontrar uma resposta para o que o usuário solicitou, não invente uma resposta, nem mude o foco na resposta, peça ao usuário que enriqueça o pedido com mais detalhes.

            Limite sua mensagem apenas ao canal de comunicação escolhido pelo usuário.
            """

            # Coleta de dados com base no tema fornecido
            dados_coletados = coletar_dados(mensagem)
            if not dados_coletados:
                st.session_state.mensagem = "Desculpe, não foram encontradas informações relevantes na internet para o tema solicitado."
                return

            # Limita a quantidade de dados para evitar sobrecarga
            dados_referencia = "\n".join(dados_coletados[:2000])  
            input_prompt = f"{system_prompt} \n\nHuman: <text>{mensagem}</text> \n\nTema: {tema}\nTipo de comunicação: {tipo_comunicacao}\nCanal de comunicação: {canal_comunicacao} \nInformações Reais Coletadas: {dados_referencia}\n\nAssistant:"

            # Chamada à API com o prompt formatado
            conversation = [
                {
                    "role": "user",
                    "content": [{"text": input_prompt}],
                }
            ]

            response = chamada_api(conversation)
            st.session_state.mensagem = response

st.set_page_config(page_title="Hackaton-SPTech")

if "mensagem" not in st.session_state:
    st.session_state.mensagem = ""

st.title("Hackaton-SPTech") 
st.markdown("Exemplo de aplicação de IA para geração de textos com base em dados reais e atualizados.")

text_spinner_placeholder = st.empty()

with st.form('message_form'):
    text = st.text_area('Escreva sua mensagem:', '')
    tema = st.text_input('Tema:', '')
    objetivo_da_publicacao = st.text_input('Objetivo da publicação:', '')
    tipo_comunicacao = st.text_input('Tipo de comunicação:', '')
    canal_comunicacao = st.selectbox('Canal de comunicação:', ['Instagram', 'LinkedIn', 'Email', 'Newsletter'])
    submitted = st.form_submit_button('Gerar texto')
    if submitted:
        gerar_textos(text)

if st.session_state.mensagem:
    st.markdown("""---""")
    st.text_area(label="Resposta:", value=st.session_state.mensagem, height=500)

image_spinner_placeholder = st.empty()