"""To combine different boxes"""
import os
import sys

if __name__ == '__main__':

    HADRONIC = sys.argv[1]

    # os.system("mkdir -p combineCards_25")
    os.system("cd combineCards_25")

    for mass in range(150, 800, 25):
        # os.system("mv combine_files_*4jets_*/ combineCards_25")
        if HADRONIC:
            os.system("combineCards.py BJetHS=combine_files_gt6_BJetHS/"
                      "razor_combine_BJetHS_gt6_T2tt_%s.0_25.0.txt "
                      "BJetLS=combine_files_gt6_BJetLS/"
                      "razor_combine_BJetLS_gt6_T2tt_%s.0_25.0.txt > "
                      "razor_combine_All_T2tt_%s.0_25.0.txt" %\
                      (str(mass), str(mass), str(mass)))

        else:
            os.system("combineCards.py Mu_4jets=combine_files_4jets_Mu/razor_combine_Mu_4jets_T2tt_%s.0_25.0.txt Mu_gt4jets=combine_files_gt4jets_Mu/razor_combine_Mu_gt4jets_T2tt_%s.0_25.0.txt Ele_4jets=combine_files_4jets_Ele/razor_combine_Ele_4jets_T2tt_%s.0_25.0.txt Ele_gt4jets=combine_files_gt4jets_Ele/razor_combine_Ele_gt4jets_T2tt_%s.0_25.0.txt > razor_combine_All_T2tt_%s.0_25.0.txt"%(str(mass),str(mass),str(mass),str(mass),str(mass)))

        os.system("combine -M Asymptotic  razor_combine_All_T2tt_%s.0_25.0.txt -n T2tt_All_%s_25 "%(mass,mass))
        os.system( "mv higgsCombine* combineCards_25" )
        os.system( " rm roostats*" )
