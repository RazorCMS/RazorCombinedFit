#! /usr/bin/env python
"""To merge datasets"""

import ROOT as rt
import RootTools
import sys

if __name__ == '__main__':
    ARGS = sys.argv[1:]
    if not ARGS:
        print "Need input files!"
        sys.exit(1)

    TMPDATA = ARGS[0]
    DATASET = RootTools.getDataSet(TMPDATA, 'RMRTree')
    ENTRIES = DATASET.numEntries()

    for i in range(1, len(ARGS)):
        INPUT_FILE = ARGS[i]
        print INPUT_FILE
        WDATA = RootTools.getDataSet(INPUT_FILE, 'RMRTree')

        print WDATA.numEntries()
        ENTRIES += WDATA.numEntries()
        DATASET.append(WDATA)

    OUTFILE = rt.TFile.Open("Parked_BJetHS.root", 'RECREATE')
    DATASET.Write()
    OUTFILE.Close()
    print ENTRIES
