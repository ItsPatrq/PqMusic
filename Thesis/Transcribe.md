
/*
stereo => mono

Paris Smaragdis and Judith C. Brown. Non-negative matrix factorization for poly-
phonic music transcription. In 2003 IEEE Workshop on Applications of Signal

Processing to Audio and Acoustics, pages 177–180, 2003.

Mark C. Wirt. MIDIUtil: A pure python library for creating multi-track MIDI
files. https://pypi.org/project/MIDIUtil/, 2018.
*/

/*
Old way to transcribe required lower sample rate or artifically down-sample input

Antonio Pertusa and Jose M. I  ́ nesta. Multiple fundamental frequency estima-  ̃
tion using Gaussian smoothness. In IEEE International Conference on Acoustics,
Speech and Signal Processing (ICASSP 2008), pages 105–108, 2008.
*/


## Subtasks: 
* pitch estimation
* note tracking
* instrument detection
* harmony identification
* analiza i opis sceny muzycznej (taski poza transkrypcją, Kunio Kashino. Auditory scene analysis in music signals. In Signal Processing
Methods for Music Transcription, pages 299–325. Springer, 2006 ; Masataka Goto. Music scene description. In Signal Processing Methods for Music
Transcription, pages 327–359. Springer, 2006.)

### oszacowanie wysokości tonu
* single i multi
* Single - problem praktycznie rozwiązany, główny research poprzez estymacje mowy


### Note tracking
* Również powiązany problem z oszacowaniem rytmu i tempa
* Proste rozwiązanie zakłada próg długości nuty i jej głośności (Arnaud Dessein, Arshia Cont, and Guillaume Lemaitre. Real-time polyphonic
music transcription with non-negative matrix factorization and beta-divergence.
In 11th International Society for Music Information Retrieval Conference (ISMIR
2010), pages 489–494, 2010.)


# PDA (Pitch Estimation Algorithm)

## estymacja oparta na okresowości
Pierwsze algorytmy szukające częstotliwości funamentalnych operowały na wejściowym sygnale szukając wzorców w odległościach pomiędzy pikami fali i regularnościach tej fali. Analiza pików fali jest nieużywana w algorytmach estymaujących fundamentalną wysokość, tak wyszukiwanie wzorców i periodyczności jest szeroko używane. Założenie -> fala quazi-okresowa w wymiarach czas-amplituda. Funkcja korelacji jest funkcją od okresu (czasu) która zwraca pomiar tego, jak dobrze to oszacowanie okresowości pokrywa się z regularnością kształtu fali. Są dość odporne na szumy. Minusy - potrzeba długiego okna czasowego tej samej częstotliwości (problem przy wykrywaniu mowy) i częste pomyłki hipotezy o częstotliwości będącej wielokrotnością  poprawnego wyniku (jeśli coś jest T-okresowe, to jest też 2T, 3T... okresowe). Bardziej problematyczne jest granie więcej niż jednej nuty w tym samym czasie. T1 i T2 obu nut, fala nie będzie okresowa w żadnym z tych okresów (chyba że są wielokrotnością siebie). Przy częstotliwościach składowych nie jest to problem, ponieważ zawsze będą wielokrotnością fundamentalnej.
### Algorytmy wykorzystukące okresowość do wygenerowania wagowej hipotezy fundamentalnej częstotliwości:
* ACF -> autocorelation function _[Lawrence Rabiner. Ontheuseofautocorrelationanalysisforpitchdetection. IEEE TransactionsonAcoustics,Speech,andSignalProcessing,25(1):24–33,1977]_

    asdas $\sum{}$
* NCCF -> Normalized Cross-corelation function  _[David Talkin A robust algorithm for pitch tracking (RAPT). Speech Coding and Synthesis,495:518,1995.]_ (w tym artykule także "What is pitch?")


