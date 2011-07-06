void compareFitresults(TString filename) {
  
  TFile* file = new TFile(filename);
  RooFitResult* fitResult[6];
  TString BoxName[6];
  BoxName[0] = "MuMu";
  BoxName[1] = "MuEle";
  BoxName[2] = "Mu";
  BoxName[3] = "EleEle";
  BoxName[4] = "Ele";
  BoxName[5] = "Had";
  RooArgList finalPars[6];

  for(int i = 0; i<6; i++) {
    fitResult[i]= (RooFitResult*) file->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[i] = fitResult[i]->floatParsFinal();
  }    

  TH1D* histo[8];
  // loop over the parameters
  for(int j=0; j<8;j++) {
    RooRealVar* var = (RooRealVar*) fitResult[0]->floatParsFinal().at(j);
    TString parName(var.GetName());
    histo[j] = new TH1D(parName, parName, 6, 0, 6);
    // fill the hitogram
    for(int i=0;i<6;i++) {
      histo[j]->GetXaxis()->SetBinLabel(i+1, BoxName[i]);
      histo[j]->SetBinContent(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getVal());
      histo[j]->SetBinError(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getError());
    }
  }

  TFile* outFile = new TFile("output.root","recreate");
  for(int j=0; j<8;j++) {
    histo[j]->Write();
  }
  outFile->Close();
}
