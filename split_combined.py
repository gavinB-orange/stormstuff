#!/usr/bin/env python3
#

# take a combined data set and split into per-day files


import argparse
import logging

EXPECTEDHDR = "xid,yid,date_id,hour,wind\n"


def do_split(args):
    output_files = {}
    with open(args.input, "r") as inp:
        # do header things
        inline = inp.readline()
        assert inline == EXPECTEDHDR, "Input file does not have expected header"
        inline = inp.readline()
        # OK - now do the splits. Ouch.
        try:
            while inline != '':
                xid, yid, date_id, hour, wind = inline[:-1].split(',')
                try:
                    out = output_files[date_id]
                except KeyError:
                    out = open("{}_{}.csv".format(args.output, date_id), "w")
                    output_files[date_id] = out
                    out.write(EXPECTEDHDR)
                out.write(inline)
                inline = inp.readline()
        except IOError as e:
            logging.critical("IO Error : {}".format(e))
        finally:
            for k in output_files.keys():
                output_files[k].close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="combined.csv", help="Input file to split")
    parser.add_argument("-o", "--output", default="combined_per_day", help="Root name of output file.")
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(message)s')
    do_split(args)



if __name__ == '__main__':
    main()