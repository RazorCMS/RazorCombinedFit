from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import os

if __name__ == '__main__':
    boxNames = ["BJetHS"]#,"BJetLS","Mu","Ele"]
    datasetNames = ["SMCocktail"]#,"TTJets","MuHad-Run2012ABCD","ElectronHad-Run2012ABCD"]
    #sidebandNames = ["Sideband","FULL"]
    sidebandNames = ["FULL"]
    sidebandMap = {"FULL": "Full Fit","Sideband":"Sideband Fit"}
    
    fitmodes = ["2D"]
    includeTable = True
    
    LaTeXMap = {"TTJets":"$t\\bar{t}$","WJets":"$W\\to\\ell\\nu$",
                "SMCocktail":"Total SM (19/fb)",
                "MuHad-Run2012ABCD":"Run2012ABCD",
                "ElectronHad-Run2012ABCD":"Run2012ABCD"}
    
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
    beamerPres.write("\\title{Razor-MultiJet Fits}\n")
    beamerPres.write("\\subtitle{}\n")
    beamerPres.write("\\author{Lucie, Will, Maurizio, Sezen, Emmanuele}\n")
    beamerPres.write("\\date{\\today}\n")
    beamerPres.write("\\begin{document}\n")
    beamerPres.write("\n")
    
    beamerPres.write("\\frame{\\maketitle}\n")
    for fitmode in fitmodes:
        for datasetName in datasetNames:
            for box in boxNames:
                for sideband in sidebandNames:
                    ffDir = "toys_%s/%s_%s_FF"%((datasetName,sideband,box))
                    if not os.path.isdir("%s"%(ffDir)): continue
                    if not os.path.exists("%s/MR_%s_%s.pdf"%(ffDir,sideband,box)): continue
                    if not os.path.exists("%s/RSQ_%s_%s.pdf"%(ffDir,sideband,box)): continue
                    if not os.path.exists("%s/nSigmaLog_%s.pdf"%(ffDir,box)): continue
                    print ffDir
                    beamerPres.write("\n")
                    rootFile = rt.TFile.Open("%s/expected_sigbin_%s.root"%(ffDir,box))
                    myTree = rootFile.Get("myTree")
                    nToys = myTree.GetEntries()
                    rootFile.Close()
                    del myTree
                    beamerPres.write("\\begin{frame}{%s %s %s $N_{\\text{toys}}=%i$}\n"%(box,LaTeXMap[datasetName],sidebandMap[sideband],nToys))
                    beamerPres.write("\\begin{changemargin}{-0.75in}{-0.75in}\n")
                    beamerPres.write("\\begin{center}\n")
                    beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/MR_%s_%s.pdf}\n"%(ffDir,sideband,box))
                    beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/RSQ_%s_%s.pdf}\n"%(ffDir,sideband,box))
                    beamerPres.write("\\\\ ")
                    beamerPres.write("\\includegraphics[width=.51\\textwidth]{%s/nSigmaLog_%s.pdf}\n"%(ffDir,box))
                    beamerPres.write("\\end{center}\n")
                    beamerPres.write("\\end{changemargin}\n")
                    beamerPres.write("\\end{frame}\n")
                    beamerPres.write("\n")

                    if not includeTable: continue
                    try:
                        tableFile = open("%s/table_%s.tex"%(ffDir,box))
                        tableList = tableFile.readlines()
                        beamerPres.write("\\begin{frame}{%s %s %s $N_{\\text{toys}}=%i$}\n"%(box,LaTeXMap[datasetName],sidebandMap[sideband],nToys))
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
    
