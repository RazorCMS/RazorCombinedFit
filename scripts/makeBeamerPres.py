from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import os

if __name__ == '__main__':
    boxNames = ["MuEle","MuMu","EleEle","MuTau","Mu","EleTau","Ele","Jet","TauTauJet","MultiJet"]
    #boxNames = ["MuMu","Mu","Ele"]
    #datasetNames = ["TTJets","WJets","SMCocktail","MuHad-Run2012AB","ElectronHad-Run2012AB"]
    datasetNames = ["SMCocktail"]
    #datasetNames = ["MuHad-Run2012AB","ElectronHad-Run2012AB","HT-HTMHT-Run2012AB"]
    sidebandNames = ["Sideband","FULL"]
    #sidebandNames = ["FULL"]
    sidebandMap = {"FULL": "Full Fit","Sideband":"Sideband Fit"}
    #btagNames = ["","_1b","_2b","_3b","_4b"]
    btagNames = [""]
    
    #fitmodes = ["2D","3D"]
    fitmodes = ["3D"]
    includeTable = True
    
    LaTeXMap = {"TTJets":"$t\\bar{t}$","WJets":"$W\\to\\ell\\nu$",
                "DYJetsToLL":"$Z\\to\\ell\\ell$","ZJetsToNuNu":"$Z\\to\\nu\\nu$",
                "SMCocktail":"Total SM (5/fb)",
                "MuHad-Run2012AB":"Run2012AB",
                "ElectronHad-Run2012AB":"Run2012AB",
                "HT-HTMHT-Run2012AB":"Run2012AB"}
    
    btagMap = {"":"", "_1b":"1 $b$-tag", "_2b":"2 $b$-tag", "_3b":"3 $b$-tag", "_4b": "$\geq$ 4 $b$-tag"}
    
    #prepare the latex table
    beamerPres = open("beamerPres.tex","w")
    beamerPres.write("\\documentclass[hyperref=pdftex, 10pt,presentation,table]{beamer}\n")
    beamerPres.write("\\mode<presentation> {\\usetheme{default}}\n")
    beamerPres.write("\\usepackage{graphicx}\n")
    beamerPres.write("\\usepackage[english]{babel}\n")
    beamerPres.write("\\usepackage[latin1]{inputenc}\n")
    beamerPres.write("\\usepackage{times}\n")
    beamerPres.write("\\usepackage{ulem}\n")
    beamerPres.write("\\usepackage[T1]{fontenc}\n")
    beamerPres.write("\\usepackage{verbatim}\n")
    beamerPres.write("\\newenvironment{changemargin}[2]{\n")
    beamerPres.write("\\begin{list}{}{\\setlength{\\topsep}{0pt}\n")
    beamerPres.write("\\setlength{\\leftmargin}{#1}\n")
    beamerPres.write("\\setlength{\\rightmargin}{#2}\n") 
    beamerPres.write("\\setlength{\\listparindent}{\\parindent}\n")
    beamerPres.write("\\setlength{\\itemindent}{\\parindent}\n")
    beamerPres.write("\\setlength{\\parsep}{\\parskip}}\n")
    beamerPres.write("\\item[]}{\\end{list}}\n")
    beamerPres.write("\\title{Razor-b MC Fits}\n")
    beamerPres.write("\\author{Javier Duarte}\n")
    beamerPres.write("\\date{\\today}\n")
    beamerPres.write("\\begin{document}\n")
    beamerPres.write("\n")
    
    beamerPres.write("\\frame{\\maketitle}\n")
    for fitmode in fitmodes:
        for datasetName in datasetNames:
            for box in boxNames:
                for sideband in sidebandNames:
                    for btag in btagNames:
                        ffDir = "toys_%s_%s/%s_%s_FF"%((datasetName,fitmode,sideband,box))
                        if not os.path.isdir("%s"%(ffDir)): continue
                        if not os.path.exists("%s/MR%s_%s_%s_%s.pdf"%(ffDir,btag,datasetName,sideband,box)): continue
                        if not os.path.exists("%s/RSQ%s_%s_%s_%s.pdf"%(ffDir,btag,datasetName,sideband,box)): continue
                        if not os.path.exists("%s/BTAG%s_%s_%s_%s.pdf"%(ffDir,btag,datasetName,sideband,box)): continue
                        if not os.path.exists("%s/nSigmaLog%s_%s.pdf"%(ffDir,btag,box)): continue
                        beamerPres.write("\n")
                        rootFile = rt.TFile.Open("%s/expected_sigbin_%s.root"%(ffDir,box))
                        myTree = rootFile.Get("myTree")
                        nToys = myTree.GetEntries()
                        rootFile.Close()
                        del myTree
                        beamerPres.write("\\begin{frame}{%s %s %s %s $N_{\\text{toys}}=%i$}\n"%(box,LaTeXMap[datasetName],sidebandMap[sideband],btagMap[btag],nToys))
                        beamerPres.write("\\begin{changemargin}{-0.75in}{-0.75in}\n")
                        beamerPres.write("\\begin{center}\n")
                        beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/MR%s_%s_%s_%s.pdf}\n"%(ffDir,btag,datasetName,sideband,box))
                        beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/RSQ%s_%s_%s_%s.pdf}\n"%(ffDir,btag,datasetName,sideband,box))
                        beamerPres.write("\\\\ ")
                        if not (box=="MuEle" or box=="MuMu" or box=="EleEle" or box=="TauTauJet"):
                            beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/BTAG%s_%s_%s_%s.pdf}\n"%(ffDir,btag,datasetName,sideband,box))
                        beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/nSigmaLog%s_%s.pdf}\n"%(ffDir,btag,box))
                        beamerPres.write("\\end{center}\n")
                        beamerPres.write("\\end{changemargin}\n")
                        beamerPres.write("\\end{frame}\n")
                        beamerPres.write("\n")

                        if not includeTable: continue
                        try:
                            tableFile = open("%s/table%s_%s.tex"%(ffDir,btag,box))
                            tableList = tableFile.readlines()
                            beamerPres.write("\\begin{frame}{%s %s %s %s $N_{\\text{toys}}=%i$}\n"%(box,LaTeXMap[datasetName],sidebandMap[sideband],btagMap[btag],nToys))
                            beamerPres.write("\\begin{changemargin}{-0.75in}{-0.75in}\n")
                            for tableLine in tableList[3:-1]:
                                beamerPres.write(tableLine)
                            beamerPres.write("\\end{changemargin}\n")
                            beamerPres.write("\\end{frame}\n")
                            beamerPres.write("\n")
                        except IOError:
                            print "table does not exist, not writing"

    
    beamerPres.write("\\end{document}\n")
    beamerPres.close()
    
