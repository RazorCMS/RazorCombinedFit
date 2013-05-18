import os, sys, pickle, re

directory = sys.argv[1]
norms = []
file = ''
#outfilename = re.sub('_[0-9]+.pkl','.pkl',file)
#print outfilename
outfilename = 'SMS-T2tt_mStop-Combo_mLSP_0.0_8TeV-Pythia6Z-Summer12-START52_V9_FSIM-v1-SUSY.pkl'
outfile = open(outfilename, 'wb')
norms = {}
all = 0
for file in sorted(os.listdir(directory)) :
    print file
    if file.endswith('.pkl'):
        f = open(directory+file,'rb')
        massPoints = pickle.load(f)
        for massPoint in massPoints.iteritems() :
            if massPoint[0] in norms.keys() :
                norms[(massPoint[0][0],0.0)] += massPoint[1]
            else :
                norms[(massPoint[0][0],0.0)]  = massPoint[1]
            all+=massPoint[1]
print norms
print all
pickle.dump(norms,outfile)
