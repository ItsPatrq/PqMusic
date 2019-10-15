
# Transkrypcja muzyki: 
* Implementacja algorytmu Pertusa estymacji wysokości tonu (transkrypcja) (2-3)
* Dokończenie rozdziału - opis estymacji fundamentalnej i wielotonowej, opisanie Onsets and Frames razem z modelem Pertusa, przedstawienie Tensorboard ze statystykami z MIREX oraz porównanie wyników (3-4)

(5-7 dni)

# Generowanie muzyki
* Opis RNN i podpięcie implementacji do aplikacji. Stworzenie kilku zbiorów danych (3)
* Opis LSTM i jego użyteczności przy generowaniu muzyki (2)
* Opis Relative Position jako rozwinięcie LSTM do procesu generowania muzyki + implementacja na podstawie Magenta Music Transformer (4)
* OSzacowanie poprawności wyniku (tutaj wymagany research, możliwie użycie Generative Adversarial Networks (GANs)) (5?)

(około 14 dni)

## jesli starczy czasu
Dodanie sieci dla perkusji (nie powinno być większym problemem) + generator basu (na podstawie wyniku generowanej muzyki dopasować harmoniczny bas) aby złożyć utwór w całość

(max 5 dni?)

# Aplikacja

z racji na użyte technologie (aplikacja React + TS, server flask py3) można opisać dużo technikalii