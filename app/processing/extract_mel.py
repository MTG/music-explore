import argparse
import os

import numpy as np
from essentia.pytools.extractors.melspectrogram import melspectrogram

SR = 16000
N_MELS = 96
FRAME_SIZE = 512
HOP_SIZE = 256


def main(filename, melbands_file, force=False):
    if not os.path.exists(melbands_file) or force:
        melbands = melspectrogram(filename,
                                  sample_rate=SR,
                                  frame_size=FRAME_SIZE,
                                  hop_size=HOP_SIZE,
                                  window_type='hann',
                                  low_frequency_bound=0,
                                  high_frequency_bound=SR / 2,
                                  number_bands=N_MELS,
                                  warping_formula='slaneyMel',
                                  weighting='linear',
                                  normalize='unit_tri',
                                  bands_type='power',
                                  compression_type='shift_scale_log').astype('float16')

        fp = np.memmap(melbands_file + '.mmap', dtype='float16', mode='w+', shape=melbands.shape)
        fp[:] = melbands[:]
        del fp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Computes the mel spectrogram of a given audio file.')

    parser.add_argument('filename',
                        help='the name of the file from which to read')
    parser.add_argument('melbands_file', type=str,
                        help='the name of the output file')
    parser.add_argument('--force', '-f', action='store_true',
                        help='force')

    main(**vars(parser.parse_args()))
