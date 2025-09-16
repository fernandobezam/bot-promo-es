import requests
import asyncio
import json
import io
import os
from telegram import Bot

# --- CREDENCIAIS TELEGRAM ---
TELEGRAM_TOKEN = "SEU_TOKEN_BOT"
CHAT_ID = "-1002988443967"

# --- CREDENCIAIS MERCADO LIVRE ---
CLIENT_ID = "4617853811180461"
CLIENT_SECRET = "IGW8CS63levVzZCkGXD8jQGYBn36eaec"
TOKEN_FILE = "tokens.json"   # gerado pelo flask_oauth_ml.py

# -------------------- FUNÇÕES AUXILIARES --------------------

def load_tokens():
    """Carrega tokens do arquivo JSON"""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Arquivo tokens.json não encontrado. Rode primeiro o flask_oauth_ml.py para gerar os tokens.")
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def save_tokens(tokens):
    """Salva tokens no arquivo JSON"""
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def refresh_tokens():
    """Atualiza access_token usando refresh_token"""
    tokens = load_tokens()
    refresh_token = tokens.get("refresh_token")

    url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }

    r = requests.post(url, data=data)
    r.raise_for_status()
    new_tokens = r.json()
    save_tokens(new_tokens)
    print("🔄 Tokens atualizados com sucesso!")
    return new_tokens

def get_access_token():
    """Garante que temos um access_token válido"""
    tokens = load_tokens()
    return tokens.get("access_token")

# -------------------- MERCADO LIVRE --------------------

def get_products_from_mercadolivre(keyword):
    """
    Busca produtos no Mercado Livre usando access_token
    """
    tokens = load_tokens()
    access_token = tokens.get("access_token")

    url = f"https://api.mercadolibre.com/sites/MLB/search?q={keyword}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "MeuBotPromocoes/1.0",
        "Accept": "application/json"
    }

    r = requests.get(url, headers=headers)

    # Se o token expirou → renovar e tentar de novo
    if r.status_code == 401:
        print("⚠️ Access token expirado. Atualizando...")
        tokens = refresh_tokens()
        access_token = tokens.get("access_token")
        headers["Authorization"] = f"Bearer {access_token}"
        r = requests.get(url, headers=headers)

    r.raise_for_status()
    data = r.json()

    products = []
    if "results" in data:
        for item in data["results"][:5]:  # pega só 5 primeiros para teste
            products.append({
                "title": item.get("title", "Produto sem nome"),
                "price": f"R$ {item.get('price', 0):.2f}",
                "link": item.get("permalink", ""),
                "image_url": item.get("thumbnail", "")
            })
    return products

# -------------------- TELEGRAM --------------------

async def send_product_to_telegram(product):
    """Envia produto para Telegram (com foto ou só texto)"""
    bot = Bot(token=TELEGRAM_TOKEN)

    caption = (
        f"🔥 {product['title']}\n"
        f"💰 Preço: {product['price']}\n\n"
        f"🔗 [Clique aqui para conferir]({product['link']})"
    )

    try:
        if product.get("image_url"):
            img = requests.get(product["image_url"], stream=True)
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=io.BytesIO(img.content),
                caption=caption,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=caption,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        print(f"✔ Produto enviado: {product['title']}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

# -------------------- MAIN --------------------

async def main():
    print("🚀 Bot iniciado...")
    products = get_products_from_mercadolivre("pc gamer")

    if products:
        for product in products:
            await send_product_to_telegram(product)
            await asyncio.sleep(2)
    else:
        print("Nenhum produto encontrado.")

if __name__ == "__main__":
    asyncio.run(main())
