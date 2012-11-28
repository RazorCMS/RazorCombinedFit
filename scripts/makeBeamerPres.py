from optparse import OptionParser
import ROOT as rt
from array import *
import sys
import os

if __name__ == '__main__':
    boxNames = ["MuEle","MuMu","MuTau","Mu","Ele","EleEle","EleTau"]
    datasetNames = ["TTJets","WJets","SMCocktail","MuHad-Run2012AB","ElectronHad-Run2012AB"]
    sidebandNames = ["SidebandL","FULL"]

    includeTable = True
    
    LaTeXMap = {"TTJets":"$t\\bar{t}$","WJets":"$W\\to\\ell\\nu$",
                "ZJets":"$Z\\to\\ell\\ell$","ZJNuNu":"$Z\\to\\nu\\nu$",
                "SMCocktail":"SM Cocktail (5.0 fb$^{-1})$",
                "MuHad-Run2012AB":"Run2012AB",
                "ElectronHad-Run2012AB":"Run2012AB"}
    
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
    beamerPres.write("\\title{Razor-b Fits}\n")
    beamerPres.write("\\author{Javier Duarte}\n")
    beamerPres.write("\\date{\\today}\n")
    beamerPres.write("\\begin{document}\n")
    beamerPres.write("\n")
    
    beamerPres.write("\\frame{\\maketitle}\n")

    for box in boxNames:
        for datasetName in datasetNames:
            for sideband in sidebandNames:
                if not os.path.isdir("toys_%s/%s_%s_FF"%(datasetName,sideband,box)): continue
                beamerPres.write("\n")
                beamerPres.write("\\begin{frame}{%s %s %s}\n"%(box,LaTeXMap[datasetName],sideband))
                beamerPres.write("\\begin{changemargin}{-0.75in}{-0.75in}\n")
                beamerPres.write("\\begin{center}\n")
                beamerPres.write("\\includegraphics[width=.6\\textwidth]{toys_%s/%s_%s_FF/MR_%s_%s_%s.pdf}\n"%(datasetName,sideband,box,datasetName,sideband,box))
                beamerPres.write("\\includegraphics[width=.6\\textwidth]{toys_%s/%s_%s_FF/RSQ_%s_%s_%s.pdf}\\\\\n"%(datasetName,sideband,box,datasetName,sideband,box))
                beamerPres.write("\\includegraphics[width=.6\\textwidth]{toys_%s/%s_%s_FF/nSigma_%s.pdf}\n"%(datasetName,sideband,box,box))
                beamerPres.write("\\end{center}\n")
                beamerPres.write("\\end{changemargin}\n")
                beamerPres.write("\\end{frame}\n")
                beamerPres.write("\n")

                if not includeTable: continue
                tableFile = open("toys_%s/%s_%s_FF/table_%s.tex"%(datasetName,sideband,box,box))
                tableList = tableFile.readlines()
                beamerPres.write("\\begin{frame}{%s %s %s}\n"%(box,LaTeXMap[datasetName],sideband))
                beamerPres.write("\\begin{changemargin}{-0.75in}{-0.75in}\n")
                for tableLine in tableList[3:-1]:
                    beamerPres.write(tableLine)
                beamerPres.write("\\end{changemargin}\n")
                beamerPres.write("\\end{frame}\n")
                beamerPres.write("\n")

    
    beamerPres.write("\\end{document}\n")
    beamerPres.close()
    
