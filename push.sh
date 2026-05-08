#!/data/data/com.termux/files/usr/bin/bash

cd /data/data/com.termux/files/home/storage/proj/MessagePx2

echo "========================================"
echo "PUSH RAPIDO - MessagePx2"
echo "========================================"

git add .

echo ""
echo "Mensagem do commit (ou Enter para automatica):"
read mensagem

if [ -z "$mensagem" ]; then
    mensagem="Atualizacao rapida - $(date '+%d/%m/%Y %H:%M:%S')"
fi

git commit -m "$mensagem"

git push origin main

echo ""
echo "Push concluido!"
