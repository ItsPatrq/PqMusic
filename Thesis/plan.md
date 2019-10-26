
# Transkrypcja muzyki: 
* Implementacja algorytmu Pertusa estymacji wysokości tonu (transkrypcja) (2-3)
* Dokończenie rozdziału - opis estymacji fundamentalnej i wielotonowej, opisanie Onsets and Frames razem z modelem Pertusa, przedstawienie Tensorboard ze statystykami z MIREX oraz porównanie wyników (3-4)
    * Algorytmy rozpoznawania wzorców dla polifonicznych
transkrypcja muzyki / Oparty na konwulencyjnej rekursywnej sieci


(5-7 dni)

# Generowanie muzyki
* Opis RNN i podpięcie implementacji do aplikacji. Stworzenie kilku modeli i zbiorów danych  (3)
    * model Magenta Melody RNN
        * Gotowe wytrenowane modele (basic_rnn, mono_rnn, lookback_rnn)
        * Wytrenowanie i ewaluacja modelu z użyciem SequenceExamples, porównanie wyników
    * Własny RNN
        * MIDI -> text -> RNN -> text -> MIDI == przygotowanie konwertera MIDI -> text i text -> MIDI który będzie użyty też w LSTM
        * Trenowanie tym samym zbiorym danych co model Magenty i porównanie
        * dokładny opis vanishing gradient problem z pokazaniem go w rezultacie
* Opis LSTM jako rozwinięcia RNN i jego użyteczności przy generowaniu muzyki (przykład impl) (2)
* [JEŚLI STARCZY CZASU] Opis + podpięcie do aplikacji GRU (Gated Recurrent Unit) jako uproszczone rozwiązanie LSTM
* Opis Relative Position jako rozwinięcie LSTM do procesu generowania muzyki + implementacja na podstawie Magenta Music Transformer (4)
    * Relative position
    * Dwa modele - jeden tworzący kontynuacje zadanego poczatku melodi, drógi uzupełniający melodię
* GPU w celu przyspieszenia trenowania
* OSzacowanie poprawności wyniku (tutaj wymagany research, możliwie użycie Generative Adversarial Networks (GANs)) (5?)

(około 14 dni)

## jesli starczy czasu
Dodanie sieci dla perkusji (nie powinno być większym problemem) + generator basu (na podstawie wyniku generowanej muzyki dopasować harmoniczny bas) aby złożyć utwór w całość

(max 5 dni?)

# Aplikacja

z racji na użyte technologie (aplikacja React + TS, server flask py3) można opisać dużo technikalii


# Seminaria
    Wtorki godz. 14:00