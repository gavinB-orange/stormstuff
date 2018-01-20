#!/usr/bin/env python
#

import argparse
import random
import logging
import sys

slimit = 15

steps_per_layer = 4

class Cell(object):

    def __init__(self, value):
        self.value = value
        self.parent = None
        self.steps = []

    def __str__(self):
        return "Value = {}, parent = {}, steps = {}".format(self.value, self.parent, self.steps)

    def __repr__(self):
        return "Value = {}, parent = {}, steps = {}".format(self.value, self.parent, self.steps)

    def get_value(self):
        return self.value

    def set_value(self, v):
        self.value = v

    def has_value(self, v):
        return self.value == v

    def value_is_not(self, v):
        return self.value != v

    def set_parent(self, x, y):
        self.parent = (x, y)

    def get_parent(self):
        return self.parent

    def add_step(self, s):
        self.steps.append(s)

    def get_step(self):
        return self.steps


class Board(object):

    TARGET = '*'
    BAD = 'X'
    CLEAR = -1
    START = 0

    def __init__(self, xsize, ysize, cities, layers):
        self.pass_count = 0
        start = cities[0]
        finish = cities[1]
        self.pass_store = [[start]]  # record initial pos
        self.xsize = xsize
        self.ysize = ysize
        self.cells = [[Cell(Board.CLEAR) for x in range(xsize)] for y in range(ysize)]
        logging.warning("Start is {}".format(start))
        logging.warning("Finish is {}".format(finish))
        self.cells[start[0]][start[1]].set_value(Board.START)
        self.cells[finish[0]][finish[1]].set_value(Board.TARGET)
        self.layers = layers

    def get_xsize(self):
        return self.xsize

    def get_ysize(self):
        return self.ysize

    def next_pass(self, worms):
        self.pass_count += 1
        self.pass_store.append(worms)

    def take_step(self, current, layer):
        """
        Take a step from x, y using current marker
        """
        live = self.pass_store[-1]  # get edges
        next = []
        for x, y in live:
            if self.layers[layer][x][y] >= slimit:  # starting badly
                return live, None  # just wait around until next hour
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if abs(dx) == abs(dy):  # no diags
                        continue
                    nx = x + dx
                    ny = y + dy
                    if nx < 0 or \
                       nx >= self.xsize or \
                       ny < 0 or \
                       ny >= self.ysize:
                        continue
                    # ok, nx, ny on board
                    if self.cells[nx][ny].has_value(Board.TARGET) and \
                       self.layers[layer][nx][ny] < slimit:  # if the target is stormy, you need to wait
                        self.cells[nx][ny].set_parent(x, y)
                        self.cells[nx][ny].add_step(current)
                        return next, (nx, ny)
                    if self.cells[nx][ny].value_is_not(Board.BAD) and self.cells[nx][ny].value_is_not(Board.TARGET):
                        if self.cells[nx][ny].get_value() < 0:  # i.e. is untouched
                            logging.info("{},{} is empty location".format(nx, ny))
                            if self.layers[layer][nx][ny] < slimit:
                                logging.info("   and is under storm limit - marking")
                                self.cells[nx][ny].set_value(current)
                                self.cells[nx][ny].set_parent(x, y)
                                logging.info("Cell at {},{} has parent set to {}".format(nx, ny, self.cells[nx][ny].get_parent()))
                                self.cells[nx][ny].add_step(current)
                                next.append((nx, ny))
        return next, None

    def report_pathXXXX(self, cell):
        if cell.has_value(Board.START):
            print("Start cell = {}".format(cell))
            return cell
        else:
            parent = cell.get_parent()
            path = self.report_path(self.cells[parent[0], parent[1]])
            path.append(cell)

    def solver(self):
        step = 1
        found = None
        while found is None:
            layer = int(step / steps_per_layer)
            next_thing, found = self.take_step(step, layer)
            step += 1
            self.pass_store.append(next_thing)
        return found

    def show_path(self, txy):
        """
        Starting from found target, go back to start
        :return: 
        """
        target = self.cells[txy[0]][txy[1]]
        # OK - how did I get here?
        if target.get_parent() is not None:
            self.show_path(target.get_parent())
        #print(target)
        logging.info("Target {}, {} => {}".format(txy[0], txy[1], target))



