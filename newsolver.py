#!/usr/bin/env python3
#
# Solve the storm problem using a different data structure

import argparse
import logging

WEATHERHEADER = "xid,yid,date_id,hour,wind\n"
MESSAGE_COUNT = 100000


class Cell(object):
    """
    Hold the cell info
    """
    def __init__(self, x, y, t, parent, value):
        self.x = x
        self.y = y
        self.t = t
        self.parent = parent
        self.value = value

    @staticmethod
    def get_hash_key(x, y, t):
        return "{}_{}_{}".format(x, y, t)

    @staticmethod
    def expand_hash_key(key):
        return map(int, key.split('_'))

    def get_my_key(self):
        return Cell.get_hash_key(self.x, self.y, self.t)

    def get_my_coords(self):
        return self.x, self.y, self.t

    def get_parent(self):
        return self.parent

    def get_value(self):
        return self.value


class SolverStore(object):
    """
    The main workhorse of the solver - holds all the items
    """

    MAX_HOUR = 21
    MIN_HOUR = 3
    STEPS_PER_HOUR = 30

    def __init__(self, cell, layers, xsize, ysize, wthing, step=90):
        self.store = {}
        self.store[cell.get_my_key()] = cell
        self.xsize = xsize
        self.ysize = ysize
        self.wthing = wthing
        self.step = step
        self.layers = layers

    def validate(self, x, y, t):
        if x < 0:
            return False
        if x >= self.xsize:
            return False
        if y < 0:
            return False
        if y >= self.ysize:
            return False
        if t < (SolverStore.MIN_HOUR * SolverStore.STEPS_PER_HOUR):
            return False
        if t >= (SolverStore.MAX_HOUR * SolverStore.STEPS_PER_HOUR):
            return False
        return True

    @staticmethod
    def to_layer_index(t):
        li = int(t / SolverStore.STEPS_PER_HOUR) - SolverStore.MIN_HOUR
        assert li >= 0, "Bad calculation!"
        return li

    def calc_value(self, current, wind):
        return current * (1 - self.wthing.get_prob(wind))

    def generate_children(self, current):
        """
        Children = stay here or move 1 in up/down/left/right
        :param current:
        :return:
        """
        cx, cy, ct = current.get_my_coords()
        nt = ct + 1
        children = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy:
                    continue  # no diags
                nx = cx + dx
                ny = cy + dy
                if self.validate(nx, ny, nt):
                    nv = self.calc_value(current.get_value(), self.layers[self.to_layer_index(nt)][nx][ny])
                    children.append(Cell(nx, ny, nt, current, nv))
        # and stay in place for a step
        # TODO - this needs to change as only a change of hour causes staying in place to
        # TODO - be re-evaluated.
        if self.validate(cx, cy, nt):
            nv = self.calc_value(current.get_value(), self.layers[self.to_layer_index(nt)][cx][cy])
            children.append(Cell(cx, cy, nt, current, nv))
        return children

    def take_step(self):
        children = []
        for k in self.store.keys():
            current = self.store[k]
            children.append(self.generate_children(current))
        for c in children:
            self.store[c.cell.get_my_key()] = c

    def report_path(self, entry):
        assert entry is not None, "Entry must not be None!"
        coords = entry.get_my_coords()
        if entry.get_parent is None:  # no parent, so at start
            return "{},{},{}\n".format(coords[0], coords[1], coords[2])
        else:
            return "{},{},{}\n".format(coords[0], coords[1], coords[2]) +\
                   self.report_path(entry.get_parent())

    def find_best_path(self, city):
        best = None
        bestconfidence = 0
        for t in range(SolverStore.MIN_HOUR * SolverStore.STEPS_PER_HOUR,
                       SolverStore.MAX_HOUR * SolverStore.STEPS_PER_HOUR - 1):
            try:
                thisone = self.store[Cell.get_hash_key(city[0], city[1], t)]
                if thisone.get_value() > bestconfidence:
                    bestconfidence = thisone.get_value()
                    best = thisone
            except KeyError:
                continue  # normal - a lot of early time, city not reached
        assert best is not None, "No path found no matter how ludicrous!"
        # OK - now walk back from here
        self.report_path(best)


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
        with open(args.weightfile, "r") as f:
            line = f.readline()
            # skip comments as weight file has a lot of extra stuff
            while line != '' and line[0] == '#':
                line = f.readline()
            self.values = map(float, line[:-1].split(','))
        assert len(list(self.values)) == Weighter.Nprobs, "Unexpected number of probabilities!"
        for v in self.values:
            assert v <= Weighter.MAX, "Bad value"

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
                msxh = hid
            if hid < minh:
                minh = hid
            line = f.readline()
        return mx, my, minh, maxh


def read_layers(args):
    xsize, ysize, minh, maxh = scan_file_for_dimensions(args.weatherfile)
    assert minh >= SolverStore.MIN_HOUR, "Unexpected early hour!"
    assert maxh < SolverStore.MAX_HOUR, "Unexpected late hour!"
    hsize = SolverStore.MAX_HOUR - SolverStore.MIN_HOUR
    layers = [[[0 for y in range(ysize)] for x in range(xsize)] for h in range(hsize)]
    with open(args.weatherfile, "r") as f:
        line = f.readline()
        assert line == WEATHERHEADER, "Unexpected header for weather data"
        line = f.readline()
        while line != '':
            xid_r, yid_r, date_id_r, hour_r, wind_r = line[:-1].split(',')
            xid, yid, hour, wind = int(xid_r), int(yid_r), int(hour_r), float(wind_r)
            layers[hour][xid][yid] = wind
            line = f.readline()
    return layers, xsize, ysize


def read_cities(args):
    cities = {}
    with open(args.cities, "r") as f:
        line = f.readline()
        assert line == "cid,xid,yid\n", "Malformed city file"
        line = f.readline()
        while line != '':
            cid, xid, yid = map(int, line[:-1].split(','))
            cities[cid] = (xid, yid)
            line = f.readline()
    return cities


def confidence(before, prob):
    return before * (1 - prob)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weatherfile", default="combined_day_1.csv",
                        help="Weather prediction data in csv format")
    parser.add_argument("-c", "--cities", default="CityData.csv", help="City data in csv format")
    parser.add_argument("-p", "--probfile", default="ProbData.csv", help="Mapping of wind to prob >= 15")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(message)s')
    layers, xsize, ysize = read_layers(args)
    cities = read_cities(args)
    weighter = Weighter(args)
    start_time = SolverStore.MIN_HOUR * SolverStore.STEPS_PER_HOUR
    london = Cell(cities[0][0], cities[0][1],
                  start_time,
                  None,
                  confidence(1, weighter.get_prob(layers[0][cities[0][0]][cities[0][1]])))
    ss = SolverStore(london, layers, xsize, ysize, weighter)
    # build up a complete set of ways of getting to everywhere
    for step in range(start_time, SolverStore.MAX_HOUR * SolverStore.STEPS_PER_HOUR - 1):
        ss.take_step()
    # now see what the best path is to every city
    for city in cities[1:]:
        ss.find_best_path(city)

if __name__ == '__main__':
    main()