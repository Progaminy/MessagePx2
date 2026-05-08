import subprocess
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configurações
INTERVALO_LOC = 300  # 5 minutos entre atualizações de GPS

# Dados em memória
dados_bateria = {}
dados_localizacao = {"latitude": "N/D", "longitude": "N/D"}
ultima_atualizacao_loc = "Nunca"

def atualizar_localizacao():
    """Atualiza a localização a cada INTERVALO_LOC segundos"""
    global dados_localizacao, ultima_atualizacao_loc
    while True:
        try:
            resultado = subprocess.run(
                ['termux-location'],
                capture_output=True,
                text=True,
                timeout=30
            )
            dados = json.loads(resultado.stdout)
            dados_localizacao = {
                "latitude": dados.get('latitude', 'N/D'),
                "longitude": dados.get('longitude', 'N/D'),
                "altitude": dados.get('altitude', 'N/D'),
                "velocidade": dados.get('speed', 'N/D'),
                "precisao": dados.get('accuracy', 'N/D')
            }
            ultima_atualizacao_loc = time.strftime('%d/%m/%Y %H:%M:%S')
            print(f"📍 Localização atualizada: {dados_localizacao['latitude']}, {dados_localizacao['longitude']}")
        except subprocess.TimeoutExpired:
            print("📍 GPS timeout. Verifique se o aparelho tem sinal.")
        except Exception as e:
            print(f"📍 Erro no GPS: {e}")
        
        time.sleep(INTERVALO_LOC)

class MeuServidor(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Atualiza bateria
            bat = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
            dados_bateria = json.loads(bat.stdout)
            
            # Dados da localização
            lat = dados_localizacao.get('latitude', 'N/D')
            lon = dados_localizacao.get('longitude', 'N/D')
            alt = dados_localizacao.get('altitude', 'N/D')
            prec = dados_localizacao.get('precisao', 'N/D')
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <title>Pxp - Painel</title>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <style>
                    body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 10px; margin: 0; }}
                    h1 {{ color: #00ff88; text-align: center; font-size: 20px; }}
                    .card {{ background: #2a2a2a; padding: 15px; border-radius: 10px; margin: 10px 0; }}
                    .card h2 {{ margin-top: 0; font-size: 18px; }}
                    .info {{ color: #aaa; font-size: 11px; }}
                    .valor {{ font-size: 24px; font-weight: bold; color: #00ff88; }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
                    #mapa {{ height: 300px; border-radius: 12px; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <h1>📡 Pxp - Painel do Servidor</h1>
                
                <div class="card">
                    <h2>🔋 Bateria</h2>
                    <p><span class="valor">{dados_bateria['percentage']}%</span></p>
                    <p>Status: {dados_bateria['status']}</p>
                    <p>Temperatura: {dados_bateria['temperature']}°C</p>
                </div>
                
                <div class="card">
                    <h2>📍 Localização</h2>
                    <div class="grid">
                        <div>
                            <p style="font-size:12px;color:#aaa">Latitude</p>
                            <p style="font-size:16px;font-weight:bold">{lat}</p>
                        </div>
                        <div>
                            <p style="font-size:12px;color:#aaa">Longitude</p>
                            <p style="font-size:16px;font-weight:bold">{lon}</p>
                        </div>
                        <div>
                            <p style="font-size:12px;color:#aaa">Altitude</p>
                            <p>{alt}m</p>
                        </div>
                        <div>
                            <p style="font-size:12px;color:#aaa">Precisão</p>
                            <p>{prec}m</p>
                        </div>
                    </div>
                    <div id="mapa"></div>
                    <p class="info" style="margin-top:10px">🕐 Atualizado: {ultima_atualizacao_loc}</p>
                </div>
                
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <script>
                    var lat = {lat};
                    var lon = {lon};
                    if (lat !== 'N/D' && lon !== 'N/D') {{
                        var mapa = L.map('mapa').setView([lat, lon], 15);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: '© OpenStreetMap'
                        }}).addTo(mapa);
                        L.marker([lat, lon]).addTo(mapa)
                            .bindPopup('📍 Você está aqui')
                            .openPopup();
                    }} else {{
                        document.getElementById('mapa').innerHTML = '<p style="text-align:center;color:#888;padding:50px">📍 Aguardando localização...</p>';
                    }}
                </script>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    print("=" * 50)
    print("📡 PXP - PAINEL DO SERVIDOR")
    print("=" * 50)
    print(f"📍 Localização a cada {INTERVALO_LOC}s (5 min)")
    
    # Inicia thread do GPS
    thread_gps = threading.Thread(target=atualizar_localizacao, daemon=True)
    thread_gps.start()
    
    # Inicia servidor web
    servidor = HTTPServer(('127.0.0.1', 8080), MeuServidor)
    print('Servidor rodando em http://127.0.0.1:8080')
    print("-" * 50)
    
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor encerrado.')
