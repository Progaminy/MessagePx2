import subprocess
import requests
import time
import re
import threading
import json
import base64

# Carrega configurações
with open('/data/data/com.termux/files/home/storage/proj/MessagePx2/guardiao/config.json') as f:
    cfg = json.load(f)

TOKEN = cfg['TOKEN']
CHAT_ID = cfg['CHAT_ID']
GITHUB_TOKEN = "COLE_SEU_TOKEN_GITHUB_AQUI"
GITHUB_REPO = "Progaminy/MessagePx2"

ultima_url = ""

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": mensagem}, timeout=10)
        print(f"Telegram: {mensagem[:50]}...")
    except:
        pass

def extrair_url(texto):
    match = re.search(r'https://[a-zA-Z0-9.-]+\.serveousercontent\.com', texto)
    return match.group(0) if match else None

def atualizar_github(nova_url):
    try:
        url_api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/server_api_url.txt"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        resposta = requests.get(url_api, headers=headers, timeout=10)
        dados = resposta.json()
        sha = dados.get('sha', '')
        conteudo = base64.b64encode(nova_url.encode()).decode()
        body = {"message": "Atualizar URL da API", "content": conteudo, "sha": sha}
        requests.put(url_api, headers=headers, json=body, timeout=10)
        print(f"GitHub atualizado: {nova_url}")
    except:
        pass

def manter_tunel_vivo(url):
    while True:
        try:
            r = requests.get(url, timeout=10)
            print(f" Ping API: {r.status_code}")
        except:
            print(" Ping API falhou")
        time.sleep(15)

def iniciar_tunel():
    global ultima_url
    processo = subprocess.Popen(
        ['autossh', '-M', '0',
         '-o', 'ServerAliveInterval=30',
         '-o', 'ServerAliveCountMax=3',
         '-R', '80:localhost:8081', 'serveo.net'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for linha in processo.stdout:
        url = extrair_url(linha)
        if url and url != ultima_url:
            ultima_url = url
            print(f"\n✅ URL da API: {url}")
            atualizar_github(url)
            enviar_telegram(f"📡 API MessagePx2 ativa:\n{url}")
            threading.Thread(target=manter_tunel_vivo, args=(url,), daemon=True).start()
        else:
            print(linha.strip())

if __name__ == '__main__':
    print("=" * 50)
    print("GUARDIÃO API - Porta 8081")
    print("=" * 50)
    enviar_telegram("🟢 API MessagePx2 iniciada.")
    while True:
        try:
            iniciar_tunel()
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)
