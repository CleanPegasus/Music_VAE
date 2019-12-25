import utils
import os
import numpy as np


def preprocess_songs(data_folders):
    """
    Load and preprocess the songs from the data folders and turn them into a dataset of samples/pitches and lengths of the tones.
    :param data_folders:
    :return:
    """

    all_samples = []
    all_lengths = []

    # keep some statistics
    succeeded = 0
    failed = 0
    ignored = 0

    # load songs
    print("Loading songs...")
    # walk folders and look for midi files
    for folder in os.listdir(data_folders):
        print(folder)
        for root, _, files in os.walk(os.path.join(data_folders, folder)):
            for file in files:
                print(file)
                path = os.path.join(root, file)
                if not (path.endswith('.mid') or path.endswith('.midi')):
                    continue

                # turn midi into samples
                try:
                    samples = utils.midi_to_samples(path)
                except Exception as e:
                    print("ERROR ", path)
                    print(e)
                    failed += 1
                    continue

                # if the midi does not produce the minimal number of sample/measures, we skip it
                if len(samples) < 16:
                    print('WARN', path, 'Sample too short, unused')
                    ignored += 1
                    continue

                # transpose samples (center them in full range to get more training samples for the same tones)
                samples, lengths = utils.generate_centered_transpose(samples)
                all_samples += samples
                all_lengths += lengths
                print('SUCCESS', path, len(samples), 'samples')
                succeeded += 1

    assert (sum(all_lengths) == len(all_samples))  # assert equal number of samples and lengths

    # save all to disk
    print("Saving " + str(len(all_samples)) + " samples...")
    all_samples = np.array(all_samples, dtype=np.uint8)  # reduce size when saving
    all_lengths = np.array(all_lengths, dtype=np.uint32)
    np.save('data/samples.npy', all_samples)
    np.save('data/lengths.npy', all_lengths)
    print('Done: ', succeeded, 'succeded,', ignored, 'ignored,', failed, 'failed of', succeeded + ignored + failed, 'in total')


preprocess_songs('midi_data')