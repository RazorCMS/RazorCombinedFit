#!/usr/bin/env bash -x

export POINT=$1
export BOX=$2
export WD=/tmp/$USER/RazorStop2012_${POINT}_${BOX}

mkdir -p $WD
cd $WD
scramv1 project CMSSW CMSSW_5_3_7_patch4
cd CMSSW_5_3_7_patch4/src
eval `scramv1 run -sh`
source /afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin/thisroot.sh

export CVSROOT=:gserver:cmssw.cvs.cern.ch:/local/reps/CMSSW
cvs co -r wreece_101212_2011_style_fits -d RazorCombinedFit UserCode/wreece/RazorCombinedFit
cd RazorCombinedFit
mkdir lib
source setup.sh
make

export NAME="SMS_T2tt_jan30_MR500.0_R0.22360679775"

cp /afs/cern.ch/user/w/wreece/public/Razor2012/500_0_05/FullRegion/Run2012ABCD_Full_Search-280113.root $PWD
cp /afs/cern.ch/user/s/ssekmen/public/forWill/RzrMJSMS/${NAME}*${POINT}*.root $PWD

if [ "$BOX" == "LEP" ]
then
    python scripts/runAnalysis.py --multijet --full-region -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_Ele.root ${NAME}_${POINT}_Mu.root -o RazorStop2012Limit_${POINT}_Lep.root
elif [ "$BOX" == "HAD" ]
then
    python scripts/runAnalysis.py --multijet --full-region -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_BJetHS.root ${NAME}_${POINT}_BJetLS.root -o RazorStop2012Limit_${POINT}_Had.root
elif [ "$BOX" == "ALL" ]
then
    python scripts/runAnalysis.py --multijet --full-region -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_Ele.root ${NAME}_${POINT}_Mu.root ${NAME}_${POINT}_BJetHS.root ${NAME}_${POINT}_BJetLS.root -o RazorStop2012Limit_${POINT}_All.root
else
    python scripts/runAnalysis.py --multijet --full-region -c config_winter2012/MultiJet_All_fR1fR2fR3fR4_2012.cfg -i Run2012ABCD_Full_Search-280113.root --run-cls -l --nosave-workspace ${NAME}_${POINT}_${BOX}.root -o RazorStop2012Limit_${POINT}_${BOX}.root

fi

#TODO: Copy the results somewhere

#rm -rf $WD