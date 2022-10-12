#!/usr/bin/python3

##
# get_rasters.py
#
# This script generates mean 580Y frequency scripts based upon the 2036 (15-year)
# data set under the status quo for Burkina Faso. The script assumes that all of
# the relevant data will be under study id 9 and end with the -sq.yml filename
# suffix. 
# 
# The frequency and infected individuals queries only capture one month - 
# January 2036 - worth of data to try and maintain some consistency with the 
# PLOS GPH manuscript.
##
import csv
import os
import statistics
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import ascFile as asc
from database import select
from utility import progressBar

# Directory to cache the replicate data in
CACHE = "data/cache"

# Connection string for the database
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=burkinafaso user=sim password=sim"

# Number of replicates that we are looking for
REPLICATE_COUNT = 25

# The number of days elapsed from the start of simulation for January 2036
DAYS_ELAPSED = 10592


def get_580y_frequency(replicateId):
    sql = """
    SELECT iq.location, sum(weightedoccurrences) AS weightedoccurrences
    FROM (
        SELECT mgd.location, mgd.genomeid, sum(mgd.weightedoccurrences) AS weightedoccurrences
        FROM sim.monthlydata md 
            INNER JOIN sim.monthlygenomedata mgd ON mgd.monthlydataid = md.id
        WHERE md.replicateid = %(replicateId)s
          AND md.dayselapsed = %(dayselapsed)s
        GROUP BY mgd.location, mgd.genomeid) iq
        INNER JOIN sim.genotype g on iq.genomeid = g.id
    WHERE g.name ~ '^.....Y..'
    GROUP BY iq.location"""
    return select(CONNECTION, sql, {'replicateId': replicateId, 'dayselapsed': DAYS_ELAPSED})

def get_header(replicateId):
    sql = """
    SELECT ncols, nrows, xllcorner, yllcorner, cellsize 
    FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
    WHERE r.id = %(replicateId)s"""
    return select(CONNECTION, sql, {'replicateId': replicateId})

def get_infected_individuals(replicateId):
    sql = """
    SELECT msd.location, sum(infectedindividuals)
    FROM sim.monthlydata md
        INNER JOIN sim.monthlysitedata msd ON msd.monthlydataid = md.id
    WHERE md.replicateid = %(replicateId)s
      AND md.dayselapsed = %(dayselapsed)s
    GROUP BY msd.location"""
    return select(CONNECTION, sql, {'replicateId': replicateId, 'dayselapsed': DAYS_ELAPSED})

def get_locations(replicateId):
    sql = """
    SELECT l.id, l.x, l.y
    FROM sim.replicate r
        INNER JOIN sim.configuration c ON c.id = r.configurationid
        INNER JOIN sim.location l ON l.configurationid = c.id
    WHERE r.id = %(replicateId)s"""
    return select(CONNECTION, sql, {'replicateId': replicateId})

def get_replicates():
    sql = """
    SELECT c.filename, r.id
    FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
    WHERE c.studyid = 9
      AND c.filename LIKE '%-sq.yml'
      AND r.endtime IS NOT NULL
    ORDER BY c.filename"""
    return select(CONNECTION, sql, None)


def process(replicates, filename):
    NODATA = -9999

    # Read in and sum the frequency and infected individuals
    frequency = {}
    for replicate in replicates:
        count, individuals = {}, {}
        read("{}/{}-580y.csv".format(CACHE, replicate), count)
        read("{}/{}-infections.csv".format(CACHE, replicate), individuals)
        for key in count.keys():
            if key not in frequency:
                frequency[key] = []
            frequency[key].append(count[key] / individuals[key])
      
    # Prepare the ASC header
    ascheader = asc.get_header()
    result = get_header(replicates[0])
    ascheader['ncols'] = result[0][0]
    ascheader['nrows'] = result[0][1]
    ascheader['xllcorner'] = result[0][2]
    ascheader['yllcorner'] = result[0][3]
    ascheader['cellsize'] = result[0][4]
    ascheader['nodata'] = NODATA
    
    # Prepare the matrix for the data
    ascdata = []
    for ndx in range(ascheader['nrows']):
        ascdata.append([NODATA] * ascheader['ncols'])

    # Map the locations and store the frequency to the ASC data
    for row in get_locations(replicates[0]):
        key = row[0]
        x = row[1]
        y = row[2]
        ascdata[x][y] = statistics.median(frequency[key])

    # Save the data to disk
    asc.write_asc(ascheader, ascdata, filename)


def main():
    # Inner function to check the status of the processing block
    def check(ids, filename):
        if len(ids) == REPLICATE_COUNT:
            print("Preparing ASC file (n = {}) ...".format(len(ids)))
            process(ids, "out/{}".format(filename.replace('.yml', '.asc')))
        else:
            progressBar(REPLICATE_COUNT, REPLICATE_COUNT)
            print("Missing replicates, n  = {}, expected = {}".format(len(ids), REPLICATE_COUNT))    

    filename = None
    for replicate in get_replicates():
        # Set the filename if it has not been yet
        if filename is None or replicate[0] != filename:
            if filename is not None:
                check(ids, filename)

            # Reset our variables, note the status
            ids = []
            filename = replicate[0]
            print("Loading {}...".format(filename.replace('.yml', '')))

        # Save the data to disk if we don't already have it
        ids.append(replicate[1])
        if not os.path.exists("{}/{}-580y.csv".format(CACHE, ids[-1])):
            write(get_580y_frequency(ids[-1]), "{}/{}-580y.csv".format(CACHE, ids[-1]))
            write(get_infected_individuals(ids[-1]), "{}/{}-infections.csv".format(CACHE, ids[-1]))

        # Update the progress bar
        progressBar(len(ids), REPLICATE_COUNT)

    # Final check-block for the loop
    check(ids, filename)


def read(filename, dictionary):
    with open(filename, 'r') as read:
        for row in csv.reader(read):
            dictionary[int(row[0])] = float(row[1])

def write(data, filename):
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)


if __name__ == "__main__": 
    if not os.path.exists(CACHE): os.makedirs(CACHE)
    main()