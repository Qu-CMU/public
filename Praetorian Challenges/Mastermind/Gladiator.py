import sys
import time
from Util import *
from random import sample
from weaponDeduction import weaponDeduction

## Max amount of time to spend updating knowledge (removing impossible answers)
updateTimeout = 4

## Max amount of time to spend computing before forcing a guess
## guessTimeout - updateTimeout = Time to spend finding optimal guess
guessTimeout = 9

## Set timeout very high for debugging and stepping through the program
##guessTimeout = 10000
##updateTimeout = 10000

## Generate a list of combinations/permutations when search space is smaller cutoff
## Increase to potentially decrease worst-case number of guesses while increasing compute time
## Decrease if program is unable to update possible combinations/permutations in the time limit
approximateCutoffSize = 4000000

## Switch to an approximation of Kunth's Mastermind algorithm when search space is smaller than cutoff
## Increase to potentially decrease worst-case number of guesses while increasing compute time
## Decrease if program is unable to compute an optimal guess in the time limit
optimalCutoffSize = 2000

class Gladiator:
    def __init__(self, numWeapons, numOpponents):
        self.numWeapons = numWeapons
        self.numOpponents = numOpponents
        self.numCombinations = calculate_number_combinations(numWeapons, numOpponents)
        self.numPermutations = calculate_number_permutations(numWeapons, numOpponents)

        self.startTime = time.time()
        self.guessState = 0
        
        self.previousGuesses = list()
        self.previousResponses = list()
        self.possibleCombinations = list()
        self.possiblePermutations = list()

        ## Set to true if last update was not finished in time
        ## Stays true until all impossible guesses have been removed
        self.unfinishedUpdate = False
        self.unfinishedIndex = 0

        self.weaponSolver = weaponDeduction(numWeapons, numOpponents)

        if self.numCombinations < approximateCutoffSize:
            ## Number of combinations is small enough that we can generate it in a reasonable amount of time and that we can store in memory
            self.possibleCombinations = generate_combinations(numWeapons, numOpponents)
            self.guessState = 1
        if self.numCombinations < optimalCutoffSize:
            ## Number of combinations is small enough that we can use a near-optimal deterministic strategy for selecting the next guess
            self.guessState = 2
        if self.numCombinations == 1 and self.numPermutations > approximateCutoffSize:
            ## Unimplemented, would require number of opponents > 10
            self.guessState = 3 
        if self.numPermutations < approximateCutoffSize:
            ## Number of permutations is small enough that we can generate it in a reasonable amount of time and that we can store in memory
            self.possiblePermutations = generate_grouped_permutations(self.possibleCombinations, numOpponents)
            self.guessState = 4
        if self.numPermutations < optimalCutoffSize:
            ## Number of permutations is small enough that we can use a near-optimal deterministic strategy for selecting the next guess
            self.guessState = 5

        ## Setting update and guess strategies for each state
        self._updateStrategy = [0] * 6
        self._updateStrategy[0] = self.weapon_solver_update     ## Combinations > approximateCutoffSize
        self._updateStrategy[1] = self.combination_update       ## Combinations > optimalCutoffSize
        self._updateStrategy[2] = self.combination_update       ## Combinations < optimalCutoffSize and Permutations > approximateCutoffSize
        self._updateStrategy[3] = self.position_solver_update   ## Combinations == 1 and Permutations > approximateCutoffSize
        self._updateStrategy[4] = self.permutation_update       ## Permutations > optimalCutoffSize
        self._updateStrategy[5] = self.permutation_update       ## Permutations < optimalCutoffSize

        self._guessStrategy = [0] * 6
        self._guessStrategy[0] = self.weapon_solver_guess
        self._guessStrategy[1] = self.combination_approx_guess
        self._guessStrategy[2] = self.combination_optimal_guess
        self._guessStrategy[3] = self.position_solver_guess
        self._guessStrategy[4] = self.permutation_approx_guess
        self._guessStrategy[5] = self.permutation_optimal_guess

        ## Set first guess to [1,2,3, ... numOpponents - 1]
        self.previousGuesses.append(tuple(range(numOpponents)))

    ## Update internal knowledge given response
    ## Update will set unfinishedUpdate to true if it runs out of time and continue from when it left off the next update
    ## Update will call the appropriate update and guess function based on guessState
    def update(self, weaponsCorrect, positionsCorrect):
        self.startTime = time.time()
        previousGuess = self.previousGuesses[-1]
        self.previousResponses.append((weaponsCorrect, positionsCorrect))

        if self.unfinishedUpdate:
            assert self.guessState != 0
            for index in range(self.unfinishedIndex, len(self.previousGuesses)):
                if time.time() - self.startTime > updateTimeout:
                    self.unfinishedUpdate = True
                    self.unfinishedIndex = index
                    break
                
                guess = self.previousGuesses[index]
                response = self.previousResponses[index]
                self._updateStrategy[self.guessState](guess, response[0], response[1])

            self.unfinishedUpdate = False
            self.unfinishedIndex = 0

        self._updateStrategy[self.guessState](previousGuess, weaponsCorrect, positionsCorrect)
        self._guessStrategy[self.guessState]()

    ## Update the WeaponSolver
    ## The benefit of the WeaponSolver is that is very quick. Assumed to always finish before the updateTimeout in our use cases
    ## Calculate the new number of possible combinations. Update guessState and generate all possible combinations
    ## Because the WeaponSolver does not eliminate all impossible combinations, we have to run combination_update() over the possible combinations with all of the previous guesses
    def weapon_solver_update(self, previousGuess, weaponsCorrect, positionsCorrect):
        self.weaponSolver.learn(previousGuess, weaponsCorrect)
        numPossibleCombinations = calculate_number_combinations(len(self.weaponSolver.unknownWeapons), self.numOpponents - len(self.weaponSolver.correctWeapons))

        if numPossibleCombinations < approximateCutoffSize:
            self.possibleCombinations = generate_combinations_from_set(self.weaponSolver.correctWeapons, self.weaponSolver.unknownWeapons, self.numOpponents)
            self.guessState = 1
            
            for index, (guess, response) in enumerate(zip(self.previousGuesses, self.previousResponses)):
                if time.time() - self.startTime > updateTimeout:
                    self.unfinishedUpdate = True
                    self.unfinishedIndex = index
                    return

                self.combination_update(guess, response[0], response[1])

            self.unfinishedUpdate = False
            self.unfinishedIndex = 0

    ## Placeholder function
    ## Unimplemented
    def position_solver_update(self, previousGuess, weaponsCorrect, positionsCorrect):
        print("position_solver_update: unimplemented")
        sys.exit()

    ## Update the set of possible combinations
    ## Remove combinations that would not produce the same response from the server if they were assumed to be the correct answer
    ## Update guessState and generate permutations if the appropriate conditions have been met
    ## Because combination_update() does not eliminate all impossible permutations, we have to run permutation_update() over the possible permutations with all of the previous guesses
    def combination_update(self, guess, weaponsCorrect, positionCorrect):
        possibleCombinations = list()
            
        for combination in self.possibleCombinations:
            if weaponsCorrect == count_correct_weapons(guess, combination):
                possibleCombinations.append(combination)

        self.possibleCombinations = possibleCombinations

        if len(self.possibleCombinations) < optimalCutoffSize:
            self.guessState = 2
        if len(self.possibleCombinations) == 1:
            self.guessState = 3
        if len(self.possibleCombinations) * calculate_number_permutations(self.numOpponents, self.numOpponents) < approximateCutoffSize:
            self.guessState = 4
            self.possiblePermutations = generate_grouped_permutations(self.possibleCombinations, self.numOpponents)
            
            for index, (guess, response) in enumerate(zip(self.previousGuesses, self.previousResponses)):
                if time.time() - self.startTime > updateTimeout:
                    self.unfinishedUpdate = True
                    self.unfinishedIndex = index
                    return

                self.permutation_update(guess, response[0], response[1])

            self.unfinishedUpdate = False
            self.unfinishedIndex = 0

    ## Update the set of possible permutations
    ## Remove permutations that would not produce the same response from the server if they were assumed to be the correct answer
    ## Update guessState and if the appropriate conditions have been met
    def permutation_update(self, guess, weaponsCorrect, positionsCorrect):
        possiblePermutations = list()

        for subSet in self.possiblePermutations:
            for permutation in subSet:
                break
            if weaponsCorrect == count_correct_weapons(guess, permutation):
                newSubSet = set()
                for permutation in subSet:
                    if positionsCorrect == count_correct_positions(permutation, guess):
                        newSubSet.add(permutation)

                if len(newSubSet) != 0:
                    possiblePermutations.append(newSubSet)

        self.possiblePermutations = possiblePermutations

        numPermutations = 0
        for subSet in self.possiblePermutations:
            numPermutations += len(subSet)

        if numPermutations < optimalCutoffSize:
            self.guessState = 5

    ## Make a guess using information from the WeaponsSolver
    ## Use 1/4 of guess time to generate as many random samples of combinations from WeaponsSolver knowledge
    ## Use remaining time to run an approximation of Kunth's Mastermind Algorithm and select the best guess
    def weapon_solver_guess(self):
        bestGuess = None
        minMax = self.numCombinations
        emptyResponseCounter = [0] * (self.numOpponents + 1)
        
        correctSet = self.weaponSolver.correctWeapons
        unknownSet = self.weaponSolver.unknownWeapons

        timeRemaining = guessTimeout - (time.time() - self.startTime)
        randomSubset = set()
        sampleSize = self.numOpponents - len(correctSet)
        stopTime = guessTimeout - (0.75*timeRemaining)
        
        while time.time() - self.startTime < stopTime:
            for _ in range(25):
                temp = sample(unknownSet, sampleSize)
                temp.sort()
                randomSubset.add(tuple(temp))
        
        while time.time() - self.startTime < guessTimeout:
            responseCounter = list(emptyResponseCounter)
            randomGuess = sample(unknownSet, sampleSize)
            for combination in randomSubset:
                responseCounter[count_correct_weapons(randomGuess,combination)] += 1
                
            currentMax = max(responseCounter)
            if currentMax < minMax:
                bestGuess = randomGuess + list(correctSet)
                minMax = currentMax

        if bestGuess == None:
            print("RAN OUT OF TIME: RANDOMLY GUESSING weapon_solver_guess")
            bestGuess = sample(range(self.numWeapons), self.numOpponents)
        
        bestGuess = sample(bestGuess, len(bestGuess))
        self.previousGuesses.append(tuple(bestGuess))

    ## Select a random subset of combinations from the list of possible combinations
    ## Run a variation of Kunth's Mastermind Algorithm over the subset and select the best guess
    def combination_approx_guess(self):
        bestGuess = None
        minMax = self.numCombinations
        emptyResponseCounter = [0] * (self.numOpponents + 1)

        randomSubset = sample(self.possibleCombinations, min(len(self.possibleCombinations), 3000))
        while time.time() - self.startTime < guessTimeout:
            responseCounter = list(emptyResponseCounter)
            randomGuess = sample(self.possibleCombinations, 1)[0]
            for combination in randomSubset:
                responseCounter[count_correct_weapons(randomGuess, combination)] += 1

            currentMax = max(responseCounter)
            if currentMax < minMax:
                bestGuess = randomGuess
                minMax = currentMax

        if bestGuess == None:
            print("RAN OUT OF TIME: RANDOMLY GUESSING combination_approx_guess")
            bestGuess = sample(range(self.numWeapons), self.numOpponents)
        
        bestGuess = sample(bestGuess, len(bestGuess))
        self.previousGuesses.append(tuple(bestGuess))

    ## Run a variation of Kunth's Mastermind Algorithm over the list of combinations and select the best guess
    def combination_optimal_guess(self):
        bestGuess = None
        minMax = self.numCombinations
        emptyResponseCounter = [0] * (self.numOpponents + 1)
            
        for combination1 in self.possibleCombinations:
            responseCounter = list(emptyResponseCounter)
            if time.time() - self.startTime > guessTimeout:
                print("Did not finish combination guess calculation")
                break
            for combination2 in self.possibleCombinations:
                responseCounter[count_correct_weapons(combination1, combination2)] += 1

            currentMax = max(responseCounter)
            if currentMax < minMax:
                bestGuess = combination1
                minMax = currentMax

            bestGuess = sample(bestGuess, len(bestGuess))

        if bestGuess == None:
            print("RAN OUT OF TIME: RANDOMLY GUESSING combination_optimal_guess")
            bestGuess = sample(range(self.numWeapons), self.numOpponents)

        bestGuess = sample(bestGuess, len(bestGuess))
        self.previousGuesses.append(tuple(bestGuess))

    ## Placeholder function
    ## Unimplemented
    def position_solver_guess(self):
        print("position_solver_guess: unimplemented")
        sys.exit()

    ## Select a random subset of permutations from the list of possible permutations
    ## Run an approximation of Kunth's Mastermind Algorithm over the subset and select the best guess
    def permutation_approx_guess(self):
        bestGuess = None
        minMax = self.numPermutations
        emptyResponseCounter = dict()

        for i in range(self.numOpponents + 1):
            for j in range(i + 1):
                emptyResponseCounter[(i,j)] = 0

        comboSplit = min(len(self.possiblePermutations), 50)
        permSplit = int(round(2500 / comboSplit))
        randCombos = sample(self.possiblePermutations, comboSplit)
        randPermutations = list()
        for permSet in randCombos:
            randPermutations.append(sample(permSet, min(len(permSet), permSplit)))

        while (time.time() - self.startTime) < guessTimeout:
            permutation1 = sample(sample(self.possiblePermutations, 1)[0], 1)[0]
            responseCounter = emptyResponseCounter.copy()
            for comboSet in randPermutations:
                for elem in comboSet:
                    break
                weaponsCorrect = count_correct_weapons(elem, permutation1)
                for permutation2 in comboSet:
                    responseCounter[(weaponsCorrect, count_correct_positions(permutation1, permutation2))] += 1

            currentMax = max(responseCounter.values())
            if currentMax < minMax:
                bestGuess = permutation1
                minMax = currentMax    
                        
        if bestGuess == None:
            print("RAN OUT OF TIME: RANDOMLY GUESSING permutation_approx_guess")
            bestGuess = sample(range(self.numWeapons), self.numOpponents)
            bestGuess = sample(bestGuess, len(bestGuess))

        self.previousGuesses.append(tuple(bestGuess))

    ## Run an approximation of Kunth's Mastermind Algorithm over the list of permutations and select the best guess
    def permutation_optimal_guess(self):
        bestGuess = None
        minMax = self.numPermutations
        emptyResponseCounter = dict()

        for i in range(self.numOpponents + 1):
            for j in range(i + 1):
                emptyResponseCounter[(i,j)] = 0
        
        for permutationSubset1 in self.possiblePermutations:
            for permutation1 in permutationSubset1:
                if (time.time() - self.startTime) > guessTimeout:
                    print("Did not finish permutation guess calculation")
                    break
                responseCounter = emptyResponseCounter.copy()
                for permutationSubset2 in self.possiblePermutations:
                    for permutation2 in permutationSubset2:
                        break
                    weaponsCorrect = count_correct_weapons(permutation1, permutation2)
                    for permutation2 in permutationSubset2:
                        responseCounter[(weaponsCorrect, count_correct_positions(permutation1, permutation2))] += 1
                
                currentMax = max(responseCounter.values())
                if currentMax < minMax:
                    bestGuess = permutation1
                    minMax = currentMax

        if bestGuess == None:
            print("RAN OUT OF TIME: RANDOMLY GUESSING permutation_optimal_guess")
            bestGuess = sample(range(self.numWeapons), self.numOpponents)
            bestGuess = sample(bestGuess, len(bestGuess))
            
        self.previousGuesses.append(bestGuess)

    ## Return the next "best" guess to make
    def get_next_guess(self):
        return self.previousGuesses[-1]

    ## Reset Gladiator object to initial state with the same parameters (numWeapons, numOpponents)
    def reset(self):
        self.startTime = time.time()
        self.guessState = 0
        
        self.previousGuesses = list()
        self.previousResponses = list()
        self.possibleCombinations = list()
        self.possiblePermutations = list()

        self.unfinishedUpdate = False
        self.unfinishedIndex = 0

        self.weaponSolver.reset()

        if self.numCombinations < approximateCutoffSize:
            self.possibleCombinations = generate_combinations(self.numWeapons, self.numOpponents)
            self.guessState = 1
        if self.numCombinations < optimalCutoffSize:
            self.guessState = 2
        if self.numCombinations == 1 and self.numPermutations > approximateCutoffSize:
            self.guessState = 3 ## Unimplemented
        if self.numPermutations < approximateCutoffSize:
            self.possiblePermutations = generate_grouped_permutations(self.possibleCombinations, self.numOpponents)
            self.guessState = 4
        if self.numPermutations < optimalCutoffSize:
            self.guessState = 5

        self.previousGuesses.append(tuple(range(self.numOpponents)))
