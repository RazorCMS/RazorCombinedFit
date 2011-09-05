import ROOT as rt
import sys
import RootTools
import glob
from math import *
import os

def calcCLs(lzValues_sb,lzValues_b,Box):
    BoxName, lzCrit = Box
    CLsb = float(len([lz for lz in lzValues_sb if lz < lzCrit]))/len(lzValues_sb)
    CLb = float(len([lz for lz in lzValues_b if lz < lzCrit]))/len(lzValues_b)
    
    CLs = -9999999999
    if CLb!= 0: CLs = CLsb / CLb
    print "Critical Value for %s box is %f" % (BoxName,lzCrit)
    print "Using %i b entries, %i s+b entries" % (len(lzValues_b), len(lzValues_sb))
    print "CLs+b = %f" %CLsb
    print "CLb = %f" %CLb
    print "CLs = %f" %CLs
    
    return CLs

def getQdist(m0, m12, BoxName,directory):

    if BoxName=='Had':
        MR='400.0'
        R='0.4'
    else:
        MR='300.0'
        R='0.3'

    lzValues_b = []
    lzValues_sb = []

    critValueData = -99999999
    FirstFile = True
    
    spbFileList = glob.glob("%s/LimitBkgSigToys_MR%s_R%s_mSUGRA_tanB10_PDF_M0-%s_M12-%s_%s_*.root" %(directory, MR, R, m0, m12, BoxName))
 
    for spbFile in spbFileList:
        # check if file is at least 40K and contains 4 keys in the box subdirectory
        # otherwise the file probably didn't finish writing or didn't close properly
        if os.stat(spbFile).st_size < 40000: continue 
        input = rt.TFile.Open(spbFile)
        if input.Get(BoxName).GetNkeys() < 4:
            input.Close()
            continue
        if FirstFile:
            critValueData  = input.Get("%s/Lz_%s" %(BoxName, BoxName)).get().getRealValue("LzData")
            FirstFile = False
        # get the tree entries using this funny Draw() trick
        tSpB=input.Get("%s/myTree" %BoxName)
        tSpB.Draw('>>elistSpB','','entrylist')
        elistSpB = rt.gDirectory.Get('elistSpB')
        entry = -1;
        while True:
            entry = elistSpB.Next()
            if entry == -1: break
            tSpB.GetEntry(entry)
            #if fabs(tSpB.Lz) < 400:
            lzValues_sb.append(tSpB.Lz)
        input.Close()

    bFileList =  glob.glob("%s/LimitBkgToys_MR%s_R%s_mSUGRA_tanB10_PDF_M0-%s_M12-%s_%s_*.root" %(directory, MR, R, m0, m12, BoxName))

    for bFile in bFileList:
        # check if file is at least 40K and contains 4 keys in the box subdirectory
        # otherwise the file probably didn't finish writing or didn't close properly
        if os.stat(bFile).st_size < 40000: continue
        input = rt.TFile.Open(bFile)
        if input.Get(BoxName).GetNkeys() < 4:
            input.Close()
            continue
        # get the tree entries using this funny Draw() trick
        tB=input.Get("%s/myTree" %BoxName)
        tB.Draw('>>elistB','','entrylist')
        elistB = rt.gDirectory.Get('elistB')
        entry = -1;
        while True:
            entry = elistB.Next()
            if entry == -1: break
            tB.GetEntry(entry)
            lzValues_b.append(tB.Lz)
        input.Close()

    # sort the lists 
    lzValues_b.sort()
    lzValues_sb.sort()

    return lzValues_sb, lzValues_b, critValueData


