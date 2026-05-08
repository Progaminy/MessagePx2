const GITHUB_API_URL = 'https://raw.githubusercontent.com/Progaminy/MessagePx2/main/server_api_url.txt';
let urlAPI = '';
let abaAtual = 'recebidas';

document.addEventListener('DOMContentLoaded', () => {
    carregarUrlAPI();
    setInterval(atualizarDados, 30000);
});

async function carregarUrlAPI() {
    try {
        const resposta = await fetch(GITHUB_API_URL);
        urlAPI = await resposta.text();
        urlAPI = urlAPI.trim();
        console.log('API:', urlAPI);
        document.getElementById('ultima-atualizacao').textContent = 'Conectado à API';
        atualizarDados();
    } catch (erro) {
        document.getElementById('lista-mensagens').innerHTML = 
            '<p style="color:#ff4444">Erro ao conectar ao servidor.</p>';
    }
}

function mudarAba(aba) {
    abaAtual = aba;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    atualizarDados();
}

async function atualizarDados() {
    if (!urlAPI) return;
    
    try {
        let endpoint = abaAtual === 'recebidas' ? '/api/recebidas' :
                       abaAtual === 'enviadas' ? '/api/enviadas' : '/api/alertas';
        
        const resposta = await fetch(urlAPI + endpoint);
        const dados = await resposta.json();
        exibirDados(dados);
        
        document.getElementById('ultima-atualizacao').textContent = 
            'Atualizado: ' + new Date().toLocaleTimeString('pt-BR');
    } catch (erro) {
        document.getElementById('ultima-atualizacao').textContent = 
            'Erro ao conectar. Tentando novamente...';
    }
}

function exibirDados(dados) {
    const lista = document.getElementById('lista-mensagens');
    
    if (!dados || dados.length === 0) {
        lista.innerHTML = '<p style="color:#888">Nenhum dado encontrado.</p>';
        return;
    }

    let html = '';
    
    if (abaAtual === 'alertas') {
        dados.forEach(alerta => {
            html += `
                <div class="alerta ${alerta.porcentagem <= 20 ? 'bateria-baixa' : 'bateria-ok'}">
                    <strong>🔋 ${alerta.porcentagem}%</strong> - ${alerta.status}
                    <div>🌡 ${alerta.temperatura}°C</div>
                    <div>📍 ${alerta.latitude}, ${alerta.longitude}</div>
                    <div style="font-size:12px;color:#888">🕐 ${alerta.data}</div>
                </div>
            `;
        });
    } else {
        dados.forEach(msg => {
            html += `
                <div class="mensagem nova">
                    <div class="numero">👤 ${msg.numero || 'Desconhecido'}</div>
                    <div class="texto">${msg.mensagem || msg.body || ''}</div>
                    <div class="data">🕐 ${msg.data || ''}</div>
                </div>
            `;
        });
    }
    
    lista.innerHTML = html;
}
