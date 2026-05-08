import subprocess
import json
import time
import smtplib
import imaplib
from email.mime.text import MIMEText

# Carrega configurações
with open('/data/data/com.termux/files/home/storage/proj/MessagePx2/servidor/config.json') as f:
    cfg = json.load(f)

EMAIL = cfg['EMAIL']
SENHA = cfg['SENHA']
INTERVALO = 300  # 5 minutos

def apagar_email_anterior():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(EMAIL, SENHA.replace(' ', ''))
        mail.select('"[Gmail]/Sent Mail"')
        status, mensagens = mail.search(None, 'SUBJECT "Relatorio de SMS"')
        if mensagens[0]:
            ids = mensagens[0].split()
            for id_email in ids:
                mail.store(id_email, '+FLAGS', '\\Deleted')
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
        print(f"Email enviado: {assunto}")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def pegar_sms(tipo, limite=5):
    """Tenta ler SMS. Se falhar, retorna lista vazia."""
    try:
        resultado = subprocess.run(
            ['termux-sms-list', '-t', tipo, '-l', str(limite)],
            capture_output=True,
            text=True,
            timeout=10
        )
        saida = resultado.stdout.strip()
        
        if not saida:
            return []
        
        dados = json.loads(saida)
        
        # Se for um dicionário com erro, retorna vazio
        if isinstance(dados, dict) and 'error' in dados:
            return []
        
        # Se for uma lista, retorna
        if isinstance(dados, list):
            return dados
        
        return []
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Erro ao pegar SMS ({tipo}): {e}")
        return []

if __name__ == '__main__':
    print("=" * 50)
    print("RELATORIO DE SMS POR EMAIL")
    print("=" * 50)
    print(f"Intervalo: {INTERVALO}s (5 min)")
    print("-" * 50)

    while True:
        try:
            recebidas = pegar_sms('inbox', 5)
            enviadas = pegar_sms('sent', 5)

            if not recebidas and not enviadas:
                print("Nenhuma SMS encontrada ou sem permissao.")
            else:
                relatorio = "📱 RELATORIO DE SMS\n"
                relatorio += "═" * 30 + "\n\n"

                relatorio += "📥 RECEBIDAS:\n"
                relatorio += "─" * 20 + "\n"
                if recebidas:
                    for msg in recebidas[:5]:
                        numero = msg.get('number', msg.get('address', '?'))
                        texto = msg.get('body', msg.get('msg', '?'))
                        relatorio += f"De: {numero}\n"
                        relatorio += f"Msg: {str(texto)[:50]}\n"
                        relatorio += "─" * 10 + "\n"
                else:
                    relatorio += "Nenhuma\n"
                    relatorio += "─" * 10 + "\n"

                relatorio += "\n📤 ENVIADAS:\n"
                relatorio += "─" * 20 + "\n"
                if enviadas:
                    for msg in enviadas[:5]:
                        numero = msg.get('number', msg.get('address', '?'))
                        texto = msg.get('body', msg.get('msg', '?'))
                        relatorio += f"Para: {numero}\n"
                        relatorio += f"Msg: {str(texto)[:50]}\n"
                        relatorio += "─" * 10 + "\n"
                else:
                    relatorio += "Nenhuma\n"
                    relatorio += "─" * 10 + "\n"

                print(relatorio)
                apagar_email_anterior()
                enviar_email("Relatorio de SMS", relatorio)

        except Exception as e:
            print(f"Erro geral: {e}")

        time.sleep(INTERVALO)
