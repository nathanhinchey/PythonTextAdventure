import textwrap
import os

##############################
#classes

class GameObject(object):
    """Set the uniqueName to a unique string"""
    def __init__(self, uniqueName):
        super(GameObject, self).__init__()
        self.uniqueName = uniqueName
        GameObject.AllObjectsDict[uniqueName] = self
        self.inventory = []
        self.description = {"name":uniqueName}
        self.equippedItems = []

    hitpoints = 10
    AllObjectsDict = {"":None}
    saveGameSuffix = ".SAVEGAME"

    def setDescription(self,long,short,name):
        """Sets the description values for the GameObject"""
        self.description = {"long":long,"short":short,"name":name}

    def addInventory(self,newItemString):
        """Adds the item with the uniqueName given"""
        self.inventory = [newItemString]

    def describe(self,longDescription=True):
        """Gives the description for this object"""
        return "\n" + self.description["long"]

    def listInventory(self,longDescription=False):
        """Lists an inventory; use True to force a long description"""
        outputString = ""
        
        if longDescription:
            if len(self.inventory) == 0:
                outputString = "There is nothing in there."
            else:
                for i in range(len(self.inventory)):
                    outputString += GameObject.AllObjectsDict[self.inventory[i]].description["long"] + " "
        else:
            if len(self.inventory) > 1:
                outputString = "There is "
                for i in range(len(self.inventory)):
                    if i == len(self.inventory) - 1:
                        outputString += "and " + GameObject.AllObjectsDict[self.inventory[i]].article + self.inventory[i] + ". "
                    else:
                        outputString += GameObject.AllObjectsDict[self.inventory[i]].article + self.inventory[i] + ", "
            elif len(self.inventory) == 1:
                outputString = "There is " + GameObject.AllObjectsDict[self.inventory[0]].article + self.inventory[0] + ". "
            else:
                outputString = ""
        return outputString

    def saveString(self):
        """returns a string that contains all saveable data for this GameObject"""
        outputString = "@" + self.uniqueName
        outputString += "#gameType," + self.gameType
        outputString += "#hitpoints," + str(self.hitpoints)
        outputString += "#inventory,"
        for inventoryItem in self.inventory:
            outputString += inventoryItem + ","
        outputString += "#equippedItems,"
        for inventoryItem in self.equippedItems:
            outputString += inventoryItem + ","
        return outputString

    def saveGameState(player,fileName):
        """Writes all saveable game data to a file"""
        saveFile = open(fileName,"w")
        outputString = ""
        for key in GameObject.AllObjectsDict:
            if key:
                outputString += GameObject.AllObjectsDict[key].saveString()
        saveFile.write(outputString)
        saveFile.close()

    def loadGameState(player,fileName):
        """Loads a game state from a file"""
        loadFile = open(fileName, "r")
        loadString = loadFile.read()
        
        loadList = loadString[1:].split("@")
        loadDict = {}
        for i in range(len(loadList)):
            loadList[i] = loadList[i].split("#")
        for i in range(len(loadList)):
            loadDict[loadList[i][0]] = loadList[i][1:]
        for key in loadDict:
            for i in range(len(loadDict[key])):
                loadDict[key][i] = loadDict[key][i].split(",")
            tempList = loadDict[key]
            loadDict[key] = {}
            for i in range(len(tempList)):
                loadDict[key][tempList[i][0]] = tempList[i][1:]

        for key in loadDict:
            if key:
                GameObject.AllObjectsDict[key].inventory = []
                for inventoryItem in loadDict[key]["inventory"]:
                    if inventoryItem:
                        GameObject.AllObjectsDict[key].inventory.append(inventoryItem)
                GameObject.AllObjectsDict[key].equippedItems = []
                for inventoryItem in loadDict[key]["equippedItems"]:
                    if inventoryItem:
                        GameObject.AllObjectsDict[key].equippedItems.append(inventoryItem)
                GameObject.AllObjectsDict[key].hitpoints = int(loadDict[key]["hitpoints"][0])
        
        player.activeRoom = GameObject.AllObjectsDict[loadDict[player.uniqueName]["activeRoom"][0]]


