#!/usr/bin/env python3

WEIGHTSTR = "1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0"
EMPTY10 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
FILENAME = "ForecastDataforTraining_201712.csv"
OUTPUT = "processed_data_for_training.csv"
NEWHEADER = "xid,yid,date_id,hour,wind\n"

import argparse
import sys


class Cacher(object):
    """
    We need to build up the model data over multiple lines.
    This takes the xid, yid, date_id, hour and creates a key
    used for caching. The key links to an array of values for
    each model. 
    If the key does not match the current active key, write out
    the processed value for that (xid, yid, date_id, hour) and
    start a new
    """

    
    def __init__(self, weights):
        self.model_data = EMPTY10
        self.key = None
        self.added = 0
        self.weights = weights
        self.wsum = 0
        for w in self.weights:
            self.wsum += w

    def calc(self):
        value = 0
        for i in range(len(self.model_data)):
            value += self.model_data[i] * self.weights[i]
        value /= self.wsum
        return value

    def add_line(self, line):
        if line is None:  # special case - write what we have
            assert self.key is not None
            return "{0},{1},{2},{3},{4}\n".format(self.key[0],
                                                  self.key[1],
                                                  self.key[2],
                                                  self.key[3],
                                                  self.calc())
        xid_r, yid_r, date_id_r, hour_r, model_r, wind_r = line.split(',')
        xid, yid, date_id, hour, model, wind = int(xid_r), int(yid_r), int(date_id_r), int(hour_r), int(model_r), float(wind_r)
        model -= 1  # models are 1 .. 10
        newkey = (xid, yid, date_id, hour)
        if self.key is None:  # first time 
            self.added = 1
            self.key = newkey
            self.model_data = EMPTY10
            self.model_data[model] = wind
            return None
        if newkey != self.key:  # only one key at a time
            assert self.added == 10
            self.added = 1
            result = "{0},{1},{2},{3},{4}\n".format(self.key[0],
                                                    self.key[1],
                                                    self.key[2],
                                                    self.key[3],
                                                    self.calc())
            self.key = newkey
            self.model_data = EMPTY10
            self.model_data[model] = wind
            return result
        # OK - we just record this model's data and return None
        self.added += 1
        self.model_data[model] = wind
        return None 
        



def scan_file_and_process(infile, outfile, weights):
    counter = 0
    cache = Cacher(weights)
    with open(infile, "r") as fin:
        with open(outfile, "w") as fout:
            line = fin.readline()
            line = line[:-1]  # drop \n
            # First line is a header - write new header and skip
            assert line == "xid,yid,date_id,hour,model,wind", "line is : " + line
            fout.write(NEWHEADER)
            line = fin.readline()
            while line != '':
                try:
                    if line[-1] == '\n':
                        line = line[:-1]  # drop \n
                except IndexError:
                    print("Bad line is " + line)
                    raise
                if counter % 1000 == 0:
                    print(counter)
                counter += 1
                result = cache.add_line(line)
                if result != None:
                    fout.write(result)
                line = fin.readline()
            # still has data for last line - write it
            fout.write(cache.add_line(None))


def get_weights(wstr):
    texts = wstr.split(',')
    if len(texts) != 10:
        return None
    try:
        ws = [float(x) for x in texts]
    except ValueError:
        return None
    return ws
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=FILENAME, help="file to process")
    parser.add_argument("-o", "--output", default=OUTPUT, help="filename for results")
    parser.add_argument("-w", "--weights", default=WEIGHTSTR, help="comma separated weights e.g. 1.0,0.9,0.2,0.4 ...")
    args = parser.parse_args()
    print("Input file is " + args.input)
    print("Output file is " + args.output)
    weights = get_weights(args.weights)
    assert weights is not None, "Malformed weights string"
    scan_file_and_process(args.input, args.output, weights)

if __name__ == '__main__':
    main()
