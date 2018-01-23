#!/usr/bin/python3
#
# forecase has : xid,yid,date_id,hour,model,wind
# insitu has : xid,yid,date_id,hour,wind

mfile = "ForecastDataforTraining_201712.csv"
rfile = "In_situMeasurementforTraining_201712.csv"
ofile = "ModelErrorFile.csv"

message_count = 10000  # every message_count iterations, output a message

with open(ofile, "w") as o:
    with open(rfile, "r") as r:
        with open(mfile, "r") as m:
            rline = r.readline()
            assert rline == "xid,yid,date_id,hour,wind\n"
            mline = m.readline()
            assert mline == "xid,yid,date_id,hour,model,wind\n"
            oline = "xid,yid,date_id,hour,model,wind,error\n"
            o.write(oline)
            # we rely on the in-situ and model files to be aligned
            # the asserts below enforce this
            rline = r.readline()
            counter = 0
            while rline != '':
                if counter % message_count == 0:
                    print(counter)
                counter += 1
                xid, yid, date_id, hour, wind = rline[:-1].split(',')
                for mthing in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                    mline = m.readline()
                    mxid, myid, mdate_id, mhour, model, mwind = mline[:-1].split(',')
                    assert mxid == xid and myid == yid, "Locations do not match"
                    assert mdate_id == date_id, "Dates do not match"
                    assert mhour == hour, "Hour does not match"
                    err = float(wind) - float(mwind)
                    oline = "{},{},{},{},{},{},{}\n".format(xid, yid, date_id, hour, model, wind, err)
                    o.write(oline)
                rline = r.readline()
    
            
 
        
    

