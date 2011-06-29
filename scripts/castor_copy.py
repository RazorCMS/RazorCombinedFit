#! /usr/bin/env python
import os
import sys
################################################
# list folder (source and target)
################################################
#castor_folder = "/castor/cern.ch/user/c/crogan/CMST3/SUSY/LM1/root/"
castor_folder = sys.argv[1]
target_folder = sys.argv[2]

# make folder if not already done
os.system("mkdir "+target_folder)
os.system("cd "+target_folder)

# make copy.src file
os.system("nsls "+castor_folder+" > "+target_folder+"copy_tmp.src")

list_file = target_folder+"copy_tmp.src"
src_file  = target_folder+"copy.src"

#read the list of files and copy files
input = open(list_file)
for ntpfile in input:
    os.system('echo rfcp '+castor_folder+"/"+ntpfile[:-1]+" "+target_folder)
    os.system('export STAGE_HOST=castorcms; export STAGE_SVCCLASS=cmst3; rfcp '+castor_folder+"/"+ntpfile[:-1]+" "+target_folder)
    continue
input.close
os.system("rm "+target_folder+"copy_tmp.src")