def get_test_data():
    xsize = 10
    ysize = 10
    # test data set
    layers = []
    # layer 0
    layers.append([])
    layers[0].append([1, 1, 1, 1, 1, 5, 7, 9, 15, 14])
    layers[0].append([1, 2, 3, 4, 5, 6, 7, 10, 15, 10])
    layers[0].append([2, 2, 2, 2, 3, 3, 5, 9, 15, 15])
    layers[0].append([3, 3, 4, 4, 6, 6, 8, 10, 13, 16])
    layers[0].append([5, 5, 6, 6, 7, 7, 8, 8, 11, 14])
    layers[0].append([7, 7, 6, 6, 6, 6, 7, 7, 9, 12])
    layers[0].append([6, 6, 6, 6, 6, 6, 6, 6, 7, 9])
    layers[0].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[0].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[0].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 1)
    layers.append(([]))
    layers[1].append([1, 1, 1, 1, 1, 5, 7, 9, 13, 15])
    layers[1].append([1, 2, 3, 4, 5, 6, 7, 14, 14, 10])
    layers[1].append([2, 2, 2, 2, 3, 3, 5, 9, 15, 15])
    layers[1].append([3, 3, 4, 4, 6, 6, 8, 10, 15, 16])
    layers[1].append([5, 5, 6, 6, 7, 7, 8, 8, 11, 14])
    layers[1].append([7, 7, 6, 6, 6, 6, 7, 7, 9, 12])
    layers[1].append([6, 6, 6, 6, 6, 6, 6, 6, 7, 9])
    layers[1].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[1].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[1].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 2)
    layers.append(([]))
    layers[2].append([1, 1, 1, 1, 5, 7, 9, 10, 14, 15])
    layers[2].append([1, 3, 4, 5, 6, 7, 10, 12, 13, 8])
    layers[2].append([2, 2, 2, 3, 3, 5, 9, 12, 15, 12])
    layers[2].append([3, 4, 4, 6, 6, 8, 10, 13, 16, 14])
    layers[2].append([5, 6, 6, 7, 7, 8, 8, 11, 14, 12])
    layers[2].append([7, 6, 6, 6, 6, 7, 7, 9, 12, 10])
    layers[2].append([6, 6, 6, 6, 6, 6, 6, 7, 9, 8])
    layers[2].append([8, 8, 6, 6, 6, 6, 6, 6, 7, 7])
    layers[2].append([8, 8, 6, 6, 6, 6, 6, 6, 7, 7])
    layers[2].append([8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 3)
    layers.append(([]))
    layers[3].append([1, 1, 1, 5, 7, 9, 10, 12, 10, 8])
    layers[3].append([3, 4, 5, 6, 7, 10, 10, 11, 10, 7])
    layers[3].append([2, 2, 3, 3, 5, 9, 12, 14, 15, 12])
    layers[3].append([4, 4, 6, 6, 8, 10, 13, 15, 15, 15])
    layers[3].append([6, 6, 7, 7, 8, 8, 11, 14, 12, 10])
    layers[3].append([6, 6, 6, 6, 7, 7, 9, 12, 10, 8])
    layers[3].append([6, 6, 6, 6, 6, 6, 7, 9, 9, 9])
    layers[3].append([8, 6, 6, 6, 6, 6, 6, 7, 7, 7])
    layers[3].append([8, 6, 6, 6, 6, 6, 6, 7, 8, 9])
    layers[3].append([8, 6, 6, 6, 6, 6, 6, 7, 9, 10])
    # layer 4)
    layers.append(([]))
    layers[4].append([1, 1, 5, 7, 9, 10, 12, 10, 8, 6])
    layers[4].append([4, 5, 6, 7, 10, 10, 11, 10, 7, 7])
    layers[4].append([2, 3, 3, 5, 9, 12, 14, 15, 12, 12])
    layers[4].append([4, 6, 6, 8, 10, 13, 15, 15, 13, 15])
    layers[4].append([6, 7, 7, 8, 8, 11, 14, 12, 10, 10])
    layers[4].append([6, 6, 6, 7, 7, 9, 12, 10, 8, 10])
    layers[4].append([6, 6, 6, 6, 6, 7, 9, 9, 9, 10])
    layers[4].append([6, 6, 6, 6, 6, 6, 7, 7, 7, 9])
    layers[4].append([6, 6, 6, 6, 6, 6, 7, 8, 9, 10])
    layers[4].append([6, 6, 6, 6, 6, 6, 7, 9, 10, 14])
    nlayers = len(layers)
    for l in layers:
        assert len(l) == ysize
        for y in l:
            assert len(y) == xsize
    cities = [(9, 0), (1, 9)]
    return layers, cities, xsize, ysize


def get_big_random_data(args):
    xsize = args.xsize
    ysize = args.ysize
    mean = args.wind_average
    dev = args.wind_sd
    nlayers = args.nlayers
    layer_cells = [[[abs(int(random.gauss(mean, dev))) for x in range(xsize)] for y in range(ysize)] for l in range(nlayers)]
    c0x = abs(int(random.gauss(xsize / 4, xsize / 4)))
    if c0x >= xsize:
        c0x = xsize - 1
    c0y = abs(int(random.gauss(ysize / 4, ysize / 4)))
    if c0y >= ysize:
        c0y = ysize - 1
    c1x = abs(int(random.gauss(3 * xsize / 2, xsize / 4)))
    if c1x >= xsize:
        c1x = xsize - 1
    c1y = abs(int(random.gauss(3 * ysize / 4, ysize / 4)))
    if c1y >= ysize:
        c1y = ysize - 1
    cities = [(c0x, c0y), (c1x, c1y)]
    return layer_cells, cities, xsize, ysize


def show_layers(lys):
    logging.info("Layers :")
    for l in lys:
        for r in l:
            logging.info(r)
        logging.info("-------------------------------")
    logging.info("================================")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--xsize", default=10, type=int, help="xsize of generated test data")
    parser.add_argument("-y", "--ysize", default=10, type=int, help="ysize of generated test data")
    parser.add_argument("-H", "--nlayers", default=10, type=int, help="number of layers/hours")
    parser.add_argument("-a", "--wind_average", default=10, type=int, help="mean wind value.")
    parser.add_argument("-d", "--wind_sd", default=2, type=int, help="standard deviation of wind")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(message)s')
    if args.xsize < 0 or \
                    args.ysize < 0 or \
                    args.nlayers < 0:
        logging.critical("Malformed x, y or h values")
        sys.exit(22)
    # layers, cities, xsize, ysize = get_test_data()
    layers, cities, xsize, ysize = get_big_random_data(args)
    show_layers(layers)
    board = Board(xsize, ysize, cities,layers)
    # place cities
    res = board.solver()
    if res is not None:
        logging.warning("Found a solution = {}".format(res))
        board.show_path(res)
    else:
        logging.warning("No solution found")


if __name__ == '__main__':
    main()
