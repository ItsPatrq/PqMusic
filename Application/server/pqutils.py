from pydub import AudioSegment

def convertAudioFileToMp3(file_path):
    if file_path.endswith(".mp3"):
            mp3 = AudioSegment.from_mp3(file_path)
            file_path = file_path[:-3] + "wav"
            mp3.export(file_path, format="wav")

    if file_path.endswith(".wav"):
        return file_path
    raise BaseException("File extension not supported")