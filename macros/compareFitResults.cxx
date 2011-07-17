void compareFitResultsZ() {
  RooFitResult* fitResult[8];
  TString BoxName[4];
  TString MCSampleName;
  BoxName[0] = "Mu";
  BoxName[1] = "Ele";
  BoxName[2] = "MuMu";
  BoxName[3] = "EleEle";
  RooArgList finalPars[8];

  TFile* file[8];
  for(int i=0; i<4; i++) {
    char name[256];
    sprintf(name, "ZjetsFITS/razor_output_Zll_%s.root",BoxName[i].Data());
    file[2*i]  = new TFile(name);
    sprintf(name, "ZjetsFITS/razor_output_Zll_0btag_%s.root",BoxName[i].Data());
    file[2*i+1] = new TFile(name);
  }
  
  for(int i = 0; i<4; i++) {
    fitResult[2*i]   = (RooFitResult*) file[2*i]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[2*i] = fitResult[2*i]->floatParsFinal();    
    fitResult[2*i+1]   = (RooFitResult*) file[2*i+1]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[2*i+1] = fitResult[2*i+1]->floatParsFinal();    
  }

  TCanvas* c1 = new TCanvas("c1", "c1", 1600, 900);

  TH1D* histo[8];
  // loop over the parameters
  for(int j=0; j<8;j++) {
    RooRealVar* var = (RooRealVar*) fitResult[0]->floatParsFinal().at(j);
    TString parName(var.GetName());
    histo[j] = new TH1D(MCSampleName+"_"+parName, MCSampleName+"_"+parName, 8, 0, 8);
    histo[j]->GetYaxis()->SetTitle(parName);
    // fill the histogram
    for(int i=0;i<4;i++) {
      histo[j]->GetXaxis()->SetBinLabel(2*i+1, BoxName[i]+" All");   
      histo[j]->GetXaxis()->SetBinLabel(2*i+2, BoxName[i]+" NoBTag");   
    }
    for(int i=0;i<8;i++) {
      printf("MINUIT covQual code: %i\n",fitResult[i]->covQual());
      if (fitResult[i]->covQual() != 3) continue;
      histo[j]->SetBinContent(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getVal());
      histo[j]->SetBinError(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getError());
    }
    histo[j]->Draw();
    c1->SaveAs(parName+".pdf");
  }
  
  TFile* outFile = new TFile("output.root","update");
  for(int j=0; j<8;j++) {
    histo[j]->Write();
  }
  outFile->Close();
}


void compareFitResultsW() {
  RooFitResult* fitResult[4];
  TString BoxName[2];
  TString MCSampleName;
  BoxName[0] = "Mu";
  BoxName[1] = "Ele";
  RooArgList finalPars[4];

  TFile* file[4];
  for(int i=0; i<2; i++) {
    char name[256];
    sprintf(name, "WjetsFITS/razor_output_Wln_%s.root",BoxName[i].Data());
    file[2*i]  = new TFile(name);
    sprintf(name, "WjetsFITS/razor_output_Wln_0btag_%s.root",BoxName[i].Data());
    file[2*i+1] = new TFile(name);
  }
  
  for(int i = 0; i<2; i++) {
    fitResult[2*i]   = (RooFitResult*) file[2*i]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[2*i] = fitResult[2*i]->floatParsFinal();    
    fitResult[2*i+1]   = (RooFitResult*) file[2*i+1]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[2*i+1] = fitResult[2*i+1]->floatParsFinal();    
  }

  TCanvas* c1 = new TCanvas("c1", "c1", 1600, 900);

  TH1D* histo[8];
  // loop over the parameters
  for(int j=0; j<8;j++) {
    RooRealVar* var = (RooRealVar*) fitResult[0]->floatParsFinal().at(j);
    TString parName(var.GetName());
    histo[j] = new TH1D(MCSampleName+"_"+parName, MCSampleName+"_"+parName, 4, 0, 4);
    histo[j]->GetYaxis()->SetTitle(parName);
    // fill the histogram
    for(int i=0;i<2;i++) {
      histo[j]->GetXaxis()->SetBinLabel(2*i+1, BoxName[i]+" All");   
      histo[j]->GetXaxis()->SetBinLabel(2*i+2, BoxName[i]+" NoBTag");   
    }
    for(int i=0;i<4;i++) {
      printf("MINUIT covQual code: %i\n",fitResult[i]->covQual());
      if (fitResult[i]->covQual() != 3) continue;
      histo[j]->SetBinContent(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getVal());
      histo[j]->SetBinError(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getError());
    }
    histo[j]->Draw();
    c1->SaveAs(parName+".pdf");
  }
  
  TFile* outFile = new TFile("output.root","update");
  for(int j=0; j<8;j++) {
    histo[j]->Write();
  }
  outFile->Close();
}

