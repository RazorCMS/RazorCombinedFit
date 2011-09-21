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

def calcCLsExp(lzValues_sb,lzValues_b,Box):
    CLbValues = [0.16, 0.5, 0.84]
    lzValues_b.sort()
    lzValues_sb.sort()
    lzCritValues = [lzValues_b[int(sigma*len(lzValues_b)+0.5)] for sigma in CLbValues]
    CLsbValues = [float(len([lz for lz in lzValues_sb if lz < lzCrit]))/len(lzValues_sb) for lzCrit in lzCritValues]
    CLsExpValues = [CLsb/CLb for CLsb,CLb in zip(CLsbValues,CLbValues)]
    print "Expected for %s box"%Box[0]
    print "CLsExp+ = %f" %CLsExpValues[0]
    print "CLsExp  = %f" %CLsExpValues[1]
    print "CLsExp- = %f" %CLsExpValues[2]
    return CLsExpValues

def getQdist(m0, m12, BoxName,directory,tanB):


    lzValues_b = []
    lzValues_sb = []

    critValueData = -99999999
    FirstFile = True
    
    spbFileList = glob.glob("%s/LimitBkgSigToys_mSUGRA_tanB%i_PDF_M0-%s_M12-%s_*.root" %(directory, tanB,m0, m12))
 
    for spbFile in spbFileList:
        # check if file is at least 40K and contains 4 keys in the box subdirectory
        # otherwise the file probably didn't finish writing or didn't close properly
        if os.stat(spbFile).st_size < 40000: continue 
        input = rt.TFile.Open(spbFile)
        if input.GetNkeys() < 7:
            input.Close()
            continue
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

    bFileList =  glob.glob("%s/LimitBkgToys_mSUGRA_tanB%i_PDF_M0-%s_M12-%s_*.root" %(directory, tanB,m0, m12))

    for bFile in bFileList:
        # check if file is at least 40K and contains 4 keys in the box subdirectory
        # otherwise the file probably didn't finish writing or didn't close properly
        if os.stat(bFile).st_size < 40000: continue
        input = rt.TFile.Open(bFile)
        if input.GetNkeys() < 7:
            input.Close()
            continue
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

    return lzValues_sb, lzValues_b, critValueData


