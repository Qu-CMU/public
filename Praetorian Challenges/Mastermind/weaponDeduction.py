class weaponDeduction:
    def __init__(self, numWeapons, numOpponents):
        ## The number of weapons
        self.numWeapons     = numWeapons

        ## The number of correct weapons
        self.numOpponents   = numOpponents
        
        ## Sets of correct weapons
        self.correctWeapons = set()

        ## Sets of undetermined weapons
        self.unknownWeapons = set(range(numWeapons))

        ## Quickly lookup the status of a specific weapon: -1 if incorrect, 0 if unknown, 1 if correct
        self.weaponLookup   = [0] * numWeapons

        ## Stores previous guesses
        self.guesses        = list()

        ## Holds relations between every pair of guesses.
        self.information    = list()

        ## Set if we learn something
        self.learnedSomething = False
        
    ## Updates knowledge and learns correct weapons
    ## Return True if all correct weapons found
    ## Return False otherwise
    def learn(self, _guess, numCorrect):
        guess = set(_guess)

        ## Remove known information from guess
        numCorrect -= self.remove_known_information(guess)
        
        ## Check if undetermined weapons are all incorrect
        if numCorrect == 0:
            self.found_incorrect_weapons(guess)
            self.learnedSomething = True
            if self.done_check():
                return True
        ## Check if undetermined weapons are all correct
        elif len(guess) == numCorrect:
            self.found_correct_weapons(guess)
            self.learnedSomething = True
            if self.done_check():
                return True

        ## Update information then add guess to guesses list
        self.update_information(guess, numCorrect)
        self.guesses.append((guess, numCorrect))

        ## Remove the known information from guesses and try to learn if something new has been learned
        while self.learnedSomething:
            ## If something else new is learned, go again
            self.learnedSomething = False
            self.deduce_information()
            
        return self.done_check()

    ## Remove known weapons from self.information and self.guesses and tries to find correct/incorrect weapons
    def deduce_information(self):
        updatedInformation = list()
        
        for (weaponSet1, weaponSet2, correctnessDelta) in self.information:
            newInfo = self.apply_knowldge(weaponSet1, weaponSet2, correctnessDelta)
            if newInfo:
                    updatedInformation.append(newInfo)

        self.knowledge = updatedInformation
        self.update_guesses()

    ## Add relation between new guess and the unknown elements of previous guesses
    def update_information(self, currentGuess, numCorrect):
        ## Remove the known information from guesses if something new has been learned
        if self.learnedSomething:
            ## If something else new is learned while updating, update again
            while self.learnedSomething:
                self.learnedSomething = False
                self.update_guesses()
            self.learnedSomething = True

        ## Iterate through all previous guesses
        for previousGuess in self.guesses:
            self.add_information(previousGuess, currentGuess, numCorrect)

    ## Add relation between two guesses to self.information
    def add_information(self, previousGuess, currentGuess, numCorrect):
        weaponSet1 = previousGuess[0].difference(currentGuess)
        weaponSet2 = currentGuess.difference(previousGuess[0])
        correctnessDelta = numCorrect - previousGuess[1]

        information = self.apply_knowldge(weaponSet1, weaponSet2, correctnessDelta)
        
        ## Add to list if unknown weapons remain
        if information:
                self.information.append(information)

    ## Remove known weapons and find correct/incorrect weapons
    def apply_knowldge(self, weaponSet1, weaponSet2, correctnessDelta):
        correctnessDelta += self.remove_known_information(weaponSet1)
        correctnessDelta -= self.remove_known_information(weaponSet2)
        afterLength1 = len(weaponSet1)
        afterLength2 = len(weaponSet2)

        ## If both lists empty
        if not afterLength1 and not afterLength2:
            return ()

        ## If every element in weaponSet1 is correct
        if afterLength1 == -correctnessDelta:
            self.found_correct_weapons(weaponSet1)
            self.found_incorrect_weapons(weaponSet2)
            return ()
        ## If every element in weaponSet2 is correct
        if afterLength2 == correctnessDelta:
            self.found_correct_weapons(weaponSet2)
            self.found_incorrect_weapons(weaponSet1)
            return ()
        
        return (weaponSet1, weaponSet2, correctnessDelta)
            
    ## Remove known weapons from a set of weapons
    ## Returns number of correct weapons removed
    def remove_known_information(self, weaponSet):
        count = 0
        discardSet = set()
        
        for weapon in weaponSet:
            ## Correct = 1
            if self.weaponLookup[weapon] == 1:
                count += 1
                discardSet.add(weapon)
            ## Incorrect = -1
            elif self.weaponLookup[weapon] == -1:
                discardSet.add(weapon)
        
        weaponSet.difference_update(discardSet)
        return count

    ## Remove known information from all guesses
    def update_guesses(self):
        newGuesses = list()
        
        for guessTuple in self.guesses:
            guess = guessTuple[0]
            numCorrect = guessTuple[1] - self.remove_known_information(guess)
            
            ## If every element in guess is correct
            if len(guess) == numCorrect:
                self.found_correct_weapons(guess)
                self.learnedSomething = True
            ## If every element in guess is incorrect
            elif numCorrect == 0:
                self.found_incorrect_weapons(guess)
                self.learnedSomething = True
            else:
                newGuesses.append((guess, numCorrect))

        self.guesses = newGuesses

    ## Moves correct weapon set from unknownWeapons to correctWeapons and updates weaponLookup
    def found_correct_weapons(self, weaponSet):
        self.correctWeapons.update(weaponSet)
        self.unknownWeapons.difference_update(weaponSet)
        for weapon in weaponSet:
            self.weaponLookup[weapon] = 1

    ## Removes incorrect weapon set from unknownWeapons and updates weaponLookup
    def found_incorrect_weapons(self, weaponSet):
        self.unknownWeapons.difference_update(weaponSet)
        for weapon in weaponSet:
            self.weaponLookup[weapon] = -1

    ## Checks if all correct weapons have been found
    def done_check(self):
        ## Check if all correct weapons found
        if len(self.correctWeapons) == self.numOpponents:
            return True
        ## Check if remaining undetermined weapons must be correct
        if (len(self.correctWeapons) + len(self.unknownWeapons)) == self.numOpponents:
            self.found_correct_weapons(set(self.unknownWeapons)) ## NOTE 1
            return True
        
        return False
    ## Reset state for new round or level
    def reset(self):
        self.correctWeapons = set()
        self.unknownWeapons = set(range(self.numWeapons))
        self.weaponLookup   = [0] * self.numWeapons
        self.guesses        = list()
        self.information    = list()


