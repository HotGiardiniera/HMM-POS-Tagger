#!/usr/bin/python3

import sys, getopt
import json
from collections import OrderedDict
from State import Pos, Word

DEBUG =  False

POS = OrderedDict()
TOTAL_POS = 0

WORDS = OrderedDict()
TOTAL_WORDS = 0

def usage():
    print('train_set.py')
    print("args")
    print("-f, --file=file                  Required. Corpus to add to training set")
    print("-t, --trainingset=trainingfile   Optional. File of existing training data to add to")
    print('-d                               Optional. Debug mode')


def main():
    opts, args = getopt.getopt(sys.argv[1:], "f:t:d", ["file=", "trainingset="])
    file = ''
    json_file ='' # A ssume training set data is held in a JSON file
    global DEBUG
    global TOTAL_WORDS
    for o, a in opts:
        if o == '-d':
            DEBUG = True
        elif o in ('-f', '--file'):
            file = a
        elif o in ('-j', '--json'):
            json_file = a

    START = None
    END = None

    if json_file:
        #TODO reload training data stored at JSON file
        # This will set the START and END states
        pass

    if not file:
        print("no file supplied")
        usage()
        exit(-1)

    if not START:
        START = Pos("START")

    if not END:
        end = Pos("END", 0)

    POS["START"] = START
    POS["END"] = end

    prev_state = START  # When opening a new training file we expect it to start with a new sentence

    with open(file) as f:
        line = f.readline()
        sentences = 0  # Count of the number of sentences
        while line:
            line = line.split()
            if line:
                word = WORDS.get(line[0])
                if word:
                    word.count += 1
                else:
                    word = Word(line[0])
                    WORDS[line[0]] = word

                pos = POS.get(line[1])
                if pos:
                    pos.count += 1
                else:
                    pos = Pos(line[1])
                    POS[line[1]] = pos
                
                # Set for word probabilities
                pos.words[word] += 1
                pos.word_count += 1

                # Set for transition probabilities
                prev_state.arcs[pos] += 1
                prev_state.arc_count += 1
                prev_state = pos

            else: # Need to deal with the end of a sentence
                prev_state.arcs[end] += 1
                prev_state.arc_count += 1
                sentences += 1
                prev_state = START
                START.count += 1
            line = f.readline()

    if DEBUG:
        TOTAL_WORDS = len(WORDS)
        TOTAL_POS = len(POS)

        print("Unique word: ", TOTAL_WORDS)
        print("Unique pos: ", TOTAL_POS)
        print("\n")
    # Lastly write our probabilities to a text file as to retrain the data
    training_file = 'trainingDataPOS.json'
    with open(training_file, 'w') as out:
        json_list = dict()
        for k,v in POS.items():
            if json_list.get(k):
                print("FATAL! duplicate POS, counts will be off!")
                exit(-1)
            json_list[k] = v.as_JSON()
        json.dump(json_list, out, indent=2)
        print("Training POS data written to", training_file)
    
    training_file_words = "trainingDataWORD.json"
    with open(training_file_words, 'w') as out:
        json_list = dict()
        for k,v in WORDS.items():
            if json_list.get(k):
                print("FATAL! duplicate words, counts will be off!")
                exit(-1)
            json_list[k] = v.count

        json.dump(json_list, out, indent=2)
        print("Training WORD data written to", training_file_words)

if __name__ == '__main__':
    main()