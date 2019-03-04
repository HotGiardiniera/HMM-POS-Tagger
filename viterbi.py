#!/usr/bin/python3
import sys, getopt
import json

DEBUG =  False
WORDS = None
POS = None
UNKNOWN_WORDS = set()

# Weighting for 2nd/first degree token path and for suffix imoprtance
TOKEN_BIAS = .5
HEURISTIC_BIAS = .7
MONOGRAM_WEIGHT = 0
BIGRAM_WEIGHT = .999
TRIGRAM_WEIGHT = .001

# Known types from the PennPOS list
proper_nouns = {'NNP', 'NNPS'}
nouns = {'NN', 'NNS'}
verbs = {'VB', 'VBD', 'VBG', 'VBN', 'VBZ'}
determinient = "DT"
adjectives = {"JJ", "JJR", "JJS"}

# Suffixes
NOUN_SUFFIXES = {
    "ion",
    "sion",
    "tion",
    "acy",
    "age",
    "hood",
    "ar",
    "or",
    "ism",
    "ist",
    "ment",
    "ness",
    "y",
    "ity"
}

ADJ_SUFFIXES = {
    "al",
    "ful",
    "ly",
    "ic",
    "ish",
    "like",
    "ous",
    "y",
    "ate",
    "able",
    "ible"
}

VERB_SUFFIXES = {
    "ify",
    "ate",
    "ize",
    "en"
}

def usage():
    sys.stdout.write('viterbi.py\n')
    sys.stdout.write("Note: This program expects two json files in the same directory:\n")
    sys.stdout.write("trainingDataPOS.json\n")
    sys.stdout.write("trainingDataWORD.json\n\n")
    sys.stdout.write("args\n")
    sys.stdout.write('-d  Optional. Debug mode\n')

def get_emission(state, word):
    #TODO handle unknown words properly
    # Idea 1 suffix matching to add bias
    if word not in WORDS:
        return 1/len(POS)
        # return -1 # Flag for unknown word
    pos = POS[state]
    if not pos['words'].get(word):
        return 0
    return pos['words'][word] / pos['count']

def get_transition(state, prev_state):
    pos = POS[prev_state]
    if not pos['arcs'].get(state):
        return 0
    return pos['arcs'][state] / pos['count']

def get_transition2(state, prev_state, prev_state2, prev_word, prev_word2):
    # Caclulates a two back transition
    pos2 = POS[prev_state2]
    cap = str(1) if prev_word[0].isupper() else str(0)
    total_prev_prev2 = pos2['arc_cap'].get(",".join([prev_state, cap]))
    if not total_prev_prev2:
        return 0
    cap = str(1) if prev_word2[0].isupper() else str(0)
    total_prev = pos2['two_arcs'].get(",".join([prev_state, state, cap]))
    if not total_prev:
        return 0
    return total_prev / total_prev_prev2

# Hueristic for proper noun checking
def checkproper(word, prev_state, state):
    bias = 0
    if word.istitle():
        if word.lower() in WORDS:
            if word[-1] == 's' and state == 'NNS':
                bias = HEURISTIC_BIAS
            if word[-1] != 's' and state == 'NN':
                bias = HEURISTIC_BIAS

        if prev_state == determinient or prev_state in verbs:
            if word[-1] == 's' and word[:-1] in UNKNOWN_WORDS:
                if state == 'NNPS':
                    bias = HEURISTIC_BIAS
            if word[-1] != 's' and state == 'NNP':
                bias = HEURISTIC_BIAS
    return bias

# Hueristic for checking suffixes
def check_suffix(word, state):
    # Firs strip out any plural form
    plural = False
    if len(word) > 3:
        if word[-3:] == "ies":
            plural = True
            word = word[:-3]
        elif word[-2:] == "es":
            plural = True
            word = word[:-2]
        elif word[-1] == "s":
            plural = True
            word = word[:-1]

    bias = 0

    if state in nouns and word.endswith(tuple(NOUN_SUFFIXES)):
        # Possible noun
        bias = .2
    elif state in verbs and word.endswith(tuple(ADJ_SUFFIXES)):
        # Possible Adj
        bias = .2
    elif state in adjectives and word.endswith(tuple(VERB_SUFFIXES)):
        # Possible verb TODO deal with superlatives
        bias = .2
    return bias




