#! /usr/bin/env python
from optparse import OptionParser

import ROOT as rt
import os, re

if __name__ == '__main__':
    
    resultDir = "/afs/cern.ch/work/l/lucieg/private/toys10k_gt4jets_SingleMu_3D_/FULL_Mu/"

    histo = rt.TH1F("histo","over 10k toys, number of bins above 2 sigmas", 100, 0., 100.)

   
  #  res = os.listdir("%s/absSigma/"%resultDir)
    res = os.listdir("%s/largeBinning/"%resultDir)
    count = 0
    for toy in res :
        count+=1
        #if count > 4000: break
        file = open(resultDir+'largeBinning/'+toy+"/count.txt","r")
        s = file.read()
        s = s.split(' ')
        if  float(s[0]) > 2.0 :
            print toy, float(s[0])
       
        histo.Fill(float(s[0]))

    histo.SetTitle("over 10k toys, number of bins above 2 sigmas;number of bins above 2 sigmas;# toys")
    histo.Draw()
    print 'proba to have 3 bins above 2 sigmas', histo.Integral(3,3)/histo.Integral()
    print 'proba to have less than 3 bins above 2 sigmas', histo.Integral(0,2)/histo.Integral()
    print 'proba to have more than 3 bins above 2 sigmas', histo.Integral(4,100)/histo.Integral()
    print 'proba to have at least 3 bins above 2 sigmas', histo.Integral(3,100)/histo.Integral()
   # print  histo.GetEntries()
