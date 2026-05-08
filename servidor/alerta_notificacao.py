import subprocess
import json
import time

INTERVALO = 5  # segundos para teste

def notificar_bateria(titulo, mensagem):
    try:
        subprocess.run([
            'termux-notification',
            '--id', 'bateria-alerta',
            '--title', titulo,
            '--content', mensagem,
            '--priority', 'high'
        ], timeout=10)
        print("Notificacao atualizada.")
    except Exception as e:
        print(f"Erro na notificacao: {e}")

def verificar_bateria():
    resultado = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
    return json.loads(resultado.stdout)

if __name__ == '__main__':
    print("Monitor de bateria via Notificacao iniciado...")
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
            elif porcentagem <= 20:
                emoji = '🪫'
            else:
                emoji = '🔋'

            titulo = f"{emoji} Bateria: {porcentagem}%"
            mensagem = f"Status: {status} | Temp: {temperatura}°C | Saude: {saude}"

            print(f"{titulo} | {mensagem}")
            notificar_bateria(titulo, mensagem)

        except Exception as e:
            print(f"Erro: {e}")

        time.sleep(INTERVALO)
