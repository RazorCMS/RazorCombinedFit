import ROOT as rt
import sys
import RootTools
import glob

def calcCLs(hist_sb,hist_b,lzCrit):
  
    critBin_b = hist_b.FindBin(lzCrit)
    uppBin_b = hist_b.GetNbinsX()

    critBin_sb = hist_sb.FindBin(lzCrit)
    
    CLb = 1-hist_b.Integral(critBin_b,uppBin_b)/hist_b.Integral()
    CLsb = hist_sb.Integral(1,critBin_sb)/hist_sb.Integral()

    CLs = CLsb / CLb
    print "Critical Value for %s id %f" %(hist_sb.GetName(), lzCrit)
    print "CLs+b = %f" %CLsb
    print "CLb = %f" %CLb
    print "CLs = %f" %CLs

    return CLs


def getQdist(m0, m12, BoxName):

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

    for spbFile in glob.glob("/Users/maurizio/SIGNALMODELTOYS/LimitBkgSigToys_MR%s_R%s_mSUGRA_tanB10_M0-%s_M12-%s_%s_*.root" %(MR, R, m0, m12, BoxName)):
        input = rt.TFile.Open(spbFile)
        if FirstFile:
            critValueData  = input.Get("%s/Lz_%s" %(BoxName, BoxName)).get().getRealValue("LzData")
            FirstFile = False
        tSpB=input.Get("%s/myTree" %BoxName)
        tSpB.Draw('>>elistSpB','','entrylist')
        elistSpB = rt.gDirectory.Get('elistSpB')
        entry = -1;
        while True:
            entry = elistSpB.Next()
            if entry == -1: break
            tSpB.GetEntry(entry)
            lzValues_sb.append(tSpB.Lz)
        input.Close()

    for bFile in glob.glob("/Users/maurizio//SIGNALMODELTOYS/LimitBkgToys_MR%s_R%s_mSUGRA_tanB10_M0-%s_M12-%s_%s_*.root" %(MR, R, m0, m12, BoxName)):
        input = rt.TFile.Open(bFile)
        tB=input.Get("%s/myTree" %BoxName)
        tB.Draw('>>elistB','','entrylist')
        elistB = rt.gDirectory.Get('elistB')
        entry = -1;
        while True:
            entry = elistB.Next()
            if entry == -1: break
            tB.GetEntry(entry)
            lzValues_b.append(tB.Lz)

    #calculate the area integral of the distribution  
    lzValues_b.sort()
    lzValues_sb.sort()

    lzValuesSum_b = sum(map(abs,lzValues_b))
    lzValuesSum_sb = sum(map(abs,lzValues_sb))

    zMin_b = min(lzValues_b)
    zMax_b = max(lzValues_b)
    zMin_sb = min(lzValues_sb)
    zMax_sb = max(lzValues_sb)

    hSpB = rt.TH1D("SpB_%s"% BoxName, "SpB_%s"% BoxName, 200, min(zMin_sb,zMin_b), max(zMax_sb,zMax_b))
    hB = rt.TH1D("B_%s"% BoxName, "B_%s"% BoxName,200, min(zMin_sb,zMin_b), max(zMax_sb,zMax_b))

    for i in range(0, len(lzValues_sb)): hSpB.Fill(lzValues_sb[i])
    for i in range(0, len(lzValues_b)): hB.Fill(lzValues_b[i])

    return hSpB, hB, critValueData


def getCLs(m0, m12):
    
    histoSpB = []
    histoB = []
    
    # we store the boxes in the format [ Name, Q_data^box]
    Boxes = [["Mu", 0], ["Ele", 0], ["Had", 0]]
    
    # build the S+B and B-only distributions of Q = -log(L(S+B/L(B))
    minQ = 100000000000000
    maxQ = 0
    for Box in Boxes:
        BoxName = Box[0]
        THIShistoSpB, THIShistoB, Box[1] = getQdist(m0, m12, BoxName)
        histoSpB.append(THIShistoSpB)
        histoB.append(THIShistoB)
        
    # save histograms in ROOT file
    #pippo = rt.TFile.Open("outfile.root","recreate")
    #for hSpB in histoSpB: hSpB.Write()
    #for hB in histoB: hB.Write()
    #pippo.Close()
    #return 0
    # sample 10K toy results from the box-by-box distribution and
    # build the Q_tot = SUM_box Q_box
    lQspb = []
    lQb = []
    for i in range (0,10000):
        Qspb = 0
        Qb = 0
        for hSpB in histoSpB: Qspb = Qspb + hSpB.GetRandom()
        for hB in histoB: Qb = Qb + hB.GetRandom()
        lQspb.append(Qspb)
        lQb.append(Qb)

    lQspb.sort()
    lQb.sort()
    totalhistoSpB = rt.TH1D("SpB_TOTAL", "SpB_TOTAL", 400, min(min(lQspb),min(lQb)), max(max(lQspb),max(lQb)))
    totalhistoB = rt.TH1D("B_TOTAL", "B_TOTAL", 400, min(min(lQspb),min(lQb)), max(max(lQspb),max(lQb)))
    for i in range(0, len(lQspb)): totalhistoSpB.Fill(lQspb[i])
    for i in range(0, len(lQb)): totalhistoB.Fill(lQb[i])
    # critical value for combination
    Qtot = 0
    for Box in Boxes: Qtot = Qtot + Box[1]
    # built the TOTAL box
    Boxes.append(["Tot",Qtot])
    histoSpB.append(totalhistoSpB)
    histoB.append(totalhistoB)

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
    if len(Boxes) > 0: s.CL0 = calcCLs(histoSpB[0], histoB[0], Boxes[0][1])
    if len(Boxes) > 1: s.CL1 = calcCLs(histoSpB[1], histoB[1], Boxes[1][1])
    if len(Boxes) > 2: s.CL2 = calcCLs(histoSpB[2], histoB[2], Boxes[2][1])
    if len(Boxes) > 3: s.CL3 = calcCLs(histoSpB[3], histoB[3], Boxes[3][1])
    if len(Boxes) > 4: s.CL4 = calcCLs(histoSpB[4], histoB[4], Boxes[4][1])
    if len(Boxes) > 5: s.CL5 = calcCLs(histoSpB[5], histoB[5], Boxes[5][1])
    if len(Boxes) > 6: s.CL6 = calcCLs(histoSpB[6], histoB[6], Boxes[6][1])
    
    clTree.Fill()

    fileOut = rt.TFile.Open("CLs_m0_%s_m12_%s.root" %(m0, m12), "recreate")
    clTree.Write()
    for i in range(0, len(Boxes)):
        histoSpB[i].Write()
        histoB[i].Write()
    fileOut.Close()
    
if __name__ == '__main__':
    m0 = sys.argv[1]
    m12 = sys.argv[2]
    getCLs(m0, m12)
