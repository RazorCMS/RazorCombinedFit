import os, sys, pickle, re

directory = sys.argv[1]
norms = []
file = ''
#outfilename = re.sub('_[0-9]+.pkl','.pkl',file)
#print outfilename
outfilename = 'SMS-T2tt_mStop-500to650_mLSP-0to225_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.pkl'
outfile = open(outfilename, 'wb')
norms = {}
for file in os.listdir(directory) :

    if file.endswith('.pkl'):
        f = open(directory+file,'rb')
        massPoints = pickle.load(f)
        for massPoint in massPoints.iteritems() :
            if massPoint[0] in norms.keys() :
                norms[(massPoint[0][0],0.0)] += massPoint[1]
            else :
                norms[(massPoint[0][0],0.0)]  = massPoint[1]
    
pickle.dump(norms,outfile)
