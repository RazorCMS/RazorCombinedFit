import sys
import os

#this is global, to be reused in the plot making
def BinningFine(Box, noBtag):
    if Box == "Jet" or Box == "TauTauJet" or Box == "MultiJet":
        MRbins = [400, 480, 600, 740, 900, 1200, 1600, 2500]
        if noBtag: Rsqbins = [0.18,0.22,0.26,0.30,0.35,0.40,0.45,0.50]
        else: Rsqbins = [0.18,0.24,0.32,0.41,0.52,0.64,0.80,1.5]
    else:
        MRbins = [350, 410, 480, 560, 650, 750, 860, 980, 1200, 1600, 2500]
        if noBtag: Rsqbins = [0.11,0.15,0.2,0.25,0.30,0.35,0.40,0.45,0.50]
        else: Rsqbins = [0.11,0.15,0.2,0.25,0.30,0.35,0.40,0.45,0.50,0.56,0.62,0.70,0.80,1.5]
    if noBtag: nBtagbins = [0.0,1.0]
    else: nBtagbins = [1.0,2.0,3.0,4.0,5.0]
    return MRbins, Rsqbins, nBtagbins

def Binning(Box, noBtag, newFR):
    if newFR:
        if Box == "Jet" or Box == "TauTauJet" or Box == "MultiJet":
            MRbins = [250, 400, 550, 700, 900, 1200, 1600, 2500]
            if noBtag: Rsqbins =  [0.18,0.24,0.35,0.50]
            else: Rsqbins = [0.10,0.15,0.21,0.30,0.41,0.52,0.64,0.80,1.5]
        else:
            MRbins = [250, 400, 550, 700, 900, 1200, 1600, 2500]
            if noBtag: Rsqbins = [0.18,0.24,0.35,0.50]
            else: Rsqbins = [0.10,0.15,0.21,0.30,0.41,0.52,0.64,0.80,1.5]
    else:
        if Box == "Jet" or Box == "TauTauJet" or Box == "MultiJet":
            MRbins = [400, 550, 700, 900, 1200, 1600, 2500]
            if noBtag: Rsqbins = [0.18,0.22,0.26,0.30,0.35,0.40,0.45,0.50]
            else: Rsqbins = [0.18,0.24,0.32,0.41,0.52,0.64,0.80,1.5]
        else:
            MRbins = [350, 420, 500, 600, 740, 900, 1200, 1600, 2500]
            if noBtag: Rsqbins = [0.11,0.17,0.23,0.35,0.50]
            else: Rsqbins = [0.11,0.15,0.21,0.30,0.41,0.52,0.64,0.80,1.5]
    if noBtag: nBtagbins = [0.0,1.0]
    else: nBtagbins = [1.0,2.0,3.0,4.0,5.0]
    return MRbins, Rsqbins, nBtagbins

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print "\nRun the script as follows:\n"
        print "python scripts/makeBluePlot.py BoxName ToyDir DataFile OutDir"
        print "with:"
        print "- BoxName = name of the Box (MuMu, MuEle, etc)"
        print "- ToyDir = directory with the .txt files generated by the fit"
        print "- DataFile = name of the corresponding data file"
        print "- OutDir = name of the output directory"
        print ""
        print "After the inputs you can specify the following options"
        print " --plotOnly  Run the plot-making macro from already computed bkg predictions"
        print " --noBtag    this is a 0btag box (i.e. R2 stops at 0.5)"
        print " --newFR    this the new fit region"
        sys.exit()
    else:
        Box = sys.argv[1]
        ToyDir = sys.argv[2]
        if ToyDir[-1]=="/": ToyDir = ToyDir[:-1]
        Data = sys.argv[3]
        Label = sys.argv[4]
        noBtag = ""
        plotOnly = False
        for i in range(5,len(sys.argv)):
            if sys.argv[i] == "--noBtag": noBtag = "--noBtag"
            if sys.argv[i] == "--plotOnly": plotOnly = True
            if sys.argv[i] == "--newFR": newFR = True

    if not plotOnly:
        os.system("python scripts/convertToyToROOT.py %s/frtoydata_%s" %(ToyDir, Box))
        os.system("rm %s.txt" %(ToyDir))
        os.system("ls %s/frtoydata_*.root > %s.txt" %(ToyDir, ToyDir))
        os.system("mkdir -p %s"%(Label))
        os.system("python scripts/expectedYield_sigbin.py 1 %s/expected_sigbin_%s.root %s %s.txt"%(Label,Box, Box, ToyDir))
        os.system("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s"%(Box, Label, Box, Data, Label, noBtag))
    else:
        os.system("mkdir -p %s"%(Label))
        os.system("rm %s/pvalue_%s.root" %(Label,Box))
        os.system("python scripts/makeToyPVALUE_sigbin.py %s %s/expected_sigbin_%s.root %s %s %s"%(Box, Label, Box, Data, Label, noBtag))

    # compile the latex table
    os.system("cd %s; pdflatex table_%s.tex" %(Label, Box))
