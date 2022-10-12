#!/usr/bin/python3

##
# get_movement_rasters.py
#
# This script generates a single ASC raster based upon the mean of the 
# travel movement count replicates for a given configuration.
##
import os
import sys

# From the PSU-CIDD-MaSim-Support repository
sys.path.insert(1, '../../../PSU-CIDD-MaSim-Support/Python/include')
import ascFile as asc
from database import select

# Connection string for the database
CONNECTION = "host=masimdb.vmhost.psu.edu dbname=burkinafaso user=sim password=sim"


def get_header(replicateId):
    sql = """
    SELECT ncols, nrows, xllcorner, yllcorner, cellsize 
    FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
    WHERE r.id = %(replicateId)s"""
    return select(CONNECTION, sql, {'replicateId': replicateId})

def get_locations(replicateId):
    sql = """
    SELECT l.index, l.x, l.y
    FROM sim.replicate r
        INNER JOIN sim.configuration c ON c.id = r.configurationid
        INNER JOIN sim.location l ON l.configurationid = c.id
    WHERE r.id = %(replicateId)s"""
    return select(CONNECTION, sql, {'replicateId': replicateId})

def get_replicate(replicateId):
    sql = """
    SELECT dm.destination AS index, sum(dm.count)
    FROM sim.districtmovement dm
    WHERE dm.replicateid = %(replicateId)s
    GROUP BY dm.destination"""
    return select(CONNECTION, sql, {'replicateId': replicateId})

def get_replicates():
    sql = """
    SELECT c.filename, r.id
    FROM sim.configuration c
        INNER JOIN sim.replicate r ON r.configurationid = c.id
    WHERE c.studyid = 9
      AND filename NOT LIKE '%-sq.yml'
    ORDER BY c.filename"""
    return select(CONNECTION, sql, None)


def main():
    file = None
    for replicate in get_replicates():
        # Set the filename if it has not been yet
        if file is None or replicate[0] != file:
            # Check to see if we need to save the ASC file
            if file is not None:
                print("Preparing ASC file (n = {})...".format(count))
                write(movements, count, "out/{}.asc".format(file.replace('.yml', '')), replicate[1])

            # Reset our variables, note the status
            movements = {}
            count = 0
            file = replicate[0]
            print("Loading {}...".format(file.replace('.yml', '')))

        # Load the movement count for the replicate
        for row in get_replicate(replicate[1]):
            if row[0] not in movements:
                movements[row[0]] = 0
            movements[row[0]] += row[1]
        count += 1

    # We're out of the loop, so save the lsat of the data
    print("Preparing ASC file (n = {})...".format(count))
    write(movements, count, "out/{}.asc".format(file.replace('.yml', '')), replicate[1])


def write(data, count, filename, replicateId):
    NODATA = -9999

    # Prepare the ASC header
    ascheader = asc.get_header()
    result = get_header(replicateId)
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
    
    # Map the locations to the ASC data and note the mean
    for row in get_locations(replicateId):
        key = row[0]
        x = row[1]
        y = row[2]
        ascdata[x][y] = data[key] / count
    
    # Save the data to disk
    asc.write_asc(ascheader, ascdata, filename)

if __name__ == '__main__':
    if not os.path.exists('out'): os.makedir('out')
    main()