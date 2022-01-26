import json
import sys
import numpy as np
import random
from virtual_scaffold import sequence_creator
import time

# old parser, doesn't work if strands are not sequential, i.e. 0,1,3,4...


def ParseJson():
    """
    Parse cadnano json file given by as command line argument.
    Returns number of strands, length of strands (number of bases),
    scaffolds and staple data.
    """

    # Find json file location from argument input
    if len(sys.argv) < 3:
        sys.exit(
            "Not enough files provided.\nPlease use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")
    elif len(sys.argv) > 3:
        sys.exit(
            "Too many files provided provided.\nPlease use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")

    else:
        inputJson = sys.argv[1]

    # Load cadnano data
    with open(inputJson, 'r') as json_data:
        cadnanoData = json.load(json_data)

    strandData = cadnanoData['vstrands']
    numStrands = len(strandData)
    lengthStrands = len(strandData[0]['scaf'])

    # Initialize arrays
    scaffolds = np.empty(numStrands, dtype=object)
    staples = np.empty(numStrands, dtype=object)
    # row = np.empty(numStrands, dtype=object)
    # col = np.empty(numStrands, dtype=object)
    # num = np.empty(numStrands, dtype=object)

    # Load data of scaffolds and staples
    for i in range(numStrands):
        scaffolds[i] = strandData[i]['scaf']
        staples[i] = strandData[i]['stap']
        # row[i] = strandData[i]['row']
        # col[i] = strandData[i]['col']
        # num[i] = strandData[i]['num']

    return numStrands, lengthStrands, scaffolds, staples

# New parser, puts empty strands if strand is skipped, i.e. 0,1,3,4...


def ParseJsonNew():
    """
    Parse cadnano json file given by as command line argument.
    Returns number of strands, length of strands (number of bases),
    scaffolds and staple data.
    """

    # Find json file location from argument input
    if len(sys.argv) < 3:
        sys.exit(
            "Not enough files provided.\nPlease use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")
    elif len(sys.argv) > 3:
        sys.exit(
            "Too many files provided provided.\nPlease use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")

    else:
        inputJson = sys.argv[1]

    # Load cadnano data
    with open(inputJson, 'r') as json_data:
        cadnanoData = json.load(json_data)

    strandData = cadnanoData['vstrands']

    # Numbers contained in strands
    nums = []
    for i in range(len(strandData)):
        currNum = strandData[i]['num']
        nums.append(currNum)

    maxNum = max(nums)+1

    numStrands = maxNum
    lengthStrands = len(strandData[0]['scaf'])

    # Initialize arrays
    scaffolds = np.empty(numStrands, dtype=object)
    staples = np.empty(numStrands, dtype=object)
    # row = np.empty(numStrands, dtype=object)
    # col = np.empty(numStrands, dtype=object)
    # num = np.empty(numStrands, dtype=object)

    emptyStrand = []
    for i in range(lengthStrands):
        emptyStrand.append([-1, -1, -1, -1])

    # Load data of scaffolds and staples
    for i in range(numStrands):
        # If i exist in nums, set strandData
        if i in nums:
            scaffolds[i] = strandData[nums.index(i)]['scaf']
            staples[i] = strandData[nums.index(i)]['stap']
        # if strand doesn't exist
        else:
            scaffolds[i] = emptyStrand
            staples[i] = emptyStrand

    return numStrands, lengthStrands, scaffolds, staples


def RawScaffoldSequence():
    """
    Returns raw scaffold sequence from input file
    """

    # Find scaffold sequence file location from argument input
    if len(sys.argv) < 3:
        sys.exit(
            "No file provided. Please use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")
    else:
        inputScaffold = sys.argv[2]

    # Load scaffold sequence data
    with open(inputScaffold, 'r') as file:
        scaffold_seq = file.read().replace('\n', '')

    return scaffold_seq


def ForwardTraverse(strand, startBase):
    """
    Traverse scaffold/staple strand forward by a single base.
    Returns next adjacent base and block.
    """

    currentBase = startBase
    currentBlock = strand[currentBase[0]][currentBase[1]]

    nextBase = [currentBlock[2], currentBlock[3]]
    nextBlock = strand[nextBase[0]][nextBase[1]]

    return nextBase, nextBlock


def ReverseTraverse(strand, startBase):
    """
    Traverse scaffold/staple strand by a single base in reverse.
    Returns previous adjacent base and block.
    """

    currentBase = startBase
    currentBlock = strand[currentBase[0]][currentBase[1]]

    prevBase = [currentBlock[0], currentBlock[1]]
    prevBlock = strand[prevBase[0]][prevBase[1]]

    return prevBase, prevBlock