class Room(GameObject):
    """rooms are where all things happen"""
    def __init__(self, uniqueName):
        GameObject.__init__(self,uniqueName)
        self.exits = {"N": None, "S": None, "E": None, "W": None}
        self.hasLight = False
        self.timesVisited = 0

    gameType = "Room"

    def describe(self, longDescription=False):
        """Returns a string describing a room; use True to force long description"""
        outputString = ""
        if self.timesVisited < 1 or longDescription:
            outputString += "You are in a " + self.description["name"] + ". "
            outputString += self.description["long"] + " " + self.listExits() + " " + self.listInventory()

        elif self.timesVisited < 4:
            outputString += "A " + self.description["name"] + "."
            outputString += self.description["short"]+ " " + self.listExits()
        else:
            outputString += "A " + self.description["name"] + "."
        if not longDescription:
            self.timesVisited += 1
        return "\n" + outputString

    def listExits(self):
        """Returns a string listing this room's exits."""
        outputString = ""
        exitList = []
        for exit in self.exits:
            if self.exits[exit]:
                exitList.append(self.directionToText(exit))
        if len(exitList) > 1:
            outputString = "There are exits to the "
            for i in range(len(exitList)):
                if i == len(exitList) - 1:
                    outputString += "and " + exitList[i] + "."
                else:
                    outputString += exitList[i] + ", "
        elif len(exitList) == 1:
            outputString = "There is an exit to the " + exitList[0] + "."
        else:
            outputString = "There are no exits."
        return outputString

    #Why do this instead of just calling the dictionary keys "north","south",etc.??
    def directionToText(self, character):
        """converts intenal direction shorthands to player readable descriptions"""
        if character == "N":
            return "north"
        if  character == "S":
            return  "south"
        if character == "E":
            return "east"
        if character == "W":
            return  "west"
        else:
            return None

class Item(GameObject):
    """items are carried by creatures and the player"""
    def __init__(self,uniqueName):
        GameObject.__init__(self, uniqueName)
        self.article = "a "

    gameType = "Item"
    damage = None
    isLightSource = False
    isWeapon = False
    edible = 0

class Creature (GameObject):
    """creatures wander the world"""
    gameType = "Creature"
    defaultDamage = 0
    enraged = True
    damage = defaultDamage

    def takeDamage(self,damage):
        """damage directed at this creature"""
        self.hitpoints -= damage

    def attack(self,enemy):
        """apply this creature's damage to the enemy creature"""
        enemy.takeDamage(self.damage)

class Player (Creature):
    """The player character"""
    def saveString(self):
        """returns a string that contains all saveable data for this Player object"""
        outputString = GameObject.saveString(self)
        outputString += "#activeRoom,"+self.activeRoom.uniqueName+","
        return outputString

    activeRoom = "Start"

######################
# creating instances

#Define items first
# ITEMS
pipeWrench = Item("wrench")
pipeWrench.setDescription("An old, steel pipe wrench.","A pipe wrench.","wrench")

cushion = Item("cushion")
cushion.setDescription("A plush, emrboidered cushion.","A plush cushion.","cushion")

gardenGnome = Item("gnome")
gardenGnome.setDescription("A small, stout, clay figurine of a gnome with a pointed red hat.",
    "A clay gnome with a red hat.",
    "gnome")

bread = Item("bread")
bread.setDescription("A freshly baked loaf of french bread.","Fresh baked bread.","bread")
bread.edible = 1
bread.article = ""

cheese = Item("cheese")
cheese.setDescription("Pungeant, rich sharp white cheese.","White cheese.","cheese")
cheese.edible = 1
cheese.article = ""

anchor = Item("anchor")
anchor.setDescription("A rusty old anchor, with the shells of long dead barnacles.","A rust anchor.","anchor")
anchor.article = "an "


#Define creatures next
# CREATURES


