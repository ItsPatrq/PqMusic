import ctypes.util
import tensorflow as tf
import librosa
import numpy as np
import os
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
import ctypes.util

from utils.pqutils  import *

# Ignore warnings caused by pyfluidsynth
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class OnesetsFrames:
    orig_ctypes_util_find_library = ctypes.util.find_library
    filePath = os.path.dirname(os.path.abspath(__file__))
    CHECKPOINT_DIR = os.path.join(filePath, '../../../resources/onsets-frames/train')
    modelInitialized = False
    def proxy_find_library(self, lib):
        if lib == 'fluidsynth':
            return 'libfluidsynth.so.1'
        else:
            return orig_ctypes_util_find_library(lib)

    def initializeModel(self):
        if(self.modelInitialized):
            return
        print("OnesetsFrames model initialization")

        config = configs.CONFIG_MAP['onsets_frames']
        self.hparams = config.hparams
        self.hparams.use_cudnn = True
        self.hparams.batch_size = 1

        self.examples = tf.placeholder(tf.string, [None])

        self.dataset = data.provide_batch(
            examples=self.examples,
            preprocess_examples=True,
            params=self.hparams,
            is_training=False,
            shuffle_examples=False,
            skip_n_initial_records=0)

        self.estimator = train_util.create_estimator(
            config.model_fn, self.CHECKPOINT_DIR, self.hparams)

        self.iterator = tf.compat.v1.data.make_initializable_iterator(self.dataset)
        self.next_record = self.iterator.get_next()

        self.modelInitialized = True
        print("OnesetsFrames model initialized succesfully")


    def transcribe(self, requestFilePath, responseFilePath):
        self.initializeModel()

        waveFilePath = convertAudioFileToMp3(requestFilePath)
        exampleFile = open(waveFilePath, 'rb')
        uploaded = {
            str(exampleFile.name): exampleFile.read()
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
        
        sess = tf.compat.v1.Session()

        sess.run([
            tf.compat.v1.initializers.global_variables(),
            tf.compat.v1.initializers.local_variables()
        ])
        sess.run(self.iterator.initializer, {self.examples: to_process})

        def transcription_data(params):
            del params
            return tf.data.Dataset.from_tensors(sess.run(self.next_record))

        input_fn = infer_util.labels_to_features_wrapper(transcription_data)

        print("FILE HAVE BEEN UPLOADED")

        prediction_list = list(
            self.estimator.predict(
                input_fn,
                yield_single_examples=False,))

        frame_predictions = prediction_list[0]['frame_predictions'][0]
        onset_predictions = prediction_list[0]['onset_predictions'][0]
        velocity_values = prediction_list[0]['velocity_values'][0]

        sequence_prediction = sequences_lib.pianoroll_to_note_sequence(
            frame_predictions,
            frames_per_second=data.hparams_frames_per_second(self.hparams),
            min_duration_ms=0,
            min_midi_pitch=constants.MIN_MIDI_PITCH,
            onset_predictions=onset_predictions,
            velocity_values=velocity_values)


        # mm.plot_sequence(sequence_prediction)
        # mm.play_sequence(sequence_prediction, mm.midi_synth.fluidsynth,
        #                 colab_ephemeral=False)

        midi_io.sequence_proto_to_midi_file(sequence_prediction, responseFilePath)