def getCLs(m0, m12,directory,tanB):
    
    # we store the boxes in the format [ Name, Q_data^box]
    Boxes = [["Had", 0],["Mu",0], ["Ele", 0],["MuMu",0],["EleEle",0],["MuEle",0]]
        
    lzValuesAll_sb = []
    lzValuesAll_b = []

    hSpBList =[]
    hBList = []
    for Box in Boxes:
        BoxName = Box[0]
        lzValues_sb,lzValues_b, Box[1] = getQdist(m0, m12, BoxName,directory,tanB)
        
        lzValuesAll_sb.append(lzValues_sb)
        lzValuesAll_b.append(lzValues_b)
        
        zMin = min(lzValues_b+lzValues_sb)
        zMax = max(lzValues_b+lzValues_sb)
        binWidth = fabs(Box[1] - zMin)/20.
        numBins = min(1000000,int(ceil((zMax-zMin)/binWidth)))
        hSpB = rt.TH1D("SpB_%s"% Box[0], "SpB_%s"% Box[0], numBins, zMin, zMax)
        hB = rt.TH1D("B_%s"% Box[0], "B_%s"% Box[0], numBins, zMin, zMax)
        
        for i in xrange(0, len(lzValues_sb)): hSpB.Fill(lzValues_sb[i])
        for i in xrange(0, len(lzValues_b)): hB.Fill(lzValues_b[i])

        hSpBList.append(hSpB.Clone())
        hBList.append(hB.Clone())
        del hSpB
        del hB
    
    # choose number of events to generate for TOT
    # currently, we use the max number of entries in any box 
    maxEntries_sb =  max([len(lz) for lz in lzValuesAll_sb])
    maxEntries_b =  max([len(lz) for lz in lzValuesAll_b])
    maxEntries = max(maxEntries_sb,maxEntries_b)
    # or specify your own maxEntries, such as 50K
    #maxEntries = 50000

    # or to calculate CLs_Tot with just minimum stats in a box, 
    # simply set maxEntries = 1
    #maxEntries = 1
    
    extLzValuesAll_sb = []
    extLzValuesAll_b = []

    # extend the lists to maxEntries, using ROOT histogram method to sample randomly from the existing distribution
    # this way we equalize the number of entries in all the boxes
    for lzValues_sb,lzValues_b,hSpB,hB in zip(lzValuesAll_sb,lzValuesAll_b,hSpBList,hBList):
        
        if min(len(lzValues_sb),len(lzValues_b)) >= maxEntries: 
            # for "extended list", just copy the values of the initial list
            extLzValues_sb = list(lzValues_sb)
            extLzValues_b = list(lzValues_b)

            extLzValuesAll_sb.append(extLzValues_sb)
            extLzValuesAll_b.append(extLzValues_b)
            
        else:
            # for "extended list", generate from the histogram up to maxEntries
            extLzValues_sb = [hSpB.GetRandom() for i in xrange(0,maxEntries)]
            extLzValues_b = [hB.GetRandom() for i in xrange(0,maxEntries)]
        
            extLzValuesAll_sb.append(extLzValues_sb)
            extLzValuesAll_b.append(extLzValues_b)
                                
    if len(Boxes)>1:
        # sum the individual values of Lz for each box, and return a list with CLs_tot
        lzValuesTot_sb = [sum(lzZip) for lzZip in apply(zip,extLzValuesAll_sb)]
        lzValuesTot_b = [sum(lzZip) for lzZip in apply(zip,extLzValuesAll_b)]

        LepBoxes = [Boxes[apply(zip,Boxes)[0].index('Mu')],Boxes[apply(zip,Boxes)[0].index('Ele')]]
        extLzValuesLep_sb = [extLzValuesAll_sb[apply(zip,Boxes)[0].index('Mu')],extLzValuesAll_sb[apply(zip,Boxes)[0].index('Ele')]]
        extLzValuesLep_b = [extLzValuesAll_b[apply(zip,Boxes)[0].index('Mu')],extLzValuesAll_b[apply(zip,Boxes)[0].index('Ele')]]
        
        lzValuesLepTot_sb = [sum(lzZip) for lzZip in apply(zip,extLzValuesLep_sb)]
        lzValuesLepTot_b = [sum(lzZip) for lzZip in apply(zip,extLzValuesLep_b)]
        
        lzCritTot = sum(apply(zip,Boxes)[1])
        lzCritLep = sum(apply(zip,LepBoxes)[1])

        Boxes.append(["1Lep",lzCritLep])
        Boxes.append(["Tot",lzCritTot])
        lzValuesAll_sb.append(lzValuesLepTot_sb)
        lzValuesAll_b.append(lzValuesLepTot_b)
         
        lzValuesAll_sb.append(lzValuesTot_sb) 
        lzValuesAll_b.append(lzValuesTot_b)

        zMin = min(lzValuesLepTot_b+lzValuesLepTot_sb)
        zMax = max(lzValuesLepTot_b+lzValuesLepTot_sb)
        binWidth = fabs(Boxes[-1][1] - zMin)/ 20.
        numBins = min(1000000,int(ceil((zMax-zMin)/binWidth)))
        
        hSpB = rt.TH1D("SpB_1Lep", "SpB_1Lep", numBins, zMin, zMax)
        hB = rt.TH1D("B_1Lep", "B_1Lep", numBins, zMin, zMax)
        for i in xrange(0, len(lzValuesLepTot_sb)): hSpB.Fill(lzValuesLepTot_sb[i])
        for i in xrange(0, len(lzValuesLepTot_b)): hB.Fill(lzValuesLepTot_b[i])

        hSpBList.append(hSpB.Clone())
        hBList.append(hB.Clone())
        del hSpB
        del hB
                                                
        zMin = min(lzValuesTot_b+lzValuesTot_sb)
        zMax = max(lzValuesTot_b+lzValuesTot_sb)       
        binWidth = fabs(Boxes[-1][1] - zMin)/ 20.
        numBins = min(1000000,int(ceil((zMax-zMin)/binWidth)))

        hSpB = rt.TH1D("SpB_Tot", "SpB_Tot", numBins, zMin, zMax)
        hB = rt.TH1D("B_Tot", "B_Tot", numBins, zMin, zMax)
        
        for i in xrange(0, len(lzValuesLepTot_sb)): hSpB.Fill(lzValuesLepTot_sb[i])
        for i in xrange(0, len(lzValuesLepTot_b)): hB.Fill(lzValuesLepTot_b[i])

        for i in xrange(0, len(lzValuesTot_sb)): hSpB.Fill(lzValuesTot_sb[i])
        for i in xrange(0, len(lzValuesTot_b)): hB.Fill(lzValuesTot_b[i])

                
        hSpBList.append(hSpB.Clone())
        hBList.append(hB.Clone())
        del hSpB
        del hB

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
        Double_t CL6;\
        Double_t CL7;\
        Double_t CL8;\
        Double_t CL9;\
        Double_t CL10;\
        Double_t CL11;\
        Double_t CL12;\
        Double_t CL13;\
        Double_t CL14;\
        Double_t CL15;\
        Double_t CL16;};")
    from ROOT import MyStruct

    s = MyStruct()
    clTree.Branch("m0", rt.AddressOf(s,"m0"),'m0/D')
    clTree.Branch("m12", rt.AddressOf(s,"m12"),'m12/D')
    for i in range(0, len(Boxes)): clTree.Branch("CLs_%s" %Boxes[i][0], rt.AddressOf(s,"CL%i" %i),'CL%i/D' %i)

    clTree.Branch("CLs_Had_ExpPlus", rt.AddressOf(s,"CL8"),'CL8/D')
    clTree.Branch("CLs_Had_Exp", rt.AddressOf(s,"CL9"),'CL9/D')
    clTree.Branch("CLs_Had_ExpMinus", rt.AddressOf(s,"CL10"),'CL10/D')

    clTree.Branch("CLs_1Lep_ExpPlus", rt.AddressOf(s,"CL11"),'CL11/D')
    clTree.Branch("CLs_1Lep_Exp", rt.AddressOf(s,"CL12"),'CL12/D')
    clTree.Branch("CLs_1Lep_ExpMinus", rt.AddressOf(s,"CL13"),'CL13/D')

    clTree.Branch("CLs_Tot_ExpPlus", rt.AddressOf(s,"CL14"),'CL14/D')
    clTree.Branch("CLs_Tot_Exp", rt.AddressOf(s,"CL15"),'CL15/D')
    clTree.Branch("CLs_Tot_ExpMinus", rt.AddressOf(s,"CL16"),'CL16/D')

    s.m0 = float(m0)
    s.m12 = float(m12)
    if len(Boxes) > 0: s.CL0 = calcCLs(lzValuesAll_sb[0], lzValuesAll_b[0], Boxes[0])
    if len(Boxes) > 1: s.CL1 = calcCLs(lzValuesAll_sb[1], lzValuesAll_b[1], Boxes[1])
    if len(Boxes) > 2: s.CL2 = calcCLs(lzValuesAll_sb[2], lzValuesAll_b[2], Boxes[2])
    if len(Boxes) > 3: s.CL3 = calcCLs(lzValuesAll_sb[3], lzValuesAll_b[3], Boxes[3])
    if len(Boxes) > 4: s.CL4 = calcCLs(lzValuesAll_sb[4], lzValuesAll_b[4], Boxes[4])
    if len(Boxes) > 5: s.CL5 = calcCLs(lzValuesAll_sb[5], lzValuesAll_b[5], Boxes[5])
    if len(Boxes) > 6: s.CL6 = calcCLs(lzValuesAll_sb[6], lzValuesAll_b[6], Boxes[6])
    if len(Boxes) > 7: s.CL7 = calcCLs(lzValuesAll_sb[7], lzValuesAll_b[7], Boxes[7])

    if len(Boxes) > 7: s.CL8,s.CL9,s.CL10 = calcCLsExp(lzValuesAll_sb[0], lzValuesAll_b[0],Boxes[0])
    if len(Boxes) > 7: s.CL11,s.CL12,s.CL13 = calcCLsExp(lzValuesAll_sb[6], lzValuesAll_b[6],Boxes[6])
    if len(Boxes) > 7: s.CL14,s.CL15,s.CL16 = calcCLsExp(lzValuesAll_sb[7], lzValuesAll_b[7],Boxes[7])
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
    tanB = 10
    getCLs(m0, m12, directory,tanB)
