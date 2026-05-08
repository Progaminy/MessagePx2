const GITHUB_URL = 'https://raw.githubusercontent.com/Progaminy/MessagePx2/main/server_url.txt';
let abaAtual = 'recebidas';
let urlServidor = '';

document.addEventListener('DOMContentLoaded', () => {
    carregarUrlServidor();
    // Atualiza a cada 30 segundos
    setInterval(atualizarMensagens, 30000);
});

async function carregarUrlServidor() {
    try {
        const resposta = await fetch(GITHUB_URL);
        urlServidor = await resposta.text();
        urlServidor = urlServidor.trim();
        console.log('URL do servidor:', urlServidor);
        document.getElementById('ultima-atualizacao').textContent = 'Conectado ao servidor';
        atualizarMensagens();
    } catch (erro) {
        document.getElementById('lista-mensagens').innerHTML = 
            '<p style="color:#ff4444">Erro ao carregar servidor.</p>';
    }
}

function mudarAba(aba) {
    abaAtual = aba;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    atualizarMensagens();
}

async function atualizarMensagens() {
    if (!urlServidor) return;
    
    try {
        const resposta = await fetch(urlServidor + '/api/' + abaAtual);
        const dados = await resposta.json();
        exibirMensagens(dados);
        
        const agora = new Date();
        document.getElementById('ultima-atualizacao').textContent = 
            'Atualizado: ' + agora.toLocaleTimeString('pt-BR');
    } catch (erro) {
        document.getElementById('ultima-atualizacao').textContent = 
            'Erro ao conectar. Tentando novamente...';
    }
}

function exibirMensagens(dados) {
    const lista = document.getElementById('lista-mensagens');
    
    if (!dados || dados.length === 0) {
        lista.innerHTML = '<p style="color:#888">Nenhuma ' + abaAtual + ' encontrada.</p>';
        return;
    }

    let html = '';
    dados.forEach(msg => {
        if (abaAtual === 'alertas') {
            html += `
                <div class="alerta ${msg.tipo === 'baixa' ? 'bateria-baixa' : 'bateria-ok'}">
                    <strong>🔋 ${msg.porcentagem}%</strong> - ${msg.status}
                    <div style="font-size:12px;color:#888">${msg.data}</div>
                </div>
            `;
        } else {
            html += `
                <div class="mensagem nova">
                    <div class="numero">👤 ${msg.numero}</div>
                    <div class="texto">${msg.mensagem}</div>
                    <div class="data">🕐 ${msg.data}</div>
                </div>
            `;
        }
    });
    
    lista.innerHTML = html;
}