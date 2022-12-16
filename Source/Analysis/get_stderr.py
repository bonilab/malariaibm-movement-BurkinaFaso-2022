#!/usr/bin/python3

##
# get_stderr.py
#
# Generate a plot comparing the two models with their standard error noted.
##
import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
from database import select
from utility import progressBar

# General constants for the script
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=burkinafaso user=sim password=sim"
#LOCATIONS = '../../Data/analysis_cells.csv'
LOCATIONS = 'cells.csv'
REPLICATE_COUNT = 50

# Database study ids
MODEL = 17551
MARSHALL = 17546

def get_replicate_data(replicateId, filter):
    sql = """
    SELECT dm.destination AS index, sum(dm.count)
    FROM sim.districtmovement dm
    WHERE dm.replicateid = %(replicateId)s
	  AND dm.destination in ({})
	GROUP BY dm.destination"""
    return select(CONNECTION, sql.format(filter), {'replicateId': replicateId})

def get_replicates(configurationId):
    sql = """
    SELECT c.filename, r.id
    FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
    WHERE c.id = %(configurationId)s
      AND r.endtime IS NOT NULL
    ORDER BY c.filename"""
    return select(CONNECTION, sql, {'configurationId': configurationId})


# Process the replicates from the study provided and save the results to the file indicated
def process(cells, population, model, filename):
    # Prepare the filter for the queries
    filter = ','.join(cells)

    # Start by loading the replicate data from the database
    count = 0 
    data = {}    
    for replicate in get_replicates(model):
        for row in get_replicate_data(replicate[1], filter):
            key = row[0]
            if key not in data:
                data[key] = []
            data[key].append(row[1])
        
        # Update the progress bar
        count += 1
        progressBar(count, REPLICATE_COUNT)

    # Save the results to a CSV file
    with open(filename, 'w') as out:
        out.write('cell,population,mean,std,stderr\n')
        for ndx in range(0, len(cells)):
            row = np.array(data[int(cells[ndx])])
            out.write('{},{},{:.2f},{:.2f},{:.2f}\n'.format(
                cells[ndx],
                population[ndx], 
                row.mean(), 
                row.std(), 
                row.std() / math.sqrt(len(row))
            ))


def main(load):
    # Read the population and cells that were selected
    population = []
    cells = []
    with open(LOCATIONS, 'r') as input:
        reader = csv.reader(input)
        next(reader)
        for row in reader:
            population.append(row[0])
            cells.append(row[1])

    if load:
        process(cells, population, MODEL, 'model_data.csv')
        process(cells, population, MARSHALL, 'marshall_data.csv')
        print('\nData load complete!')

    model = pd.read_csv('model_data.csv', sep=',', header=0)
    marshall = pd.read_csv('marshall_data.csv', sep=',', header=0)

    fig, plot = plt.subplots()

    x = np.log10(model['population'])
    
    plot.invert_xaxis()
    plot.scatter(x, model['mean'], label='PSU')
    plot.scatter(x, marshall['mean'], label='Marshall')
    plot.legend()
    
    fig.savefig('working.png', dpi=150)


if __name__ == '__main__':
    main(True)