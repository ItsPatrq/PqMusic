#https://colab.research.google.com/notebooks/magenta/piano_transformer/piano_transformer.ipynb

import ctypes.util
import numpy as np
import os
import tensorflow as tf

from tensor2tensor import models
from tensor2tensor import problems
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.utils import decoding
from tensor2tensor.utils import trainer_lib

import magenta.music as mm
from magenta.models.score2perf import score2perf

class PianoPerformanceLanguageModelProblem(score2perf.Score2PerfProblem):
  @property
  def add_eos_symbol(self):
    return True

class MelodyToPianoPerformanceProblem(score2perf.AbsoluteMelody2PerfProblem):
    @property
    def add_eos_symbol(self):
        return True

class MusicTransformer:
    filePath = os.path.dirname(os.path.abspath(__file__))
    SF2_PATH = os.path.join(filePath, '../../../resources/transformer/Yamaha-C5-Salamander-JNv5.1.sf2')
    model_name = 'transformer'
    hparams_set = 'transformer_tpu'
    
    exampleFilenames = {
        'C major arpeggio': os.path.join(filePath, '../../../resources/transformer/primers/c_major_arpeggio.mid'),
        'C major scale': os.path.join(filePath, '../../../resources/transformer/primers/c_major_scale.mid'),
        'Clair de Lune': os.path.join(filePath, '../../../resources/transformer/primers/clair_de_lune.mid'),
    }

    melodies = {
        'Mary Had a Little Lamb': [
            64, 62, 60, 62, 64, 64, 64, mm.MELODY_NO_EVENT,
            62, 62, 62, mm.MELODY_NO_EVENT,
            64, 67, 67, mm.MELODY_NO_EVENT,
            64, 62, 60, 62, 64, 64, 64, 64,
            62, 62, 64, 62, 60, mm.MELODY_NO_EVENT,
            mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT
        ],
        'Row Row Row Your Boat': [
            60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            60, mm.MELODY_NO_EVENT, 62,
            64, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            64, mm.MELODY_NO_EVENT, 62,
            64, mm.MELODY_NO_EVENT, 65,
            67, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            72, 72, 72, 67, 67, 67, 64, 64, 64, 60, 60, 60,
            67, mm.MELODY_NO_EVENT, 65,
            64, mm.MELODY_NO_EVENT, 62,
            60, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT,
            mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT, mm.MELODY_NO_EVENT
        ],
        'Twinkle Twinkle Little Star': [
            60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
            65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT,
            67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
            67, 67, 65, 65, 64, 64, 62, mm.MELODY_NO_EVENT,
            60, 60, 67, 67, 69, 69, 67, mm.MELODY_NO_EVENT,
            65, 65, 64, 64, 62, 62, 60, mm.MELODY_NO_EVENT        
        ]
    }

    checkpoint_uc_path = os.path.join(filePath, '../../../resources/transformer/checkpoints/unconditional_model_16.ckpt')
    checkpoint_mc_path = os.path.join(filePath, '../../../resources/transformer/checkpoints/melody_conditioned_model_16.ckpt')
    SAMPLE_RATE = 16000
    targets = []
    inputs = []
    decode_length = 0

    # Decode a list of IDs.
    def decode(self, ids, encoder):
        ids = list(ids)
        if text_encoder.EOS_ID in ids:
            ids = ids[:ids.index(text_encoder.EOS_ID)]
        return encoder.decode(ids)

    # Create input generator (so we can adjust priming and
    # decode length on the fly).
    def input_generator_uc(self):
        while True:
            yield {
                'targets': np.array([self.targets], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }

    # Create input generator.
    def input_generator_mc(self):
        while True:
            yield {
                'inputs': np.array([[self.inputs]], dtype=np.int32),
                'targets': np.zeros([1, 0], dtype=np.int32),
                'decode_length': np.array(self.decode_length, dtype=np.int32)
            }


    def generateUnconditionalTransform(self, requestFilePath, responseFolderPath):
        problem = PianoPerformanceLanguageModelProblem()
        unconditional_encoders = problem.get_feature_encoders()
        # Set up HParams. "Hyperparameter Optimization" or "Hyperparameter Tuning".
        hparams = trainer_lib.create_hparams(hparams_set=self.hparams_set)
        trainer_lib.add_problem_hparams(hparams, problem)
        hparams.num_hidden_layers = 16
        hparams.sampling_method = 'random'

        # Set up decoding HParams.
        decode_hparams = decoding.decode_hparams()
        decode_hparams.alpha = 0.0
        decode_hparams.beam_size = 1

        # Create Estimator.
        run_config = trainer_lib.create_run_config(hparams)
        estimator = trainer_lib.create_estimator(
            self.model_name, hparams, run_config,
            decode_hparams=decode_hparams)

        # These values will be changed by subsequent cells.
        self.targets = []
        self.decode_length = 0

        # Start the Estimator, loading from the specified checkpoint.
        input_fn = decoding.make_input_fn_from_generator(self.input_generator_uc())
        unconditional_samples = estimator.predict(
            input_fn, checkpoint_path=self.checkpoint_uc_path)

        _ = next(unconditional_samples)

        # Generate from Scratch

        self.targets = []
        self.decode_length = 1024

        # Generate sample events.
        sample_ids = next(unconditional_samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=unconditional_encoders['targets'])
        unconditional_ns = mm.midi_file_to_note_sequence(midi_filename)

        unconditionalMidi = os.path.join(responseFolderPath, 'unconditional.mid')
        mm.sequence_proto_to_midi_file(
            unconditional_ns, unconditionalMidi)


        primer_ns = mm.midi_file_to_note_sequence(requestFilePath)

        # Handle sustain pedal in the primer.
        primer_ns = mm.apply_sustain_control_changes(primer_ns)

        # Trim to desired number of seconds.
        max_primer_seconds = 13 
        if primer_ns.total_time > max_primer_seconds:
            print('Primer is longer than %d seconds, truncating.' % max_primer_seconds)
            primer_ns = mm.extract_subsequence(
                primer_ns, 0, max_primer_seconds)

        # Remove drums from primer if present.
        if any(note.is_drum for note in primer_ns.notes):
            print('Primer contains drums; they will be removed.')
            notes = [note for note in primer_ns.notes if not note.is_drum]
            del primer_ns.notes[:]
            primer_ns.notes.extend(notes)

        # Set primer instrument and program.
        for note in primer_ns.notes:
            note.instrument = 1
            note.program = 0

                
        # Generate Continuation

        targets = unconditional_encoders['targets'].encode_note_sequence(
            primer_ns)

        # Remove the end token from the encoded primer.
        targets = targets[:-1]

        decode_length = max(0, 4096 - len(targets))
        if len(targets) >= 4096:
            print('Primer has more events than maximum sequence length; nothing will be generated.')

        # Generate sample events.
        sample_ids = next(unconditional_samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=unconditional_encoders['targets'])
        ns = mm.midi_file_to_note_sequence(midi_filename)

        # Append continuation to primer.
        continuation_ns = mm.concatenate_sequences([primer_ns, ns])

        # Download Continuation as MIDI

        result_path = os.path.join(responseFolderPath, 'result.mid')
        mm.sequence_proto_to_midi_file(
            continuation_ns, result_path)
        return result_path

    def generateMelodyConditionedTransform(self, responseFolderPath):
        problem = MelodyToPianoPerformanceProblem()
        melody_conditioned_encoders = problem.get_feature_encoders()

        # Set up HParams.
        hparams = trainer_lib.create_hparams(hparams_set=self.hparams_set)
        trainer_lib.add_problem_hparams(hparams, problem)
        hparams.num_hidden_layers = 16
        hparams.sampling_method = 'random'

        # Set up decoding HParams.
        decode_hparams = decoding.decode_hparams()
        decode_hparams.alpha = 0.0
        decode_hparams.beam_size = 1

        # Create Estimator.
        run_config = trainer_lib.create_run_config(hparams)
        estimator = trainer_lib.create_estimator(
            self.model_name, hparams, run_config,
            decode_hparams=decode_hparams)

        # These values will be changed by the following cell.
        self.inputs = []
        self.decode_length = 0



        # Start the Estimator, loading from the specified checkpoint.
        input_fn = decoding.make_input_fn_from_generator(self.input_generator_mc())
        melody_conditioned_samples = estimator.predict(
            input_fn, checkpoint_path=self.checkpoint_mc_path)

        # "Burn" one.
        _ = next(melody_conditioned_samples)


        # Choose Melody

        # Tokens to insert between melody events.
        event_padding = 2 * [mm.MELODY_NO_EVENT]

        melody = 'Twinkle Twinkle Little Star' 

        if melody == 'Upload your own!':
            # Extract melody from user-uploaded MIDI file.
            melody_ns = upload_midi()
            melody_instrument = mm.infer_melody_for_sequence(melody_ns)
            notes = [note for note in melody_ns.notes
                    if note.instrument == melody_instrument]
            del melody_ns.notes[:]
            melody_ns.notes.extend(
                sorted(notes, key=lambda note: note.start_time))
            for i in range(len(melody_ns.notes) - 1):
                melody_ns.notes[i].end_time = melody_ns.notes[i + 1].start_time
            inputs = melody_conditioned_encoders['inputs'].encode_note_sequence(
                melody_ns)
        else:
            # Use one of the provided melodies.
            events = [event + 12 if event != mm.MELODY_NO_EVENT else event
                        for e in self.melodies[melody]
                        for event in [e] + event_padding]
            inputs = melody_conditioned_encoders['inputs'].encode(
                ' '.join(str(e) for e in events))
            melody_ns = mm.Melody(events).to_sequence(qpm=150)

        # Generate Accompaniment for Melody

        # Generate sample events.
        decode_length = 4096
        sample_ids = next(melody_conditioned_samples)['outputs']

        # Decode to NoteSequence.
        midi_filename = self.decode(
            sample_ids,
            encoder=melody_conditioned_encoders['targets'])
        accompaniment_ns = mm.midi_file_to_note_sequence(midi_filename)

        result_path = os.path.join(responseFolderPath, 'result.mid')
        mm.sequence_proto_to_midi_file(
            accompaniment_ns, result_path)
        return result_path