def TraverseEntireForward(strand, startSearchBase):
    """
    Traverse entire strand forward, returns end base.
    If start search base doesn't have adjacent strands, i.e. [-1,-1,-1,-1],
    return [-1,-1]. If no breakpoint is found, will exit.
    """

    currentBase = startSearchBase
    currentBlock = strand[currentBase[0]][currentBase[1]]

    # If current block is empty, return empty base
    if currentBlock == [-1, -1, -1, -1]:
        return [-1, -1]

    nextBase, nextBlock = ForwardTraverse(strand, currentBase)

    # Traverse scaffolds until next base is [-1,-1]
    while nextBase != [-1, -1]:
        currentBlock = nextBlock
        currentBase = nextBase

        nextBase, nextBlock = ForwardTraverse(strand, currentBase)

        # Catch infinite loop when strand doesnt have breakpoint
        if nextBase == startSearchBase:
            print("Error: Loop detected at base: " +
                  str(startSearchBase[0]) + "[" + str(startSearchBase[1]) + "]")
            print("Make sure staple or scaffolds at this base has a start and end base")
            sys.exit("Scaffold or staple does not have breakpoint")

    endBase = currentBase

    return endBase


def TraverseEntireReverse(strand, startSearchBase):
    """
    Traverse entire strand in reverse, returns start base.
    If start search base doesn't have adjacent strands, i.e. [-1,-1,-1,-1],
    return [-1,-1]. If no breakpoint is found, will exit.
    """

    currentBase = startSearchBase
    currentBlock = strand[currentBase[0]][currentBase[1]]

    # If current block is empty, return empty base
    if currentBlock == [-1, -1, -1, -1]:
        return [-1, -1]

    prevBase, prevBlock = ReverseTraverse(strand, currentBase)

    # ForwardTraverse scaffolds until previous base is [-1,-1]
    while prevBase != [-1, -1]:
        currentBlock = prevBlock
        currentBase = prevBase

        prevBase, prevBlock = ReverseTraverse(strand, currentBase)

        # Catch infinite loop when strand doesnt have breakpoint
        if prevBase == startSearchBase:
            print("Error: Loop detected at base: " +
                  str(startSearchBase[0]) + "[" + str(startSearchBase[1]) + "]")
            print("Make sure staple or scaffolds at this base has a start and end")
            sys.exit("Scaffold or staple does not have breakpoint")

    startBase = currentBase

    return startBase


def FindStartEnd(strand, numStrands, lengthStrands):
    """
    Returns all start and end bases of given strand.
    """

    startBases = []
    # Check all strands
    for i in range(numStrands):
        # Check all bases in each strand
        for j in range(lengthStrands):

            startSearchBase = [i, j]
            startBase = TraverseEntireReverse(strand, startSearchBase)

            if startBase != [-1, -1]:
                startBases.append(startBase)

    # Extracts only unique start bases
    startBases = [list(x) for x in set(tuple(x)
                                       for x in startBases)]

    # Find corresponding end bases
    endBases = [None]*len(startBases)
    for i in range(len(startBases)):
        endBases[i] = TraverseEntireForward(strand, startBases[i])

    return startBases, endBases


def CheckMultipleBase(startBase):
    """
    Checks if startBase contains multiple bases, if so returns true. Ex:\n
    startBase = [0,50] -> returns false\n
    startBase = [[3, 82], [0, 45]] -> returns true\n
    This to avoid len(startBase) == 2 for both examples above.
    """

    return any(isinstance(el, list) for el in startBase)


def FindLength(strand, startSearchBase):
    """
    Returns length of sequences for the start bases provided.
    """

    maxRange = len(startSearchBase)
    length = [None] * len(startSearchBase)

    # To avoid i.e. [0,50] and [[3, 82], [0, 45]] both having length 2
    if len(startSearchBase) == 2:
        if CheckMultipleBase(startSearchBase):
            maxRange = 2
        else:
            length = [None] * 1
            maxRange = 1

    for i in range(maxRange):
        if CheckMultipleBase(startSearchBase):
            currentBase = startSearchBase[i]
        else:
            currentBase = startSearchBase

        currentBlock = strand[currentBase[0]][currentBase[1]]
        length[i] = 0

        # If current block is empty, return empty base
        if currentBlock == [-1, -1, -1, -1]:
            break

        nextBase, nextBlock = ForwardTraverse(strand, currentBase)
        length[i] = length[i] + 1

        # Traverse strand until next base is [-1,-1]
        while nextBase != [-1, -1]:
            currentBlock = nextBlock
            currentBase = nextBase

            nextBase, nextBlock = ForwardTraverse(strand, currentBase)
            length[i] = length[i] + 1

    return length


