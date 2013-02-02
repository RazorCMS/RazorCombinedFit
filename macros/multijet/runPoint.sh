#!/usr/bin/env bash -x

export POINT=$1
export BOX=$2
export WD=/tmp/$USER/Razor2012_${POINT}_${BOX}

mkdir -p $WD
cd $WD

scramv1 project CMSSW CMSSW_5_3_7_patch4
cd CMSSW_5_3_7_patch4/src
eval `scramv1 run -sh`
cd /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/
source bin/thisroot.sh
cd $WD/CMSSW_5_3_7_patch4/src

export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit
cd RazorCombinedFit
mkdir lib
source setup.sh
make

export NAME="T1bbbb_${POINT}"
export LABEL="MR450.0_R0.5"

cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/HadFits.root $PWD
cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}*${LABEL}*.root $PWD


if [ "$BOX" == "TauTauJet" ]
then   
    python scripts/runAnalysis.py -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${LABEL}_TauTauJet.root -o Razor2012Limit_${NAME}_TauTauJet.root

elif [ "$BOX" == "MultiJet" ]
then   
    python scripts/runAnalysis.py -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_MultiJet.root

elif [ "$BOX" == "Jet" ]
then   
    python scripts/runAnalysis.py -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${LABEL}_Jet.root -o Razor2012Limit_${NAME}_Jet.root

if [ "$BOX" == "ALL" ]
then
    python scripts/runAnalysis.py -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${LABEL}_TauTauJet.root ${NAME}_${LABEL}_Jet.root ${NAME}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_All.root


cp Razor2012Limit_${NAME}_Had.root woodson@lxcms127.cern.ch:/data/woodson/Razor2012Limit/

#TODO: Copy the results somewhere
cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/Razor2012Limit*.root $HOME/work/RAZORLIMTS/Scan/
cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/Asym_CL*.root $HOME/work/RAZORLIMITS/Scan/
cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/cls.png $HOME/work/RAZORLIMITS/Scan/cls_${NAME}_${BOX}.png
#rm -rf $WD
