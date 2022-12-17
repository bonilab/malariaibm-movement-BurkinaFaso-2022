#!/usr/bin/python3

##
# get_stderr.py
#
# Generate a plot comparing the two models with their standard error noted.
##
import csv
import math
import matplotlib
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

# Data filenames
MODEL_CSV = 'model_data.csv'
MARSHALL_CSV = 'marshall_data.csv'

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


# Generate the plot from the data sets
def plot():
    # Load the data from disk
    model = pd.read_csv(MODEL_CSV, sep=',', header=0)
    marshall = pd.read_csv(MARSHALL_CSV, sep=',', header=0)

    # Prepare the plot
    matplotlib.rc_file('matplotlib-scatter')
    fig, plot = plt.subplots()
    
    # Add the data to the plot
    x = np.log10(model['population'])
    plot.scatter(x, model['mean'], facecolors='#D3D3D3', edgecolors='black', label='PSU')
    plot.scatter(x, marshall['mean'], facecolors='#5A5A5A', edgecolors='black', label='Marshall')
    
    # Format the ticks
    plot.set_xticklabels(format_ticks(plot.get_xticks()))
    plot.set_ylim([0, max(max(model['mean']), max(marshall['mean'])) + 100])
    plot.set_xlim([min(x) - 0.1, max(x) + 0.1])

    # Format then rest of the plot
    plot.invert_xaxis()
    plot.set_ylabel('Trips to Cell')
    plot.set_xlabel('Cell Population')
    plot.legend(frameon=False)
    
    fig.tight_layout()
    fig.savefig('working.png', dpi=150)

def format_ticks(ticks):
    labels = []
    for tick in [math.pow(10, value) for value in ticks]:
        labels.append(int(tick))
    return labels    
    

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

    # Reload the data if need be
    if load:
        process(cells, population, MODEL, MODEL_CSV)
        process(cells, population, MARSHALL, MARSHALL_CSV)
        print('\nData load complete!')

    # Generate the plots with the saved data
    plot()


if __name__ == '__main__':
    main(True)