void compareFitResultsT() {
  RooFitResult* fitResult[15];
  TString BoxName[5];
  TString MCSampleName;
  BoxName[0] = "Mu";
  BoxName[1] = "Ele";
  BoxName[2] = "MuMu";
  BoxName[3] = "MuEle";
  BoxName[4] = "EleEle";
  RooArgList finalPars[15];

  TFile* file[15];
  for(int i=0; i<5; i++) {
    char name[256];
    sprintf(name, "TTbarFITS/razor_output_TTbar_0bTag%s.root",BoxName[i].Data());
    file[3*i]  = new TFile(name);
    sprintf(name, "TTbarFITS/razor_output_TTbar_1bTag_%s.root",BoxName[i].Data());
    file[3*i+1] = new TFile(name);
    sprintf(name, "TTbarFITS/razor_output_TTbar_2bTag_%s.root",BoxName[i].Data());
    file[3*i+2] = new TFile(name);
  }
  
  for(int i = 0; i<5; i++) {
    fitResult[3*i]   = (RooFitResult*) file[3*i]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[3*i] = fitResult[3*i]->floatParsFinal();   
    fitResult[3*i+1]   = (RooFitResult*) file[3*i+1]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[3*i+1] = fitResult[3*i+1]->floatParsFinal();    
    fitResult[3*i+2]   = (RooFitResult*) file[3*i+2]->Get(BoxName[i]+"/fitresult_fitmodel_RMRTree");
    finalPars[3*i+2] = fitResult[3*i+2]->floatParsFinal();    
  }

  TCanvas* c1 = new TCanvas("c1", "c1", 1600, 900);

  TH1D* histo[8];
  // loop over the parameters
  for(int j=0; j<8;j++) {
    RooRealVar* var = (RooRealVar*) fitResult[0]->floatParsFinal().at(j);
    TString parName(var.GetName());
    histo[j] = new TH1D(MCSampleName+"_"+parName, MCSampleName+"_"+parName, 15, 0, 15);
    histo[j]->GetYaxis()->SetTitle(parName);
    // fill the histogram
    for(int i=0;i<5;i++) {
      histo[j]->GetXaxis()->SetBinLabel(3*i+1, BoxName[i]+" 0bTag");   
      histo[j]->GetXaxis()->SetBinLabel(3*i+2, BoxName[i]+" 1bTag");   
      histo[j]->GetXaxis()->SetBinLabel(3*i+4, BoxName[i]+" 2bTag");   
    }
    for(int i=0;i<15;i++) {
      printf("MINUIT covQual code: %i\n",fitResult[i]->covQual());
      if (fitResult[i]->covQual() != 3) continue;
      histo[j]->SetBinContent(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getVal());
      histo[j]->SetBinError(i+1, ((RooRealVar*) fitResult[i]->floatParsFinal()->find(parName))->getError());
    }
    histo[j]->Draw();
    c1->SaveAs(parName+".pdf");
  }
  
  TFile* outFile = new TFile("output.root","update");
  for(int j=0; j<8;j++) {
    histo[j]->Write();
  }
  outFile->Close();
}
