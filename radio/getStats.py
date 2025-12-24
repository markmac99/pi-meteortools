import os
import sys
import shutil
import glob
import numpy as np

from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hamming

from analyse_detection import createImages

SPECGRAM_BAND = 500     # Band for displaying specgram plots is +/-500
OVERLAP = 0.75
DEFAULT_SAMPLE_RATE = 37500
NUM_FFT = 2**12
HOP=int(NUM_FFT*(1-OVERLAP))


def getSNR(filename):
    splits = os.path.basename(filename).split('_')
    centre_freq = float(splits[1])

    npz_data = np.load(filename)
    samples = npz_data['samples']
    sample_rate = DEFAULT_SAMPLE_RATE

    try:
        centre_freq = npz_data['centre_freq']
        sample_rate = npz_data['sample_rate']
    except Exception:
        pass

    window = hamming(NUM_FFT, sym=True)
    sft = ShortTimeFFT(window, hop=HOP, fs=sample_rate, mfft=NUM_FFT, fft_mode='centered')
    Pxx = sft.spectrogram(samples)

    f = sft.f
    f = (f + centre_freq - 2000) / 1e6

    freq_slice = np.where((f >= (centre_freq-SPECGRAM_BAND)/1e6) & (f <= (centre_freq+SPECGRAM_BAND)/1e6))
    f = f[freq_slice]
    f *= 1e6
    f -= (centre_freq)
    Pxx = Pxx[freq_slice,:][0]

    raw_median = np.median(Pxx[0:13])    # Calculate noise before detection
    log_mn = 10.0*np.log10(raw_median)
    log_sigmax = 10.0*np.log10(np.max(Pxx))
    snr = log_sigmax - log_mn
    return round(snr,2), log_sigmax, log_mn


def processFolder(foldername, min_snr):
    
    datadir = os.getenv('mrdatadir', default=os.path.expanduser('~/radar_data'))
    imgdir = os.path.join(datadir, 'Images')
    auddir = os.path.join(datadir, 'Audio')
    arcdir = os.path.join(datadir, 'Archive')
    
    if os.path.isfile(foldername):
        files = [os.path.split(foldername)[1]]
        foldername = os.path.split(foldername)[0]
    else:
        files = os.listdir(foldername)
    files = [x for x in files if 'SMP' in x and 'npz' in x]
    if len(files) == 0:
        print(f'nothing to do for x{foldername}x')
        return 
    donefiles = open('processed.txt', 'r').readlines()
    donefiles = [d.strip() for d in donefiles]
    for fil in files:
        if fil in donefiles:
            print(f'skipping {fil}')
            continue
        fullname = os.path.join(foldername, fil)
        snr = getSNR(fullname)[0]
        if snr > min_snr:
            print(f'interesting {fil}')
            shutil.copyfile(fullname, os.path.join(arcdir, fil))
            spls = fil.split('_')
            imgs = glob.glob(f'{imgdir}/*{spls[2]}_{spls[3]}*')
            wavs = glob.glob(f'{auddir}/*{spls[2]}_{spls[3]}*')
            if len(imgs) == 0 or len(wavs) == 0:
                imgs, wavs = createImages(fullname, imgdir=imgdir, auddir=auddir)
            imgs = [os.path.split(im)[1] for im in imgs]
            wavs = [os.path.split(wa)[1] for wa in wavs]
            for img in imgs:
                shutil.copyfile(os.path.join(imgdir, img), os.path.join(arcdir, img))
            for wav in wavs:
                shutil.copyfile(os.path.join(auddir, wav), os.path.join(arcdir, wav))
        else:
            print(f'dull {fil}')
        donefiles.append(fil)
    open('processed.txt', 'w').writelines("\n".join(donefiles))
    return 


if __name__ == '__main__':
    processFolder(sys.argv[1], 35.0)
