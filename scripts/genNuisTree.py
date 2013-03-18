import ROOT as rt
import math, os

if __name__ == '__main__':
    fileOut = rt.TFile.Open("NuisanceTree_multijet.root","recreate")

    rt.gROOT.ProcessLine("struct MyStruct{Int_t nToy; Double_t eff_prime; Double_t lumi_prime; Double_t xJes_prime; Double_t xPdf_prime; Double_t xBtag_prime; Double_t n2nd_TTj_prime;};")
    nuisTree = rt.TTree("nuisTree","nuisTree")

    from ROOT import MyStruct
    s = MyStruct()

    nuisTree.Branch("nToy", rt.AddressOf(s, "nToy"), 'nToy/I')
    nuisTree.Branch("eff_prime", rt.AddressOf(s, "eff_prime"), 'eff_prime/D')
    nuisTree.Branch("lumi_prime", rt.AddressOf(s, "lumi_prime"), 'lumi_prime/D')
    nuisTree.Branch("xJes_prime", rt.AddressOf(s, "xJes_prime"), 'xJes_prime/D')
    nuisTree.Branch("xPdf_prime", rt.AddressOf(s, "xPdf_prime"), 'xPdf_prime/D')
    nuisTree.Branch("xBtag_prime", rt.AddressOf(s, "xBtag_prime"), 'xBtag_prime/D')
    nuisTree.Branch("n2nd_TTj_prime", rt.AddressOf(s, "n2nd_TTj_prime"), 'n2nd_TTj_prime/D')

    for i in range(0,10000):
        pid = os.getpid()
        now = rt.TDatime()
        today = now.GetDate()
        clock = now.GetTime()
        seed = today+clock+pid+137+i
        gRnd = rt.TRandom3(seed)

        s.nToy = i
        s.eff_prime = gRnd.Gaus(0., 1.)
        s.lumi_prime = gRnd.Gaus(0., 1.)
        s.xJes_prime = gRnd.Gaus(0., 1.)
        s.xPdf_prime = gRnd.Gaus(0., 1.)
        s.xBtag_prime = gRnd.Gaus(0., 1.)
        s.n2nd_TTj_prime = gRnd.Gaus(0., 1.)

        nuisTree.Fill()

    nuisTree.Write()
    fileOut.Close()