## REPLACED: remove_known_information
## REASON: Less Efficient (UNCONFIRMED)
##
## ## Count number of correct weapons in weaponSet1
## temp = len(weaponSet1.intersection(self.correctWeapons))
## ## Remove all known weapons from weaponSet1
## weaponSet1 = weaponSet1.intersection(self.unknownWeapons)
## ## Add number of correct weapons in weaponSet1 to correctnessDelta
## correctnessDelta += temp

## POSSIBLE OPTIMIZATION:
## ASSESMENT: Some benefit, largely unnecessary
## 
## while self.learnedSomething:
##     self.learnedSomething = False
##     self.deduce_information()
## 
## while self.learnedSomething:
##     self.learnedSomething = False
##     self.update_guesses()
##
## Both deduce_information() and update_guesses() work the same way.
## They iterate through a list and attempt to learn something from each element
## If something is learned during the iteration, that information will also be applied to any remaining elements in the list
## However, any element that has already been inspected will not see this new information that could determine the correctness
## of additional weapons. For this reason, we update again until nothing new has been learned but we also waste time
## reinspecting all the elements in the list after the point of discovery.

## NOTE 1
## Need to create set copy passing unknownWeapons to found_correct_weapons, otherwise weaponSet = unknownWeapons
## when unknownWeapons.difference_update(weaponSet) runs, weaponSet will also become an empty set
## and weaponLookup will not be properly updated
