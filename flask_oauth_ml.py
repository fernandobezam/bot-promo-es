import json
import requests
from flask import Flask, request, redirect

# 🔑 Coloque aqui suas credenciais do Mercado Livre Developers
APP_ID = "4617853811180461"   # Seu App ID
SECRET_KEY = "IGW8CS63levVzZCkGXD8jQGYBn36eaec"  # Sua chave secreta
REDIRECT_URI = "http://localhost:5000/callback"

app = Flask(__name__)

@app.route("/")
def home():
    auth_url = (
        f"https://auth.mercadolivre.com.br/authorization"
        f"?response_type=code&client_id={APP_ID}&redirect_uri={REDIRECT_URI}"
    )
    return f"<a href='{auth_url}'>Clique aqui para autorizar o app no Mercado Livre</a>"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Erro: nenhum code recebido."

    # Troca o code pelo token
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

    # Salva em tokens.json
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)

    return f"Tokens salvos com sucesso em tokens.json ✅<br>{tokens}"

if __name__ == "__main__":
    app.run(port=5000, debug=True)
