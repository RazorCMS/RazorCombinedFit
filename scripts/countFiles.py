#! /usr/bin/env python
import os
import sys
import ROOT as rt
from optparse import OptionParser
from sets import Set

pwd = os.environ['PWD']
#boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-q','--queue',dest="queue",type="string",default="1nh", help="Name of queue to use")
    parser.add_option('-b','--box',dest="box",type="string",default="Had", help="Box To Run ON")
    parser.add_option('-i','--index',dest="iJob",type="int",default="5", help="Integer index (to label outputs)")
    
    (options,args) = parser.parse_args()
    
    print 'Input files are %s' % ', '.join(args)
 
    count = 0 
    for signalpath in args:
        signalfilename = signalpath.split('/')[-1]
        signal = signalfilename.split('.root')[0]
        M0 = int(signal.split('_')[-2].split('-')[-1])
        M12 = int(signal.split('_')[-1].split('-')[-1])
# for tanB = 40
#        M0M12Dict = {360:[400,600],560:[400,600],580:[400,600],
#                     720:[360,560],840:[300,540],
#                     1000:[200,460],1220:[160,400],
#                     1500:[160,400],1760:[160,400],
#                     1900:[160,400]}
# for tanB = 10        
#        M0M12Dict = {120:[460,660],240:[460,660],
#                     380:[400,600],560:[400,600],
#                     720:[360,560],860:[300,540],
#                     1020:[200,460],1240:[160,400],
#                     1500:[160,400],1760:[160,400],
#                     1880:[160,400]}
# for tanB = 10 UPPER       
#        M0M12Dict = {140:[460,760],240:[680,760],
#                     380:[620,760],560:[620,760],
#                     720:[580,760],840:[320,760],
#                     1020:[480,660],1240:[420,660],
#                     1500:[420,660],1760:[420,660],
#                     1880:[420,660]}
# for tanB = 10 Tot, Exp, Had, Lep, w/ Log Normal SYS scan
        M0M12Dict = {120:[460,660],240:[460,660],
                     380:[400,660],560:[400,620],
                     720:[360,620],860:[300,580],
                     1020:[200,520],1240:[160,500],
                     1500:[160,460],1760:[160,460],
                     1880:[160,460]}
# for tanB = 10 Had-only JES Test
#        M0M12Dict = {120:[400,660],240:[400,660],
#                     380:[400,600],560:[400,600],
#                     720:[360,600],860:[300,540],
#                     1020:[200,460],1240:[160,460],
#                     1500:[160,460],1760:[160,460],
#                     1880:[160,460]}

        if M0 not in M0M12Dict.keys(): continue
        if M12 < int(M0M12Dict[M0][0]): continue
        if M12 > int(M0M12Dict[M0][1]): continue
#        os.system("cp %s %s/mSUGRA_tanB10_LN" %(signalpath, pwd))
        print "mSUGRA (m0,m12)=("+str(M0)+","+str(M12)+")"

        count = count+1
    print "Count is %i"%count

