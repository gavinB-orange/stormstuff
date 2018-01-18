#!/usr/bin/env python3
#
# run a "mask" solver - see if it works
# data set is a set of 2D layers. 
# each layer represents the winds per hour
# increasing layer = next hour
#
# TODO - need to record in the cells the start and end step
# so an accurate idea of the path can be got.

import argparse
import random
import logging
import sys

slimit = 15

def get_test_data():
    xsize = 10
    ysize = 10
    # test data set
    layers = []
    # layer 0
    layers.append([])
    layers[0].append([ 1, 1, 1, 1, 1, 5, 7, 9,15,14])
    layers[0].append([ 1, 2, 3, 4, 5, 6, 7,10,15,10])
    layers[0].append([ 2, 2, 2, 2, 3, 3, 5, 9,15,15])
    layers[0].append([ 3, 3, 4, 4, 6, 6, 8,10,13,16])
    layers[0].append([ 5, 5, 6, 6, 7, 7, 8, 8,11,14])
    layers[0].append([ 7, 7, 6, 6, 6, 6, 7, 7, 9,12])
    layers[0].append([ 6, 6, 6, 6, 6, 6, 6, 6, 7, 9])
    layers[0].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[0].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[0].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 1)
    layers.append(([]))
    layers[1].append([ 1, 1, 1, 1, 1, 5, 7, 9,13,15])
    layers[1].append([ 1, 2, 3, 4, 5, 6, 7,14,14,10])
    layers[1].append([ 2, 2, 2, 2, 3, 3, 5, 9,15,15])
    layers[1].append([ 3, 3, 4, 4, 6, 6, 8,10,15,16])
    layers[1].append([ 5, 5, 6, 6, 7, 7, 8, 8,11,14])
    layers[1].append([ 7, 7, 6, 6, 6, 6, 7, 7, 9,12])
    layers[1].append([ 6, 6, 6, 6, 6, 6, 6, 6, 7, 9])
    layers[1].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[1].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    layers[1].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 2)
    layers.append(([]))
    layers[2].append([ 1, 1, 1, 1, 5, 7, 9,10,14,15])
    layers[2].append([ 1, 3, 4, 5, 6, 7,10,12,13, 8])
    layers[2].append([ 2, 2, 2, 3, 3, 5, 9,12,15,12])
    layers[2].append([ 3, 4, 4, 6, 6, 8,10,13,16,14])
    layers[2].append([ 5, 6, 6, 7, 7, 8, 8,11,14,12])
    layers[2].append([ 7, 6, 6, 6, 6, 7, 7, 9,12,10])
    layers[2].append([ 6, 6, 6, 6, 6, 6, 6, 7, 9, 8])
    layers[2].append([ 8, 8, 6, 6, 6, 6, 6, 6, 7, 7])
    layers[2].append([ 8, 8, 6, 6, 6, 6, 6, 6, 7, 7])
    layers[2].append([ 8, 8, 8, 6, 6, 6, 6, 6, 6, 7])
    # layer 3)
    layers.append(([]))
    layers[3].append([ 1, 1, 1, 5, 7, 9,10,12,10, 8])
    layers[3].append([ 3, 4, 5, 6, 7,10,10,11,10, 7])
    layers[3].append([ 2, 2, 3, 3, 5, 9,12,14,15,12])
    layers[3].append([ 4, 4, 6, 6, 8,10,13,15,15,15])
    layers[3].append([ 6, 6, 7, 7, 8, 8,11,14,12,10])
    layers[3].append([ 6, 6, 6, 6, 7, 7, 9,12,10, 8])
    layers[3].append([ 6, 6, 6, 6, 6, 6, 7, 9, 9, 9])
    layers[3].append([ 8, 6, 6, 6, 6, 6, 6, 7, 7, 7])
    layers[3].append([ 8, 6, 6, 6, 6, 6, 6, 7, 8, 9])
    layers[3].append([ 8, 6, 6, 6, 6, 6, 6, 7, 9,10])
    # layer 4)
    layers.append(([]))
    layers[4].append([ 1, 1, 5, 7, 9,10,12,10, 8, 6])
    layers[4].append([ 4, 5, 6, 7,10,10,11,10, 7, 7])
    layers[4].append([ 2, 3, 3, 5, 9,12,14,15,12,12])
    layers[4].append([ 4, 6, 6, 8,10,13,15,15,13,15])
    layers[4].append([ 6, 7, 7, 8, 8,11,14,12,10,10])
    layers[4].append([ 6, 6, 6, 7, 7, 9,12,10, 8,10])
    layers[4].append([ 6, 6, 6, 6, 6, 7, 9, 9, 9,10])
    layers[4].append([ 6, 6, 6, 6, 6, 6, 7, 7, 7, 9])
    layers[4].append([ 6, 6, 6, 6, 6, 6, 7, 8, 9,10])
    layers[4].append([ 6, 6, 6, 6, 6, 6, 7, 9,10,14])
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
    cells = [[[abs(int(random.gauss(mean, dev))) for x in range(xsize)] for y in range(ysize)] for l in range(nlayers)]
    c0x = abs(int(random.gauss(xsize/4, xsize/4)))
    if c0x >= xsize:
        c0x = xsize - 1
    c0y = abs(int(random.gauss(ysize/4, ysize/4)))
    if c0y >= ysize:
        c0y = ysize - 1
    c1x = abs(int(random.gauss(3 * xsize/2, xsize/4)))
    if c1x >= xsize:
        c1x = xsize - 1
    c1y = abs(int(random.gauss(3 * ysize/4, ysize/4)))
    if c1y >= ysize:
        c1y = ysize - 1
    cities = [(c0x, c0y), (c1x, c1y)]
    return cells, cities, xsize, ysize

    

