import argparse
from functools import partial
from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
import soundfile as sf
import psola

SEMITONES_IN_OCTAVE = 12

def get_scale_degrees(scale: str):
    """Retorna as classes de tom (graus) correspondentes à escala fornecida."""
    degrees = librosa.key_to_degrees(scale)
    degrees = np.concatenate((degrees, [degrees[0] + SEMITONES_IN_OCTAVE]))
    return degrees

def round_to_nearest_pitch(f0):
    """Arredonda os valores de tom para os números de nota MIDI mais próximos."""
    midi_note = np.around(librosa.hz_to_midi(f0))
    nan_indices = np.isnan(f0)
    midi_note[nan_indices] = np.nan
    return librosa.midi_to_hz(midi_note)

def nearest_pitch_in_scale(f0, scale):
    """Encontra a tom mais próxima de f0 dentro da escala fornecida."""
    if np.isnan(f0):
        return np.nan
    degrees = get_scale_degrees(scale)
    midi_note = librosa.hz_to_midi(f0)
    degree = midi_note % SEMITONES_IN_OCTAVE
    degree_id = np.argmin(np.abs(degrees - degree))
    degree_difference = degree - degrees[degree_id]
    midi_note -= degree_difference
    return librosa.midi_to_hz(midi_note)

def map_to_scale_pitches(f0, scale):
    """Mapeia cada tom no array f0 para a tom mais próxima dentro da escala fornecida."""
    sanitized_pitch = np.zeros_like(f0)
    for i in range(f0.shape[0]):
        sanitized_pitch[i] = nearest_pitch_in_scale(f0[i], scale)
    smoothed_sanitized_pitch = sig.medfilt(sanitized_pitch, kernel_size=11)
    smoothed_sanitized_pitch[np.isnan(smoothed_sanitized_pitch)] = sanitized_pitch[np.isnan(smoothed_sanitized_pitch)]
    return smoothed_sanitized_pitch

def perform_autotune(audio, sr, correction_function, plot=False):
    frame_length = 2048
    hop_length = frame_length // 4
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')
    f0, _, _ = librosa.pyin(audio, frame_length=frame_length, hop_length=hop_length, sr=sr, fmin=fmin, fmax=fmax)
    corrected_f0 = correction_function(f0)

    if plot:
        stft = librosa.stft(audio, n_fft=frame_length, hop_length=hop_length)
        time_points = librosa.times_like(stft, sr=sr, hop_length=hop_length)
        log_stft = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(log_stft, x_axis='time', y_axis='log', ax=ax, sr=sr, hop_length=hop_length, fmin=fmin, fmax=fmax)
        fig.colorbar(img, ax=ax, format="%+2.f dB")
        ax.plot(time_points, f0, label='tom original', color='cyan', linewidth=2)
        ax.plot(time_points, corrected_f0, label='tom corrigida', color='orange', linewidth=1)
        ax.legend(loc='upper right')
        plt.ylabel('Frequência [Hz]')
        plt.xlabel('Tempo [M:SS]')
        plt.savefig('pitch_correction.png', dpi=300, bbox_inches='tight')

    return psola.vocode(audio, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vocals_file')
    parser.add_argument('--plot', '-p', action='store_true', default=False, help='produz um gráfico dos resultados se definido')
    parser.add_argument('--correction-method', '-c', choices=['closest', 'scale'], default='closest')
    parser.add_argument('--scale', '-s', type=str, help='veja librosa.key_to_degrees; usado apenas para o método de correção "scale"')
    args = parser.parse_args()

    filepath = Path(args.vocals_file)
    audio, sr = librosa.load(str(filepath), sr=None, mono=False)

    if audio.ndim > 1:
        audio = audio[0, :]

    correction_function = round_to_nearest_pitch if args.correction_method == 'closest' else partial(map_to_scale_pitches, scale=args.scale)
    pitch_corrected_audio = perform_autotune(audio, sr, correction_function, args.plot)
    output_path = filepath.parent / (filepath.stem + '_pitch_corrected' + filepath.suffix)
    sf.write(str(output_path), pitch_corrected_audio, sr)

if __name__ == '__main__':
    main()