#Define rooms last
# ROOMS
livingRoom = Room("Living Room")
livingRoom.description["long"] = "A large, beautifully apolstered room with comfortable couches and a shag carpet."
livingRoom.description["short"] = "A large, carpeted room with couches."
livingRoom.description["name"] = "living room"

livingRoom.exits["N"] = "Hallway"
livingRoom.exits["S"] = "Front Yard"
livingRoom.addInventory("cushion")

frontYard = Room("Front Yard")
frontYard.description["long"]= "A well manicured lawn, filled with the scent of freshly mown grass."
frontYard.description["short"]= "A well manicured lawn."
frontYard.description["name"]= "front yard"
frontYard.exits["N"] = "Living Room"
frontYard.inventory.append("gnome")
frontYard.inventory.append("wrench")

hallway = Room("Hallway")
hallway.description["long"] = "A hall with hardwood floors and wood paneling."
hallway.description["short"] = "A hall with hardwood floors."
hallway.description["name"] = "hallway"
hallway.exits["S"] = "Living Room"
hallway.exits["E"] = "Kitchen"
hallway.exits["W"] = "Bedroom"
hallway.addInventory("anchor")

kitchen  = Room("Kitchen")
kitchen.description["long"] = "A room with a tile floor, granite counter tops, and many shelves."
kitchen.description["short"] = "A room with counters and shelves."
kitchen.description["name"] = "kitchen"
kitchen.exits["W"] = "Hallway"
kitchen.inventory.append("cheese")
kitchen.inventory.append("bread")

bedroom = Room("Bedroom")
bedroom.description["long"] = "A carpeted room with a well made bed. The sheets appear to be silk."
bedroom.description["short"] = "A carpeted room with a bed."
bedroom.description["name"] = "bedroom"
bedroom.exits["E"] = "Hallway"

######################################
#functions


def mainLoop(player):
    print ("\n\nWelcome to the adventure game!\n\n")
    print ("Do you want to load from a saved game or start a new game?")
    while True:
        playerInput = input("type LOAD or NEW:  ").lower()
        if playerInput in "loadnew":
            break
    if playerInput == "load":
        saveGames = listFilesWithSuffix(GameObject.saveGameSuffix)
        print("There are "+str(len(saveGames))+" games saved:")
        for fileName in saveGames:
            print(fileName[:-len(GameObject.saveGameSuffix)])
        fileName = input("Type your the name of your saved game:  ")
        try:
            GameObject.loadGameState(player,fileName + GameObject.saveGameSuffix)
        except FileNotFoundError:
            print("File not found. Starting new game.")

    print("\n")
    startingOutput = textwrap.wrap(player.activeRoom.describe())
    for line in startingOutput:
        print (line)
    while True:
        playerInput = input("\n>> ")
        print()
        if playerInput == "exit":
            break
        for line in textwrap.wrap(parseInput(player, playerInput)):
            print (line)


    while True:
        playerInput = input("Would you like to save your progress? (Y/N) ").lower()
        if playerInput == "y":
            while True:
                fileName = input("Please create a save game name: ")
                if isAlphaNumeric(fileName):
                    break
                print ("Use only letters and numbers.")
            GameObject.saveGameState(player,fileName + GameObject.saveGameSuffix)
            break
        elif playerInput == "n":
            break
        else:
            print ("Invalid entry.")



    print("\nGoodbye!\n")

def listFilesWithSuffix(suffix):
    """Returns a list of files with the given suffix in the current directory"""
    fullList = os.listdir()
    outputList = []
    for fileName in fullList:
        if fileName[-len(suffix):] == suffix:
            outputList.append(fileName)
    return outputList

def isAllLetters(string):
    """bool: Checks if a string is composed of only letters and spaces"""
    for c in string:
        if c not in " qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM":
            return False
    return True

def isAlphaNumeric(string):
    """bool: Checks if a string is composed of letters and numbers (no spaces)"""
    for c in string:
        if c not in "0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM":
            return False
    return True