steps_per_layer = 4


class Board(object):
    """
    Hold the blackboard info
    """

    TARGET = '*'
    BAD = 'X'
    CLEAR = -1
    START = 0

    def __init__(self, xsize, ysize, cities, layers):
        self.xsize = xsize
        self.ysize = ysize
        self.cells = [[Board.CLEAR for x in range(xsize)] for y in range(ysize)]
        start = cities[0]
        finish = cities[1]
        logging.warning("Start is {}".format(start))
        logging.warning("Finish is {}".format(finish))
        self.cells[start[0]][start[1]] = Board.START
        self.cells[finish[0]][finish[1]] = Board.TARGET
        self.layers = layers

    def display(self):
        for r in self.cells:
            logging.info(r)

    def is_current(self, x, y, current):
        return self.cells[x][y] != Board.TARGET and\
               self.cells[x][y] != Board.BAD and\
               self.cells[x][y] >= Board.START and\
               self.cells[x][y] <= current

    def reset(self):
        logging.warning("Resetting board")
        for x in range(self.xsize):
            for y in range(self.ysize):
                if self.cells[x][y] != Board.TARGET and\
                   self.cells[x][y] != Board.BAD and\
                   self.cells[x][y] != Board.START:
                    self.cells[x][y] = Board.CLEAR

    def mark_bad(self, bad):
        """
        List of locations to avoid e.g. as you will get stuck later.
        """
        for x, y in bad:
            if self.cells[x][y] != Board.TARGET and\
               self.cells[x][y] != Board.START:
                self.cells[x][y] = Board.BAD

    def take_step(self, x, y, current, layer):
        """
        Take a step from x, y using current marker
        """
        if self.layers[layer][x][y] >= slimit:  # starting badly
            return None  # just wait around until next hour
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if abs(dx) == abs(dy) :  # no diags
                    continue
                nx = x + dx
                ny = y + dy
                if nx < 0 or\
                   nx >= self.xsize or\
                   ny < 0 or\
                   ny >= self.ysize:
                    continue
                # ok, nx, ny on board
                if self.cells[nx][ny] == Board.TARGET and\
                   self.layers[layer][nx][ny] < slimit:  # if the target is stormy, you need to wait
                    return (nx, ny)
                if self.cells[nx][ny] != Board.BAD and self.cells[nx][ny] != Board.TARGET :
                    if self.cells[nx][ny] < 0:  # i.e. is untouched
                        if self.layers[layer][nx][ny] < slimit:
                            self.cells[nx][ny] = current
        return None

    def report_path(self, x, y, s):
        """
        Starting from the reported target position, walk back to the start
        by following the breadcrumbs.
        """
        diff = 1
        while diff < steps_per_layer * len(self.layers):
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if abs(dx) == abs(dy) :  # no diags
                        continue
                    nx = x + dx
                    ny = y + dy
                    if nx < 0 or\
                       nx >= self.xsize or\
                       ny < 0 or\
                       ny >= self.ysize:
                        continue
                    # valid board position
                    if self.cells[nx][ny] == 0:  # found the start location
                        path = [(nx, ny)]
                        logging.info("Found start location at {},{}".format(nx,ny))
                        return path
                    else:
                        if self.cells[nx][ny] == s - diff:
                            logging.info("Recursing {},{} -> {}".format(nx, ny, s-diff))
                            path = self.report_path(nx, ny, s - diff)
                            for d in range(diff):
                                path.append((nx, ny))
                            return path
            diff += 1
            logging.info("increasing diff to {}".format(diff))
        raise Exception("No valid path found")

    def get_xsize(self):
        return self.xsize

    def get_ysize(self):
        return self.ysize
                        

