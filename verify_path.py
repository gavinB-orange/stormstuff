#!/usr/bin/env python3
#
# input format is :
# cid,date_id,hour:mins,xid,yid

import argparse
import logging
import os
import pdb
import tqdm


MESSAGE_COUNT = 100000
MAX_X = 580
MAX_Y = 580
MAX_H = 21
MIN_H = 3
DAYS = 11 
INSITUHEADER = "xid,yid,date_id,hour,wind\n"
BOOM = 15.0

def read_insitu(args):
    data = [[[[0 for h in range(MAX_H - MIN_H)] for d in range(DAYS)] for y in range(MAX_Y)] for x in range(MAX_X)]
    size = os.path.getsize(args.insitu)
    pbar = tqdm.tqdm(total=size)
    logging.warning("Reading in-situ file ...")
    with open(args.insitu, "r") as insitu:
        iline = insitu.readline()
        pbar.update(len(iline))
        assert iline == INSITUHEADER, "unexpected content in {}".format(args.insitu)
        iline = insitu.readline()
        pbar.update(len(iline))
        while iline != '':
            ix_r, iy_r, idate_r, ihour_r, iwind_r = iline[:-1].split(',')
            ix, iy, idate, ihour = int(ix_r) - 1, int(iy_r) - 1, int(idate_r), int(ihour_r) - MIN_H
            iwind = float(iwind_r)
            try:
                data[ix][iy][idate][ihour] = iwind
            except IndexError:
                pdb.set_trace()
            iline = insitu.readline()
            pbar.update(len(iline))
    return data


def walk_path(insitu, args):
    ok_count = 0
    bad_places = []
    size = os.path.getsize(args.pathfile)
    pbar = tqdm.tqdm(total=size)
    logging.warning("Reading path file and verifying ...")
    with open(args.pathfile, "r") as path:
        line = path.readline()
        pbar.update(len(line))
        while line != '':
            cid_r, date_id_r, ts_r, xid_r, yid_r = line[:-1].split(',')
            cid = int(cid_r)
            date_id = int(date_id_r)
            h_r, _ = ts_r.split(':')
            hour = int(h_r) - MIN_H
            xid, yid = int(xid_r) - 1, int(yid_r) - 1
            if insitu[xid][yid][date_id][hour] >= BOOM:
                bad_places.append((cid, xid + 1, yid + 1, date_id, hour + MIN_H, insitu[xid][yid][date_id][hour]))
            else:
                ok_count += 1
            line = path.readline()
            pbar.update(len(line))
    print("Result :")
    if len(bad_places) > 0:
        print("  FAILED - hit the following :")
        print("  xid, yid, date, hour, wind")
        for bad in bad_places:
            print("  {}".format(bad))
        print("Score = 24h")
        print("  Number of OK steps = {}".format(ok_count))
    else:
        print("  OK steps = {}".format(ok_count))
        print("  And no storms hit. Congratulations.")
        print("  Score = {}".format(ok_count * 2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pathfile", default="output_path.csv", help="Path file in csv format")
    parser.add_argument("-i", "--insitu", default="insitu.csv", help="Insitu file for the day")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(asctime)s : %(message)s')
    insitu = read_insitu(args)
    walk_path(insitu, args)


if __name__ == '__main__':
    main()
