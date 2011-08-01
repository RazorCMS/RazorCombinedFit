from optparse import OptionParser
from runAnalysis import defineParser

import os
import sys
import subprocess

def runLocal(scriptFile, output, options):
    print 'Running the script locally...'
    stdout, stderr = subprocess.Popen(["sh", scriptFile], stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    out = file(output,'w')
    out.write('STDOUT::\n')
    out.write(stdout)
    out.write('\nSTDERR::\n')
    out.write(stderr)
    out.close()
    
def runLSF(scriptFile, output, options):
    print 'Running the script on LSF'
    cmd = 'bsub -q %s -o %s %s' % (options.queue_name,output,scriptFile)
    os.system(cmd)

if __name__ == '__main__':

    parser = defineParser()
    parser.add_option('--job-dir',dest="job_dir",default="JobDir",
                      help="The directory to put the output in")
    parser.add_option('--command',dest="command",default="",
                      help="The command to run")
    parser.add_option('--queue_name',dest="queue_name",default="1nh",
                      help="Name of LSF queue to run on")
    parser.add_option('--local',dest="local",action="store_true", default=False,
                  help="Run the script locally rather than on the batch")
    parser.add_option('--number-of-toys',dest="number_of_toys",type="int", default=1,
                  help="The number of toys to run")        
    (options,args) = parser.parse_args()

    pwd = os.getcwd()
    cmd = options.command
    
    topdir = os.environ['RAZORFIT_BASE']
    setup = os.path.join(os.environ['RAZORFIT_BASE'],'setup.sh')
    
    batch_script = """
#!/usr/bin/env bash

export RAZORFIT_BASE="%s"
export WORKDIR="%s"
pushd $RAZORFIT_BASE

#dump the environment to start with
printf "Environment:\\n\\n"
env
ulimit -v 3000000

#do a cmsenv
eval `scramv1 runtime -sh`

#now setup the Razor fit
source $RAZORFIT_BASE/setup.sh

printf "Checking for pyROOT:\\n\\n"
which python
python -c "import ROOT"

cd $WORKDIR
echo "Running the command:"
echo %s
echo
`%s`

tar cfvz output.tar.gz *.root *.log *.txt
rm -f *.root *.log *.txt

popd
    """

    if not os.path.exists(options.job_dir):
        os.mkdir(options.job_dir)
        
    for i in xrange(options.number_of_toys):
        jobDir = os.path.join(options.job_dir,'Job_%i' % i)
        if not os.path.exists(jobDir):
            os.mkdir(jobDir)
        scriptFile = os.path.join(jobDir,'run.sh')
        
        #set the random seen per toy
        cmd = '%s --seed=%i' % (cmd,i*997)
        
        script = batch_script % (topdir, jobDir, cmd, cmd)
        sc = file(scriptFile,'w')
        sc.write(script)
        sc.close()
        
        std_out = os.path.join(jobDir,'STDOUT')
        
        if options.local:
            runLocal(scriptFile, std_out, options)
        else:
            runLSF(scriptFile, std_out, options)
        