# Unused
def RandomScaffoldSequence(length):
    """
    Generates random sequence of size length with each base equal probability.
    """

    randomSequence = []

    # Random number based on uniform distribution
    for i in range(length):
        randomNum = random.uniform(0, 1)

        if randomNum <= 0.25:
            randomSequence.append('A')
        elif randomNum > 0.25 and randomNum <= 0.5:
            randomSequence.append('T')
        elif randomNum > 0.5 and randomNum <= 0.75:
            randomSequence.append('G')
        elif randomNum > 0.75:
            randomSequence.append('C')

    # Convert list to string
    randomSequence = ''.join(randomSequence)

    return randomSequence


def FindSingleScaffold(scaffold, startBase, inputSequence):
    """
    Appends base letter from inputSequence to each base in scaffold.
    Returns sequence containing bases and base letters.
    """

    finalSequence = []

    currentBase = startBase
    currentBlock = scaffold[currentBase[0]][currentBase[1]]

    currentBase.append(inputSequence[0])
    finalSequence.append(currentBase)

    nextBase, nextBlock = ForwardTraverse(scaffold, currentBase)
    cnt = 1

    # Traverse scaffold until nextBase is [-1,-1]
    while nextBase != [-1, -1]:

        currentBase = nextBase
        currentBlock = nextBlock

        currentBase.append(inputSequence[cnt])
        finalSequence.append(currentBase)

        nextBase, nextBlock = ForwardTraverse(scaffold, currentBase)
        cnt += 1

    return finalSequence


def FindScaffoldSequences(scaffold, scaffoldStartBase, rawScaffoldSequence):
    """
    Returns all scaffolds sequences, assigns the rawScaffoldSequence to the
    longest scaffold. The other scaffolds get pseudorandomly generated sequences.
    """

    lengthScaffolds = FindLength(scaffold, scaffoldStartBase)

    # Exit if no scaffold is found
    if lengthScaffolds == []:
        sys.exit("No scaffolds found")

    maxIndex = np.argmax(lengthScaffolds)
    maxRange = len(lengthScaffolds)
    finalSequence = [None] * maxRange

    # Exit if scaffold sequence provided is not long enough
    if lengthScaffolds[maxIndex] > len(rawScaffoldSequence):
        sys.exit(
            "Scaffold sequence given is not long enough.\nScaffold input length: "
            + str(len(rawScaffoldSequence)) + "\nLongest scaffold: "
            + str(lengthScaffolds[maxIndex]) + "\nPlease provide a longer sequence.")

    for i in range(maxRange):
        if CheckMultipleBase(scaffoldStartBase):
            currentBase = scaffoldStartBase[i]
        else:
            currentBase = scaffoldStartBase

        if i == maxIndex:
            finalSequence[i] = FindSingleScaffold(
                scaffold, currentBase, rawScaffoldSequence)
        else:
            # Generate random sequence based on GC content, etc (from virtual_scaffold.py)
            randomScaffoldSequence, _ = sequence_creator(lengthScaffolds[i])
            finalSequence[i] = FindSingleScaffold(
                scaffold, currentBase, randomScaffoldSequence)

    return finalSequence


def Complement(inputBase):
    """
    Returns the complementary base of input base.
    """

    if inputBase == 'A':
        return 'T'
    elif inputBase == 'T':
        return 'A'
    elif inputBase == 'G':
        return 'C'
    elif inputBase == 'C':
        return 'G'
    else:
        sys.exit("Not a valid base")


def FindStapleBase(stapleBase, scaffoldSequence):
    """
    Runs through all scaffolds to find the letter at same position as the staple base.
    If found, returns complement of that letter. If not found, the staple base
    is not connected to a scaffold, and it will be assigned the base letter 'A'.
    """

    baseLetter = -1
    # For each scaffold
    for j in range(len(scaffoldSequence)):
        # For every base in scaffold
        currentScaffold = scaffoldSequence[j]
        for i in range(len(currentScaffold)):
            # If base matches staple base, return complement
            if stapleBase[0] == currentScaffold[i][0] and stapleBase[1] == currentScaffold[i][1]:
                baseLetter = Complement(currentScaffold[i][2])

    # If no corresponding scaffolds is found, assign 'A'
    if baseLetter == -1:
        baseLetter = 'A'

    return baseLetter


