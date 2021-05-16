import pygame
import random
import time
import noise
import opensimplex

# Initializes the Window
pygame.init()

# How many Rectangles there should be in both dimensions
numrects = 50

# The screen resolution in pixels. Should be multiple of numrects.
screenres = 1000
# The size (width and height) of each rectangle.
size = (screenres / numrects)

# Sets up the window with pygame
screen = pygame.display.set_mode((screenres, screenres))
pygame.display.set_caption("Pathfinding algorithms")
# Draws the background the first time for the lines between the rectangles to be gray
screen.fill("gray")


def randomWalk():
    """Returns a random Tile from all open Tiles."""
    return openTiles[random.randrange(len(openTiles))]


def bestFirst():
    """Returns the Tile that is the closest to the End in openTiles."""
    recordDist = numrects**2  # The record Distance to the end. Is set to very high in the beginning
    recordCoords = (-1, -1)  # The Coordinates of the record

    for localTile in openTiles:
        # Manhattan Distance to end
        dist = abs(localTile[0]-(numrects-1))+abs(localTile[1]-(numrects-1))

        # If the Distance to the end is smaller than the record distance, set it and the coords to the values of localTile.
        if(dist < recordDist):
            recordDist = dist
            recordCoords = localTile

    return recordCoords


def AStar():
    """Returns the Tile that is best searched according to the A* algorithm."""
    recordHeuristic = numrects**2  # The best Heuristic found.
    recordCoords = (-1, -1)  # The Coordinates of the record

    for localTile in openTiles:
        # Heuristic of Tile
        if (not allowDiagonalMovement):
            heuristic = (abs(localTile[0]-(numrects-1))+abs(localTile[1] -
                                                            (numrects-1)))+(abs(localTile[0])+abs(localTile[1]))
        else:
            heuristic = allTiles[localTile[0]][localTile[1]].distToBeginning + \
                ((((numrects-1-localTile[0])**2) +
                 (numrects-1-localTile[1])**2)**0.5)

        # If the Heuristic is better than the record heuristic, set the record to that Tile
        if (heuristic < recordHeuristic):
            recordHeuristic = heuristic
            recordCoords = localTile

    return recordCoords


# Seed of the noise-functions. It is set to a random number for every Run to be different
noiseSeed = random.randrange(0, 1000)


def randomWalls(i, j):
    """Generates walls randomly by the given chance."""
    return random.random() < wallChance


def perlinWalls(i, j):
    """Generates walls with the help of the perlin noise function."""
    # The wallchance is 0:1, perlinnoise is -1:1
    return noise.pnoise2(i/10.0, j/10.0, base=noiseSeed, repeatx=1_048_576, repeaty=1_048_576) < (wallChance*2-1)


# The opensimplex generator that generates simplexnoise
mySimplex = opensimplex.OpenSimplex(seed=noiseSeed)


def simplexWalls(i, j):
    """Generates walls with the help of the simplexnoise function"""
    return mySimplex.noise2d(i/5.0, j/5.0) < (wallChance*2-1)


done = False  # Whether the program is finished and the window should be closed

# Whether a valid path from the beginnning to the end has already been found
pathFound = False

# Whether a valid path from the beginning to the end has been drawn
pathDrawn = False

# Whether diagonal movement should be allowed
allowDiagonalMovement = True

# The width of the borders between rectangles
borderWidth = 1

# Chance of any Tile being a wall; noise wall generators are affected, too
wallChance = 0.35

# The chosen wall-generation algorithm
wallAlgorithm = simplexWalls
#wallAlgorithm = randomWalls
#wallAlgorithm = perlinWalls

# The chosen pathfinding algorithm
pathAlgorithm = AStar
#pathAlgorithm = bestFirst
#pathAlgorithm = randomWalk


# Time of the last drawn frame.It is used to have 60 fps steadily
prev_time = time.time()


class Tile():
    """
    A Tile in a Pathfinding algorithm. Has various properties, like the coordinates of the tile this is coming from.
    """

    previousTile = None  # The Coordinates of the previous Tile as a tuple
    # The current distance to the beginning. It is used by A* to keep track of the distance to the beginning
    distToBeginning = numrects**2

    # Updates the distance to beginning as well as the previousTile. Is used by A*
    def update(self, coords, otherTile):
        if (allowDiagonalMovement):
            distToOther = (((coords[0]-otherTile[0])**2) +
                           ((coords[1]-otherTile[1])**2))**0.5
        else:
            distToOther = abs(coords[0]-otherTile[0]) + \
                abs(coords[1]-otherTile[1])

        # Updates the previousTile if the path across it is shorter
        if(distToOther+(allTiles[otherTile[0]][otherTile[1]].distToBeginning) < self.distToBeginning):
            self.distToBeginning = distToOther + \
                (allTiles[otherTile[0]][otherTile[1]].distToBeginning)
            self.previousTile = otherTile


allTiles = [[Tile() for i in range(numrects)]
            for i in range(numrects)]  # An Array containing all Tiles
openTiles = []  # All coordinates that are currently "open": in concideration
closedTiles = []  # All coordinates that were already visited
wallTiles = []  # All coordinates of walls

openTiles.append((0, 0))  # Adds the beginning to the open Tiles
# Sets the beginnings distance to itself to 0
allTiles[0][0].distToBeginning = 0


# Generating Walls with the chosen algorithm


for i in range(numrects):
    for j in range(numrects):
        if (wallAlgorithm(i, j)):
            wallTiles.append((i, j))


# Removes Beginning and End Points from walls
if ((0, 0) in wallTiles):
    wallTiles.remove((0, 0))
