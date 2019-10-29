* Spectral smoothness - gładzenie widma opiera się na zalożeniu, że fundamentalne nie zmieniają sie gwałtownie, i fakcie iż amplituda spada wraz ze wzrosetem hz 
* Learned Note Model opera się na niezerowej faktoryzacji macierzowej. Potrzebne są wektory dźwięków fundamentalnych danego instrumentu, które następnie porównywane są z badanym sygnałem przez ich modulacje

* Iterative Multi-Pitch estimation - iteruje przez wszystkie hipotezy F0 w kolejności zależnej od głośności lub wysokości. Każda iteracja wybiera fundamentalną, usuwa harmoniczne z transformaty, potem następna iteracja używa zmodyfikowanego spektrum. Az do moment kiedy nie mozna znalezc mocnej hipotezy. Dodatkowo poprawia jakość nałożenie modelu instrumentalnego i łagodzenia spektrum

### joined methods

* feature-based approach - Salience Score = loudness x smoothness dla każdego kandydata. Aplituda wszystkich harmonicznych kandydata a następnie interpolacyjno-wygładzony kształt jest generowany i odejmowany z pozostałych spektrum. Następnie wyliczany smoothnes factor na podstawie  modelu Gaussian, oraz sharpness factor dla highest-calculated harmonic. Ostateczna waga to dot produkt do kwadratu obu faktorów.


### Neural network

CNN + LSTM

loss function is the sum of two cross-entropy losses: one from the onset side and one from the frame side. Within the frame-based loss term, we apply a weighting to encourage accuracy at the start of the note. Because the weight vector assigns higher weights to the early frames of notes, the model is incentivized to predict the beginnings of notes accurately, thus preserving the most important musical events of the piece.