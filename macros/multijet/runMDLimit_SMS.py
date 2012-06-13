#! /usr/bin/env python
import os
import sys
from optparse import OptionParser
import time, random

pwd = os.environ['PWD']
#boxes = ['Had','Mu','Ele','MuMu','EleEle','MuEle']
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option('-q','--queue',dest="queue",type="string",default="1nh", help="Name of queue to use")
    parser.add_option('-t','--toys',dest="toys",type="int",default="40", help="Number of toys per job")
    parser.add_option('--tree_name',dest="tree_name",type="string",default='EVENTS', help="The name of the TTree to look at")    
    parser.add_option('-i','--index',dest="iJob",type="int",default="5", help="Integer index (to label outputs)")
    parser.add_option('-n','--number',dest="numJobs",type="int",default="100", help="number of jobs")
    parser.add_option('-b','--bjet',dest="doBjet", default=False, action='store_true', help="Run the RazorB analysis")
    parser.add_option('-m','--multijet',dest="doMultijet", default=False, action='store_true', help="Run the Razor Multijet analysis")    
    parser.add_option("--input",dest="input",default="razor_output.root", help="input file containing the bkg fits") 
    parser.add_option('--xsec',dest="xsec",type="float",default="-99", help="Signal cross section (in pb) for SMSs limit setting")
    parser.add_option('-c','--config',dest="config",type="string",default="config_winter2012/SingleBoxFit_Prompt_fR1fR2fR3fR4_2012_TightRsq.cfg", help="Name of the config file to use")
    parser.add_option('-f','--file',dest='inputFile',type='string',default='RAZORFITS/razor_output_all_Winter2012.root', help='Input file with the fit results for the bkg model')
    
    # the config files are committed in the CVS repository
    # INCLUSIVE: config_winter2012/SingleBoxFit_Prompt_fR1fR2fR3fR4_2012_TightRsq.cfg
    # BJET:      config_winter2012/RazorB_fR1fR2fR3fR4_winter2012_TightRsq.cfg
    # TAU:       
    # MULTIJET:  
    # DIPHOTON:  

    # the input file has to be provided. The default are
    # INCLUSIVE: /afs/cern.ch/user/m/mpierini/public/RAZORFITS/razor_output_all_Winter2012.root
    # BJET:      /afs/cern.ch/user/m/mpierini/public/RAZORFITS/razor_output_BJET_all_Winter2012.root
    # TAU:       
    # MULTIJET:  
    # DIPHOTON:  
    # make a local copy, not to get AFS paralized
    
    (options,args) = parser.parse_args()
    
    print '#Input files are %s' % ', '.join(args)

    toys = options.toys
    xsec = options.xsec
    input = options.input
    script = "Chris2BinnedDataset_ALLBOXES_BYPROCESS.py"
    treeName = options.tree_name

    for signalpath in args:

        mStop = int(treeName.split('_')[-2])
        mLSP = int(treeName.split('_')[-1])
        signal = 'SMS-T2tt_Mstop-225to1200_mLSP-50to1025_7TeV-Pythia6Z-Summer11-PU_START42_V11_FastSim-v1-wreece_030412-ByPoint-2'
        print "#Creating jobs for %s\n" % ('SMS-T2tt-%i-%i' % (mStop,mLSP))

        jobdir = 'Job_%i_%s' % (mStop,mLSP)
        if not os.path.exists(jobdir):
            os.mkdir(jobdir)
        print 'pushd %s' % jobdir      
        time.sleep(1)#just to make extra sure the seed is unique        
        for i in range(options.iJob,options.iJob+options.numJobs):

            outputFileName = "%s_%s_xsec_%f" %(signal, options.tree_name, xsec)
            outputname = os.path.join(jobdir,"%s_%i.src" %(outputFileName,i))
            outputfile = file(outputname,'w')
            outputfile.write('#!/bin/bash\n')
            mydir = "/tmp/wreece/%s_%s_xsec_%f_%i" %(signal,options.tree_name,xsec,i)
            outputfile.write("mkdir %s\n" %mydir)
            outputfile.write("cd %s\n" %mydir)
            outputfile.write("scramv1 project CMSSW CMSSW_4_2_8\n")
            outputfile.write("cd CMSSW_4_2_8/src\n")
            outputfile.write("eval `scramv1 run -sh`\n")  
            outputfile.write("source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.33.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh\n")          
            
            #outputfile.write("cmsStage /store/cmst3/user/wreece/Razor2011/MultiJetAnalysis/everything.tgz .\n")
            outputfile.write("cp /afs/cern.ch/user/w/wreece/work/LimitSetting/RazorMultiJet2011/everything.tgz .\n")
                        
            outputfile.write("tar zxvf everything.tgz >& /dev/null\n")
            outputfile.write("cd RazorCombinedFit\n")
            outputfile.write("source setup.sh\n")
            outputfile.write("make >& /dev/null\n")

            # run options
            runOptions = ""
            makePDFOptions = ""
            if options.doBjet:
                runOptions = runOptions+" --bjet"
                makePDFOptions = makePDFOptions +" --b 1"
            elif options.doMultijet:
                runOptions = runOptions+" --multijet"

            # convert original signal file to box-by-box datasets
            pid = os.getpid()
            now = int(time.mktime(time.gmtime()))#seconds since the start of the UNIX epoch
            seed = now+pid+137*i
            random.seed(seed)

            def writeJob(stream, xs, seedlocal, index):
                fn = "%s_%s_xsec_%f" %(signal, options.tree_name, xs)
                stream.write("\n########## Start %f - %d\n" % (xs,index))
                # perform limit toys(signal + bkgd) setting fits
                stream.write("python scripts/runAnalysis.py --nosave-workspace -a SingleBoxFit --xsec %f -s %i -c %s -o %s/LimitBkgSigToys_%s_%s_%i.root -i %s %s/CMSSW_4_2_8/src/RazorCombinedFit/%s_MR*.root -b --limit -t %i %s >& /dev/null \n" %(xs,seedlocal,options.config,mydir,fn,options.tree_name,index,input,mydir,signal,toys,runOptions))
                #update the seed
                seedlocal += 1000
                # perform limit toys(bkgd only) setting fits
                stream.write("python scripts/runAnalysis.py --nosave-workspace -a SingleBoxFit --xsec %f -s %i -c %s -o %s/LimitBkgToys_%s_%s_%i.root -i %s %s/CMSSW_4_2_8/src/RazorCombinedFit/%s_MR*.root -b --limit -e -t %i %s >& /dev/null \n" %(xs,seedlocal,options.config,mydir,fn,options.tree_name,index,input,mydir,signal,toys,runOptions))
                #sleep for some time to spread the scp load
                stream.write("sleep %d\n" % random.randint(0,180))
                # copy output files
                strxc = str(xc).replace('.','_')
                stream.write("scp -o StrictHostKeyChecking=no -o ConnectionAttempts=10 %s/LimitBkgSigToys_%s_%s_%i.root %s/LimitBkgToys_%s_%s_%i.root wreece@cmsphys09.cern.ch:/nfsdisk/wreece/LimitSetting/T2tt/%s/\n" %(mydir,fn,options.tree_name,index,mydir,fn,options.tree_name,index,strxc))
                stream.write("########## End %f - %d\n\n" % (xs,index))

            #run ten jobs in 1 to maximise CPU use
            xsecs = [10,5,1,0.5,0.1,0.05,0.01,0.001]
            for j in xrange(8):
                # run SMS - the seed is set internally
                outputfile.write("python scripts/%s %s --tree_name %s -c %s --sms -t %i %s %s >& /dev/null\n" %(script, runOptions, options.tree_name, options.config, toys, signalpath,makePDFOptions))
                random.shuffle(xsecs)

                for xc in xsecs:
                    writeJob(outputfile,xc,random.randint(0,1000000000000),(i*10 + j) )
            
            
            outputfile.write("cd /tmp; rm -rf %s\n" %(mydir))
            outputfile.close
            # submit to batch
            name = '%s_%f' % (options.tree_name,xsec)
            cmd = "bsub -q "+options.queue+" -J "+name+" source  "+pwd+"/"+outputname
            print cmd
            print "sleep 0.1"
            continue

        print 'popd'
