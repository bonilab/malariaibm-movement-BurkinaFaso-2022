#!/usr/bin/python3

##
# select_cells.py
#
# This script prepares a list of cells to use for model validation based upon the sorted
# list of the population in a given cell). 
##
import numpy
import random
import sys

FILENAME = 'cells.csv'
POPULATION = '../../Data/GIS/bfa_population.asc'

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import ascFile as asc

[header, data] = asc.load_asc(POPULATION)

# Load the population data
population = []
for row in range(0, header['nrows']):
    for col in range(0, header['ncols']):
        if data[row][col] == header['nodata']: continue
        population.append(int(data[row][col]))

# Convert to a numpy array and sort,  note the original indices
population = numpy.array(population)
indices = numpy.argsort(population)
population = numpy.sort(population)

# Open the file we will write to, start by writing the header
with open(FILENAME, 'w') as cells:
    cells.write('population,cell\n')
    
    # Itinerate through the list in reverse, randomly select a cell from the blocks
    last = len(population) - 1
    first = last - 100
    while last > 0: 
        # Select a random value from the range
        ndx = random.randrange(first, last)
        print(ndx, population[ndx], indices[ndx])
        cells.write('{},{}\n'.format(population[ndx], indices[ndx]))

        # Move to the next bin
        last -= 100
        first -= 100
        if first < 0:
            first = 0
