#!/usr/bin/env python

# walk the path and report problems


import argparse
import json
import logging


EXPECTEDHDR = "xid,yid,date_id,hour,wind\n"
message_count = 100000


def scan_file_for_dimensions(fn):
    mx = 0
    my = 0
    mxh = 0
    minh = 24  # hour cannot be beyond end of day
    count = 0
    logging.warning("Scanning input file for size information ...")
    with open(fn, "r") as f:
        line = f.readline()
        assert line == EXPECTEDHDR, "Malformed file - header does not match expectations"
        line = f.readline()
        while line != '':
            if count % message_count == 0:
                print(count)
            count += 1
            # note dropping of final \n
            xid_r, yid_r, date_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hid = int(xid_r), int(yid_r), int(hour_r)
            if xid > mx:
                mx = xid
            if yid > my:
                my = yid
            if hid > mxh:
                mxh = hid
            if hid < minh:
                minh = hid
            line = f.readline()
        return mx, my, minh, mxh


def read_data_and_shift_one(filename):
    xsize, ysize, minh, maxh = scan_file_for_dimensions(filename)
    # create empty structure
    data = [[[0 for y in range(ysize)] for x in range(xsize)] for h in range(maxh - minh)]
    with open(filename, "r") as f:
        line = f.readline()
        assert line == EXPECTEDHDR, "Unexpected format for insitu file"
        line = f.readline()
        while line != '':
            xid_r, yid_r, date_id_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hour, wind = int(xid_r), int(yid_r), int(date_id_r), float(wind_r)
            data[hour - minh][x - 1][y - 1] = wind
    return data


def check_points(filename, data):
    with open(filename, "r") as f:
        line = f.readline()
        while line != '':
            x, y, h = line[:-1].split(',')
            if data[h][x][y] >= BOOM:
                raise Exception("BOOM - {},{} @ {} -> {}".format(x, y, h, data[h][x][y]))


def main():
    parser = argparse.ArgumentParser
    parser.add_argument("-p", "--pathfile", default=None, help="File with path information")
    parser.add_argument("-i", "--insitu", default=None, help="Actual weather data")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(message)s')
    data = read_data_and_shift_one(args.insitu)
    check_points(args.pathfile, data)



if __name__ == '__main__':
    main()