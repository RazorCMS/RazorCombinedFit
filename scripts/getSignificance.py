import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os
from array import *
from getCLs import *

if __name__ == '__main__':

    boxInput = sys.argv[1]
    model = sys.argv[2]
    directory = sys.argv[3]

    
    gchipairs = getGChiPairs(model)
    #gchipairs = reversed(gchipairs)

    boxes = boxInput.split("_")

    for mg, mchi in gchipairs:
        xsec = getXsecRange(model,mchi,mg)[0]
        xsecString = str(xsec).replace(".","p")

        print "INFO: now checking for files missing "
        print "      for mg = %i, mchi = %i, xsec = %f"%(mg, mchi, xsec)
        print "      for boxes %s" % ("+".join(boxes))
        anyfilesNotFound = []
        BAllBoxList = glob.glob(getFileName("B",mg,mchi,xsec,"*",model,directory)+"*")
        print "INFO: %i files found for B" % (len(BAllBoxList))
        boxDictB = {}
        for box in boxes:
            boxDictB[box] = sorted([fileName for fileName in BAllBoxList if fileName.find("_%s_"%box)!=-1],key=sortkey)
            anyfilesNotFound.append(not boxDictB[box])
        if any(anyfilesNotFound):
            print "ERROR: at least one box missing all files! moving on to next point!"
            continue

        Xmin = 0
        LzCut = ""
        for box in boxes:
            LzCut+="H0covQual_%s>=2&&H1covQual_%s>=3&&LzSR_%s>=0.&&"%(box,box,box)
            LzCut = LzCut[:-2]
    

        LH1DataBox = []
        for box in boxes:
            fileName = boxDictB[box][0]
            print fileName
            
            dataTree = rt.TChain("myDataTree")
            addToChain = fileName+"/"+box+"/myDataTree"
            dataTree.Add(addToChain)

            dataTree.Draw('>>elist','','entrylist')
            elist = rt.gDirectory.Get('elist')
            entry = elist.Next()
            dataTree.GetEntry(entry)
            LH1DataBox.append(eval('dataTree.LH1xSR_%s'%box))
        LH1Data = sum(LH1DataBox)

        LH0Data = -3.48716859880006814e+04
        print "-log(L(0))         = %f"%LH0Data
        print "-log(L(^s))         = %f"%LH1Data
        disc = -2.*(LH0Data - LH1Data)
        print "-2(log(L(0)) - log(L(^s))) = %f"%(disc)

