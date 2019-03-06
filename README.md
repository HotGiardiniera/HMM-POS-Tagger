Hidden Markov Model Part of Speech Tagger using the Viterbi algorithm

Requirments: Python 3.x


------------------------------------------------------------------------
Training:

Invoked with ./train\_set.py -f \<path to training file\>

Other arguments can be seen through ./train\_set.py --help

------------------------------------------------------------------------
Viterbi:

Invoked with ./viterbi.py

With no arguments it assumes there is a file in the invoking directory called 'WSJ\_24.words'

You can specify a sentence file with the '-s' argument as in ./viterbi.py -s \<path\_to\_sentence\_file\>
All sentence files are assumed to be a word on each line and sentences seperated by a new line

Other arguments can be seen through ./viterbi.py --help

Note: This program expects two json files in the same directory:
trainingDataPOS.json
trainingDataWORD.json

