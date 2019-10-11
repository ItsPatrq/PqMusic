import ctypes.util
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
from magenta.models.onsets_frames_transcription import infer_util
from magenta.models.onsets_frames_transcription import train_util
from magenta.music import midi_io
from magenta.protobuf import music_pb2
from magenta.music import sequences_lib
# Ignore warnings caused by pyfluidsynth
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
orig_ctypes_util_find_library = ctypes.util.find_library
CHECKPOINT_DIR = '../../../resources/onsets-frames/train'

def proxy_find_library(lib):
  if lib == 'fluidsynth':
    return 'libfluidsynth.so.1'
  else:
    return orig_ctypes_util_find_library(lib)
ctypes.util.find_library = proxy_find_library

print("Model initialization")

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

print("Model initialized succesfully")


exampleFile = open('./chopin-waltz.wav', 'rb')
uploaded = {
  'chopin-waltz.wav': exampleFile.read()
}
to_process = []
for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))
  wav_data = uploaded[fn]
  example_list = list(
      audio_label_data_utils.process_record(
          wav_data=wav_data,
          ns=music_pb2.NoteSequence(),
          example_id=fn,
          min_length=0,
          max_length=-1,
          allow_empty_notesequence=True))
  assert len(example_list) == 1
  to_process.append(example_list[0].SerializeToString())
  
  print('Processing complete for', fn)
  
sess = tf.Session()

sess.run([
    tf.initializers.global_variables(),
    tf.initializers.local_variables()
])

sess.run(iterator.initializer, {examples: to_process})

def transcription_data(params):
  del params
  return tf.data.Dataset.from_tensors(sess.run(next_record))
input_fn = infer_util.labels_to_features_wrapper(transcription_data)

print("FILE HAVE BEEN UPLOADED")

prediction_list = list(
    estimator.predict(
        input_fn,
        yield_single_examples=False))
assert len(prediction_list) == 1

frame_predictions = prediction_list[0]['frame_predictions'][0]
onset_predictions = prediction_list[0]['onset_predictions'][0]
velocity_values = prediction_list[0]['velocity_values'][0]

sequence_prediction = sequences_lib.pianoroll_to_note_sequence(
    frame_predictions,
    frames_per_second=data.hparams_frames_per_second(hparams),
    min_duration_ms=0,
    min_midi_pitch=constants.MIN_MIDI_PITCH,
    onset_predictions=onset_predictions,
    velocity_values=velocity_values)


mm.plot_sequence(sequence_prediction)
mm.play_sequence(sequence_prediction, mm.midi_synth.fluidsynth,
                 colab_ephemeral=False)