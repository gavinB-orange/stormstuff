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
H24 = 24 * 60


def read_insitu(args):
    logging.warning("Creating empty insitu structure ...")
    data = [[[[0 for h in range(MAX_H - MIN_H)] for d in range(DAYS)] for y in range(MAX_Y)] for x in range(MAX_X)]
    logging.warning("  done")
    size = os.path.getsize(args.insitu)
    logging.warning("Reading in-situ file ...")
    pbar = tqdm.tqdm(total=size)
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
    pbar.close()
    return data


def walk_path(insitu, cities, args):
    bad_places = []
    cities_seen = {}
    for cx, cy in cities:
        cities_seen["{}-{}".format(cx, cy)] = False
    cities_count = [0 for c in cities]
    logging.warning("Reading path file and verifying ...")
    size = os.path.getsize(args.pathfile)
    pbar = tqdm.tqdm(total=size)
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
            if "{}-{}".format(xid, yid) in cities_seen:
                cities_seen["{}-{}".format(xid, yid)] = True
            if insitu[xid][yid][date_id][hour] >= BOOM:
                bad_places.append((cid, xid + 1, yid + 1, date_id, hour + MIN_H, insitu[xid][yid][date_id][hour]))
                cities_count[cid] = H24
            else:
                if cities_count[cid] < H24:
                    cities_count[cid] += 2
            line = path.readline()
            pbar.update(len(line))
    pbar.close()
    for i in range(len(cities)):
        k = "{}-{}".format(cities[i][0], cities[i][1])
        if not cities_seen[k]:
            print("Do not see city endpoint for city {}".format(i))
            cities_count[i] = H24
    print("Result :")
    if len(bad_places) > 0:
        print("  FAILED - hit the following :")
        print("  xid, yid, date, hour, wind")
        for bad in bad_places:
            print("  {}".format(bad))
    print("City, time")
    for i in range(len(cities_count)):
        print("{},{}".format(i, cities_count[i]))
    print("Total = {}".format(sum(cities_count)))


def read_cities(args):
    logging.warning("Reading city information")
    tmp = {}
    with open(args.cities, "r") as f:
        line = f.readline()
        assert line == "cid,xid,yid\n", "Malformed city file"
        line = f.readline()
        while line != '':
            cid, xid, yid = list(map(int, line[:-1].split(',')))
            tmp[cid] = (xid - 1, yid - 1)  # shift by 1 due to 0 starting arrays
            line = f.readline()
    cities = []
    for k in sorted(tmp.keys()):
        cities.append(tmp[k])
    assert tmp[0] == cities[0], "Something wrong reading cities"
    logging.warning("  done")
    return cities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pathfile", default="output_path.csv", help="Path file in csv format")
    parser.add_argument("-i", "--insitu", default="insitu.csv", help="Insitu file for the day")
    parser.add_argument("-c", "--cities", default="CityData.csv", help="City data in csv format")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(asctime)s : %(message)s')
    insitu = read_insitu(args)
    cities = read_cities(args)
    walk_path(insitu, cities, args)


if __name__ == '__main__':
    main()
