// Configuração
const GITHUB_CONFIG_URL = 'https://raw.githubusercontent.com/Progaminy/MessagePx2/main/pxp/config.json';
let midiaAtual = null;

// Ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    carregarConfig();
});

async function carregarConfig() {
    try {
        const resposta = await fetch(GITHUB_CONFIG_URL);
        const config = await resposta.json();
        
        // Carrega fotos
        config.fotos.forEach((url, i) => {
            const img = document.getElementById(`foto-${i}`);
            if (img && url) {
                img.src = url;
                img.style.display = 'block';
                img.parentElement.querySelector('.placeholder').style.display = 'none';
            }
        });
        
        // Carrega vídeos
        config.videos.forEach((url, i) => {
            const video = document.getElementById(`video-${i}`);
            if (video && url) {
                video.src = url;
                video.style.display = 'block';
                video.parentElement.querySelector('.placeholder').style.display = 'none';
            }
        });
        
        document.getElementById('status-texto').textContent = 
            '✅ Atualizado: ' + new Date().toLocaleTimeString('pt-BR');
            
    } catch (erro) {
        document.getElementById('status-texto').textContent = 
            '❌ Erro ao carregar. Verifique sua internet.';
    }
}

function abrirMidia(tipo, indice) {
    const modal = document.getElementById('modal');
    const modalImg = document.getElementById('modal-img');
    const modalVideo = document.getElementById('modal-video');
    
    modal.style.display = 'flex';
    
    if (tipo === 'foto') {
        const img = document.getElementById(`foto-${indice}`);
        modalImg.src = img.src;
        modalImg.style.display = 'block';
        modalVideo.style.display = 'none';
        midiaAtual = { tipo: 'foto', src: img.src };
    } else {
        const video = document.getElementById(`video-${indice}`);
        modalVideo.src = video.src;
        modalVideo.style.display = 'block';
        modalImg.style.display = 'none';
        midiaAtual = { tipo: 'video', src: video.src };
    }
}

function fecharModal() {
    document.getElementById('modal').style.display = 'none';
    const modalVideo = document.getElementById('modal-video');
    modalVideo.pause();
    modalVideo.src = '';
}

function baixarMidia() {
    if (!midiaAtual) return;
    
    const link = document.createElement('a');
    link.href = midiaAtual.src;
    link.download = midiaAtual.tipo === 'foto' ? 'pxp-foto.jpg' : 'pxp-video.mp4';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