def parseInput(player, inputString):
    """Converts a string into commands"""
    commandDictionary = {

    "go":commandGo,
    "n":commandGo,
    "north":commandGo,
    "s":commandGo,
    "south":commandGo,
    "e":commandGo,
    "east":commandGo,
    "w":commandGo,
    "west":commandGo,

    "eat":commandEat,
    "take":commandTake,
    "drop":commandDrop,
    "help":commandHelp,
    "look":commandLook,
    "inventory":commandInventory,
    "use":commandUse
    }

    verbs = list(commandDictionary.keys())

    nouns = list(GameObject.AllObjectsDict.keys())
    
    shortWords = ["to","the","from","a","an", "I", "me", "at", " ", ""]

    wholeVocabulary = verbs + nouns

    #clean up input

    l = inputString.lower().split(" ")
    
    for i in range(len(l)-1,-2,-1): #goes through starting at last item
        if l[i] in shortWords:
            del l[i]

    if not isAllLetters(inputString):
        return "Please use only letters."

    unknownWords = []
    for word in l:
        if not word in wholeVocabulary:
            unknownWords.append(word)
    if unknownWords:
        outputString = "I don't know these words:"
        for word in unknownWords:
            outputString += " " + word
        return outputString + "."

    try:
        return commandDictionary[l[0]](l)
    except KeyError:
        #This catches any times that all input words are valid, but are not in the expected dictionary
        #(commandDictionary or GameObject.AllObjectsDict). It's more useful than I thought!
        return "I'm not sure what you're saying."
    except IndexError:
        return "That command requires an additional word."



####### player command functions #######

def commandGo(inputList):

    if inputList[0] == "go":
        direction = inputList[1]
    else:
        direction = inputList[0]
    try:
        player.activeRoom = GameObject.AllObjectsDict[player.activeRoom.exits[directionToCommand(direction)]]
        return player.activeRoom.describe()
    except KeyError:
        return "You can't go that way."

def commandUse(inputList):
    try:
        return GameObject.AllObjectsDict[inputList[1]].use()
    except AttributeError:
        return "You can't use that."


def commandEat(inputList):
    if not GameObject.AllObjectsDict[inputList[1]].edible:
        return "That is inedible."
    try:
        player.inventory.remove(inputList[1])
    except ValueError:
        try:
            player.activeRoom.inventory.remove(inputList[1])
        except ValueError:
            return "There is no " + inputList[1] + " here."                 #this is repeated in commandTake
    player.hitpoints += GameObject.AllObjectsDict[inputList[1]].edible
    return "NOM NOM NOM"

def commandTake(inputList):
        try:
            player.activeRoom.inventory.remove(inputList[1])
            player.inventory.append(inputList[1])
            return "You take the " + inputList[1]
        except ValueError:
            return "There is no " + inputList[1] + " here."                 #this is repeated in commandEat

def commandDrop(inputList):
        try:
            player.inventory.remove(inputList[1])
            player.activeRoom.inventory.append(inputList[1])
            return "You drop the " + inputList[1]
        except ValueError:
            return "You don't have any " + inputList[1] +" to drop."

def commandHelp(inputList):
        outputString = "These are the things you can do:"
        for word in verbs:
            outputString += "\n"+ word
        return outputString

def commandLook(inputList):
        try:
            if inputList[1] in player.inventory or inputList[1] in player.activeRoom.inventory:
                return GameObject.AllObjectsDict[inputList[1]].describe(True)
        except IndexError:
            return player.activeRoom.describe(True)

def commandInventory(inputList):
        return player.listInventory(True)

def directionToCommand(directionString):
    """converts  a direction string to a capital letter"""
    north = ["n","north"]
    south  = ["s","south"]
    east  = ["e","east"]
    west  = ["w","west"]
    anyDirection = north + south + east + west

    if directionString in north:
        direction = "N"
    elif directionString in south:
        direction = "S"
    elif directionString in east:
        direction = "E"
    else:
        direction = "W"
    return direction

player = Player("Player")
player.activeRoom = livingRoom
mainLoop(player)