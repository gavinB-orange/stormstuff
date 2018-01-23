#!/usr/bin/env python3
"""
Splits the input file into per-day sets
"""

import argparse

FILENAME = "ForecastDataforTraining_201712.csv"
OUTPUT = "processed_data_for_training"
NEWHEADER = "xid,yid,date_id,hour,model,wind\n"
message_count = 10000  # every message_count iterations, output a message

day_files = {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=FILENAME, help="file to process")
    parser.add_argument("-o", "--output", default=OUTPUT, help="filename for results")
    args = parser.parse_args()
    print("Input file is " + args.input)
    print("Output file is " + args.output)
    counter = 0
    with open(args.input, "r") as fin:
        line = fin.readline()  # should be the header line
        assert line == "xid,yid,date_id,hour,model,wind\n", "line is : " + line
        line = fin.readline()
        while line != '':
            if counter % message_count == 0:
                print(counter)
            counter += 1
            xid_r, yid_r, date_id_r, hour_r, model_r, wind_r = line.split(',')
            try:
                _ = day_files[date_id_r]
            except KeyError:
                outfilename = "{0}.{1}.csv".format(args.output, date_id_r)
                fout = open(outfilename, "w")
                print("Opened {} for writing".format(outfilename))
                day_files[date_id_r] = fout
                try:
                    day_files[date_id_r].write(NEWHEADER)
                except IOError:
                    day_files[date_id_r].close()
            try:
                day_files[date_id_r].write(line)
                line = fin.readline()
            except IOError:
                for tf in day_files.keys():
                    day_files[tf].close()
                raise

if __name__ == '__main__':
    main()
        
            
        
    
