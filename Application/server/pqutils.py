from pydub import AudioSegment
import ntpath
ntpath.basename("a/b/c")

def convertAudioFileToMp3(file_path):
    if file_path.endswith(".mp3"):
            mp3 = AudioSegment.from_mp3(file_path)
            file_path = file_path[:-3] + "wav"
            mp3.export(file_path, format="wav")

    if file_path.endswith(".wav"):
        return file_path

    exception = BaseException("File extension not supported")
    raise exception

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)