
import sys, os


if __name__ == '__main__':

   for mass in range(150,800,25):
       os.system("mkdir -p combineCards_25_Sideband")
       os.system("cd combineCards_25_Sideband")
       os.system("combineCards.py Mu_4jets=combine_files_4jets_Mu/razor_combine_Mu_T2tt_MG_%s.000000_MCHI_25.000000.txt Mu_gt4jets=combine_files_gt4jets_Mu/razor_combine_Mu_T2tt_MG_%s.000000_MCHI_25.000000.txt Ele_4jets=combine_files_4jets_Ele/razor_combine_Ele_T2tt_MG_%s.000000_MCHI_25.000000.txt Ele_gt4jets=combine_files_gt4jets_Ele/razor_combine_Ele_T2tt_MG_%s.000000_MCHI_25.000000.txt > combineCards_25_Sideband/razor_combine_All_T2tt_MG_%s.000000_MCHI_25.000000.txt"%(str(mass),str(mass),str(mass),str(mass),str(mass)))


       os.system("combine -M Asymptotic  combineCards_25_Sideband/razor_combine_All_T2tt_MG_%s.000000_MCHI_25.000000.txt -n T2tt_All_%s_25 "%(mass,mass))
       os.system( "mv higgsCombine* combineCards_25_Sideband" )
       os.system( " rm roostats*" ) 
