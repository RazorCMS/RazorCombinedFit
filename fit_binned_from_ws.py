"""Quickly fit the binned pdf in the workspace for combine"""
import ROOT as rt
import sys
import RootTools

if __name__ == "__main__":
    # rt.gSystem.Load("lib/libRazor.so")
    rt.gSystem.Load("../../lib/slc5_amd64_gcc472/libHiggsAnalysisCombinedLimit.so")
    FILE_NAME = sys.argv[1]
    ROOT_FILE = rt.TFile.Open(FILE_NAME)
    ws = ROOT_FILE.Get("wBJetLS")

    # Get normalizations
    N_tot_ttj1 = ws.var("Ntot_TTj1b_BJetLS")
    N_tot_ttj2 = ws.var("Ntot_TTj2b_BJetLS")
    f3 = ws.var("f3_TTj2b_BJetLS")
    N2 = N_tot_ttj2.getVal()
    N_tot_ttj2.setVal(N2 * (1.0 - f3.getVal()))
    N_tot_ttj3 = rt.RooRealVar("Ntot_TTj3b_BJetLS", "Ntot_TTj3b_BJetLS",
                               N2 * f3.getVal())
    N_tot_vpj = ws.var("Ntot_Vpj_BJetLS")

    # Get pdf's
    pdfs = ws.allPdfs()
    tt1 = pdfs.find("BJetLS_TTj1b")
    tt2 = pdfs.find("BJetLS_TTj2b")
    tt3 = pdfs.find("BJetLS_TTj3b")
    vpj = pdfs.find("BJetLS_Vpj")
    vpj.Print()

    binned_pdf = rt.RooAddPdf("binned_pdf", "binned_pdf",
                              rt.RooArgList(tt1, tt2, tt3, vpj),
                              rt.RooArgList(N_tot_ttj1, N_tot_ttj2,
                                            N_tot_ttj3, N_tot_vpj))

    data = ws.data("data_obs")
    data.Print()

    fr = binned_pdf.fitTo(data, rt.RooFit.Save(True))
    # print "Parameters before fit"
    # fr.floatParsInit().Print("s")
    # print "Parameters after fit"
    fr.floatParsFinal().Print("v")
    print "Status:", fr.status()
    print "Cov Qual:", fr.covQual()
    print "edm:", fr.edm()

    th1x = ws.var("th1x")
    fframe = th1x.frame()
    data.plotOn(fframe)
    binned_pdf.plotOn(fframe)
    c1 = rt.TCanvas()
    fframe.Draw()
    c1.Print("wtf.png")

    OUT_FILE = rt.TFile.Open("binned_fit_output.root", 'RECREATE')
    fr.Write()
    c1.Write()
    OUT_FILE.Close()
