#!/usr/bin/env python
#

import argparse
import logging
import pdb

WEATHERHEADER = "xid,yid,date_id,hour,wind\n"
MESSAGE_COUNT = 400000


class Cell(object):
    """
    Hold all cell info
    """

    INP_VAL = 0
    INP_TIM = 1
    INP_WHO = 2

    OUT_VAL = 0
    OUT_TIM = 1

    def __init__(self, x, y, layers, wthing):
        self.x = x
        self.y = y
        self.layers = layers
        self.wthing = wthing
        self.input_value_list = []        # value, when, who
        self.output_value_list = []        # value, when

    def force_input_value(self):
        self.calc_value(0, 1)
        self.input_value_list.append((0, 0, None))

    def force_output_value(self):
        self.output_value_list.append((1, 0))

    def calc_value(self, now, iv=None):
        if iv is None:
            ival = self.input_value_list[-1][Cell.INP_VAL]
        else:
            ival = iv
        oval = ival * (1 - self.wthing.get_prob(self.layers[int(now / TriggerSolver.STEPS_PER_HOUR)][self.x][self.y]))
        return oval

    def poked(self, culprit, now):
        """
        Get poked - iff the input value is better than I have currently as an input value,
        store the value, time, and culprit reference
        :param culprit:
        :param now:
        :return:
        """
        try:
            ival = self.input_value_list[-1][Cell.INP_VAL]
        except IndexError:
            ival = 0
        if culprit.output_value_list[-1][0] > ival:
            self.input_value_list.append((culprit.output_value_list[-1][Cell.OUT_VAL], now, culprit))
            self.output_value_list.append((self.calc_value(now, iv=culprit.output_value_list[-1][Cell.OUT_VAL]), now))
            return True
        else:
            return False



class TriggerSolver(object):

    MAX_HOUR = 21
    MIN_HOUR = 3
    STEPS_PER_HOUR = 30
    MIN_STEPS = MIN_HOUR * STEPS_PER_HOUR
    MAX_STEPS = MAX_HOUR * STEPS_PER_HOUR
    TOTAL_STEPS = (MAX_HOUR - MIN_HOUR) * STEPS_PER_HOUR

    def __init__(self, xsize, ysize, layers, wthing):
        self.xsize = xsize
        self.ysize = ysize
        self.store = [[Cell(x, y, layers, wthing) for y in range(ysize)] for x in range(xsize)]
        self.active = []
        self.next = []

    def poke_cell(self, me, nextdoor, now):
        """
        Ping my nextdoor neighbour and flag him about my
        :param me: my cell - potentially his parent
        :param nextdoor: target
        :param now: step
        :return:
        """
        if nextdoor.poked(me, now):
            self.next.append(nextdoor)

    def validate(self, x, y):
        if x < 0 or x >= self.xsize:
            return False
        if y < 0 or y >= self.ysize:
            return False
        return True

    def poke_all_neighbours(self, me, now):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if abs(dx) == abs(dy):
                    continue  # no diags
                nx = me.x + dx
                ny = me.y + dy
                if self.validate(nx, ny):
                    self.poke_cell(me, self.store[nx][ny], now)
        if now % TriggerSolver.STEPS_PER_HOUR:  # hour change - poke myself
            self.poke_cell(me, me, now)

    def take_step(self, now):
        logging.warning("Step {}".format(now))
        for i in range(len(self.active)):
            current = self.active[i]
            self.poke_all_neighbours(current, now)
        self.active = None
        self.active = self.next
        self.next = []

    def get_right_one(self, pl, t):
        for i in range(len(pl) - 1, -1, -1):
            if t >= pl[i][1]:  # choose this one
                return pl[i][Cell.INP_WHO]

    def trace_back(self, x, y, w, cid, did, fout):
        line = ("{},{},{}:{},{},{}".format(cid, did, int(w / TriggerSolver.STEPS_PER_HOUR), 2 * (w % TriggerSolver.STEPS_PER_HOUR), x, y))
        print(line)
        f.write(line + "\n")
        prevlist = self.store[x][y].input_value_list
        prev = self.get_right_one(prevlist, w - 1)
        if prev is not None:  # stop here if something
            self.trace_back(prev.x, prev.y, w - 1, cid, did, fout)

    def find_best_path(self, cid, cities, dayid, fout):
        cityx, cityy = cities[cid][0], cities[cid][1]
        when = self.store[cityx][cityy].input_value_list[-1][1]
        self.trace_back(cityx, cityy, when, cid, dayid, fout)


