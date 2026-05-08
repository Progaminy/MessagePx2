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
            const container = document.getElementById(`foto-${i}`).parentElement;
            const img = document.getElementById(`foto-${i}`);
            if (img && url) {
                img.src = url;
                img.style.display = 'block';
                container.querySelector('.placeholder').style.display = 'none';
            }
        });
        
        // Carrega vídeos (YouTube embed)
        config.videos.forEach((url, i) => {
            const container = document.getElementById(`video-${i}`).parentElement;
            const videoEl = document.getElementById(`video-${i}`);
            
            if (videoEl && url) {
                if (url.includes('youtube.com/embed/') || url.includes('youtube.com/watch')) {
                    // Cria iframe para YouTube
                    let videoId = url;
                    if (url.includes('watch?v=')) {
                        videoId = url.split('v=')[1].split('&')[0];
                        videoId = `https://www.youtube.com/embed/${videoId}`;
                    }
                    
                    const iframe = document.createElement('iframe');
                    iframe.src = videoId;
                    iframe.width = '100%';
                    iframe.height = '100%';
                    iframe.style.border = 'none';
                    iframe.style.borderRadius = '12px';
                    iframe.allowFullscreen = true;
                    
                    videoEl.style.display = 'none';
                    container.appendChild(iframe);
                    container.querySelector('.placeholder').style.display = 'none';
                } else {
                    // Vídeo normal
                    videoEl.src = url;
                    videoEl.style.display = 'block';
                    container.querySelector('.placeholder').style.display = 'none';
                }
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
        const container = document.getElementById(`video-${indice}`).parentElement;
        const videoEl = container.querySelector('video');
        const iframe = container.querySelector('iframe');
        
        if (iframe) {
            // Para YouTube, abre o link diretamente
            window.open(iframe.src, '_blank');
            modal.style.display = 'none';
            return;
        } else if (videoEl) {
            modalVideo.src = videoEl.src;
            modalVideo.style.display = 'block';
            modalImg.style.display = 'none';
            midiaAtual = { tipo: 'video', src: videoEl.src };
        }
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
    
    if (midiaAtual.tipo === 'foto') {
        const link = document.createElement('a');
        link.href = midiaAtual.src;
        link.download = 'pxp-foto.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
