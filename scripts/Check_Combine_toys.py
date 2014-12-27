"""Look for failed jobs from the runCombineLimits scripts on the Cornell T3"""

import ROOT as rt
import os
import sys

if __name__ == '__main__':

    MODEL = sys.argv[1]
    LSP = sys.argv[2]

    DONE_FILES = []

    SEARCH_DIR = ("/home/uscms208/cms/CMSSW_6_1_2/src/RazorCombinedFit_lucieg_"
                  "May29/Combine/%s/step1/mLSP%s/" % (MODEL, LSP))

    ALL_FILES = os.listdir(SEARCH_DIR)
    for root_file in ALL_FILES:

        if root_file.startswith("razor_combine_"):
            continue

        if root_file.find('higgsCombineGrid') != -1 and \
        root_file.find('xsec') != -1:
            file_to_check = rt.TFile.Open(SEARCH_DIR + root_file)
            limit = file_to_check.Get("limit")
            if limit == None:
                continue
            elif limit.GetEntries() == 0:
                continue
            else:
                DONE_FILES.append(root_file)

    print '\n'.join(DONE_FILES)

    DONE_FILE = open("done.txt", 'w')
    DONE_FILE.write('\n'.join(DONE_FILES))
