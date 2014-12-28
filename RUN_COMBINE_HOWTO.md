The module scripts/prepareCombineSimple.py is what creates the data cards for HiggsCombine.
* The flags pdfmode and fitmode were used to test various fit configurations; we should use their default values.

The module scripts/runCombineLimitsFromGrid_T3_US_Cornell.py is what we use to submit jobs to the queues for the toy-based limit.

The module scripts/runPreparescript.py is what we use to run the asymptotic limit in interactive mode for one mLSP strip.


## Asymptotic limit
python scripts/runPreparescript.py MODEL box directory with the SMS files

python scripts/runPreparescript.py T2tt Mu Leptonic/Dec2014/T2ttMu0p15


## Toy-based limit

### Step 1
python scripts/runCombineLimitsFromGrid_T3_US_Cornell.py Mu T2tt donefile.txt --mchi-lt 50 --xsec-file stop.root --asymptotic-file Tests/Rsq_gte0.15/combine_files_T2tt_Mu_3D_split/asymptoticFile_T2tt_Mu_3D_split_25.root --no-sub --mg-geq 450 --mg-lt 475

### Step 2
python scripts/runCombineLimitsFromGrid_T3_US_Cornell.py Mu T2tt donefile.txt --mchi-lt 50 --xsec-file stop.root --asymptotic-file Tests/Rsq_gte0.15/combine_files_T2tt_Mu_3D_split/asymptoticFile_T2tt_Mu_3D_split_25.root --iterations 10 --step2

### Plot
python scripts/plotLimitToys.py T2tt Mu