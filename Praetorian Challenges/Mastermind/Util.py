## Return the number of weapons guessed correctly
def count_correct_weapons(answer, guess):
    return len(set(answer).intersection(set(guess)))

## Return the number of weapons in the correct positions
def count_correct_positions(answer, guess):
    positionsCorrect = 0
    for weapon1, weapon2 in zip(answer, guess):
        if weapon1 == weapon2:
            positionsCorrect += 1

    return positionsCorrect

## Calculate n! / ((n - c)! * c!)
## Return the number of combinations
def calculate_number_combinations(n, c):
    if c <= 0 or n < c:
        return 0
        
    ans = calculate_number_permutations(n, c)
    for i in range(c, 0, -1):
        ans /= i
    
    return int(ans)

## Calculate n! / (n - c)!
## Return the number of permutations
def calculate_number_permutations(n, c):
    if c <= 0 or n < c:
        return 0
    
    ans = 1
    for i in range(n, n - c, -1):
        ans *= i
    
    return int(ans)

## Generates a set of all combinations
## Return a set of tuples
def generate_combinations(n, c):
    if calculate_number_combinations(n, c) == 0:
        return set()
    
    combinations = set()
    weaponSet = set(range(n))
    combination = list(range(c))

    index = c - 1
    maxVal = n - 1
    combinations.add(tuple(combination))

    ## Increment combinations like a base n counter
    while _increment_combination(combination, index, maxVal):
        combinations.add(tuple(combination))

    return combinations

## Recursive part of generate_combinations()
## Return False if combination[0] == maxValue == (n - c). Value is passed backed up to generate_combinations()
## Return True otherwise
def _increment_combination(combination, index, maxVal):
    if combination[index] == maxVal:
        if index == 0  or _increment_combination(combination, index - 1, maxVal - 1) == 0:
            return False
        else:
            combination[index] = combination[index - 1] + 1
    else:
        combination[index] += 1

    return True

## Generate all combinations of length _c that include all weapons from includeSet and a subset of remainderSet
def generate_combinations_from_set(includeSet, remainderSet, _c):
    n = len(remainderSet)
    c = _c - len(includeSet)
    
    if c == 0:
        return set([tuple(includeSet)])
    if calculate_number_combinations(n, c) == 0:
        return set()
    
    indices = list(range(c))
    remainderList = list(remainderSet)
    combination = remainder[:c] + list(includeSet)
    combinations = set()

    index = c - 1
    maxVal = n - 1
    combinations.append(tuple(combination))

    ## Increment indicies and translate index to value of remainderList[index]
    while _increment_combination_from_set(combination, remainderList, indices, index, maxVal):
        combinations.append(tuple(combination))

    return combinations

def _increment_combination_from_set(combination, remainderList, indices, index, maxVal):
    indices[index] += 1
    if indices[index] > maxVal:
        if index == 0:
            return 0
        if _increment_combination_from_set(combination, remainderList, indices, index - 1, maxVal - 1) == 0:
            return 0
        indices[index] = indices[index - 1] + 1

    combination[index] = remainderList[indices[index]]
    return 1

## Generates a list of all permutations grouped by combinations
## Return a list of sets of tuples
def generate_grouped_permutations(combinations, c):
    groupedPermutations = list()

    permutation = [0] * c
    newIndex = c - 1
    
    for combination in combinations:
        weaponSet = set(combination)
        groupedPermutations.append(set())
        permutations = groupedPermutations[-1]
        for weapon in weaponSet:
            permutation[0] = weapon
            weaponSet.remove(weapon)            
            _recursive_permute(permutations, permutation, weaponSet, newIndex)
            weaponSet.add(weapon)

    return groupedPermutations

## UNUSED
#### Generates a list of all permutations
#### Return an empty list if the number of permutations is greater than 10 million
#### Return a set of tuples
##def generate_permutations(n, c):
##    permutations = set()
##    
##    weaponSet = set(range(n))
##        
##    numPermutations = calculate_number_permutations(n, c)
##    if numPermutations > 0:
##        permutation = [0] * c
##        newIndex = c - 1
##        
##        for weapon in weaponSet:
##            permutation[0] = weapon
##            weaponSet.remove(weapon)            
##            _recursive_permute(permutations, permutation, weaponSet, newIndex)
##            weaponSet.add(weapon)
##
##    return permutations

## Recursive part of generate_permutations()
def _recursive_permute(permutations, permutation, weaponSet, index):
    if index == 1:
        for weapon in weaponSet:
            permutation[-1] = weapon
            permutations.add(tuple(permutation))
    else:
        newIndex = index - 1
        for weapon in weaponSet:
            permutation[-index] = weapon

            weaponSet.remove(weapon)
            _recursive_permute(permutations, permutation, weaponSet, newIndex)
            weaponSet.add(weapon)
