#!/usr/bin/python

# Simple Python script to process data from Burkina Faso survey by Marshall
#
# 'marshall_survey_condensed.csv' was prepared by condensing the survey 
# results from Marshall et al. (2016) ESM2 to a single CSV file containing
# the source and destination information.
import csv


# Load the condensed survey data
def parse_data():
    data = {}
    
    with open('data/marshall_survey_condensed.csv') as csvfile:
        # Prepare the reader, skip the first line
        reader = csv.reader(csvfile)
        next(reader)

        # Scan the file
        for line in reader:
            
            # Zero indexed, column two is origin circle, six is destination
            source = line[2]
            destination = line[6]

            # Update the map as needed
            if source not in data:
                data[source] = {}
            if destination not in data[source]:
                data[source][destination] = 0

            # Update the count
            data[source][destination] += 1

    return data


# Load the mapping of province name to the id value
def parse_mapping():
    mapping = {}
    with open('../Common/bfa_districts.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for line in reader:
            cercle = line[2]
            index = int(line[0])
            mapping[cercle] = index
    return mapping
            

mapping = parse_mapping()
data = parse_data()
f = open('out/marshall_processed.csv', 'w')
f.write("Source, Destination, Count\n")
for source in sorted(data.keys()):
    for destination in sorted(data[source].keys()):
        f.write("%i, %i, %i\n" % (mapping[source], mapping[destination], data[source][destination]))
f.close()    
        
