import re
import os
import glob

import time
import argparse

publicnnewspaperurndict={"key":"value"}

def readpublicnewspaperurnfile():
    yeardist=[0] * 2023

    if not os.path.exists("publicurnnewspaper.lst"):
        logerror("init","publicurnnewspaper.lst does not exist")
        exit()
    pagelines=""
    with open("publicurnnewspaper.lst","r") as fp:
        pagelines=fp.readlines()

    for p in pagelines:
        #print(p)
        if len(p.strip())> 4:
            key=p.strip()
            #print(key)
            publicnnewspaperurndict[key]= 1
            year=p.split("_")[4][:4]
            #print(str(year))
            if int(year) <= 2021:
                yeardist[int(year)]+=1
    i=1960
    while i<=2021:
        print ("for year "+ str(i) + " there is  "+ str(yeardist[int(i)]) + " public newspapers")
        i+=1

def ispublicnewspaper(urn):
    parts = urn.split("_")
    checkurn = "digavis_" + parts[0] + "_" + parts[1] + "_" + parts[2] + "_" + parts[3] + "_" + parts[4] + "_" + parts[5] + "_" + parts[6]
    if checkurn in publicnnewspaperurndict:
        return True
    else:
        return False

if __name__ == '__main__':
    #args = parse_args()
    readpublicnewspaperurnfile()
    urn="stjordalensblad_null_null_19211203_30_137_1"
    if ispublicnewspaper(urn) == True:
        print(str(urn) + " is public")
    else:
        print(str(urn) + " is not public")
    urn = "dagbladet_null_null_19211203_30_137_1"
    if ispublicnewspaper(urn) == True:
        print(str(urn) + " is public")
    else:
        print(str(urn) + " is not public")