def FindStapleSequences(staples, stapleStartBases, scaffoldSequence):
    """
    Traverses all staple sequences, finds complementary scaffold base letter and
    appends it to each staple base. Returns all staple sequences.
    """

    finalSequence = [None] * len(stapleStartBases)

    for i in range(len(stapleStartBases)):

        currentBase = stapleStartBases[i]
        currentBlock = staples[currentBase[0]][currentBase[1]]

        baseLetter = FindStapleBase(currentBase, scaffoldSequence)
        currentBase.append(baseLetter)
        finalSequence[i] = [currentBase]

        nextBase, nextBlock = ForwardTraverse(staples, currentBase)

        # ForwardTraverse scaffolds until nextBase is [-1,-1]
        while nextBase != [-1, -1]:

            currentBase = nextBase
            currentBlock = nextBlock

            baseLetter = FindStapleBase(currentBase, scaffoldSequence)
            currentBase.append(baseLetter)
            finalSequence[i].append(currentBase)

            nextBase, nextBlock = ForwardTraverse(staples, currentBase)

    return finalSequence


def PrintSequence(sequence, fileName, view=1):
    """
    Prints sequence to file, 0 = detailed view, 1 = cadnano view
    """

    # Open file
    outputFile = open(fileName, 'w')

    # Print in detailed view
    if view == 0:
        for i in range(len(sequence)):
            outputFile.write("Staple " + str(i) + ":\n")
            for seq in sequence[i]:
                outputFile.write(str(seq) + "\n")
            outputFile.write("\n")

    # Print in cadnano style view
    elif view == 1:
        outputFile.write("Start,End,Sequence,Length\n")
        for i in range(len(sequence)):
            currentSequence = sequence[i]
            outputFile.write(str(currentSequence[0][0]) + "[" + str(currentSequence[0][1]) + "]," +
                             str(currentSequence[-1][0]) + "[" + str(currentSequence[-1][1]) + "],")
            cnt = 0
            for j in range(len(currentSequence)):
                outputFile.write(str(currentSequence[j][2]))
                cnt += 1
            outputFile.write("," + str(cnt) + "\n")
    else:
        sys.exit("Not a valid print mode.")

    # Close file
    outputFile.close()


def VerifyStaples(stapleSequence):

    # Check for staples longer than 60 or shorter than 15
    for i in range(len(stapleSequence)):
        if len(stapleSequence[i]) > 60:
            print("Warning: staple " + str(i) +
                  " at " + str(stapleSequence[i][0][0]) + "[" + str(stapleSequence[i][0][1]) + "]" + " has length " + str(len(stapleSequence[i])) + " (>60)")
        elif len(stapleSequence[i]) < 15:
            print("Warning: staple " + str(i) +
                  " at " + str(stapleSequence[i][0][0]) + "[" + str(stapleSequence[i][0][1]) + "]" + " has length " + str(len(stapleSequence[i])) + " (<15)")

    # # Check for many A's next to eachother
    # for i in range(len(stapleSequence)):
    #     if len(stapleSequence[i]) >= 7:
    #         for j in range(len(stapleSequence[i]) - 6):
    #             if stapleSequence[i][j][2] == stapleSequence[i][j+1][2] == stapleSequence[i][j+2][2] == stapleSequence[i][j+3][2] == stapleSequence[i][j+4][2] == stapleSequence[i][j+5][2] == stapleSequence[i][j+6][2] == 'A':
    #                 print("Warning: staple " + str(i) +
    #                       " at " + str(stapleSequence[i][0][0]) + "[" + str(stapleSequence[i][0][1]) + "]" + " more than 7 consecutive A's")
    #                 break


def main():
    """
    Main program loop
    """

    # load data
    print("Parsing json file...")
    numStrands, lengthStrands, scaffolds, staples = ParseJsonNew()

    print("Parsing scaffold sequence...")
    rawScaffoldSequence = RawScaffoldSequence()

    # staples
    print("Finding staples...")
    stapleStartBases, stapleEndBases = FindStartEnd(
        staples, numStrands, lengthStrands)

    # scaffolds
    print("Finding scaffolds...")
    scaffoldStartBase, scaffoldEndBase = FindStartEnd(
        scaffolds, numStrands, lengthStrands)

    # Returns scaffolds sequence
    print("Generating scaffold sequences...")
    scaffoldSequence = FindScaffoldSequences(
        scaffolds, scaffoldStartBase, rawScaffoldSequence)

    # Returns staple sequences
    print("Generating staple sequences...")
    stapleSequence = FindStapleSequences(
        staples, stapleStartBases, scaffoldSequence)

    # Verifying staples
    print("Verifying staples...")
    VerifyStaples(stapleSequence)

    # IO
    print("Outputting to file...")
    PrintSequence(scaffoldSequence, "scaffolds.txt")
    PrintSequence(stapleSequence, "staples.txt")

    print("Done!")


time_start = time.time()
main()
time_elapsed = (time.time() - time_start)
print("Time elapsed: " + str(time_elapsed) + " seconds")
