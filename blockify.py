#!/usr/bin/env python3
#
# takes a NxNxT data set, and transforms to smaller MxMxT set
# where M = N / ratio.  The data value per "block" is set
# according to various strategies controller by args.

import argparse
import logging

INPUTFILE = "combined_test.csv"
OUTPUTFILE = "blockified.csv" 

class Block(object):
    """
    Holds data for a block
    """
    ADD = 0
    MAX = 1
    
    def __init__(self, x, y, d, h, points, mode):
        self.x = x
        self.y = y
        self.d = d
        self.h = h
        self.points = points
        self.value = 0.0
        self.count = 0
        self.mode = Block.ADD

    def add(self, v):
        if self.mode == Block.ADD:
            self.value += v
        else:
            if v > self.value:
                self.value = v
        self.count += 1
        if self.count == self.points:
            return True
        return False

    def get(self):
        if self.mode == Block.ADD:
            return self.value / self.count
        else:
            return self.value

    def __str__(self):
        return "Block {}.{}.{}.{} value {}".format(self.x, self.y, self.d, self.h, self.get())

    def get_line(self):
        return "{},{},{},{},{}\n".format(self.x, self.y, self.d, self.h, self.get())


class Blockifier(object):
    """
    Takes a single stream of line data and produces :
        * A file with the blockified 3-d data.
        * A file per block with the raw data.
    Input stream = xid,yid,date_id,hour,wind
    Output stream = xid',yid',date_id,hour,processed(wind)
    per-block files = selected data as per input stream
    """

    header = "bx,by,date_id,hour,wind\n"

    def __init__(self, ratio, foutn, mode):
        self.store = {}
        self.ratio = ratio
        self.max_points = ratio * ratio
        self.fout = open(foutn, "w")
        self.fout.write(Blockifier.header)
        self.mode = mode

    def add_line(self, line):
        """
        
        """
        xid_r, yid_r, date_r, hour_r, wind_r = line[:-1].split(',')
        xid, yid, date, hour, wind = int(xid_r), int(yid_r), int(date_r), int(hour_r), float(wind_r)
        bx = int(xid / self.ratio)
        by = int(yid / self.ratio)
        key = "{0}_{1}_{2}".format(bx, by, hour)
        if key in self.store:
            if self.store[key].add(wind):  # true implies full
                logging.info("{} is full".format(self.store[key]))
                newline = self.store[key].get_line()
                self.fout.write(newline)
                del(self.store[key])
                logging.info("Removed block {}".format(key))
        else:
            self.store[key] = Block(bx, by, date, hour, self.max_points, self.mode)
            logging.info("Adding new block {} - total is {}".format(key, len(self.store)))
            if self.store[key].add(wind):  # true implies full
                logging.info("{} is full".format(self.store[key]))
                newline = self.store[key].get_line()
                self.fout.write(newline)
                del(self.store[key])
                logging.info("Removed block {}".format(key))

    def drain(self):
        logging.info("Draining remaining blocks")
        sz = len(self.store)
        logging.info("Starting drain with {} items".format(sz))
        for k in self.store.keys():
            logging.info("{} -> {}".format(k, self.store[k]))
            newline = self.store[k].get_line()
            self.fout.write(newline)
            self.store[k] = None
        self.fout.close()
        
        

def process_and_block(args):
    if args.mode.upper() == 'ADD':
        blker = Blockifier(args.ratio, args.output, Block.ADD)
    else:
        if args.mode.upper() == 'MAX':
            blker = Blockifier(args.ratio, args.output, Block.MAX)
        else:
            raise("Unknown mode")
    with open(args.input, "r") as f:
        line = f.readline()
        assert line == "xid,yid,date_id,hour,wind\n", "line is : " + line
        line = f.readline()
        while line != '':
            blker.add_line(line)
            line = f.readline()
    blker.drain()
        

def scan_file_for_max(fn):
    mx = 0
    my = 0
    mh = 0
    logging.warning("Scanning input file for max_x and max_y ...")
    with open(fn, "r") as f:
        line = f.readline()
        assert line == "xid,yid,date_id,hour,wind\n", "line is : " + line
        line = f.readline()
        while line != '':
            # note dropping of final \n
            xid_r, yid_r, date_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hid = int(xid_r), int(yid_r), int(hour_r)
            if xid > mx:
                mx = xid
            if yid > my:
                my = yid
            if hid > mh:
                mh = hid
            line = f.readline()
        return mx, my, mh


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=INPUTFILE, help="file to process")
    parser.add_argument("-o", "--output", default=OUTPUTFILE, help="output file name")
    parser.add_argument("-r", "--ratio", default=10, type=int, help="ratio of reduction")
    parser.add_argument("-x", "--max_x", default=0, type=int, help="max x value - if not provided, the file will be scanned.")
    parser.add_argument("-y", "--max_y", default=0, type=int, help="max y value - if not provided, the file will be scanned.")
    parser.add_argument("-H", "--max_h", default=0, type=int, help="max hour value - if not provided, the file will be scanned.")
    parser.add_argument("-l", "--log", default='INFO', help="Logging level to use.")
    parser.add_argument("-m", "--mode", default='ADD', help="Mode to use - add or max.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(levelname)s:%(message)s')
    if args.max_x == 0 or\
       args.max_y == 0 or\
       args.max_h == 0 :
        args.max_x, args.max_y, args.max_h = scan_file_for_max(args.input)
    logging.info("Max X, Y is {}, {}".format(args.max_x, args.max_y))
    logging.info("Max hour seen = {}".format(args.max_h))
    process_and_block(args)


if __name__ == '__main__':
    main()
