import sys
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hamming
import os
import wave


FULL_FREQUENCY_BAND = 18000   # Band for psd plot is +/- 18000 Hz
SPECGRAM_BAND = 500     # Band for displaying specgram plots is +/-500

OVERLAP = 0.75           # Overlap (0.75 is 75%)

NUM_FFT = 2**12
DEFAULT_SAMPLE_RATE = 37500
HOP=int(NUM_FFT*(1-OVERLAP))


class MeteorPlotter():

    def __init__(self):

        self.cmap_color = 'GnBu'
        self.cmap_color_list = plt.colormaps()
        self.cmap_index = self.cmap_color_list.index(self.cmap_color)

    def plot_specgram(self, Pxx, f, bins, centre_freq, obs_time, outdir):
        freq_slice = np.where((f >= (centre_freq-SPECGRAM_BAND)/1e6) & (f <= (centre_freq+SPECGRAM_BAND)/1e6))

        f = f[freq_slice]
        f *= 1e6
        f -= (centre_freq)
        Pxx = Pxx[freq_slice,:][0]

        # Collect the detection stats
        mn, sigmax, init_freq, peak_freq, snr = get_capture_stats(Pxx, f, bins)

        # Convert the plot data to dB
        _ = np.float16(Pxx)
        Pxx = 10.0*np.log10(Pxx)

        # Form the stats string
        stats_string = 'Mean:{0:8.2f}  Max:{1:8.2f}  PeakF:{2:7.1f}  SNR:{3:7.2f} dB'.format(mn, sigmax, peak_freq, snr)


        fig, ax = plt.subplots(figsize=(6,9))
        ax.pcolormesh(f, bins, Pxx.T, cmap=self.cmap_color, shading='auto')
        ax.set_title('Meteor Radio Detection  ' + str(obs_time)[:-3] + '\n' + stats_string, fontsize=10)
        ax.set_xlabel('Frequency (Hz) around ' + str(centre_freq/1e6) + ' MHz')
        ax.set_ylabel('Time (s)')
        ax.ticklabel_format(axis='x', useOffset=False)
        ax.set_xlim([np.min(f), np.max(f)])

        # Save PSD as an image file
        image_filename = os.path.join(outdir,'PSD_' + str(int(centre_freq)) + obs_time.strftime('_%Y%m%d_%H%M%S_%f.png'))
        print("Saving", image_filename)
        plt.savefig(image_filename)
        plt.close()
        return image_filename


    def plot_3dspecgram(self, Pxx, f, bins, centre_freq, obs_time, sample_rate, outdir):
        # Limit the data to the narrow frequency band
        freq_slice = np.where((f >= (centre_freq-SPECGRAM_BAND)/1e6) & (f <= (centre_freq+SPECGRAM_BAND)/1e6))
        f = f[freq_slice]
        Pxx = Pxx[freq_slice,:][0]

        # Plot the 3d spectrogram
        fig = plt.figure(figsize=(10,7.5))
        ax = plt.axes(projection='3d')
        # ax = fig.gca(projection='3d')
        f -= (centre_freq/1e6)
        f *= 1e6
        ax.plot_surface(bins[None,:], f[:, None], 10.0*np.log10(Pxx), cmap='coolwarm')
        plt.title('Meteor Radio Detection  ' + str(obs_time)[:-3], y=1.08)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz) around ' + str(centre_freq/1e6) + ' MHz')
        ax.set_zlabel('Relative power (dB)')
        # ax.view_init(30, 135)
        ax.set_xlim(max(bins), min(bins))
        plt.ticklabel_format(axis='y', useOffset=False)
        fig.tight_layout()

        # Save spectrogram as an image file
        image_filename = os.path.join(outdir,'SPG_' + str(int(centre_freq)) + '_' + str(int(sample_rate)) + obs_time.strftime('_%Y%m%d_%H%M%S_%f.png'))
        print("Saving", image_filename)
        plt.savefig(image_filename)
        return image_filename
    
    def create_audio(self, samples, file_name, outdir):
        x7 = samples * (10000 / np.max(np.abs(samples)))

        # Save to file as 16-bit signed single-channel audio samples
        # Note that we can throw away the imaginary part of the IQ sample data for USB
        audio_filename = file_name.replace("SMP", "AUD")
        audio_filename = audio_filename.replace("npz", "raw")
        wav_filename = audio_filename.replace("raw", "wav")
        wav_filename = os.path.join(outdir, os.path.split(wav_filename)[1])
        print("Saving", wav_filename)
        x7.real.astype("int16").tofile(audio_filename)
        data = open(audio_filename, 'rb').read()
        with wave.open(wav_filename, 'wb') as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2)
            out_f.setframerate(44100)
            out_f.writeframesraw(data)
        return wav_filename



