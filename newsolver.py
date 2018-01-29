#!/usr/bin/env python3
#
# Solve the storm problem using a different data structure

import argparse
import logging
import pdb


WEATHERHEADER = "xid,yid,date_id,hour,wind\n"
MESSAGE_COUNT = 400000


class Cell(object):
    """
    Hold the cell info
    Methods sparse to improve performance
    """
    def __init__(self, x, y, t, parent, value):
        self.x = x
        self.y = y
        self.t = t
        self.parent = parent
        self.value = value

    def get_parent(self):
        return self.parent


class SolverStore(object):
    """
    The main workhorse of the solver - holds all the items
    """

    MAX_HOUR = 21
    MIN_HOUR = 3
    STEPS_PER_HOUR = 30
    MIN_STEPS = MIN_HOUR * STEPS_PER_HOUR
    MAX_STEPS = MAX_HOUR * STEPS_PER_HOUR
    TOTAL_STEPS = (MAX_HOUR - MIN_HOUR) * STEPS_PER_HOUR

    def __init__(self, cell, layers, xsize, ysize, wthing, furthestc, step=90):
        # store is a list of list of list so can do [x][y][t]
        # this is different from the layer structure which is [t][x][y]
        self.steps_size = SolverStore.TOTAL_STEPS
        logging.warning("Initializing store ...")
        self.store = [[[None for h in range(self.steps_size)] for y in range(ysize)] for x in range(xsize)]
        logging.warning("  done.")
        self.store[cell.x][cell.y][cell.t] = cell
        assert self.store[cell.x][cell.y][cell.t] is not None
        self.xsize = xsize
        self.ysize = ysize
        self.wthing = wthing
        self.furthestc = furthestc
        self.step = step
        self.layers = layers

    def validate(self, x, y, t):
        dist = abs(self.furthestc[0] - x) + abs(self.furthestc[1] - y)
        if dist > SolverStore.TOTAL_STEPS - t:
            return False
        if x < 0 or x >= self.xsize:
            return False
        if y < 0 or y >= self.ysize:
            return False
        if t < 0 or t >= SolverStore.TOTAL_STEPS:
            return False
        return True

    @staticmethod
    def to_layer_index(t):
        li = 0 <= int(t / SolverStore.STEPS_PER_HOUR) <= (SolverStore.MAX_HOUR - SolverStore.MIN_HOUR)
        assert li >= 0, "Bad calculation!"
        return li

    def calc_value(self, current, wind):
        return current * (1 - self.wthing.get_prob(wind))

    def merge_child(self, cell):
        # check the cell against all others with the same x,y,t - only the best survives.
        peer = self.store[cell.x][cell.y][cell.t]
        if peer is None or cell.value > peer.value:
            self.store[cell.x][cell.y][cell.t] = cell

    def generate_children(self, c):
        """
        Children = stay here or move 1 in up/down/left/right
        Merge into store
        :return: valid child cells
        """
        #pdb.set_trace()
        nt = c.t + 1
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if abs(dx) == abs(dy):
                    continue  # no diags
                nx = c.x + dx
                ny = c.y + dy
                if self.validate(nx, ny, nt):
                    nv = self.calc_value(c.value, self.layers[self.to_layer_index(nt)][nx][ny])
                    peer = self.store[nx][ny][nt]
                    if peer is None or nv > peer.value:
                        self.store[nx][ny][nt] = Cell(nx, ny, nt, c, nv)
        # and stay in place for a step
        if self.validate(c.x, c.y, nt):
            if nt % SolverStore.STEPS_PER_HOUR == 0:  # on a boundary
                nv = self.calc_value(c.value, self.layers[self.to_layer_index(nt)][c.x][c.y])
            else:  # during an hour, the cell value does not change.
                nv = c.value
            peer = self.store[c.x][c.y][nt]
            if peer is None or nv > peer.value:
                self.store[c.x][c.y][nt] = Cell(c.x, c.y, nt, c, nv)

    def take_step(self, city, step):
        diff = city.x - step
        if diff < 0:
            sx = 0
        else:
            sx = diff
        diff = city.x + step + 1
        if diff > self.xsize:
            ex = self.xsize
        else:
            ex = diff
        diff = city.y - step
        if diff < 0:
            sy = 0
        else:
            sy = diff
        diff = city.y + step + 1
        if diff > self.ysize:
            ey = self.ysize
        else:
            ey = diff
        for x in range(sx, ex):
            for y in range(sy, ey):
                for h in range(self.steps_size):
                    target = self.store[x][y][h]
                    if target is not None:
                        self.generate_children(target)

    def report_path(self, entry, city, dayid):
        """
        Output the resulting path.
        Note the need to +1 the x and y values as they are reduced by 1 internally,
        and adding 3 hours of steps to the time.
        :param entry: Cell of interest
        :return: String with path data.
        """
        assert entry is not None, "Entry must not be None!"
        if entry.get_parent is None:  # no parent, so at start
            return "{},{},{}:{},{},{}\n".format(city,
                                                dayid,
                                                (entry.t / SolverStore.STEPS_PER_HOUR) + SolverStore.MIN_HOUR,
                                                2 * (entry.t % SolverStore.STEPS_PER_HOUR),
                                                entry.x + 1,
                                                entry.y + 1)
        else:
            return "{},{},{}\n".format(city,
                                       dayid,
                                       (entry.t / SolverStore.STEPS_PER_HOUR) + SolverStore.MIN_HOUR,
                                       2 * (entry.t % SolverStore.STEPS_PER_HOUR),
                                       entry.x + 1,
                                       entry.y + 1) +\
                   self.report_path(entry.get_parent())

    def find_best_path(self, city, dayid):
        best = None
        bestconfidence = 0
        for t in range(SolverStore.TOTAL_STEPS):
            thisone = self.store[city[0]][city[1]][t]
            if thisone is None:  # city wasn't found yet
                continue
            else:
                if thisone.value > bestconfidence:
                    bestconfidence = thisone.value
                    best = thisone
        if best is None:
            pdb.set_trace()
        assert best is not None, "No path found no matter how ludicrous!"
        # OK - now walk back from here
        return self.report_path(best, city, dayid)

    def dump_debug_info(self):
        """
        Report various bits of info on the store.
        :return:
        """
        logging.warning("Reporting debug info on store ...")
        h_none_count = [0 for h in range(self.steps_size)]
        vcounts = [[0 for x in range(self.xsize)] for h in range(self.steps_size)]
        for h in range(self.steps_size):
            for x in range(self.xsize):
                for y in range(self.ysize):
                    if self.store[h][x][y] is None:
                        h_none_count[h] += 1
                    else:
                        vcounts[h][x] += self.store[h][x][y]
        print("steps_size = {}, xsize = {}, ysize = {}".format(self.steps_size, self.xsize, self.ysize))
        print("None per step = ")
        for h in range(self.steps_size):
            print("{} => {}".format(h, h_none_count[h]))
        print("Sum of values per y column = ")
        for h in range(self.steps_size):
            for x in range(self.xsize):
                print("{}:{} => {}".format(h, x, vcounts[h][x]))




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
    assert minh >= SolverStore.MIN_HOUR, "Unexpected early hour!"
    assert maxh < SolverStore.MAX_HOUR, "Unexpected late hour!"
    hsize = SolverStore.MAX_HOUR - SolverStore.MIN_HOUR
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
            xid, yid, hour, wind = int(xid_r) - 1, int(yid_r) - 1, int(hour_r) - SolverStore.MIN_HOUR, float(wind_r)
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
    parser.add_argument("-d", "--dayid", default=1, help="Which day is being processed. Used during output only")
    parser.add_argument("-D", "--debug", action="store_true", help="Debug mode - some extra output is provided.")
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
    start_time = 0  # just remember need to add MIN_STEPS on output
    london = Cell(cities[0][0], cities[0][1],
                  start_time,
                  None,
                  confidence(1, weighter.get_prob(layers[0][cities[0][0]][cities[0][1]])))
    furthest_city = get_furthest_city(cities)
    ss = SolverStore(london, layers, xsize, ysize, weighter, furthest_city)
    # build up a complete set of ways of getting to everywhere
    for step in range(SolverStore.TOTAL_STEPS):
        logging.warning("Step {}".format(step))
        ss.take_step(london, step)
    if args.debug:
        ss.dump_debug_info()
    # now see what the best path is to every city
    logging.warning("Finding paths ...")
    for city in cities[1:]:
        path = ss.find_best_path(city, args.dayid)

if __name__ == '__main__':
    main()
