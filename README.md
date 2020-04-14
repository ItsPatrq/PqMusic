# PqMusic 
_eng_

Project written as part of magister thesis research on studying state of the art on music transcription system.

* *Thesis* folder contains complete papier with LaTex source code and images used.
* *Application/static* folder contains GUI written as a web application
* *Application/server* folder contains algorithms implemented in python as well as server side of GUI

***
_pl_


* Folder *Thesis* zawiera pełny papier z kodem źródłowym LaTex i wykorzystanymi obrazami.
* Folder *Application/static* zawiera GUI napisane jako aplikacja internetowa
* Folder *Application/server* zawiera algorytmy zaimplementowane w Pythonie oraz po stronie serwera GUI

***
Wszystkie algorytmy dostępne są w folderze Application/transcription/*.py. Każdy z nich zawiera sekcje _if __name__ == "__main__":_, pod którą jest skrypt do przetestowania danego algorytmu, na wzór którego można w prosty sposób zmienić parametry wywołania algorytmu.

Sposób uruchomienia GUI:

W folderze Application/static wykonać komendy _npm install_ oraz _npm build_, co spowoduje zbudowanie paczki ze stroną i skryptami. Następnie należy uruchomić skrypt z pliku Application/server/server.py. Spowoduje to uruchomienie servera HTTP hostującego GUI pod lokalnym adresem http://127.0.0.1:5000/.
***

## Wymagania:
1. Python 3.7.4 wraz z modułami dostępnymi poprzez _pip install_:
    * numpy 1.17.2
    * scipy 1.3.1
    * matplotlib 3.1.1
    * networkx 2.3
    * midiutil 1.2.1
    * mido 1.2.9
    * tensorflow 1.15.2
    * tqdm 4.36.1
    * aubio 0.4.9
    * pydub 0.23.1
    * magenta 1.2.2 + librosa 0.7.2 (dla algorytmu Onsets and Frames)
    * reikna 0.7.4 + pycuda 2019.1.2 (dla algorytmów wykonywanych na GPU)
    * flask 1.1.1 + flask_cors 3.0.8 (dla GUI)
1. Node.js v12.13.1 (GUI)
1. npm 6.12.1 (GUI)
1. ffmpeg 4.2 (brew install ffmpeg)
1. FluidSynth (1.1) _(brew install fluid-synth)_ ->
(brew install pkg-config
(git clone https://github.com/FluidSynth/fluidsynth.git
cd fluidsynth
git checkout 1.1.x
mkdir build
cd build
cmake ..
sudo make install
fluidsynth --version) or
(brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/34dcd1ff65a56c3191fa57d3dd23e7fffd55fae8/Formula/fluid-synth.rb)