def show_layers(lys):
    logging.info("Layers :")
    for l in lys:
        for r in l:
            logging.info(r)
        logging.info("-------------------------------")
    logging.info("================================")


def track_path(path, layers):
    count = 0
    logging.warning("Path :")
    for x, y in path:
        lr = int(count / steps_per_layer)
        count += 1
        logging.warning("{}: {},{} -> {}".format(lr, x, y, layers[lr][x][y]))


def verify_path(path, layers, maxstep):
    """
    If stalled in position for a while you can get "stranded" on a
    storm point. In that case, the path can have bad wind values.
    Find those, and return the list so those locations can be excluded.

    TODO: If we wait a while on a cell e.g. start before can begin then
          the layer info is wrong and a path can be wrongly considered to
          have bad values

    """
    count = 0
    bad = []
    for x, y in path:
        lr = int(count / steps_per_layer)
        count += 1
        if layers[lr][x][y] >= slimit:  # possible bad case
            logging.warning("Found something bad. {},{} => {}".format(x, y, layers[lr][x][y]))
            bad.append((x, y))
    return bad


def solver(board, layers):
    solved = False
    solver_iteration = 0
    while not solved:
        logging.warning("Starting solver iteration {}".format(solver_iteration))
        solver_iteration += 1
        board.reset()
        if solver_iteration >= board.xsize:  # give up
            return False
        solved = solve_it(board, layers)
    return True


def solve_it(board, layers):
    for hour_layer in range(len(layers)):
        logging.info("Hour {}".format(hour_layer))
        for s in range(steps_per_layer):
            step = hour_layer * steps_per_layer + s
            logging.info("Step : {}".format(step))
            # find current in board
            # for now just search - TODO optimize this
            for x in range(board.xsize):
                for y in range(board.ysize): 
                    if board.is_current(x, y, step):
                        xy = board.take_step(x, y,
                                             step + 1,
                                             hour_layer)
                        if xy is not None:
                            logging.warning("FOUND TARGET at {}, {} step {}".format(xy[0], xy[1], step + 1))
                            path = board.report_path(xy[0], xy[1], step + 1)
                            path.append((xy[0], xy[1]))
                            bad_pos = verify_path(path, layers, step + 1)
                            if len(bad_pos) == 0:
                                track_path(path, layers)
                                return True
                            else:
                                board.mark_bad(bad_pos)
                                return False
            board.display()

          
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
                        format='%(levelname)s:%(message)s')
    if args.xsize < 0 or\
       args.ysize < 0 or\
       args.nlayers < 0:
        logging.critical("Malformed x, y or h values")
        sys.exit(22)
    #layers, cities, xsize, ysize = get_test_data()
    layers, cities, xsize, ysize = get_big_random_data(args)
    show_layers(layers)
    # place cities
    board = Board(xsize, ysize, cities, layers)
    board.display()
    if solver(board, layers):
        logging.warning("Found a solution")
    else:
        logging.warning("No solution found")
                    

if __name__ == '__main__':
    main()