if((numrects-1, numrects-1) in wallTiles):
    wallTiles.remove((numrects-1, numrects-1))


def backtracePath():
    """
    Backtraces the Path from the end to the beginning by looking at the previousTile attribute of all Tiles linked beginning from the endpoint. 
    """

    global pathDrawn  # Needs to write to pathdrawn to set it to true

    # Sets the beginnning of the backtrace to the end
    currentTile = (numrects-1, numrects-1)

    # tilePath will contain the coordinates of all tiles that are part of the backtrace. The beginning node will not be included in the backtrace.
    tilePath = [(0, 0)]

    while currentTile != (0, 0):  # Until the Beginning is reached,
        # Add this tile to the tilePath
        tilePath.append(currentTile)
        # And set currentTile to the previous tile of the current tile.
        currentTile = allTiles[currentTile[0]][currentTile[1]].previousTile

    outArray = []  # All updates. This array will be returned.

    for localTile in tilePath:  # Fills the array so every tile in tilePath gets drawn in green
        outArray.append([localTile, "green"])

    # Sets the global variable to True. This prevents anything to happen later.
    pathDrawn = True

    return outArray


def oneIteration(algorithm):
    """
    Simulates one Iteration of a the given Pathfinding algorithm.
    """

    # Needs to change the open and closed Tiles
    global closedTiles, openTiles, pathFound

    if(len(openTiles) == 0):  # If no path is possible, return empty.
        return []

    # Pick an open Tile according to the given algorithm
    randomTile = algorithm()
    # If it is the end node, end correctly
    if(randomTile == (numrects-1, numrects-1)):
        pathFound = True
        return []

    # Generate the next open tiles
    possibleNewOpens = []  # Possible new Open Tiles

    # Possible new tiles in the cardinal directions
    possibleNewOpens.append(((randomTile[0]+1), (randomTile[1])))
    possibleNewOpens.append(((randomTile[0]-1), (randomTile[1])))
    possibleNewOpens.append(((randomTile[0]), (randomTile[1]+1)))
    possibleNewOpens.append(((randomTile[0]), (randomTile[1]-1)))

    # If they are allowed, possible new tiles on the diagonals
    if(allowDiagonalMovement):
        possibleNewOpens.append(((randomTile[0]-1), (randomTile[1]-1)))
        possibleNewOpens.append(((randomTile[0]+1), (randomTile[1]-1)))
        possibleNewOpens.append(((randomTile[0]-1), (randomTile[1]+1)))
        possibleNewOpens.append(((randomTile[0]+1), (randomTile[1]+1)))

    # Removes every tile that is a wall
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if localTile not in wallTiles]

    # removes every tile that is offgrid
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if (localTile[0] >= 0)]
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if (localTile[1] >= 0)]
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if (localTile[0] < numrects)]
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if (localTile[1] < numrects)]

    # Updates the heuristic of possibleNewOpens (for A*)
    for localTile in possibleNewOpens:
        allTiles[localTile[0]][localTile[1]].update(
            (localTile[0], localTile[1]), randomTile)

    # Removes every tile that is in closed
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if localTile not in closedTiles]
    # Removes every tile that is in opens (no doubles are allowed)
    possibleNewOpens = [
        localTile for localTile in possibleNewOpens if localTile not in openTiles]

    # Add the current tile to closed tiles
    closedTiles.append(randomTile)

    # Remove from open tiles
    openTiles.remove(randomTile)

    # Add new Tiles to open tiles
    for localTile in possibleNewOpens:
        openTiles.append(localTile)

    # Creates an array that will be returned that contains all changes
    outArray = []

    # Draws the tile that was updated in blue
    outArray.append([randomTile, "blue"])

    for localTile in possibleNewOpens:
        # Draws all tiles that were added to the open tiles in purple
        outArray.append([localTile, "purple"])

    return outArray


# Draws the entire grid once, with walls in concideration
for i in range(numrects):
    for j in range(numrects):
        tileColor = "white"
        if (i == 0 and j == 0):  # Gives the beginning node a yellow color
            tileColor = "yellow"
        if(i == numrects-1 and j == numrects-1):  # Gives the end node an orange color
            tileColor = "orange"

        if ((i, j) in wallTiles):  # Draws walls in black
            tileColor = "black"

        x1 = borderWidth + (i*size)
        y1 = borderWidth + (j*size)
        xlength = size - borderWidth
        ylength = size - borderWidth
        pygame.draw.rect(screen, tileColor, (x1, y1, xlength, ylength))

numframe = 0 #The current frame number. Mainly used for debugging.

# Main drawing loop:
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #Ends the loop if the game should quit
            done = True

    # A list of Updates to the grid. Contains a tuple of coordinates and a color to draw that tile in. (structure: [(tupleX,tupleY),"Color"],[...])
    updates = []

    # Now, the screen is drawn with the changes

    if (not pathFound):
        # Runs one iteration of the chosen pathfinding algorithm, if the path was not already found
        updates = oneIteration(pathAlgorithm)
    elif(not pathDrawn):
        updates = backtracePath()

    for update in updates:  # Draws the tile of every update in the given color
        (i, j) = update[0]
        x1 = borderWidth + (i*size)
        y1 = borderWidth + (j*size)
        xlength = size - borderWidth
        ylength = size - borderWidth
        pygame.draw.rect(screen, update[1], (x1, y1, xlength, ylength))

    if(len(updates) > 0):  # Only updates the screen if necessary
        pygame.display.flip()
    numframe += 1

    # Sleeps until the next frame needs to be drawn
    curr_time = time.time()
    diff = curr_time - prev_time
    delay = max(1.0/60.0 - diff, 0)
    time.sleep(delay)
    prev_time = curr_time
