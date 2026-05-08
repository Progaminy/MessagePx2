import subprocess
import requests
import time
import re
import threading
import os
import base64

# CONFIGURE AQUI
TOKEN = "8557708504:AAG2hnmS81MzE4Dj3wscfBIa6gc8hfJS6Yw"
CHAT_ID = "7756976956"
GITHUB_TOKEN = "COLE_SEU_TOKEN_GITHUB_AQUI"
GITHUB_REPO = "Progaminy/MessagePx2"
# ------------------

ultima_url = ""

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": mensagem}, timeout=10)
        print(f"Telegram: {mensagem[:50]}...")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def extrair_url(texto):
    match = re.search(r'https://[a-zA-Z0-9.-]+\.serveousercontent\.com', texto)
    return match.group(0) if match else None

def atualizar_github(nova_url):
    """Atualiza o arquivo server_url.txt no GitHub"""
    try:
        # 1. Pega o conteúdo atual do arquivo
        url_api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/server_url.txt"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        resposta = requests.get(url_api, headers=headers, timeout=10)
        dados = resposta.json()
        sha = dados.get('sha', '')
        
        # 2. Atualiza o arquivo com a nova URL
        conteudo = base64.b64encode(nova_url.encode()).decode()
        
        body = {
            "message": "Atualizar URL do servidor SMS",
            "content": conteudo,
            "sha": sha
        }
        
        requests.put(url_api, headers=headers, json=body, timeout=10)
        print(f"GitHub atualizado: {nova_url}")
    except Exception as e:
        print(f"Erro ao atualizar GitHub: {e}")

def manter_tunel_vivo(url):
    while True:
        try:
            r = requests.get(url, timeout=10)
            print(f" Ping SMS: {r.status_code}")
        except:
            print(" Ping SMS falhou")
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
            print(f"\n✅ Nova URL: {url}")
            
            # 1. Atualiza o GitHub (principal)
            atualizar_github(url)
            
            # 2. Envia ao Telegram (backup)
            enviar_telegram(f"📥 Link do servidor SMS:\n{url}")
            
            # 3. Mantém o túnel vivo
            threading.Thread(target=manter_tunel_vivo, args=(url,), daemon=True).start()
        else:
            print(linha.strip())

if __name__ == '__main__':
    print("=" * 50)
    print("GUARDIÃO SMS - Atualização Automática")
    print("=" * 50)
    print(f"Repositório: {GITHUB_REPO}")
    print("-" * 50)
    
    enviar_telegram("🟢 Guardião SMS iniciado.")
    
    while True:
        try:
            iniciar_tunel()
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)
