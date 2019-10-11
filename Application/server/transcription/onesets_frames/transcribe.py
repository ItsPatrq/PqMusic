def transcribe(requestFile, responseFile):
    exampleFile = open(requestFile)
    uploaded = {
        exampleFile.name: exampleFile.read()
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
    midi_filename = (responseFile)
    midi_io.sequence_proto_to_midi_file(sequence_prediction, midi_filename)

    file.save(midi_filename)
