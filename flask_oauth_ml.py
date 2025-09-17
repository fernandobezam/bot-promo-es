import json
import requests
import os  # 1. Importamos a biblioteca OS
from flask import Flask, request

# 🔑 Suas credenciais agora são lidas das Variáveis de Ambiente do Render
#    Os nomes aqui (ex: 'ML_CLIENT_ID') devem ser EXATAMENTE os mesmos que você usou no Render.
APP_ID = os.getenv('ML_CLIENT_ID')
SECRET_KEY = os.getenv('ML_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

app = Flask(__name__)

@app.route("/")
def home():
    # O restante do código não precisa de nenhuma alteração
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code&client_id={APP_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=read%20offline_access" # Adicionado escopos para garantir
    )
    return f"<h2>Bot Mercado Livre</h2><br><a href='{auth_url}'>Clique aqui para autorizar o app no Mercado Livre</a>"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Erro: nenhum code recebido."

    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": APP_ID,
        "client_secret": SECRET_KEY,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    r = requests.post(token_url, data=payload)
    if r.status_code != 200:
        return f"Erro ao pegar tokens: {r.text}"

    tokens = r.json()

    # Este código salva o tokens.json DENTRO do ambiente do Render,
    # então você precisa copiar a resposta da tela.
    # Em um app real, você salvaria isso em um banco de dados.
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)

    return f"✅ Tokens salvos com sucesso!<br><pre>{json.dumps(tokens, indent=4)}</pre>"

if __name__ == "__main__":
    # 2. Modificação para ser compatível com o Render
    #    Ele vai pegar a porta da variável de ambiente PORT, que o Render define automaticamente.
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
