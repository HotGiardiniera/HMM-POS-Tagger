#!/usr/bin/python3
import sys, getopt
import json

DEBUG =  False
WORDS = None
POS = None

def usage():
    print('viterbi.py')
    print("Note: This program expects two json files in the same directory:")
    print("trainingDataPOS.json")
    print("trainingDataWORD.json\n")
    print("args")
    print('-d  Optional. Debug mode')

def get_emission(state, word):
    pos = POS[state]
    if not pos['words'].get(word):
        #TODO handle unknown words properly
        return 1/pos['word_count']
    return pos['words'][word] / pos['word_count']

def get_transition(state, prev_state):
    pos = POS[prev_state]
    if not pos['arcs'].get(state):
        return 0
    return pos['arcs'][state] / pos['arc_count']

def maxargmaxprob(t, N, state, emission, unique_pos, Viterbi):
    pmax = -1
    argmax = (0,t-1)
    for state_prime in range(1, N):
        trans = get_transition(unique_pos[state], unique_pos[state_prime])
        local_prob = Viterbi[state_prime][t-1] * trans * emission
        if local_prob > pmax:
            pmax = local_prob
            argmax = (state_prime, t-1)
    return pmax, argmax


def main():
    global DEBUG
    VERBOSE = False
    sentence_file = "WSJ_POS_CORPUS_FOR_STUDENTS/WSJ_24.words"
    opts, args = getopt.getopt(sys.argv[1:], "hds:v", ["help","sentences="])
    for o, a in opts:
        if o == '-d':
            DEBUG = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--sentences"):
            sentence_file = a
        elif o == '-v':
            VERBOSE = True

    global WORDS
    global POS

    try:
        with open('trainingDataPOS.json') as f:
            POS = json.load(f)
            unique_pos = {p for p in POS}
            unique_pos = list(unique_pos) # These will be used for our POS column matching
            unique_pos.sort() # keep sorted so its consistent across runs of this program and debugging
            start = unique_pos.index("START")
            end = unique_pos.index("END")
            del unique_pos[start]
            del unique_pos[end]
            unique_pos.insert(0, "START")
            unique_pos.insert(len(unique_pos),"END")
    except IOError:
        print('trainingDataPOS.json is not in invoking directory! Exiting...')
        sys.exit()

    try:
        with open('trainingDataWORD.json') as f:
            WORDS = json.load(f)
            unique_words = {w for w in WORDS}  # Set toe check if a word we are reding is in 
    except IOError:
        print('trainingDataWORD.json is not in invoking directory! Exiting...')
        sys.exit()

    # print(POS)


    # Read our sentence file and split into sentences on newlines
    sentences = None
    with open(sentence_file) as f:
        data = f.read()
        sentences = data.split('\n\n')
        sentences = sentences[:-1]  # Need to remove the last space in the sentence
    
    N = len(unique_pos)  # This is our number of part of speeches includes start and end
    print(sentences)

    # File we are writing to
    outfile = sentence_file.split('/')[-1]
    outfile = outfile.split('.')[0]
    outfile = ".".join([outfile, "pos"])


    for sentence in sentences:
    # for i in range(2):
        # sentence = sentences[i].split('\n')
        sentence = sentence.split('\n')
        # print(s)
        T = len(sentence) # This is our time or columns

        print("sentence", sentence)

        viterbi = [ [0] * (T+2) for _ in range(N)]  # Generate a zero matrix of viterbi probabilities
        back_pointers = [ [0] * (T+2) for _ in range(N)]  

        # Intialize the verterbit for the start state(s)
        viterbi[0][0] = 1
        for i in range(1, len(unique_pos)-1):
            viterbi[i][1] = get_emission(unique_pos[i], sentence[0]) * get_transition(unique_pos[i], "START") * 100
            back_pointers[i][1] = (0,0)

        for t in range(2, T+1):
            for s in range(1, N-1):
                emission_here = get_emission(unique_pos[s], sentence[t-1])
                pmax, argmax = maxargmaxprob(t, N-1, s, emission_here, unique_pos, viterbi)
                viterbi[s][t] = pmax
                back_pointers[s][t] = argmax

        # print("Final time", T)
        best, endback = maxargmaxprob(T+1, N-1, len(unique_pos)-1, 1, unique_pos, viterbi)
        viterbi[N-1][T] = best
        back_pointers[N-1][len(sentence)] = endback

        pos_indicies = list()
        while(endback[1]):
            pos_indicies.append(unique_pos[endback[0]])
            endback = back_pointers[endback[0]][endback[1]]
        pos_indicies.reverse()

        # for t in range(1, N-1):
        #     print(unique_pos[t])
        # print("{0: <5} {1}".format('',list(range(T+1))))
        # for i, row in enumerate(back_pointers):
        #     print("{0: <5} {1}".format(unique_pos[i], row))
        print(pos_indicies)

        # Finally write to a file called 

if __name__ == '__main__':
    main()