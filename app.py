from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask + Ngrok OK!"

@app.route("/run", methods=["POST"])
def run_command():
    try:
        # Ép lấy JSON, nếu sai format sẽ tự động 400
        data = request.get_json(force=True)

        # Log dữ liệu nhận được
        print("[DEBUG] Data nhận từ client:", data)

        ipport = data.get("ipport", "").strip()
        if not ipport or ":" not in ipport:
            return jsonify({"error": "Sai định dạng, phải nhập IP:PORT"}), 400

        # Tách IP và PORT
        ip, port = ipport.split(":", 1)

        # Câu lệnh cần chạy
        cmd = ["./bgmi", ip, port, "200", "200"]

        # Chạy background, không block Flask
        subprocess.Popen(cmd)

        print(f"[DEBUG] Đã chạy lệnh: {' '.join(cmd)}")

        return jsonify({"message": f"Đã chạy: {' '.join(cmd)}"}), 200

    except Exception as e:
        print("[ERROR]", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
