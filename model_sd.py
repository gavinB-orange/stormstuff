#!/usr/bin/python

import math

header = "xid,yid,date_id,hour,model,wind,error\n"
errors_file = "ModelErrorFile.csv"
sd_file = "sd_file.csv"
sd_bucket_file = "sd_bucket_file.csv"

Nmodels = 10
message_count = 10000  # every message_count iterations, output a message
values = {}
variances = {}
values_per_bucket = {}
variances_per_bucket = {}
counts = {}
counts_per_bucket = {0:{}, 1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}, 7:{}, 8:{}, 9:{}, 10:{}}
bucket_titles=["0..5-", "5..10-", "10..15-", "15..20-", "20..25-", "25+"]


with open(errors_file, "r") as f:
    line = f.readline()
    assert line == header
    line = f.readline()
    counter = 0
    for b in range(len(bucket_titles)):
        variances_per_bucket[b] = {}
        values_per_bucket[b] = {}
        for m in range(Nmodels):
            counts_per_bucket[b][m+1] = 0
    while line != '':
        if counter % message_count == 0:
            print(counter)
        counter += 1
        xid, yid, date_id, hour, model, wind, err = line[:-1].split(',')
        w = float(wind)
        # bucketize
        bucket = int(w / 5)
        if bucket > 5:
            bucket = 5
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
with open(sd_file, "w") as sdf:
    sdf.write("model,sd\n")
    with open(sd_bucket_file, "w") as bf:
        bf.write("model,b0,b1,b2,b3,b4,b5\n")
        for m in sorted(values.keys()):
            assert counts[m] != 0
            variance = variances[m] / counts[m]
            av_err = values[m] / counts[m]
            sd = math.sqrt(variance)
            print("Model {} has variance = {}, SD = {} and average error {}".format(m, variance, sd, av_err))
            sdf.write("{},{}\n".format(m, sd))
            bvals = []
            for b in range(len(bucket_titles)):
                vb = variances_per_bucket[b][m] / counts_per_bucket[b][m]
                sdb = math.sqrt(vb)
                valb = values_per_bucket[b][m] / counts_per_bucket[b][m]
                print("  bucket {} has variance = {}, SD = {} and average error {}".format(bucket_titles[b], vb, sdb, valb))
                bvals.append(sdb)
            bf.write("{},{},{},{},{},{},{}\n".format(m, bvals[0], bvals[1], bvals[2], bvals[3], bvals[4], bvals[5]))
print("Done")

    
