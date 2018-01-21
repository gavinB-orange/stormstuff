#!/usr/bin/env python3
#
# This program does the following
#    * Take the standard deviations per model and per model/per value bucket, and the
#      per model data.
#    * Using the variance, estimate a wind value per location by the following formula :
#          new cell value at location = sum_over_all_models(vn*rn)/sum(vn)
#      where vn is variance of model n and rn is wind value for model n at that location
#      that gives a new predicted value for each location based on models and their perceived accuracy.
#    * Use this new set of data to do a second similar pass, but this time, rather than use the global model variance,
#      use the variance per bucket, where buckets are defined wind values between
#      0...5-, 5..10-, 10..15-, 15..20-,20..25-, 25+
#      for the value calculated above.
#    * This gives a new updated value per cell.
#    * Calculate the standard deviation of this new data set versus the in-situ real data.
#    * Using these new data sets, bucketize the predicted wind value down to one decimal place, and show which of the
#      buckets correspond to a case where the real value was >= 15. Express as a % of the total number of items in that
#      bucket. And show the total number.
#    * Once these values are accepted by the customer, create a new predicted dataset replacing the windvalues with
#      confidence ratings
#      (confidence rating = 1 - % defined above) - [this confidence rating will be the input to the path finding model]
#

import argparse
import logging

Nmodels = 10  # but they start at 1


class CacherOne(object):
    """
    We need to build up the model data over multiple lines.
    This takes the xid, yid, date_id, hour and creates a key
    used for caching. The key links to an array of values for
    each model.
    If the key does not match the current active key, write out
    the processed value for that (xid, yid, date_id, hour) and
    start a new
    """

    def __init__(self, sds, args):
        self.sds = sds
        self.variances = [x * x for x in self.sds]
        self.vsum = sum(self.variances)
        self.args = args
        self.model_data = [0 for x in range(Nmodels)]  # zero'd array
        self.key = None
        self.added = 0

    def calc(self):
        """
        At this point we should have all 10 model values available - we need to combine
        that data using the magic formula
        :return:
        """
        value = 0
        for i in range(len(self.model_data)):
            value += self.model_data[i] * self.variances[i]
        value /= self.vsum
        return value

    def add_line(self, line):
        if line is None:  # special case - write what we have
            assert self.key is not None
            return "{0},{1},{2},{3},{4}\n".format(self.key[0],
                                                  self.key[1],
                                                  self.key[2],
                                                  self.key[3],
                                                  self.calc())
        xid_r, yid_r, date_id_r, hour_r, model_r, wind_r = line[:-1].split(',')
        xid, yid, date_id, hour, model, wind = int(xid_r), int(yid_r), int(date_id_r), int(hour_r), int(model_r), float(
            wind_r)
        model -= 1  # models are 1 .. 10
        newkey = (xid, yid, date_id, hour)
        if self.key is None:  # first time
            self.added = 1
            self.key = newkey
            self.model_data = [0 for x in range(Nmodels)]
            self.model_data[model] = wind
            return None
        if newkey != self.key:  # only one key at a time
            assert self.added == Nmodels
            self.added = 1
            result = "{0},{1},{2},{3},{4}\n".format(self.key[0],
                                                    self.key[1],
                                                    self.key[2],
                                                    self.key[3],
                                                    self.calc())
            self.key = newkey
            self.model_data = [0 for x in range(Nmodels)]
            self.model_data[model] = wind
            return result
        # OK - we just record this model's data and return None
        self.added += 1
        self.model_data[model] = wind
        return None


class WeighingMachine(object):
    """
    Class that wraps up the various methods required. Grouped as a class as a lot of
    overlap expected.

    Buckets are:
    b0 : 0..5-
    b1 : 5..10-
    b2 : 10..15-
    b3 : 15..20-
    b4 : 20..25-
    b5 : 25+
    """

    NEWHEADER = "xid,yid,date_id,hour,wind\n"

    def __init__(self, args):
        """
        Initialize things and store the run-time params passed as args
        :param args: parsed argparse info
        """
        self.args = args


    def get_first_wind_estimate(self):
        """
        Expect sdfile data to be
        model,sd
        Expect sdbucketfile data to be
        model,b0-sd,b1-sd,b2-sd,b3-sd,b4-sd,b5-sd
        :return:
        """
        # suck in the model sd info
        model_data = {}
        with open(self.args.sdfile, "r") as f:
            line = f.readline()
            assert line=="model,sd\n", "Malformed sd file"
            line = f.readline()
            while line != '':
                model, data = line[:-1].split(',')
                model_data[model] = data
#        # model_bucket_data
#        model_bucket_data = {}
#        for i in range(1, 1 + Nmodels):
#            model_bucket_data[i] = []
#        with open(self.args.sdbucketfile, "r") as f:
#            line = f.readline()
#            assert line=="model,b0,b1,b2,b3,b4,b5\n"
#            line = f.readline()
#            while line != '':
#                model, b0, b1, b2, b3, b4, b5 = line[:-1].split(',')
#                model_data[model] = [b0, b1, b2, b3, b4, b5]
        # OK - now we have the values
        cacher = CacherOne(model_data, self.args)
        counter = 0
        with open(self.args.combined, "w") as out:
            with open(self.args.model_file, "r") as inp:
                line = inp.readline()
                assert line == "xid,yid,date_id,hour,model,wind", "line is : " + line
                out.write(WeighingMachine.NEWHEADER)
                line = inp.readline()
                while line != '':
                    if counter % 1000 == 0: print(counter)
                    counter += 1
                    result = cacher.add_line(line)
                    if result is not None:
                        out.write(result)
                    line = inp.readline()
                out.write(cacher.add_line(None))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", default='WARNING', help="Logging level to use.")
    parser.add_argument("-s", "--sdfile", default='sd_file.csv',
                        help="File name for file containing the sd info per model.")
    parser.add_argument("-b", "--sdbucketfile", default='sd_bucket_file.csv',
                        help="File name for file containing the sd info per bucket per model.")
    parser.add_argument("-m", "--model_file", default='ForecastDataforTraining_201712.csv',
                         help="File name for file containing the sd info per model.")
    parser.add_argument("-i", "--insitu_data", default='In_situMeasurementforTraining_201712.csv',
                        help="File name for file containing the insitu data.")
    parser.add_argument("-c", "--combined", default='combined.csv',
                        help="File name for file containing the new predicted data based on combining model info")

    args = parser.parse_args()
    nl = getattr(logging, args.log.upper(), None)
    if not isinstance(nl, int):
        raise ValueError("Invalid log level: {}".format(args.log))
    logging.basicConfig(level=nl,
                        format='%(message)s')
    wm = WeighingMachine(args)
    wm.get_first_wind_estimate()


if __name__ == '__main__':
    main()
