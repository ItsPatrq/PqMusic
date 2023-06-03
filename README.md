
# PqMusic

Demo available <a href="https://pqmusic.fly.dev/">here</a>

## ENG

### Application for music transcription

* The *static* folder contains a GUI written as a web application
* The *server* folder contains the algorithms implemented in Python and server-side GUI

All algorithms are available in the transcription/*.py folder. Each of them contains the section _if __name__ == "__main__":_, under which there is a script to test a given algorithm, following the example of which you can easily change the parameters of the algorithm call.

For the Onsets and Frames algorithm to work properly, it is required to download the checkpoint of the trained model from the Onsets and Frames repository and place it in the server/transcription/train directory

Methods are prepared in the server/utils/evaluate module for evaluating all methods. The attached files contain the "monoSound" database that allows you to test the algorithms on monophonic signals. To test polyphonic signals, it is best to download the Maestro database, whose metadata.json is compatible with the project, and place it in a dedicated directory.

*How to launch the GUI*:

In the static folder, execute the commands _npm install_ and _npm build_, which will build a package with the website and scripts. Then run the script from the server/server.py file. This will start the HTTP server hosting the GUI at the local address http://127.0.0.1:5000/.

#### Requirements

1. Python 3.7.4:
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
    * magenta 1.2.2 + librosa 0.7.2 (for Onsets and Frames)
    * reikna 0.7.4 + pycuda 2019.1.2 (for GPU algorithms)
    * flask 1.1.1 + flask_cors 3.0.8 (for GUI)
1. Node.js v12.13.1 (GUI)
1. npm 6.12.1 (GUI)
1. ffmpeg 4.2
1. FluidSynth (1.1)

    (git clone https://github.com/FluidSynth/fluidsynth.git

    cd fluidsynth

    git checkout 1.1.x

    mkdir build

    cd build

    cmake ..

    sudo make install

    fluidsynth --version)

Required python libraries are listed in the requirements.txt file to facilitate pip installation

## PL

### Aplikacja  do transkrypcji muzycznej

* Folder *static* zawiera GUI napisane jako aplikacja internetowa
* Folder *server* zawiera algorytmy zaimplementowane w Pythonie oraz po stronie serwera GUI

Wszystkie algorytmy dostępne są w folderze transcription/*.py. Każdy z nich zawiera sekcje _if __name__ == "__main__":_, pod którą jest skrypt do przetestowania danego algorytmu, na wzór którego można w prosty sposób zmienić parametry wywołania algorytmu.

Dla poprawnego działania algorytmu Onsets and Frames wymagane jest pobranie checkpoint-a wytrenowanego modelu z repozytorium Onsets and Frames i umieszczenie go w katalogu server/transcription/train

Do ewaluacji wszystkich metod przygotowane są w module server/utils/evaluate metody. Załączone pliki zawierają bazę "monoSound" pozwalającą przetestować algorytmy na sygnałach monofonicznych. Do przetestowania sygnałów polifonicznych najlepiej pobrać bazę Maestro, której metadane.json są kompatybilne z projektem, i umieścić w dedykowanym katalogu.

Sposób uruchomienia GUI:

W folderze static wykonać komendy _npm install_ oraz _npm build_, co spowoduje zbudowanie paczki ze stroną i skryptami. Następnie należy uruchomić skrypt z pliku server/server.py. Spowoduje to uruchomienie servera HTTP hostującego GUI pod lokalnym adresem http://127.0.0.1:5000/.

#### Wymagania:

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
1. FluidSynth (1.1) _(brew install fluid-synth)_ -> instalacja:
(brew install pkg-config)

    (git clone https://github.com/FluidSynth/fluidsynth.git

    cd fluidsynth

    git checkout 1.1.x

    mkdir build

    cd build

    cmake ..

    sudo make install

    fluidsynth --version)

    or

    (brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/34dcd1ff65a56c3191fa57d3dd23e7fffd55fae8/Formula/fluid-synth.rb)

W pliku requirements.txt wylistowane są wyamagne biblioteki python w celu ułatwienia instalacji przez pip
