import subprocess
import json
import time
import requests

# Carrega configurações
with open('/data/data/com.termux/files/home/storage/proj/MessagePx2/servidor/config.json') as f:
    cfg = json.load(f)

TOKEN = cfg['TOKEN']
CHAT_ID = cfg['CHAT_ID']
INTERVALO = 5  # segundos para teste

ultimo_id_telegram = None

def apagar_mensagem_anterior():
    global ultimo_id_telegram
    if ultimo_id_telegram:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
            requests.get(url, params={"chat_id": CHAT_ID, "message_id": ultimo_id_telegram}, timeout=5)
            print("Mensagem anterior apagada.")
        except:
            pass

def enviar_telegram(mensagem):
    global ultimo_id_telegram
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        resposta = requests.get(url, params={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}, timeout=10)
        dados = resposta.json()
        if dados.get('ok'):
            ultimo_id_telegram = dados['result']['message_id']
            print(f"Mensagem enviada ao Telegram (ID: {ultimo_id_telegram})")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def verificar_bateria():
    resultado = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
    return json.loads(resultado.stdout)

if __name__ == '__main__':
    print("Monitor de bateria via Telegram iniciado...")
    print(f"Atualizando a cada {INTERVALO} segundos")
    print("-" * 40)

    while True:
        try:
            dados = verificar_bateria()
            porcentagem = dados['percentage']
            status = dados['status']
            temperatura = dados['temperature']
            saude = dados.get('health', 'N/D')

            if status == 'CHARGING':
                emoji = '⚡'
            else:
                emoji = '🔋'

            mensagem = (
                f"{emoji} *Relatorio de Bateria*\n"
                f"────────────────────\n"
                f"📊 *Nivel:* {porcentagem}%\n"
                f"📈 *Status:* {status}\n"
                f"🌡 *Temperatura:* {temperatura}°C\n"
                f"💚 *Saude:* {saude}"
            )

            print(mensagem.replace('*', '').replace('\n', ' | '))
            apagar_mensagem_anterior()
            enviar_telegram(mensagem)

        except Exception as e:
            print(f"Erro: {e}")

        time.sleep(INTERVALO)
