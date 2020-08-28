from Util import *
import sys

debugger_combination = None
debugger_permutation = None

## Test function generate_combinations() for a range of (n, c)
## Verify by checking if number of elements in the generated combination set match the expected number calculated.
## Save output of generate_combinations(n,c) to debugger_combination for quick analysis in shell
def test_generate_combinations():
    global debugger_combination
    
    for n in range(1, 25):
        print("starting n = " + str(n))
        for c in range(1, n):
            debugger_combination = generate_combinations(n,c)
            if len(debugger_combination) != calculate_number_combinations(n,c):
                print("generate_combinations() failed " + str(n) + ' ' + str(c))
                sys.exit()

    print("generate_combinations() passed")

## Test function generate_permutations() for a range of (n, c)
## Verify by checking if number of elements in the generated permutation set match the expected number calculated.
## Save output of generate_permutations(n,c) to debugger_permutation for quick analysis in shell
def test_generate_grouped_permutations():
    for n in range(1,11):
        print("starting n = " + str(n))
        for c in range(1,8):
            combinations = generate_combinations(n,c)
            debugger_combination = combinations
            permutations = generate_grouped_permutations(combinations, c)
            debugger_permutation = permutations
            expected = calculate_number_permutations(c,c)
            for i in permutations:
                if len(i) != expected:
                    print("generate_permutations() failed " + str(n) + ' ' + str(c))
                    sys.exit()

    print("generate_permutations() passsed")

## Test function generate_combinations_from_set()
## Verify by checking if number of elements in the generated combination set match the expected number calculated.
## Verify that all combinations include the includeSet
## Save output of generate_combinations_from_set() to debugger_combination for quick analysis in shell
def test_generate_combinations_from_set():
    global debugger_combination

    includeSet = set([])
    remainderSet = set(range(10))
    for c in range(1, 10):
        print("starting c = " + str(c))
        debugger_combination = generate_combinations_from_set(includeSet, remainderSet, c)
        if len(debugger_combination) != calculate_number_combinations(len(remainderSet), c - len(includeSet)):
            print("test_generate_combinations_from_set() failed " + str(includeSet))
            sys.exit()

    includeSet = set([0, 1])
    remainderSet = set(range(2, 10))
    for c in range(3, 10):
        print("starting c = " + str(c))
        debugger_combination = generate_combinations_from_set(includeSet, remainderSet, c)
        if len(debugger_combination) != calculate_number_combinations(len(remainderSet), c - len(includeSet)):
            print("test_generate_combinations_from_set() failed " + str(includeSet))
            sys.exit()
        for combination in debugger_combination:
            if len(set(combination).intersection(set(includeSet))) != 2:
                print("test_generate_combinations_from_set() failed " + str(includeSet) + str(combination))
                sys.exit()

    includeSet = set([0, 1])
    remainderSet = set(range(2, 10))
    c = 2
    print("starting edge case 1")
    debugger_combination = generate_combinations_from_set(includeSet, remainderSet, c)
    if len(debugger_combination) != 1:
        print("test_generate_combinations_from_set() failed " + str(c))
        sys.exit()

    includeSet = set(range(10))
    remainderSet = set([])
    c = 10
    print("starting edge case 2")
    debugger_combination = generate_combinations_from_set(includeSet, remainderSet, c)
    if len(debugger_combination) != 1:
        print("test_generate_combinations_from_set() failed " + str(c))
        sys.exit()

    print("test_generate_combinations_from_set() passed")
