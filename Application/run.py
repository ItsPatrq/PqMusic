import tensorflow as tf
import librosa
import numpy as np

from magenta.common import tf_utils
from magenta.music import audio_io
import magenta.music as mm
from magenta.models.onsets_frames_transcription import audio_label_data_utils
from magenta.models.onsets_frames_transcription import configs
from magenta.models.onsets_frames_transcription import constants
from magenta.models.onsets_frames_transcription import data
from magenta.models.onsets_frames_transcription import train_util
from magenta.music import midi_io
from magenta.protobuf import music_pb2
from magenta.music import sequences_lib


## Define model and load checkpoint
## Only needs to be run once.
CHECKPOINT_DIR = "../onsets_frames_dataset_maestro_v1.0.0/"
config = configs.CONFIG_MAP['onsets_frames']
hparams = config.hparams
hparams.use_cudnn = False
hparams.batch_size = 1

examples = tf.placeholder(tf.string, [None])

dataset = data.provide_batch(
    examples=examples,
    preprocess_examples=True,
    params=hparams,
    is_training=False,
    shuffle_examples=False,
    skip_n_initial_records=0)

estimator = train_util.create_estimator(
    config.model_fn, CHECKPOINT_DIR, hparams)

iterator = dataset.make_initializable_iterator()
next_record = iterator.get_next()