def maxargmaxprob(t, N, state, word, unique_pos, Viterbi, last_state, prev_word, prev_word2):
    pmax = -1
    argmax = (0,t-1)
    if word == "END":
        emission = 1
    else:
        emission = get_emission(unique_pos[state], word)
    for state_prime in range(1, N):
        trans = get_transition(unique_pos[state], unique_pos[state_prime])
        # trans = BIGRAM_WEIGHT*trans + TRIGRAM_WEIGHT*get_transition2(unique_pos[state], unique_pos[state_prime], last_state)
        local_prob = Viterbi[state_prime][t-1]
        if word not in WORDS and word != "END":
            trans = BIGRAM_WEIGHT*trans + TRIGRAM_WEIGHT*get_transition2(unique_pos[state], unique_pos[state_prime], last_state, prev_word, prev_word2)
            trans += MONOGRAM_WEIGHT* POS[unique_pos[state]]['count']/N
            # Proper noun check
            trans += checkproper(word, unique_pos[state_prime], unique_pos[state])
            # trans += check_suffix(word, unique_pos[state])
            emission = 1
        UNKNOWN_WORDS.add(word)

        local_prob *= trans * emission * 100

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
        sys.stdout.write('trainingDataPOS.json is not in invoking directory! Exiting...\n')
        sys.exit()

    try:
        with open('trainingDataWORD.json') as f:
            WORDS = json.load(f)
            unique_words = {w for w in WORDS}  # Set toe check if a word we are reding is in 
    except IOError:
        sys.stdout.write('trainingDataWORD.json is not in invoking directory! Exiting...\n')
        sys.exit()


    # Read our sentence file and split into sentences on newlines
    sentences = None
    with open(sentence_file) as f:
        data = f.read()
        sentences = data.split('\n\n')
        sentences = sentences[:-1]  # Need to remove the last space in the sentence
    
    N = len(unique_pos)  # This is our number of part of speeches includes start and end

    # File we are writing to
    outfile = sentence_file.split('/')[-1]
    outfile = outfile.split('.')[0]
    outfile = ".".join([outfile, "pos"])
    outfile = open(outfile, "w")

    for sentence in sentences:
    # for i in range(1):
    #     sentence = sentences[i]
        sentence = sentence.split('\n')
        T = len(sentence) # This is our time or columns


        viterbi = [ [0] * (T+2) for _ in range(N)]  # Generate a zero matrix of viterbi probabilities
        back_pointers = [ [0] * (T+2) for _ in range(N)]  

        # Intialize the verterbit for the start state(s)
        viterbi[0][0] = 1
        for i in range(1, len(unique_pos)-1):
            viterbi[i][1] = get_emission(unique_pos[i], sentence[0]) * get_transition(unique_pos[i], "START") * 100
            back_pointers[i][1] = (0,0)

        last_state = "START"

        for t in range(2, T+1):
            for s in range(1, N-1):
                pmax, argmax = maxargmaxprob(t, N-1, s, sentence[t-1], unique_pos, viterbi, last_state, sentence[t-2], sentence[t-3])
                viterbi[s][t] = pmax
                back_pointers[s][t] = argmax
                last_state = unique_pos[argmax[0]]

        best, endback = maxargmaxprob(T+1, N-1, len(unique_pos)-1, "END", unique_pos, viterbi, last_state, len(unique_pos)-2, len(unique_pos)-3)
        viterbi[N-1][T] = best
        back_pointers[N-1][len(sentence)] = endback

        pos_indicies = list()
        while(endback[1]):
            pos_indicies.append(unique_pos[endback[0]])
            endback = back_pointers[endback[0]][endback[1]]
        pos_indicies.reverse()

        # Below is for debugging our Viterbi matrix TODO delete when done
        # for t in range(1, N-1):
        #     print(unique_pos[t])
        # print("{0: <5} {1}".format('',list(range(T+1))))
        # for i, row in enumerate(back_pointers):
        #     print("{0: <5} {1}".format(unique_pos[i], row))
        # print(pos_indicies)

        # Finally write our sentence to the outfile
        for i, word in enumerate(sentence):
            word += "\t"+pos_indicies[i]+"\n"
            outfile.write(word)
        outfile.write("\n")

    outfile.close()
    sys.stdout.write("Done!\n")

if __name__ == '__main__':
    main()