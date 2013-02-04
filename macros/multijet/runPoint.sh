#!/usr/bin/env bash -x

export POINT=$1
export BOX=$2
export WD=/tmp/${USER}/Razor2012_${POINT}_${BOX}

mkdir -p $WD
cd $WD

scramv1 project CMSSW CMSSW_5_3_7_patch4
cd CMSSW_5_3_7_patch4/src
eval `scramv1 run -sh`
source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh

export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
cvs co -d RazorCombinedFit UserCode/wreece/RazorCombinedFit
cd RazorCombinedFit
source setup.sh
make

export NAME="T1bbbb"
export LABEL="MR450.0_R0.5"

cp /afs/cern.ch/user/w/woodson/public/Razor2013/Background/HadFits.root $PWD
cp /afs/cern.ch/user/w/woodson/public/Razor2013/Signal/${NAME}_${POINT}_${LABEL}*.root $PWD


if [ "$BOX" == "TauTauJet" ]
then   
    python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${LABEL}_TauTauJet.root -o Razor2012Limit_${NAME}_${POINT}_TauTauJet.root -t 1000

elif [ "$BOX" == "MultiJet" ]
then   
    python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_${POINT}_MultiJet.root -t 1000

elif [ "$BOX" == "Jet" ]
then   
    python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${LABEL}_Jet.root -o Razor2012Limit_${NAME}_${POINT}_Jet.root -t 1000
elif [ "$BOX" == "All" ]
then
    python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${LABEL}_Jet.root ${NAME}_${POINT}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_${POINT}_All.root -t 1000
else    
    python scripts/runAnalysis.py -a SingleBoxFit -c config_summer2012/RazorInclusive2012_3D_limit.config -i HadFits.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${LABEL}_Jet.root ${NAME}_${POINT}_${LABEL}_MultiJet.root -o Razor2012Limit_${NAME}_${POINT}_All.root -t 1000

fi

#TODO: Copy the results somewhere
cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/*.root $HOME/work/RAZORLIMITS/Scan/
cp $WD/CMSSW_5_3_7_patch4/src/RazorCombinedFit/cls.png $HOME/work/RAZORLIMITS/Scan/cls_${NAME}_${POINT}_${BOX}.png

rm -rf $WD