from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import requests
from bs4 import BeautifulSoup
import logging
import json
import base64
from io import BytesIO

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicialização do Flask
app = Flask(__name__)
CORS(app)  # Ativar CORS para todos os endpoints

# Configuração do cliente da IA
client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def chamada_api_texto(prompt):
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

def chamada_api_imagem(prompt):
    logging.info("Chamando a API de IA para gerar imagem.")
    request = json.dumps({
        "text_prompts": [{"text":prompt,"weight":1}],
        "cfg_scale": 20,
        "steps": 150,
        "seed": 23,
        "width": 768,
        "height": 768,
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

@app.route('/generate-text', methods=['POST'])
def gerar_textos():
    data = request.json
    mensagem = data.get("mensagem")
    
    if not mensagem:
        return jsonify({"error": "Mensagem não fornecida"}), 400

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
        return jsonify({"mensagem": "Desculpe, não foram encontradas informações relevantes na internet para o tema solicitado."})

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

    response = chamada_api_texto(conversation)

    return jsonify({"mensagem": response})

@app.route('/generate-image', methods=['POST'])
def gerar_imagens():
    data = request.json
    mensagem = data.get("mensagem")
    
    if not mensagem:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    with app.app_context():
        # Coleta de dados com base no tema fornecido
        dados_coletados = coletar_dados(mensagem)
        if not dados_coletados:
            return jsonify({"error": "Desculpe, não foram encontradas informações relevantes na internet para o tema solicitado."}), 400

        # Limita a quantidade de dados para evitar sobrecarga
        dados_referencia = " ".join(dados_coletados[:20000])  
        prompt_para_imagem = f"{mensagem}. Informações adicionais: {dados_referencia}"

        # Chamada à API com o prompt formatado
        imagem_bites = chamada_api_imagem(prompt_para_imagem)
        imagem_base64 = base64.b64encode(imagem_bites.getvalue()).decode('utf-8')

        return jsonify({"imagem_base64": imagem_base64})

if __name__ == '__main__':
    app.run(debug=True)
