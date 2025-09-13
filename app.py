from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

bgmi_process = None
bgmi_pid = None

@app.route("/run", methods=["POST"])
def run_bgmi():
    global bgmi_process, bgmi_pid

    data = request.get_json()
    ip = data.get("ip")
    port = data.get("port")

    if not ip or not port:
        return jsonify({"error": "missing ip or port"}), 400

    try:
        # chạy binary bgmi
        bgmi_process = subprocess.Popen(["./bgmi", ip, str(port), "200", "200"])
        bgmi_pid = bgmi_process.pid
        return jsonify({"status": "started", "pid": bgmi_pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stop", methods=["GET"])
def stop_bgmi():
    global bgmi_process, bgmi_pid

    pid = request.args.get("pid", type=int)

    if bgmi_process and bgmi_pid == pid:
        try:
            bgmi_process.terminate()
            bgmi_process.wait()
            bgmi_process = None
            bgmi_pid = None
            return jsonify({"status": "stopped"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "no running process"}), 400


if __name__ == "__main__":
    # chạy trong Codespace → host 0.0.0.0
    app.run(host="0.0.0.0", port=5000)