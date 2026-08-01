import numpy as np
from scipy import stats
from scipy.fft import fft


class UniversalFeatureExtractor:
    FEATURE_NAMES = [
        "rms",
        "peak",
        "peak_to_peak",
        "kurtosis",
        "skewness",
        "crest_factor",
        "std",
        "variance",
        "dominant_freq",
        "spectral_energy",
        "spectral_entropy",
        "spectral_mean",
        "spectral_std",
    ]

    def extract(self, signal: np.ndarray, sampling_rate: int = 20480) -> np.ndarray:
        x = signal.flatten().astype(np.float64)
        rms = float(np.sqrt(np.mean(x**2)))
        peak = float(np.max(np.abs(x)))
        n = len(x)
        fv = np.abs(fft(x))[: n // 2]
        fr = np.fft.fftfreq(n, 1.0 / sampling_rate)[: n // 2]
        psd = fv**2
        tot = np.sum(psd) + 1e-8
        prob = psd / tot
        sm = float(np.sum(fr * prob))
        return np.array(
            [
                rms,
                peak,
                float(np.max(x) - np.min(x)),
                float(stats.kurtosis(x)),
                float(stats.skew(x)),
                float(peak / (rms + 1e-8)),
                float(np.std(x)),
                float(np.var(x)),
                float(fr[np.argmax(fv)]),
                float(tot),
                float(-np.sum(prob * np.log(prob + 1e-10))),
                sm,
                float(np.sqrt(np.sum(((fr - sm) ** 2) * prob))),
            ],
            dtype=np.float32,
        )
