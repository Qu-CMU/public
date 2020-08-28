import time
from random import sample
from random import randint
from Util import *
from Gladiator import Gladiator

debugger_gladiator = None
debugger_answer = None

## Simulate Server
def serverResponse(answer, guess, start, end):
    weaponsCorrect = count_correct_weapons(answer, guess)
    positionsCorrect = count_correct_positions(answer, guess)

    ## Less than 10 to be more strict and account for latency
    assert (end - start) < 9.5

    return (weaponsCorrect, positionsCorrect)

## Check if answer is correct
def isCorrect(response, opponents):
    if response[0] == opponents and response[1] == opponents:
        return True

    return False

## Configurable function simulate a game round
## Save Gladiator object to debugger_gladiator for quick analysis in shell
## Save answer to debugger_answer for quick analysis in shell
def test(numWeapons, numOpponents, answer=None, maxGuesses=None, verbose=False):
    global debugger_gladiator
    global debugger_answer
    
    if answer is None:
        ## No static answer provided, generating random answer.
        answer = sample(range(0, numWeapons), numOpponents)
    else:
        ## Basic input checking
        if len(answer) != numOpponents:
            print("len(answer) != numOpponents")
            return False
        if min(answer) < 0 or max(answer) >= numWeapons:
            print("invalid answer")
            return False

    if maxGuesses is None:
        ## Set upper-bound if maxGueses was not provided.
        maxGuesses = numWeapons

    ## Initialize Gladiator and timers.
    if verbose:
        print("Answer: " + str(answer))
        
    start = time.time()
    
    gladiator = Gladiator(numWeapons, numOpponents)
    debugger_gladiator = gladiator
    debugger_answer = answer
    guess = gladiator.get_next_guess()
    
    end = time.time()
    
    response = serverResponse(answer, guess, start, end)
    correct = isCorrect(response, numOpponents)
    numGuesses = 1

    while not isCorrect(response, numOpponents):
        start = time.time()
        
        if numGuesses > maxGuesses:
            print("Too many guesses")
            return False
        
        gladiator.update(response[0], response[1])
        guess = gladiator.get_next_guess()
        
        end = time.time()
        
        response = serverResponse(answer, guess, start, end)
        numGuesses += 1
        
        if verbose:
            print("Guess: " + str(guess))
            print("Response: " + str(response))
        
    if verbose:    
        print("Test succeeded")
        
    return True

## Run three tests from a wide range of sizes
## WARNING: Takes over an hour
def test_all():
    for numWeapons in range(1,25):
        for numOpponents in range(1, min(numWeapons, 8)):
            if test(numWeapons, numOpponents) == False:
                print("Something went wrong" + str(numWeapons) + " " + str(numOpponents))
                sys.exit()
            if test(numWeapons, numOpponents) == False:
                print("Something went wrong" + str(numWeapons) + " " + str(numOpponents))
                sys.exit()
            if test(numWeapons, numOpponents) == False:
                print("Something went wrong" + str(numWeapons) + " " + str(numOpponents))
                sys.exit()
