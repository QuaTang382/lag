#!/bin/bash

# stop nếu có session cũ
pkill -f "python app.py"
pkill -f "ngrok"

# chạy Flask ở background
echo "[*] Starting Flask server..."
python app.py &

# đợi 2 giây để Flask khởi động
sleep 2

# chạy ngrok
echo "[*] Starting ngrok tunnel..."
./ngrok http 5000