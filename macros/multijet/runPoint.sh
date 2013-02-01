#!/usr/bin/env bash -x

export POINT=$1
export WD=/tmp/$USER/Razor2013_${POINT}_Had

mkdir -p $WD
cd $WD
scramv1 project CMSSW CMSSW_6_0_1
cd CMSSW_6_0_1/src
eval `scramv1 run -sh`
# it's not this ROOT:
#source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh

export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit
cd RazorCombinedFit
source setup.sh
mkdir lib
make

export NAME="T1bbbb_${POINT}"
export LABEL="MR450.0_R0.5"

cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/HadFits.root $PWD
cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}*${LABEL}*.root $PWD

python scripts/runAnalysis.py -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${LABEL}_TauTauJet.root ${NAME}_${LABEL}_Jet.root ${NAME}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_Had.root

scp Razor2012Limit_${NAME}_Had.root woodson@lxcms127.cern.ch:/data/woodson/Razor2013Limit/
#TODO: Copy the results somewhere

#rm -rf $WD