class Weighter(object):
    """
    This reads probabilities from a file, then
    uses this to map winds to probs
    The data is a single line of probabilities for buckets of 0.5 each
    """

    Nprobs = 60
    BucketWidth = 0.5
    MAX = 1.0

    def __init__(self, args):
        self.values = None
        logging.warning("Reading probabilites ...")
        with open(args.probfile, "r") as f:
            line = f.readline()
            # skip comments as weight file has a lot of extra stuff
            while line != '' and line[0] == '#':
                line = f.readline()
            self.values = list(map(float, line[:-1].split(',')))
        assert len(list(self.values)) == Weighter.Nprobs, "Unexpected number of probabilities!"
        for v in self.values:
            assert v <= Weighter.MAX, "Bad value"
        logging.warning("  done.")

    def get_prob(self, wind):
        index = int(wind / Weighter.BucketWidth)
        if index >= Weighter.Nprobs:
            index = Weighter.Nprobs - 1
        return self.values[index]

def scan_file_for_dimensions(fn):
    mx = 0
    my = 0
    maxh = 0
    minh = 24  # hour cannot be beyond end of day
    count = 0
    logging.warning("Scanning input file for size information ...")
    with open(fn, "r") as f:
        line = f.readline()
        assert line == WEATHERHEADER, "Malformed file - header does not match expectations"
        line = f.readline()
        while line != '':
            if count % MESSAGE_COUNT == 0:
                print(count)
            count += 1
            # note dropping of final \n
            xid_r, yid_r, date_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hid = int(xid_r), int(yid_r), int(hour_r)
            if xid > mx:
                mx = xid
            if yid > my:
                my = yid
            if hid > maxh:
                maxh = hid
            if hid < minh:
                minh = hid
            line = f.readline()
        return mx, my, minh, maxh

def read_layers(args):
    xsize, ysize, minh, maxh = scan_file_for_dimensions(args.weatherfile)
    assert minh >= TriggerSolver.MIN_HOUR, "Unexpected early hour!"
    assert maxh < TriggerSolver.MAX_HOUR, "Unexpected late hour!"
    hsize = TriggerSolver.MAX_HOUR - TriggerSolver.MIN_HOUR
    logging.warning("Creating layer structure ...")
    layers = [[[0 for y in range(1, ysize + 1)] for x in range(1, xsize + 1)] for h in range(minh, maxh + 1)]
    logging.warning("Reading weather file data into layers...")
    with open(args.weatherfile, "r") as f:
        line = f.readline()
        assert line == WEATHERHEADER, "Unexpected header for weather data"
        line = f.readline()
        read_count = 0
        while line != '':
            if read_count % MESSAGE_COUNT == 0:
                print(read_count)
            read_count += 1
            xid_r, yid_r, date_id_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hour, wind = int(xid_r) - 1, int(yid_r) - 1, int(hour_r) - TriggerSolver.MIN_HOUR, float(
                wind_r)
            layers[hour][xid][yid] = wind
            line = f.readline()
    return layers, xsize, ysize

def read_cities(args):
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
    return cities

def confidence(before, prob):
    return before * (1 - prob)

def get_furthest_city(cities):
    maxd = 0
    fc = None
    for c in cities[1:]:
        dist = abs(c[0] - cities[0][0]) + abs(c[1] - cities[0][1])
        if dist > maxd:
            maxd = dist
            fc = c
    return fc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weatherfile", default="combined_day_1.csv",
                        help="Weather prediction data in csv format")
    parser.add_argument("-c", "--cities", default="CityData.csv", help="City data in csv format")
    parser.add_argument("-p", "--probfile", default="ProbData.csv", help="Mapping of wind to prob >= 15")
    parser.add_argument("-o", "--output", default="paths_output.csv", help="Output path information")
    parser.add_argument("-d", "--dayid", default=1, help="Which day is being processed. Used during output only")
    #parser.add_argument("-D", "--debug", action="store_true", help="Debug mode - some extra output is provided.")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(asctime)s : %(message)s')
    layers, xsize, ysize = read_layers(args)
    cities = read_cities(args)
    weighter = Weighter(args)
    # forcing initial behaviour
    london = Cell(cities[0][0], cities[0][1], layers, weighter)
    london.force_output_value()
    ts = TriggerSolver(xsize, ysize, layers, weighter)
    ts.store[london.x][london.y].force_input_value()
    ts.poke_cell(london, ts.store[london.x][london.y], 0)
    ts.active = ts.next
    ts.next = []
    # end of initial forcing
    for now in range(1, TriggerSolver.TOTAL_STEPS):
        size = len(ts.active)
        if size == 1:
            logging.warning("1 entry in the active list.")
        else:
            logging.warning("{} entries in the active list.".format(size))
        ts.take_step(now)
    # completed the process - now extract a path
    logging.warning("Finding paths ...")
    with open(args.output, "w") as fout:
        for cityid in range(1, len(cities[1:])):
            ts.find_best_path(cityid, cities, args.dayid, fout)


if __name__ == '__main__':
    main()