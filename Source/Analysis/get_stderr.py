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
import os
import pandas as pd
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
from database import select
from utility import progressBar

# General constants for the script
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=burkinafaso user=sim password=sim"
LOCATIONS = '../../Data/Movement/analysis_cells.csv'
REPLICATE_COUNT = 50

# Database study ids
MODEL = 17551
MARSHALL = 17546

# Data filenames
MERGED_CSV = '../../Data/Movement/merged_data.csv'
MODEL_CSV = '../../Data/Movement/model_data.csv'
MARSHALL_CSV = '../../Data/Movement/marshall_data.csv'
RAW_MODEL_CSV = '../../Data/Movement/raw_model_data.csv'
RAW_MARSHALL_CSV = '../../Data/Movement/raw_marshall_data.csv'


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


def plot_scatter_trips():
    # Load the data from disk
    data = pd.read_csv(MERGED_CSV, sep=',', header=0)
    data = data.sort_values(by='model_mean', ascending=False)
    print(data)

    # Prepare the plot
    matplotlib.rc_file('matplotlib-scatter')
    fig, plot = plt.subplots()
        
    x = range(0, len(data['population']))
    plot.errorbar(x, data['marshall_mean'], data['marshall_sd'], 
                  linestyle='None', ecolor='black', elinewidth=1.5, zorder=1)    
    plot.scatter(x, data['marshall_mean'], c=data['population'],
                 label='Marshall et al. Model',
                 cmap='gist_gray', edgecolors='black', zorder=3)        
    
    plot.errorbar(x, data['model_mean'], data['model_sd'], 
                  linestyle='None', ecolor='black', elinewidth=1.5, zorder=2)
    sp = plot.scatter(x, data['model_mean'], c=data['population'], 
                      label='Mathmatical Model with Travel Surface',
                      marker='s', cmap='gist_gray', edgecolors='black', zorder=4)    
    
    plot.set_xlim([-1, len(data['model_mean']) + 1])
    plot.set_ylim([0, max(data['model_mean']) + 100])
    plot.set_ylabel('Mean Trips to Cell')
    plot.xaxis.set_major_formatter(plt.NullFormatter())
    plot.legend(frameon=False)
    
    cb = fig.colorbar(sp)
    cb.set_label('Cell Population')

    fig.tight_layout()
    fig.savefig('out/testing.png')


def plot_scatter():
    # Load the data from disk
    model = pd.read_csv(MODEL_CSV, sep=',', header=0)
    marshall = pd.read_csv(MARSHALL_CSV, sep=',', header=0)

    # Prepare the plot
    matplotlib.rc_file('matplotlib-scatter')
    fig, plot = plt.subplots()

    # Plot by population and mean
    x = np.log10(model['population'])
    plot.errorbar(x, marshall['mean'], marshall['std'], 
                    linestyle='None', ecolor='black', elinewidth=1.5, zorder=1)    
    plot.scatter(x, marshall['mean'], label='Marshall et al. Model',
                    facecolors='#5A5A5A', edgecolors='black', zorder=3)        
    plot.errorbar(x, model['mean'], model['std'], 
                    linestyle='None', ecolor='black', elinewidth=1.5, zorder=2)
    plot.scatter(x, model['mean'], label='Mathmatical Model with Travel Surface',
                    facecolors='#D3D3D3', edgecolors='black', zorder=4)    
    
    # # Plot by mean and population    
    # plot.errorbar(marshall['mean'], marshall['population'], marshall['std'], 
    #                 linestyle='None', ecolor='black', elinewidth=1.5, zorder=1)    
    # plot.scatter(marshall['mean'], marshall['population'], label='Marshall',
    #                 facecolors='#5A5A5A', edgecolors='black', zorder=3)        
    # plot.errorbar(model['mean'], model['population'], model['std'], 
    #                 linestyle='None', ecolor='black', elinewidth=1.5, zorder=2)
    # plot.scatter(model['mean'], model['population'], label='PSU',
    #                 facecolors='#D3D3D3', edgecolors='black', zorder=4)
    # plot.set_ylim([0, 220000])
    # plot.set_xlim([0, 4100])
    
    
    # Add the labeled points to the map
    plot.annotate('Bobo-Dioulasso', (np.log10(56000), 3400))        # Bobo-Dioulasso, population = 57734, trips = 3474.14
    plot.annotate('Ouagadougou', (np.log10(200000), 3800))          # Ouagadougou, population = 203266, trips = 3981.72
    plot.annotate('Ouagadougou (Outskirts)', (np.log10(2100), 986)) # Ouagadougou / Outskirts, population = 2159, trips = 986
            
    # Format the ticks
    plot.set_xticklabels(format_ticks(plot.get_xticks()))
    plot.set_ylim([0, max(max(model['mean']), max(marshall['mean'])) + 100])
    plot.set_xlim([min(x) - 0.1, max(x) + 0.1])

    # Format then rest of the plot
    plot.invert_xaxis()
    plot.set_ylabel('Mean Trips to Cell')
    plot.set_xlabel('Cell Population')
    plot.legend(frameon=False)
    
    fig.tight_layout()
    fig.savefig('out/Fig. 5 - 300 dpi.png')

def format_ticks(ticks):
    labels = []
    for tick in [math.pow(10, value) for value in ticks]:
        labels.append(int(tick))
    return labels  


# Generate the plot from the data sets
def plot_boxplot():
    # Load the data from disk
    model = pd.read_csv(RAW_MODEL_CSV, sep=',', header=None)
    x  = model.loc[:,1].tolist()
    model = model.drop(columns=[0, 1])
    marshall = pd.read_csv(RAW_MARSHALL_CSV, sep=',', header=None)
    marshall = marshall.drop(columns=[0, 1])

    # Prepare the plot
    matplotlib.rc_file('matplotlib-scatter')
    fig, plot = plt.subplots()
    
    # Add the data to the plot
    bp_model = plot.boxplot(model.T, 
                            showfliers=False, notch=True, patch_artist=True, 
                            boxprops=dict(facecolor='#D3D3D3', color='black'), medianprops=dict(color='black'))
    bp_marshall = plot.boxplot(marshall.T, 
                               showfliers=False, notch=True, patch_artist=True, 
                               boxprops=dict(facecolor='#5A5A5A', color='black'), medianprops=dict(color='black'))

    # Format the plot
    plot.set_ylabel('Trips to Cell')
    plot.set_ylim([0, 4500])
    plot.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plot.legend([bp_model["boxes"][0], bp_marshall["boxes"][0]], ['PSU', 'Marshall'], loc='upper right', frameon=False)

    fig.tight_layout()
    fig.savefig('working.png')
    

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
    plot_scatter_trips()


if __name__ == '__main__':
    if not os.path.exists('out'): os.mkdir('out')
    main(False)