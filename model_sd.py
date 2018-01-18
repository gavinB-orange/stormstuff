#!/usr/bin/python

import math

header = "xid,yid,date_id,hour,model,wind,error\n"
errors_file = "ModelErrorFile.csv"

values = {}
variances = {}
values_per_bucket = {}
variances_per_bucket = {}
counts = {}
counts_per_bucket = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}, 8:{}, 9:{}, 10:{}}
bucket_titles=["0..5", "5+..10", "10+..15", "15+"]

with open(errors_file, "r") as f:
    line = f.readline()
    assert line == header
    line = f.readline()
    counter = 0
    variances_per_bucket[0] = {}
    variances_per_bucket[1] = {}
    variances_per_bucket[2] = {}
    variances_per_bucket[3] = {}
    values_per_bucket[0] = {}
    values_per_bucket[1] = {}
    values_per_bucket[2] = {}
    values_per_bucket[3] = {}
    for m in range(10):
        counts_per_bucket[0][m+1] = 0
        counts_per_bucket[1][m+1] = 0
        counts_per_bucket[2][m+1] = 0
        counts_per_bucket[3][m+1] = 0
    while line != '':
        if counter % 1000 == 0:
            print(counter)
        counter += 1
        xid, yid, date_id, hour, model, wind, err = line[:-1].split(',')
        w = float(wind)
        # bucketize
        bucket = 3
        if w <=5 :
            bucket = 0
        else:
            if w <= 10:
                bucket = 1
            else:
                if w <= 15:
                    bucket = 2
        #
        errval =  float(err)
        modelval = int(model)
        v2 = errval * errval
        try:
            variances[modelval] += v2
            values[modelval] += errval
            counts[modelval] += 1
            variances_per_bucket[bucket][modelval] += v2
            values_per_bucket[bucket][modelval] += errval
            counts_per_bucket[bucket][modelval] += 1
        except KeyError:
            variances[modelval] = v2
            values[modelval] = errval
            counts[modelval] = 1
            variances_per_bucket[bucket][modelval] = v2
            values_per_bucket[bucket][modelval] = errval
        line = f.readline()
print("Results")
for m in sorted(values.keys()):
    assert counts[m] != 0
    variance = variances[m] / counts[m]
    av_err = values[m] / counts[m]
    sd = math.sqrt(variance)
    print("Model {} has variance = {}, SD = {} and average error {}".format(m, variance, sd, av_err))
    for b in [0, 1, 2, 3]:
        vb = variances_per_bucket[b][m] / counts_per_bucket[b][m]
        sdb = math.sqrt(vb)
        valb = values_per_bucket[b][m] / counts_per_bucket[b][m]
        print("  bucket {} has variance = {}, SD = {} and average error {}".format(bucket_titles[b], vb, sdb, valb))
    
