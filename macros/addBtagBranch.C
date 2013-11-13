#include <iostream>
#include <cstdio>
#include <string>
#include <stdio.h>
#include <vector>
#include <map>
#include <fstream>
#include <sstream>
#include <unistd.h>
#include <algorithm>
#include <numeric>
#include <list>
#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TH3D.h>
#include <TString.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TProfile.h>
#include <TVector.h>
#include <TVector3.h>
#include <TLorentzVector.h>
#include <TTree.h>
#include <TBranch.h>
//#include <RooRealVar.h>
//#include <RooDataSet.h>
#include <TRandom3.h>
#include <TDatime.h>
#include <TLatex.h>
#include <TColor.h>
#include <TStyle.h>
#include <TMultiGraph.h>
#include <TGraphErrors.h>
#include <TGraph.h>
#include <TF1.h>
#include <TColorWheel.h>

using namespace std;
using namespace TMath;


struct EventIndex {
	int RunNumber;
	Long64_t EventNumber;
	
	EventIndex() : RunNumber(0), EventNumber(0) {}
	
	bool operator <(const EventIndex &other) const
	{
		if(RunNumber < other.RunNumber)
			return true;
		if(RunNumber > other.RunNumber)
			return false;
		
		if(EventNumber < other.EventNumber)
			return true;
		if(EventNumber > other.EventNumber)
			return false;
		
		return false;
	}
};


map<EventIndex, int> nomBtag;
map<EventIndex, int> upBtag;
map<EventIndex, int> downBtag;
map<EventIndex, int> rawBtag;

void InitEventFlag(char *s_Event);


void InitEventFlag(char *s_Event){
  ifstream inputfile(s_Event);
  string MODEL;
  int RUN_NUMBER;
  Long64_t EVENT_NUMBER;
  int btag_nom;
  int btag_up;
  int btag_down;
  int btag_raw;
  int btag_half;
  
  EventIndex index;
  
  cout << "Reading btag event list" << endl;
	
  while(!inputfile.eof()){
    inputfile >> MODEL >> RUN_NUMBER >> EVENT_NUMBER >> btag_raw >> btag_half >> btag_up >> btag_nom >> btag_down;
    
    index.RunNumber = RUN_NUMBER;
    index.EventNumber = EVENT_NUMBER;
    
    //cout << RUN_NUMBER << " " << EVENT_NUMBER << " " <<  btag_raw << " " << btag_half <<  " " << btag_up << " " << btag_nom << " " << btag_down << endl;
    
    if(index.RunNumber < 0 || index.EventNumber < 0)
      continue;
    
    nomBtag.insert( pair<EventIndex, int>(index, btag_nom));
    upBtag.insert( pair<EventIndex, int>(index, btag_up));
    downBtag.insert( pair<EventIndex, int>(index, btag_down));
    rawBtag.insert( pair<EventIndex, int>(index, btag_raw));

  }
}


void addBtagBranch()
{
  InitEventFlag("BTAG_LIST.txt");

  char Buffer[500];
  char MyRootFile[2000]; 
  ifstream *inputFile = new ifstream("FILE_LIST.txt");

  while(!inputFile->eof()){
    inputFile->getline(Buffer,500);
    if (!strstr(Buffer,"#") && !(strspn(Buffer," ") == strlen(Buffer)))
      {
	sscanf(Buffer,"%s",MyRootFile);
      }
    
    TFile file(MyRootFile,"update");
    TTree *tree = (TTree*) file.Get("EVENTS");
    
    Int_t nentries =  tree->GetEntries();
    Int_t RUN_NUM;
    Long64_t EVENT_NUM;
    Int_t btag_nom;
    Int_t btag_up;
    Int_t btag_down;
    Int_t btag_raw;
    
    TBranch *b_EVENT_NUM = tree->GetBranch("b_EVENT_NUM");
    TBranch *b_RUN_NUM = tree->GetBranch("b_RUN_NUM");
    
    TBranch *b_btag_nom = tree->Branch("btag_nom",&btag_nom,"btag_nom/I");
    TBranch *b_btag_up = tree->Branch("btag_up",&btag_up,"btag_up/I");
    TBranch *b_btag_down = tree->Branch("btag_down",&btag_down,"btag_down/I");
    TBranch *b_btag_raw = tree->Branch("btag_raw",&btag_raw,"btag_raw/I");
    
    tree->SetBranchStatus("EVENT_NUM",1);
    tree->SetBranchAddress("EVENT_NUM",&EVENT_NUM,&b_EVENT_NUM);
    tree->SetBranchStatus("RUN_NUM",1);
    tree->SetBranchAddress("RUN_NUM",&RUN_NUM,&b_RUN_NUM);
    
    cout << "total entries = " << nentries << endl;
    for (Int_t i=0; i<nentries; i++){
      tree->GetEntry(i);
      
      EventIndex index;
      index.EventNumber = EVENT_NUM;
      index.RunNumber = RUN_NUM;
      
      btag_nom = Min(3,nomBtag[index]);
      btag_up = Min(3,upBtag[index]);
      btag_down = Min(3,downBtag[index]);
      btag_raw = Min(3,rawBtag[index]);
      
      //tree->Fill();
      b_btag_nom->Fill();
      b_btag_up->Fill();
      b_btag_down->Fill();
      b_btag_raw->Fill();

      if(i%10000 == 0){
	cout << " : event = " << i << " / " << nentries << endl;
	cout << "nomBtag = " << btag_nom << endl;
	cout << "upBtag = " << btag_up << endl;
	cout << "downBtag = " << btag_down << endl;
	cout << "rawBtag = " << btag_raw << endl;
      }
    }
    //file = tree->GetCurrentFile(); //to get the pointer to the current file
    tree->Write("",TObject::kOverwrite);
    file.Close();
  }
}
