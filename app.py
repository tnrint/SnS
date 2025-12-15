from flask import Flask, request, send_file
import os
from Averaging_IR import estimate_ir

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def index():
    return "Impulse Response Backend is running!"
def process():
    ref = request.files["ref"]
    recs = request.files.getlist("recs")

    os.makedirs("uploads", exist_ok=True)

    ref_path = "uploads/ref.wav"
    ref.save(ref_path)

    rec_paths = []
    for i, r in enumerate(recs):
        p = f"uploads/rec{i}.wav"
        r.save(p)
        rec_paths.append(p)

    out = estimate_ir(ref_path, rec_paths)
    return send_file(out, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
