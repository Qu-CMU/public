from weaponDeduction import weaponDeduction
from Util import *
from random import sample
from random import randint
import time
import sys

debugger_weaponSolver = None

def random_guess(weaponSolver):
    return set(sample(range(weaponSolver.numWeapons), weaponSolver.numOpponents))

## Versatile test function
## 'next_guess' field was intended to be used to test and compare guessing algorithms but was never implemented
def test(numWeapons, numOpponents, answer=None, guesses=None, maxGuesses=None, next_guess=random_guess):
    global debugger_weaponSolver
    weaponSolver = weaponDeduction(numWeapons, numOpponents)
    debugger_weaponSolver = weaponSolver
    
    ## Error Checking Inputs
    if answer is None:
        answer = set(sample(range(0, numWeapons), numOpponents))
    else:
        if len(answer) != numOpponents:
            print("Error: len(answer) does not equal numOpponents")
            sys.exit()
        elif len(set(answer)) != numOpponents:
            print("Error: answer contains duplicate values")
            sys.exit()
        elif min(answer) < 0 or max(answer) >= numWeapons:
            print("Error: answer contains values not in range(0, numWeapons)")
            sys.exit()

    if guesses is None:
        pass
    else:
        for index, guess in enumerate(guesses):
            if len(guess) != numOpponents:
                print("Error: len() of guess " + str(index) + " does not equal numOpponents")
                sys.exit()
            elif len(set(guess)) != numOpponents:
                print("Error: guess " + str(index) + "contains duplicate values")
                sys.exit()
            elif min(answer) < 0 or max(answer) >= numWeapons:
                print("Error: guess " + index + " contains values not in range(0, numWeapons)")
                sys.exit()

    if maxGuesses is None:
        maxGuesses = int(min(1000, numWeapons * (numWeapons - 1) / 2))

    ## Normal test
    print("----------------------\n")
    numGuesses = 0
    if guesses is None:
        print("Beginning Random Test")
        guess = tuple(range(numOpponents))
        guesses = [guess]
        response = count_correct_weapons(answer, guess)

        ## While we have not learned the correct answer, keep trying
        while weaponSolver.learn(guess, response) == False:
            numGuesses += 1
            
            ## Make sure next guess has not been guessed before
            while tuple(guess) in guesses:
                guess = next_guess(weaponSolver)
                
            response = count_correct_weapons(answer, guess)
            guesses.append(tuple(guess))

            ## Stop if we have reached maxGuesses
            if numGuesses > maxGuesses:
                print("Ran out of guesses")
                break
            
    ## Replay test
    else:
        print("Beginning Replay Test")

        ## Make predetermined guesses
        for guess in guesses:
            response = count_correct_weapons(answer, guess)
            if weaponSolver.learn(guess, response) == True:
                break
            
            numGuesses += 1

        ## Check if correct combination has been found after all guesses
        if len(weaponSolver.correctWeapons) != numOpponents:
            print("Ran out of guesses")

    print("Test Finished\n")
    return numGuesses

## Print state after initialization]
##weaponSolver = weaponDeduction(10, 5)
##print("numWeapons: " + str(weaponSolver.numWeapons))
##print("Correct Weapons: " + str(weaponSolver.correctWeapons))
##print("Unknown Weapons: " + str(weaponSolver.unknownWeapons))
##print("Weapon Lookup: " + str(weaponSolver.weaponLookup))
##print("Guesses: " + str(weaponSolver.guesses))
##print("Information: " + str(weaponSolver.information))

## Static Test
## Hard-coded scenario
test(6, 3, answer={0,3,5}, guesses=[[0,1,2],[0,1,4],[1,2,4]])

## Random Tests
## Randomized guesses and answers
for numWeapons in range(1,11):
    for numOpponents in range(1, numWeapons + 1):
        print("numWeapons:" + str(numWeapons))
        print("numOpponents:" + str(numOpponents))
        test(numWeapons, numOpponents)
        test(numWeapons, numOpponents)
        test(numWeapons, numOpponents)

## Large Test
numWeapons = 100
numOpponents = 50

guesses = list()
guessSet = set(range(51))

for i in range(51):
    guessSet.remove(i)
    guesses.append(tuple(guessSet))
    guessSet.add(i)

for i in range(2, 51):
    guessSet = set(range(i, i + 50))
    guesses.append(tuple(guessSet))

test(numWeapons, numOpponents, guesses=guesses)
