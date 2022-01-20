import json
import sys
import numpy as np


def ParseJson():
    """
    Parse cadnano json file
    """

    if len(sys.argv) < 3:
        sys.exit(
            "No file provided. Please use \"Python3 seq_designer.py <filename.json> <scaffoldseq.txt>\" ")
    else:
        inputJson = sys.argv[1]
        inputScaffold = sys.argv[2]

    with open(inputScaffold, 'r') as file:
        scaffold_seq = file.read().replace('\n', '')

    # outputFile = sys.argv[2]

    with open(inputJson, 'r') as json_data:
        cadnano_data = json.load(json_data)

    # filename = cadnano_data['name']

    strand_data = cadnano_data['vstrands']
    num_strands = len(strand_data)
    length_strands = len(strand_data[0]['scaf'])

    # Initialize arrays
    scaffold = np.empty(num_strands, dtype=object)
    staples = np.empty(num_strands, dtype=object)
    row = np.empty(num_strands, dtype=object)
    col = np.empty(num_strands, dtype=object)
    num = np.empty(num_strands, dtype=object)

    for i in range(num_strands):
        scaffold[i] = strand_data[i]['scaf']
        staples[i] = strand_data[i]['stap']
        row[i] = strand_data[i]['row']
        col[i] = strand_data[i]['col']
        num[i] = strand_data[i]['num']

    return num_strands, length_strands, scaffold, staples, row, col, num, strand_data, scaffold_seq


def FindStart(scaffold, length_strands):
    """
    Looks for a start base and returns if found.
    If not found, returns [-1, -1]
    """

    currentBase = [0, 0]  # Start searching at strand 0, base 0
    currentBlock = scaffold[currentBase[0]][currentBase[1]]

    # Go through first empty bases until nonempty base is found
    while currentBlock == [-1, -1, -1, -1]:

        # Shift one base to the right
        nextBase = [currentBase[0], currentBase[1]+1]
        nextBlock = scaffold[nextBase[0]][nextBase[1]]

        # If entire strand is empty, start searching next strand at base 0
        if(nextBase[1] == length_strands-1):
            nextBase = [currentBase[0]+1, 0]
            nextBlock = scaffold[nextBase[0]][nextBase[1]]

        currentBase = nextBase
        currentBlock = nextBlock

    firstNonEmpty = currentBase

    # From first nonempty base, traverse until end is reached
    while currentBase != [-1, -1]:
        nextBase, nextBlock = TraverseScaffold(scaffold, currentBase)

        # Break if end base is found
        if nextBase == [-1, -1]:
            break

        # If a loop is reached, there is no breakpoint
        if nextBase == firstNonEmpty:
            sys.exit("Scaffold does not have breakpoint")

        currentBlock = nextBlock
        currentBase = nextBase

    endBase = currentBase

    # For even strands start base is on the right of end base
    if endBase[0] % 2 == 0:
        startBase = [endBase[0], endBase[1]+1]
    # For odd strands start base is on the left of end base
    else:
        startBase = [endBase[0], endBase[1]-1]

    return startBase


def TraverseScaffold(scaffold, startBase):
    """
    Traverse scaffold by a single base
    """
    currentBase = startBase
    currentBlock = scaffold[currentBase[0]][currentBase[1]]
    nextBase = [currentBlock[2], currentBlock[3]]
    nextBlock = scaffold[nextBase[0]][nextBase[1]]
    return nextBase, nextBlock


def TraverseEntireScaffold(scaffold, startBase, scaffold_seq):
    """
    Traverse and print scaffold, returns end base
    """

    if startBase == [-1, -1]:
        print("Invalid start base")
        return

    finalSequence = []
    currentBase = startBase
    currentBlock = scaffold[currentBase[0]][currentBase[1]]
    currentBlock.append(scaffold_seq[0])
    cnt = 1

    finalSequence.append(currentBlock)

    nextBase, nextBlock = TraverseScaffold(scaffold, currentBase)

    # Traverse scaffold until nextBase is [-1,-1]
    while nextBase != [-1, -1]:
        currentBlock = nextBlock
        currentBase = nextBase
        currentBlock.append(scaffold_seq[cnt])

        finalSequence.append(currentBlock)
        cnt += 1

        nextBase, nextBlock = TraverseScaffold(scaffold, currentBase)

    endBase = currentBase

    # check if end and start base are next to each other!
    if startBase[0] != endBase[0]:
        sys.exit("Start and end of scaffold do not connect!")
    else:
        if endBase[0] % 2 == 0 and endBase[1]+1 != startBase[1]:
            sys.exit("Start and end of scaffold do not connect!")
        elif endBase[0] % 2 == 1 and endBase[1]-1 != startBase[1]:
            sys.exit("Start and end of scaffold do not connect!")

    return endBase, finalSequence


def PrintScaffold(finalSequence):
    for seq in finalSequence:
        print(seq)


num_strands, length_strands, scaffold, staples, row, col, num, strand_data, scaffold_seq = ParseJson()
startBase = FindStart(scaffold, length_strands)
endBase, finalSequence = TraverseEntireScaffold(
    scaffold, startBase, scaffold_seq)
PrintScaffold(finalSequence)

print(startBase)
print(endBase)
