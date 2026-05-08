import subprocess
import json
import time
import smtplib
import imaplib
from email.mime.text import MIMEText

with open('/data/data/com.termux/files/home/storage/proj/MessagePx2/servidor/config.json') as f:
    cfg = json.load(f)

EMAIL = cfg['EMAIL']
SENHA = cfg['SENHA']
INTERVALO = 5

def apagar_email_anterior():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(EMAIL, SENHA.replace(' ', ''))
        mail.select('"[Gmail]/Sent Mail"')
        status, mensagens = mail.search(None, 'SUBJECT "Alerta de Bateria"')
        if mensagens[0]:
            ids = mensagens[0].split()
            mail.store(ids[-1], '+FLAGS', '\\Deleted')
            mail.expunge()
            print("Email anterior apagado.")
        mail.logout()
    except Exception as e:
        print(f"Erro ao apagar: {e}")

def enviar_email(assunto, mensagem):
    try:
        msg = MIMEText(mensagem)
        msg['Subject'] = assunto
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL, SENHA.replace(' ', ''))
        server.sendmail(EMAIL, EMAIL, msg.as_string())
        server.quit()
        print(f"Email enviado para {EMAIL}")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def pegar_localizacao():
    try:
        with open('/data/data/com.termux/files/home/storage/proj/MessagePx2/servidor/localizacao_cache.json') as f:
            dados = json.load(f)
        return dados.get('latitude', 'N/D'), dados.get('longitude', 'N/D')
    except:
        return 'N/D', 'N/D'

def verificar_bateria():
    resultado = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
    return json.loads(resultado.stdout)

if __name__ == '__main__':
    print("Monitor de bateria via Email iniciado...")
    print(f"Email a cada {INTERVALO} segundos")
    print("-" * 40)

    while True:
        try:
            dados = verificar_bateria()
            lat, lon = pegar_localizacao()
            
            porcentagem = dados['percentage']
            status = dados['status']
            temperatura = dados['temperature']
            saude = dados.get('health', 'N/D')

            mensagem = (
                f"Relatorio de Bateria\n"
                f"====================\n"
                f"Nivel: {porcentagem}%\n"
                f"Status: {status}\n"
                f"Temperatura: {temperatura}°C\n"
                f"Saude: {saude}\n"
                f"----------------------\n"
                f"📍 Localizacao\n"
                f"Latitude: {lat}\n"
                f"Longitude: {lon}"
            )

            print(mensagem.replace('\n', ' | '))
            apagar_email_anterior()
            enviar_email("Alerta de Bateria", mensagem)

        except Exception as e:
            print(f"Erro: {e}")

        time.sleep(INTERVALO)
