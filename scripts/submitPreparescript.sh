#$ -S /bin/sh
#$ -l arch=lx24-amd64
#PBS -m ea
#PBS -M es575@cornell.edu
#PBS -j oe

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc5_amd64_gcc462
cd /home/uscms208/cms/CMSSW_6_1_2/src/RazorCombinedFit_lucieg_May29
eval `scramv1 runtime -sh`
source setup.sh ../

python scripts/runPreparescript.py

exit