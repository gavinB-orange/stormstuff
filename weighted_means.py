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

import argparse

class WeighingMachine(object):
    """
    Class that wraps up the various methods required. Grouped as a class as a lot of
    overlap expected.
    """

    def __init__(self, args):
        """
        Initialize things and store the run-time params passed as args
        :param args: parsed argparse info
        """
        self.args = args


    def get_first_wind_estimate(self):
        """
        Start with a csv file holding the SD per model
        e.g.
        model,sd

        :return:
        """
        #1,1.2345
        #2,2.3456




def main():
    pass


if __name__ == '__main__':
    main()
