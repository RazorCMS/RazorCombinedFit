void compareFitResults(TString filename) {
  TFile* file = new TFile(filename);
  RooFitResult* fitResult[6];
  TString BoxName[6];
  TString MCSampleName;
  BoxName[0] = "MuMu";
  BoxName[1] = "MuEle";
  BoxName[2] = "Mu";
  BoxName[3] = "EleEle";
  BoxName[4] = "Ele";
  BoxName[5] = "Had";
  RooArgList finalPars[6];
  
  MCSampleName = filename.Remove(filename.Index("_"),filename.Length());
  for(int i = 0; i<6; i++) {
    fitResult[i]= (RooFitResult*) file->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[i] = fitResult[i]->floatParsFinal();    
  }    

  TH1D* histo[8];
  // loop over the parameters
  for(int j=0; j<8;j++) {
    RooRealVar* var = (RooRealVar*) fitResult[0]->floatParsFinal().at(j);
    TString parName(var.GetName());
    histo[j] = new TH1D(MCSampleName+"_"+parName, MCSampleName+"_"+parName, 6, 0, 6);
    // fill the histogram
    for(int i=0;i<6;i++) {
      histo[j]->GetXaxis()->SetBinLabel(i+1, BoxName[i]);   
      printf("MINUIT covQual code: %i\n",fitResult[i]->covQual());
      if (fitResult[i]->covQual() != 3) continue;
      histo[j]->SetBinContent(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getVal());
      histo[j]->SetBinError(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getError());
    }
  }
  
  TFile* outFile = new TFile("output.root","update");
  for(int j=0; j<8;j++) {
    histo[j]->Write();
  }
  outFile->Close();
}