def get_observation_data(filename):
    splits = filename.split('_')
    centre_freq = float(splits[1])
    if len(splits)> 5:
        sample_rate = int(splits[2])
        obs_date = splits[3]
        obs_time = splits[4]
        obs_timefrac = splits[5].split('.')[0]
    else:
        sample_rate = None
        obs_date = splits[2]
        obs_time = splits[3]
        obs_timefrac = splits[4].split('.')[0]
    obs_time = datetime.datetime.strptime(obs_date + '_' + obs_time + '_' + obs_timefrac, '%Y%m%d_%H%M%S_%f')
    print("Observation time", obs_time, "Frequency", centre_freq, "Sample rate", sample_rate)
    return obs_time, centre_freq, sample_rate


def get_capture_stats(Pxx, f, bins):
    # Calculate the signal level stats over the detection band
    raw_mean = np.mean(Pxx[0:13])
    mn = 10.0*np.log10(raw_mean)
    sigmax = 10.0*np.log10(np.max(Pxx))
    maxpos = np.argmax(np.max(Pxx, axis=1))
    peak_freq = f[maxpos]
    snr = sigmax - mn
    snr_threshold = 22

    # Find time range where snr > threshold
    try:
        Pxx_snr = Pxx/raw_mean
        s = np.nonzero(Pxx_snr > snr_threshold)
        imin, imax = np.min(s[1]), np.max(s[1])
        detection_time = bins[imax] - bins[imin]
        detection_freq = f[s[0][-1]]
    except Exception as e:
        print(e)
        detection_time = 0.0
        detection_freq = peak_freq

    stats_string = 'Mean:{0:10.4f}  Max:{1:10.4f}  Duration:{2:7.2f}  Frequency:{3:12.6f}  MaxSNR:{4:7.2f} dB'.format(mn, sigmax, detection_time, detection_freq, snr)
    print(stats_string)
    return mn, sigmax, detection_freq, peak_freq, snr


def createImages(filename, imgdir=None, auddir=None):

    # Create a meteor plotter object
    meteor_plotter = MeteorPlotter()

    print(f'processing {filename}')
    if os.path.isfile(filename):

        # Get observation data from file name e.g. SPG_143050000_300000_20210204_222326_281976.npz
        if imgdir is None:
            imgdir = os.path.split(filename)[0]
        if auddir is None:
            auddir = os.path.split(filename)[0]
        basefname = os.path.split(filename)[1]
        obs_time, centre_freq, sample_rate = get_observation_data(basefname)

        npz_data = np.load(filename)
        samples = npz_data['samples']
        sample_rate = DEFAULT_SAMPLE_RATE
        try:
            centre_freq = npz_data['centre_freq']
            sample_rate = npz_data['sample_rate']
            obs_time = datetime.datetime.strptime(str(npz_data['obs_time']), "%Y-%m-%d %H:%M:%S.%f")
        except Exception as e:
            print(e)

        window = hamming(NUM_FFT, sym=True)  # symmetric Gaussian window
        sft = ShortTimeFFT(window, hop=HOP, fs=sample_rate, mfft=NUM_FFT, fft_mode='centered')
        Pxx = sft.spectrogram(samples)

        T_x, N = HOP / sample_rate, Pxx.shape[1]
        bins = np.arange(N) * T_x

        f = sft.f
        f = (f + centre_freq - 2000) / 1e6

        img_2d = meteor_plotter.plot_specgram(Pxx, f, bins, centre_freq, obs_time, imgdir)
        img_3d = meteor_plotter.plot_3dspecgram(Pxx, f, bins, centre_freq, obs_time, sample_rate, imgdir)
        audio = meteor_plotter.create_audio(samples, filename, auddir)

        return [img_2d, img_3d], [audio]


if __name__ == "__main__":
    createImages(sys.argv[1])
