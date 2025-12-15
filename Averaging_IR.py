import numpy as np
import soundfile as sf
from scipy.signal import correlate

def estimate_ir(ref_path, rec_paths, out_path="impulse_response.wav"):
    x, fs = sf.read(ref_path)
    x = x[:,0] if x.ndim > 1 else x

    recordings = []
    for p in rec_paths:
        y, _ = sf.read(p)
        y = y[:,0] if y.ndim > 1 else y
        recordings.append(y)

    aligned = []
    for y in recordings:
        corr = correlate(y, x, mode="full")
        shift = np.argmax(corr) - len(x) + 1
        aligned.append(np.roll(y, -shift))

    min_len = min(len(y) for y in aligned)
    Y = np.array([y[:min_len] for y in aligned])
    y_avg = np.mean(Y, axis=0)

    N = len(y_avg) + len(x)
    H = np.fft.fft(y_avg, N) / (np.fft.fft(x, N) + 1e-6)
    h = np.real(np.fft.ifft(H))

    sf.write(out_path, h, fs)
    return out_path
