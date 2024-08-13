import streamlit as st
import boto3
import requests
from bs4 import BeautifulSoup
import logging
import io
import base64
from gtts import gTTS
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    logging.info(f"Textos coletados: {textos[:5]}...")  # Loga os primeiros 5 textos
    
    return textos

def gerar_textos(mensagem):
    st.session_state.mensagem = ""
    st.session_state.audio_base64 = ""

    with text_spinner_placeholder:
        with st.spinner("Por favor aguarde enquanto sua mensagem está sendo gerada..."):
            system_prompt = """
            Você é um assistente de IA que está ajudando um usuário a gerar legendas para publicações em redes sociais ou até emails para a rede corporativa.
 
            Você receberá uma solicitação de um usuário e deverá responder a essa solicitação.
 
            A solicitação do usuário estará dentro das tags <text></text>.
 
            Você é especialista em comunicação corporativa e é muito criativa.
 
            Você deve seguir padrões de ética da sociedade, evitando assuntos como política, raça e qualquer outro que seja muito pessoal.
 
            Nas suas respostas, siga como exemplo os padrões de boas práticas ESG
            """

            # Coleta de dados com base no tema fornecido
            dados_coletados = coletar_dados(mensagem)
            if not dados_coletados:
                st.session_state.mensagem = "Desculpe, não foram encontradas informações relevantes na internet para o tema solicitado."
                return

            # Limita a quantidade de dados para evitar sobrecarga
            dados_referencia = "\n".join(dados_coletados[:2000])  
            input_prompt = f"{system_prompt} \n\nHuman: <text>{mensagem}</text> \nInformações Reais Coletadas: {dados_referencia}\n\nAssistant:"

            # Chamada à API com o prompt formatado
            conversation = [
                {
                    "role": "user",
                    "content": [{"text": input_prompt}],
                }
            ]

            response = chamada_api(conversation)
            st.session_state.mensagem = response

            # Convertendo o texto em áudio usando gTTS
            try:
                tts = gTTS(text=response, lang='pt')
                audio_stream = io.BytesIO()
                tts.write_to_fp(audio_stream)
                audio_stream.seek(0)
                st.session_state.audio_base64 = base64.b64encode(audio_stream.read()).decode()
            except Exception as e:
                logging.error(f"Erro ao converter texto em áudio: {e}")

# Configuração do agendador
scheduler = BackgroundScheduler()
scheduler.start()

# Função para agendar postagens
def agendar_postagem(data_hora, func, *args):
    scheduler.add_job(func, 'date', run_date=data_hora, args=args)
    st.success(f"Postagem agendada para {data_hora}.")

# LinkedIn: Autenticação e Postagem
def postar_linkedin(mensagem):
    st.info("Postando no LinkedIn...")
    # Aqui você adiciona o código de autenticação e postagem usando LinkedIn API

# Instagram: Postagem
def postar_instagram(imagem_path, mensagem):
    st.info("Postando no Instagram...")
    # Aqui você adiciona o código de autenticação e postagem usando Instagram API

# Outlook: Envio de E-mail
def enviar_email_outlook(destinatario, assunto, corpo):
    st.info("Enviando e-mail via Outlook...")
    
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "elevait.oficial@outlook.com"  # Substitua pelo seu e-mail do Outlook
    sender_password = "#TecladoNumerico69!"  # Substitua pela sua senha do Outlook
    
    try:
        # Configuração do objeto MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Corpo do e-mail
        msg.attach(MIMEText(corpo, 'plain'))
        
        # Configuração do servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Inicia a conexão TLS
        server.login(sender_email, sender_password)  # Faz o login no servidor
        text = msg.as_string()
        server.sendmail(sender_email, destinatario, text)  # Envia o e-mail
        server.quit()
        
        st.success("E-mail enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o e-mail: {e}")
        logging.error(f"Erro ao enviar o e-mail: {e}")

# Newsletter: Envio
def enviar_newsletter(assinantes, assunto, corpo):
    st.info("Enviando newsletter...")
    for destinatario in assinantes:
        enviar_email_outlook(destinatario.strip(), assunto, corpo)

st.set_page_config(page_title="ElevateIT")

if "mensagem" not in st.session_state:
    st.session_state.mensagem = ""
if "audio_base64" not in st.session_state:
    st.session_state.audio_base64 = ""

st.title("Hackaton-SPTech") 
st.markdown("Exemplo de aplicação de IA para geração de textos com base em dados reais e atualizados.")

text_spinner_placeholder = st.empty()

with st.form('message_form'):
    text = st.text_area('Escreva sua mensagem:', '')
    submitted = st.form_submit_button('Gerar texto')
    if submitted:
        gerar_textos(text)

if st.session_state.mensagem:
    st.markdown(f"**Texto Gerado:**\n\n{st.session_state.mensagem}")

    if st.session_state.audio_base64:
        audio_html = f'<audio controls><source src="data:audio/mpeg;base64,{st.session_state.audio_base64}" type="audio/mpeg"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    
    # Formulário para agendar postagem ou envio de e-mails
    with st.form('schedule_form'):
        plataformas = st.multiselect('Selecione as plataformas:', ['LinkedIn', 'Instagram', 'E-mail (Outlook)', 'Newsletter'])
        data_hora = st.date_input('Data de Publicação:')
        hora = st.time_input('Hora de Publicação:')
        destinatario_email = st.text_input('Destinatário (para e-mails):')
        assunto_email = st.text_input('Assunto (para e-mails):')
        destinatarios_newsletter = st.text_area('Assinantes da Newsletter (separados por vírgula):')
        enviar_agora = st.checkbox('Enviar Agora')
        
        if st.form_submit_button('Agendar'):
            data_hora_publicacao = datetime.datetime.combine(data_hora, hora)
            if enviar_agora:
                data_hora_publicacao = datetime.datetime.now()
            
            for plataforma in plataformas:
                if plataforma == 'LinkedIn':
                    agendar_postagem(data_hora_publicacao, postar_linkedin, st.session_state.mensagem)
                elif plataforma == 'Instagram':
                    # Precisa de uma imagem para o Instagram
                    agendar_postagem(data_hora_publicacao, postar_instagram, "caminho_para_imagem.jpg", st.session_state.mensagem)
                elif plataforma == 'E-mail (Outlook)':
                    agendar_postagem(data_hora_publicacao, enviar_email_outlook, destinatario_email, assunto_email, st.session_state.mensagem)
                elif plataforma == 'Newsletter':
                    lista_destinatarios = destinatarios_newsletter.split(',')
                    agendar_postagem(data_hora_publicacao, enviar_newsletter, lista_destinatarios, assunto_email, st.session_state.mensagem)
