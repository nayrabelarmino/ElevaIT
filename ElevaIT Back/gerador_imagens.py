import streamlit as st
import boto3
import requests
from bs4 import BeautifulSoup
import logging
import json
import base64
from io import BytesIO

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do cliente da IA
client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def chamada_api(prompt):
    logging.info("Chamando a API de IA para gerar imagem.")
    request = json.dumps({
        "text_prompts": [{"text":prompt,"weight":1}],
        "cfg_scale": 10,
        "steps": 50,
        "seed": 0,
        "width": 512,
        "height": 512,
        "samples": 1,
    })

    response = client.invoke_model(modelId="stability.stable-diffusion-xl-v1", body=request)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract the image data.
    base64_image_data = model_response["artifacts"][0]["base64"]

    imagem_bites = BytesIO(base64.b64decode(base64_image_data))

    return imagem_bites

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
    logging.info("Textos coletados:")
    for i, texto in enumerate(textos[:5]):  # Exibe os primeiros 5 textos no terminal
        logging.info(f"{i + 1}: {texto}")
    
    return textos

def gerar_imagens(mensagem):
    with image_spinner_placeholder:
        with st.spinner("Por favor aguarde enquanto sua imagem está sendo gerada..."):
            
            # Coleta de dados com base no tema fornecido
            dados_coletados = coletar_dados(mensagem)
            if not dados_coletados:
                st.session_state.imagem = None
                st.error("Desculpe, não foram encontradas informações relevantes na internet para o tema solicitado.")
                return

            # Limita a quantidade de dados para evitar sobrecarga
            dados_referencia = " ".join(dados_coletados[:10])  
            prompt_para_imagem = f"{mensagem}. Informações adicionais: {dados_referencia}"

            # Chamada à API com o prompt formatado
            response = chamada_api(prompt_para_imagem)
            st.session_state.imagem = response

st.set_page_config(page_title="Hackaton-SPTech")

if "imagem" not in st.session_state:
    st.session_state.imagem = ""

st.title("Hackaton-SPTech") 
st.markdown("Exemplo de aplicação de IA para geração de imagens com base em dados reais e atualizados.")

image_spinner_placeholder = st.empty()

if not st.session_state.imagem:
    with st.form('image_form'):
        text = st.text_area('Descreva sua imagem:', '')
        submitted = st.form_submit_button('Gerar imagem')
        if submitted:
            gerar_imagens(text)
            if st.session_state.imagem:
                st.image(st.session_state.imagem)
else:
    with st.form('image_form'):
        text = st.text_area('Descreva sua imagem:', '')
        submitted = st.form_submit_button('Gerar imagem')
        if submitted:
            gerar_imagens(text)
            if st.session_state.imagem:
                st.image(st.session_state.imagem)

image_spinner_placeholder = st.empty()
