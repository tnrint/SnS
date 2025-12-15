from flask import Flask, request, jsonify
import numpy as np
import soundfile as sf
from scipy.signal import correlate
import io

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    ref_file = request.files["ref"]
    rec_files = request.files.getlist("recs")

    # Load reference
    x, fs = sf.read(io.BytesIO(ref_file.read()))
    x = x[:,0] if x.ndim > 1 else x

    # Load recordings
    recordings = []
    for f in rec_files:
        y, _ = sf.read(io.BytesIO(f.read()))
        y = y[:,0] if y.ndim > 1 else y
        recordings.append(y)

    # Time alignment
    aligned = []
    for y in recordings:
        corr = correlate(y, x, mode="full")
        shift = np.argmax(corr) - len(x) + 1
        aligned.append(np.roll(y, -shift))

    # Averaging
    min_len = min(len(y) for y in aligned)
    Y = np.array([y[:min_len] for y in aligned])
    y_avg = np.mean(Y, axis=0)

    # IR estimation (FFT deconvolution)
    N = len(y_avg) + len(x)
    H = np.fft.fft(y_avg, N) / (np.fft.fft(x, N) + 1e-6)
    h = np.real(np.fft.ifft(H))

    # Normalize and send part of IR
    h /= np.max(np.abs(h)) + 1e-9

    return jsonify({
        "fs": fs,
        "impulse_response": h[:20000].tolist()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500)