def getCLs(m0, m12,directory):
    
    # we store the boxes in the format [ Name, Q_data^box]
    Boxes = [["Had", 0],["Mu",0], ["Ele", 0],["MuMu",0],["EleEle",0],["MuEle",0]]
    
       
    lzValuesAll_sb = []
    lzValuesAll_b = []
    for Box in Boxes:
        BoxName = Box[0]
        lzValues_sb,lzValues_b, Box[1] = getQdist(m0, m12, BoxName,directory)
        lzValuesAll_sb.append(lzValues_sb)
        lzValuesAll_b.append(lzValues_b)
        

    # choose number of events to generate for TOT
    # currently, we use the max number of entries in any box 
    maxEntries_sb =  max([len(lz) for lz in lzValuesAll_sb])
    maxEntries_b =  max([len(lz) for lz in lzValuesAll_b])
    maxEntries = max(maxEntries_sb,maxEntries_b)
    #maxEntries = 100000

    extLzValuesAll_sb = []
    extLzValuesAll_b = []
    hSpBList =[]
    hBList = []
    
    # extend the lists to maxEntries, using ROOT histogram method to sample randomly from the existing distribution
    # this way we equalize the number of entries in all the boxes
    for lzValues_sb,lzValues_b,Box in zip(lzValuesAll_sb,lzValuesAll_b,Boxes):
        
        if min(len(lzValues_sb),len(lzValues_b)) >= maxEntries: continue
        zMin = min(lzValues_b+lzValues_sb)
        zMax = max(lzValues_b+lzValues_sb)

        binWidth = fabs(Box[1] - zMin)/20.
        numBins = min(1000000,int(ceil((zMax-zMin)/binWidth)))
        print numBins
        hSpB = rt.TH1D("SpB_%s"% Box[0], "SpB_%s"% Box[0], numBins, zMin, zMax)
        hB = rt.TH1D("B_%s"% Box[0], "B_%s"% Box[0], numBins, zMin, zMax)
        
        for i in xrange(0, len(lzValues_sb)): hSpB.Fill(lzValues_sb[i])
        for i in xrange(0, len(lzValues_b)): hB.Fill(lzValues_b[i])
        extLzValues_sb = [hSpB.GetRandom() for i in xrange(0,maxEntries)]
        extLzValues_b = [hB.GetRandom() for i in xrange(0,maxEntries)]
        #extLzValues_sb.sort()
        #extLzValues_b.sort()
        extLzValuesAll_sb.append(extLzValues_sb)
        extLzValuesAll_b.append(extLzValues_b)
        hSpBList.append(hSpB.Clone())
        hBList.append(hB.Clone())
        hSpB.Delete()
        hB.Delete()

    # to calculate CLs_Tot with just minimum stats in a box, uncomment these two lines    
    #extLzValuesAll_sb = lzValuesAll_sb
    #extLzValuesAll_b = lzValuesAll_b
    
    if len(Boxes)>1:
        # sum the individual values of Lz for each box, and return a list with CLs_tot
        lzValuesTot_sb = [sum(lzZip) for lzZip in apply(zip,extLzValuesAll_sb)]
        lzValuesTot_b = [sum(lzZip) for lzZip in apply(zip,extLzValuesAll_b)]
        lzValuesTot_sb.sort()
        lzValuesTot_b.sort()
        lzCritTot = sum(apply(zip,Boxes)[1])
        Boxes.append(["Tot",lzCritTot])
        lzValuesAll_sb.append(lzValuesTot_sb) 
        lzValuesAll_b.append(lzValuesTot_b)

        zMin = min(lzValuesTot_b+lzValuesTot_sb)
        zMax = max(lzValuesTot_b+lzValuesTot_sb)       
        binWidth = fabs(Boxes[-1][1] - zMin)/ 20.
        numBins = min(1000000,int(ceil((zMax-zMin)/binWidth)))

        hSpB = rt.TH1D("SpB_Tot", "SpB_Tot", numBins, zMin, zMax)
        hB = rt.TH1D("B_Tot", "B_Tot", numBins, zMin, zMax)
        
        for i in xrange(0, len(lzValuesTot_sb)): hSpB.Fill(lzValuesTot_sb[i])
        for i in xrange(0, len(lzValuesTot_b)): hB.Fill(lzValuesTot_b[i])

        zMin = min(lzValuesTot_b+lzValuesTot_sb)
        zMax = max(lzValuesTot_b+lzValuesTot_sb)        
        
        hSpBList.append(hSpB.Clone())
        hBList.append(hB.Clone())
        hSpB.Delete()
        hB.Delete()

    clTree = rt.TTree("clTree", "clTree")
    rt.gROOT.ProcessLine(
        "struct MyStruct{\
        Double_t m0;\
        Double_t m12;\
        Double_t CL0;\
        Double_t CL1;\
        Double_t CL2;\
        Double_t CL3;\
        Double_t CL4;\
        Double_t CL5;\
        Double_t CL6;};")
    from ROOT import MyStruct

    s = MyStruct()
    clTree.Branch("m0", rt.AddressOf(s,"m0"),'m0/D')
    clTree.Branch("m12", rt.AddressOf(s,"m12"),'m12/D')
    for i in range(0, len(Boxes)): clTree.Branch("CLs_%s" %Boxes[i][0], rt.AddressOf(s,"CL%i" %i),'CL%i/D' %i)
        
    s.m0 = float(m0)
    s.m12 = float(m12)
    if len(Boxes) > 0: s.CL0 = calcCLs(lzValuesAll_sb[0], lzValuesAll_b[0], Boxes[0])
    if len(Boxes) > 1: s.CL1 = calcCLs(lzValuesAll_sb[1], lzValuesAll_b[1], Boxes[1])
    if len(Boxes) > 2: s.CL2 = calcCLs(lzValuesAll_sb[2], lzValuesAll_b[2], Boxes[2])
    if len(Boxes) > 3: s.CL3 = calcCLs(lzValuesAll_sb[3], lzValuesAll_b[3], Boxes[3])
    if len(Boxes) > 4: s.CL4 = calcCLs(lzValuesAll_sb[4], lzValuesAll_b[4], Boxes[4])
    if len(Boxes) > 5: s.CL5 = calcCLs(lzValuesAll_sb[5], lzValuesAll_b[5], Boxes[5])
    if len(Boxes) > 6: s.CL6 = calcCLs(lzValuesAll_sb[6], lzValuesAll_b[6], Boxes[6])
        
    clTree.Fill()

    fileOut = rt.TFile.Open("CLs_m0_%s_m12_%s.root" %(m0, m12), "recreate")
    clTree.Write()
    for hSpB, hB in zip(hSpBList,hBList):
        hSpB.Write()
        hB.Write()
    fileOut.Close()
    
if __name__ == '__main__':
    m0 = sys.argv[1]
    m12 = sys.argv[2]
    directory = sys.argv[3]
    getCLs(m0, m12, directory)
