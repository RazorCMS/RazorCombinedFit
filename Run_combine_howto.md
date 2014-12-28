## Asymptotic limit


## Toy-based limit

### Step 1
python scripts/runCombineLimitsFromGrid_T3_US_Cornell.py Mu T2tt donefile.txt --mchi-lt 50 --xsec-file stop.root --asymptotic-file Tests/Rsq_gte0.15/combine_files_T2tt_Mu_3D_split/asymptoticFile_T2tt_Mu_3D_split_25.root --no-sub --mg-geq 450 --mg-lt 475

### Step 2
python scripts/runCombineLimitsFromGrid_T3_US_Cornell.py Mu T2tt donefile.txt --mchi-lt 50 --xsec-file stop.root --asymptotic-file Tests/Rsq_gte0.15/combine_files_T2tt_Mu_3D_split/asymptoticFile_T2tt_Mu_3D_split_25.root --iterations 10 --step2

### Plot
python scripts/plotLimitToys.py T2tt Mu