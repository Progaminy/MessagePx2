import subprocess
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Dados em memória
dados_bateria = {}
dados_localizacao = {"latitude": "N/D", "longitude": "N/D"}
ultima_atualizacao_loc = "Nunca"
sms_recebidas = []
sms_enviadas = []
alertas = []

def atualizar_localizacao():
    global dados_localizacao, ultima_atualizacao_loc
    while True:
        try:
            resultado = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=30)
            dados = json.loads(resultado.stdout)
            dados_localizacao = {
                "latitude": dados.get('latitude', 'N/D'),
                "longitude": dados.get('longitude', 'N/D')
            }
            ultima_atualizacao_loc = time.strftime('%d/%m/%Y %H:%M:%S')
        except:
            pass
        time.sleep(300)

def atualizar_bateria():
    global dados_bateria, alertas
    while True:
        try:
            bat = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
            dados_bateria = json.loads(bat.stdout)
            
            # Gera alerta
            alerta = {
                "porcentagem": dados_bateria['percentage'],
                "status": dados_bateria['status'],
                "temperatura": dados_bateria['temperature'],
                "latitude": dados_localizacao.get('latitude', 'N/D'),
                "longitude": dados_localizacao.get('longitude', 'N/D'),
                "data": time.strftime('%d/%m/%Y %H:%M:%S')
            }
            alertas.insert(0, alerta)
            if len(alertas) > 20:
                alertas.pop()
        except:
            pass
        time.sleep(5)

class API(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/recebidas':
            self.responder(sms_recebidas)
        elif self.path == '/api/enviadas':
            self.responder(sms_enviadas)
        elif self.path == '/api/alertas':
            self.responder(alertas)
        elif self.path == '/api/tudo':
            self.responder({
                "recebidas": sms_recebidas,
                "enviadas": sms_enviadas,
                "alertas": alertas,
                "localizacao": dados_localizacao
            })
        else:
            self.send_response(404)
            self.end_headers()
    
    def responder(self, dados):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(dados).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print("API do MessagePx2 rodando na porta 8081")
    
    threading.Thread(target=atualizar_localizacao, daemon=True).start()
    threading.Thread(target=atualizar_bateria, daemon=True).start()
    
    HTTPServer(('127.0.0.1', 8081), API).serve_forever()
