#include "TF1.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TColor.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TLegend.h"
#include "TCanvas.h"

#include "RooConstVar.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooTwoSideGaussianWithAnExponentialTail.h"
#include "RooPlot.h"
#include "RooArgSet.h"
#include "RooFormulaVar.h"
#include "RooFitResult.h"
#include "RooAddPdf.h"
#include "RooProdPdf.h"
#include "RooSameAs.h"
#include "RooAtLeast.h"
#include "RooAbsPdf.h"
#include "RooExponential.h"
using namespace RooFit;

#include "OneDFitFromYi.h"

#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

ClassImp(OneDFitFromYi);

OneDFitFromYi::OneDFitFromYi():
	workspace_(new RooWorkspace()),strategy_(OneDFitFromYi::Strategy_Normal){
}

OneDFitFromYi::OneDFitFromYi(RooWorkspace* workspace, const int strategy):
	workspace_(workspace),strategy_(strategy){
}

OneDFitFromYi::~OneDFitFromYi() {
}

OneDFitFromYi::SingleFitResult OneDFitFromYi::FitWithRCut(
		const std::string& Filename, double RCut, const int Strategy) {

	TFile F(Filename.c_str());
	RooDataSet *Tree = dynamic_cast<RooDataSet*>(F.Get("RMRTree"));
	if (!Tree)
		return OneDFitFromYi::SingleFitResult();

	std::cout << "OneDFitFromYi::FitWithRCut: " << RCut << " --- " << Strategy << std::endl;
	if (Strategy != Strategy_Normal && Strategy != Strategy_IgnoreLeft&& Strategy != Strategy_IgnoreGaussian){
		std::cerr << "Unknown stratagy in OneDFitFromYi::FitWithRCut: " << Strategy << std::endl;
		return SingleFitResult();
	}

	RooRealVar* MR = dynamic_cast<RooRealVar*>(workspace_->arg("MR"));
	RooRealVar* R = dynamic_cast<RooRealVar*>(workspace_->arg("R"));
	if( !MR || !R ){
		std::cerr << "MR or R not defined in config. Exiting..." << std::endl;
		return SingleFitResult();
	}
	double MRLowerBound = MR->getMin();

	RooArgSet TreeVarSet(*MR, *R);
	RooDataSet Dataset("Dataset", "MR Dataset",TreeVarSet,Import(*Tree),Cut(Form("R > %f", RCut)));

	RooRealVar X0("X0", "gaussian mean", 150, 0, 5000, "GeV");
	RooRealVar SigmaL("SigmaL", "left-hand side gaussian width", 50, 0, 5000,
			"GeV");
	RooRealVar SigmaR("SigmaR", "right-hand side gaussian width", 50, 0, 5000,
			"GeV");
	RooRealVar S("S", "exponent of the tail", 0.01, 0, 0.5);
	RooFormulaVar NegativeS("NegativeS", "Negative S", "-S", RooArgList(S));
	RooAbsPdf *Model = NULL;
	if (Strategy == Strategy_Normal)
		Model = new RooTwoSideGaussianWithAnExponentialTail("Model", "Model",
				*MR, X0, SigmaL, SigmaR, S);
	else if (Strategy == Strategy_IgnoreLeft)
		Model = new RooTwoSideGaussianWithAnExponentialTail("Model", "Model",
				*MR, X0, SigmaR, SigmaR, S);
	else if (Strategy == Strategy_IgnoreGaussian)
		Model = new RooExponential("Model", "Model", *MR, NegativeS);

	if (Model == NULL) {
		std::cerr
				<< "Something terribly wrong has happened.  Model is NULL.  Please check."
				<< std::endl;
		return SingleFitResult();
	}

	RooFitResult* fr = Model->fitTo(Dataset, Save(true));
	std::cout << "OneDFitFromYi::FitWithRCut fit result with R=" << RCut << std::endl;
	fr->Print("V");

	SingleFitResult result;
	result.Quality = fr->covQual();
	result.Status = fr->status();
	if(result.Quality != 3 || result.Status != 0){
		std::cerr << "WARNING:: The fit did not converge cleanly." << std::endl;
	}
	workspace_->import(*fr,Form("SingleFitResult_r%f",RCut));

	double SafetyMargin = 0;

	if (Strategy == Strategy_Normal) {
		double XC = S.getVal() * SigmaR.getVal() * SigmaR.getVal()
				+ X0.getVal();

		if (MRLowerBound + SafetyMargin < X0.getVal()) {
			result.X0 = X0.getVal();
			result.X0Error = X0.getError();
			result.SigmaL = SigmaL.getVal();
			result.SigmaLError = SigmaL.getError();
			result.SigmaR = SigmaR.getVal();
			result.SigmaRError = SigmaR.getError();
			result.S = S.getVal();
			result.SError = S.getError();
			result.Strategy = Strategy;
		}

		if (MRLowerBound + SafetyMargin < XC && MRLowerBound + SafetyMargin
				>= X0.getVal())
			return FitWithRCut(Filename, RCut, Strategy_IgnoreLeft);
		if (MRLowerBound + SafetyMargin >= XC)
			return FitWithRCut(Filename, RCut, Strategy_IgnoreGaussian);
	}

	if (Strategy == Strategy_IgnoreLeft) {
		double XC = S.getVal() * SigmaR.getVal() * SigmaR.getVal()
				+ X0.getVal();

		if (MRLowerBound + SafetyMargin < XC) {
			result.X0 = X0.getVal();
			result.X0Error = X0.getError();
			result.SigmaL = SigmaR.getVal();
			result.SigmaL = SigmaR.getError();
			result.SigmaR = SigmaR.getVal();
			result.SigmaR = SigmaR.getError();
			result.S = S.getVal();
			result.SError = S.getError();
			result.Strategy = Strategy;
		}

		if (MRLowerBound + SafetyMargin >= XC)
			return FitWithRCut(Filename, RCut, Strategy_IgnoreGaussian);
	}

	if (Strategy == Strategy_IgnoreGaussian) {
		result.X0 = -1000;
		result.X0Error = -1000;
		result.SigmaL = -1000;
		result.SigmaLError = -1000;
		result.SigmaR = -1000;
		result.SigmaRError = -1000;
		result.S = -NegativeS.getVal();
		result.SError = S.getError();
		result.Strategy = Strategy;
	}

	if (Model != NULL)
		delete Model;

	return result;

}

void OneDFitFromYi::define(const std::string& Filename, std::vector<double>& RCuts){

	if (RCuts.size() == 0)
		return;
	if (RCuts.size() == 1) {
		std::cout
				<< "OneDFitFromYi::define: If you want to fit with just one R-cut, use the easy version!"
				<< std::endl;
		return;
	}

	std::sort(RCuts.begin(), RCuts.end());

	std::vector<OneDFitFromYi::SingleFitResult> SingleFitResults;
	for (unsigned int i = 0; i < RCuts.size(); i++)
		SingleFitResults.push_back(FitWithRCut(Filename, RCuts[i],
				OneDFitFromYi::Strategy_IgnoreGaussian));
	// SingleFitResults.push_back(FitWithRCut(Filename, RCuts[i], Strategy_Normal));   // turning on core

	TGraphErrors SingleCentralValues;
	SingleCentralValues.SetNameTitle("SingleCentralValues",
			"Central values from single fits");
	for (unsigned int i = 0; i < RCuts.size(); i++) {
		SingleCentralValues.SetPoint(i, RCuts[i] * RCuts[i],
				SingleFitResults[i].S);
		SingleCentralValues.SetPointError(i, 0, SingleFitResults[i].SError);
	}

	TF1 InitialParameterValues("InitialParameterValues", "pol1");
	SingleCentralValues.Fit(&InitialParameterValues);
	InitialParameterValues.SetLineWidth(1);

	double ParameterAValue = InitialParameterValues.GetParameter(0);
	double ParameterBValue = InitialParameterValues.GetParameter(1);

	SingleCentralValues.SetLineWidth(1);
	SingleCentralValues.SetMarkerStyle(8);

	SingleCentralValues.SetLineWidth(2);
	SingleCentralValues.SetMarkerStyle(1);

	/*
	 vector<string> SingleFitParameterExplanation;
	 stringstream ParameterAString;
	 ParameterAString << "Parameter A from single fit: " << ParameterAValue << " +- "
	 << InitialParameterValues.GetParError(0);
	 SingleFitParameterExplanation.push_back(ParameterAString.str());
	 stringstream ParameterBString;
	 ParameterBString << "Parameter B from single fit: " << ParameterBValue << " +- "
	 << InitialParameterValues.GetParError(1);
	 SingleFitParameterExplanation.push_back(ParameterBString.str());
	 SingleFitParameterExplanation.push_back("Friendly reminder: s = a + b * (R cut)^2");
	 SingleFitParameterExplanation.push_back("Exponential part in the fit is exp(-s * MR)");
	 PsFile.AddTextPage(SingleFitParameterExplanation);
	 */

	TFile F(Filename.c_str());
	RooDataSet* Tree = dynamic_cast<RooDataSet*>(F.Get("RMRTree"));
	if (!Tree){
		std::cerr << "OneDFitFromYi::define: RooDataSet can not be read" << std::endl;
		return;
	}

	RooRealVar* MR = dynamic_cast<RooRealVar*>(workspace_->arg("MR"));
	RooRealVar* R = dynamic_cast<RooRealVar*>(workspace_->arg("R"));
	if( !MR || !R ){
		std::cerr << "OneDFitFromYi::define: MR or R not defined in config. Exiting..." << std::endl;
		return;
	}

	RooArgSet TreeVarSet(*MR, *R);
	RooDataSet Dataset("Dataset", "MR Dataset", TreeVarSet, Import(*Tree), Cut(Form("R > %f", RCuts[0])) );

	RooRealVar ParameterA("ParameterA", "s = \"a\" + b R^2", ParameterAValue,0, 0.1);
	RooRealVar ParameterB("ParameterB", "s = a + \"b\" R^2", ParameterBValue,0, 1);

	vector<RooRealVar *> X0;
	vector<RooRealVar *> SigmaL;
	vector<RooRealVar *> SigmaR;
	vector<RooFormulaVar *> S;
	vector<RooRealVar *> SingleBinYields;
	vector<RooFormulaVar *> Yields;
	vector<RooFormulaVar *> NegativeYields;
	vector<RooFormulaVar *> NormalizedYields;
	vector<RooFormulaVar *> NormalizedNegativeYields;

	vector<RooAbsPdf *> Models;

	for (unsigned int i = 0; i < RCuts.size(); i++) {
		double GuessYield = 0;
		if (i != RCuts.size() - 1)
			GuessYield
					= Dataset.reduce(Cut(Form(
							"R > %f && R <= %f", RCuts[i],
							RCuts[i + 1])))->sumEntries();
		else
			GuessYield
					= Dataset.reduce(Cut(Form("R > %f", RCuts[i])))->sumEntries();

		cout << "Guess yield for bin " << i << " is " << GuessYield << endl;

		SingleBinYields.push_back(new RooRealVar(Form("SingleBinYield_%d", i),
				Form("Yield with R in bin %d", i), GuessYield, 0, GuessYield
						* 10));
	}

	for (unsigned int i = 0; i < RCuts.size(); i++) {
		if (SingleFitResults[i].Strategy == Strategy_Normal) {
			X0.push_back(new RooRealVar(Form("X0_%d", i), Form(
					"gaussian mean, R > %f", RCuts[i]), SingleFitResults[i].X0,
					0, 400, "GeV"));
			// X0[i]->setError(SingleFitResults[i].X0Error * 5);
			SigmaL.push_back(new RooRealVar(Form("SigmaL_%d", i), Form(
					"left-hand side gaussian width, R > %f", RCuts[i]),
					SingleFitResults[i].SigmaL, 0, 500, "GeV"));
			// SigmaL[i]->setError(SingleFitResults[i].SigmaLError * 5);
			SigmaR.push_back(new RooRealVar(Form("SigmaR_%d", i), Form(
					"right-hand side gaussian width, R > %f", RCuts[i]),
					SingleFitResults[i].SigmaR, 0, 500, "GeV"));
			// SigmaR[i]->setError(SingleFitResults[i].SigmaRError * 5);
			S.push_back(new RooFormulaVar(Form("S_%d", i), Form(
					"exponent of the tail, R > %f", RCuts[i]), Form(
					"@0 + %f * @1", RCuts[i] * RCuts[i]), RooArgList(
					ParameterA, ParameterB)));

			Models.push_back(new RooTwoSideGaussianWithAnExponentialTail(Form(
					"Model_%d", i), Form("Model for R > %f", RCuts[i]), *MR,
					*X0[i], *SigmaL[i], *SigmaR[i], *S[i]));
		} else if (SingleFitResults[i].Strategy == Strategy_IgnoreLeft) {
			X0.push_back(new RooRealVar(Form("X0_%d", i), Form(
					"gaussian mean, R > %f", RCuts[i]), SingleFitResults[i].X0,
					0, 500, "GeV"));
			X0[i]->setError(SingleFitResults[i].X0Error * 5);
			SigmaL.push_back(NULL);
			SigmaR.push_back(new RooRealVar(Form("SigmaR_%d", i), Form(
					"right-hand side gaussian width, R > %f", RCuts[i]),
					SingleFitResults[i].SigmaR, 0, 1000, "GeV"));
			SigmaR[i]->setError(SingleFitResults[i].SigmaRError * 5);
			S.push_back(new RooFormulaVar(Form("S_%d", i), Form(
					"exponent of the tail, R > %f", RCuts[i]), Form(
					"@0 + %f * @1", RCuts[i] * RCuts[i]), RooArgList(
					ParameterA, ParameterB)));

			Models.push_back(new RooTwoSideGaussianWithAnExponentialTail(Form(
					"Model_%d", i), Form("Model for R > %f", RCuts[i]), *MR,
					*X0[i], *SigmaR[i], *SigmaR[i], *S[i]));
		} else // if SingleFitResults[i].Strategy == Strategy_IgnoreGaussian
		{
			X0.push_back(NULL);
			SigmaL.push_back(NULL);
			SigmaR.push_back(NULL);
			S.push_back(new RooFormulaVar(Form("S_%d", i), Form(
					"exponent of the tail, R > %f", RCuts[i]), Form(
					"-1 * @0 - %f * @1", RCuts[i] * RCuts[i]), RooArgList(
					ParameterA, ParameterB)));

			Models.push_back(new RooExponential(Form("Model_%d", i), Form(
					"Model for R > %f", RCuts[i]), *MR, *S[i]));
		}
	}

	Yields.push_back(new RooFormulaVar(Form("Yield_%lu", RCuts.size() - 1),
			"Last bin yield", "@0", RooArgList(
					*SingleBinYields[SingleBinYields.size() - 1])));
	for (int i = RCuts.size() - 1 - 1; i >= 0; i--)
		Yields.push_back(new RooFormulaVar(Form("Yield_%d", i), Form(
				"Yield with R above %f", RCuts[i]), "@0 + @1", RooArgList(
				*Yields[Yields.size() - 1], *SingleBinYields[i])));
	reverse(Yields.begin(), Yields.end());

	for (unsigned int i = 0; i < RCuts.size(); i++)
		cout << "Yields[" << i << "] has initial value " << Yields[i]->getVal()
				<< endl;

	for (unsigned int i = 0; i < RCuts.size(); i++)
		NegativeYields.push_back(new RooFormulaVar(Form("NYield_%d", i),
				"Negative yield", "-1 * @0", RooArgList(*Yields[i])));

	for (unsigned int i = 0; i < RCuts.size() - 1; i++) {
		NormalizedYields.push_back(new RooFormulaVar(Form("NormalizedYield_%d",
				i), "Yield", "@0 / (@0 - @1)", RooArgList(*Yields[i], *Yields[i
				+ 1])));
		NormalizedNegativeYields.push_back(new RooFormulaVar(Form(
				"NormalizedNegativeYield_%d", i), "Yield", "-@1 / (@0 - @1)",
				RooArgList(*Yields[i], *Yields[i + 1])));

		// NormalizedYields.push_back(new RooFormulaVar(Form("NormalizedYield_%d", i),
		//    "Yield", "@0", RooArgList(*Yields[i], *Yields[i+1])));
		// NormalizedNegativeYields.push_back(new RooFormulaVar(Form("NormalizedNegativeYield_%d", i),
		//    "Yield", "-@1", RooArgList(*Yields[i], *Yields[i+1])));
	}

	vector<RooAbsPdf *> ModelBeforeConstraint;
	vector<RooAbsPdf *> Constraint;
	vector<RooAbsPdf *> TopLevelModels;
	vector<RooAbsReal *> TopLevelYields;

	RooArgList ModelList;
	RooArgList YieldList;

	for (unsigned int i = 0; i < RCuts.size(); i++) // ps. last bin is special
	{
		if (i == RCuts.size() - 1)
			ModelBeforeConstraint.push_back(Models[i]);
		else
			ModelBeforeConstraint.push_back(new RooAddPdf(Form(
					"ModelBeforeConstraint_%d", i), Form(
					"Model before constraint (bin %d)", i), RooArgList(
					*Models[i], *Models[i + 1]), RooArgList(
					*NormalizedYields[i], *NormalizedNegativeYields[i])));

		if (i == RCuts.size() - 1)
			Constraint.push_back(new RooAtLeast(Form("Constraint_%d", i),
					"Last bin constraint", *R, RooConst(RCuts[i])));
		else
			Constraint.push_back(new RooSameAs(Form("Constraint_%d", i), Form(
					"Constraint R = %f - %f", RCuts[i], RCuts[i + 1]), *R,
					RooConst((RCuts[i + 1] + RCuts[i]) / 2), RooConst((RCuts[i
							+ 1] - RCuts[i]) / 2)));

		if (i == RCuts.size() - 1)
			TopLevelModels.push_back(new RooProdPdf(
					Form("TopLevelModel_%d", i), Form(
							"Top level model for bin with R > %f", RCuts[i]),
					RooArgList(*ModelBeforeConstraint[i], *Constraint[i])));
		else
			TopLevelModels.push_back(new RooProdPdf(
					Form("TopLevelModel_%d", i), Form(
							"Top level model for bin with R = %f - %f",
							RCuts[i], RCuts[i + 1]), RooArgList(
							*ModelBeforeConstraint[i], *Constraint[i])));

		if (i == RCuts.size() - 1)
			TopLevelYields.push_back(Yields[i]);
		else
			TopLevelYields.push_back(new RooFormulaVar(Form("BinYield_%d", i),
					"Bin yield variable", "@0 - @1", RooArgList(*Yields[i],
							*Yields[i + 1])));

		// if(i == RCuts.size() - 1)
		//    TopLevelYields.push_back(Yields[i]);
		// else
		//    TopLevelYields.push_back(new RooRealVar(Form("DummyYield_%d", i), "Dummy variable", 1));

		ModelList.add(*TopLevelModels[i]);
		YieldList.add(*TopLevelYields[i]);
	}

	RooAddPdf FinalModel("fitmodel", "Final model!", ModelList, YieldList);
	workspace_->import(FinalModel);

	//RooFitResult *FitResult = FinalModel.fitTo(Dataset, Save(true),PrintEvalErrors(-1), NumCPU(3));

	// Cleaning....
	for (unsigned int i = 0; i < RCuts.size(); i++) {
		delete TopLevelModels[i];
		if (i != RCuts.size() - 1)
			delete ModelBeforeConstraint[i];
		delete Constraint[i];
		if (i != RCuts.size() - 1)
			delete TopLevelYields[i];

		if (i != RCuts.size() - 1) {
			delete NormalizedYields[i];
			delete NormalizedNegativeYields[i];
		}

		if (Models[i] != NULL)
			delete Models[i];
		if (Yields[i] != NULL)
			delete Yields[i];
		if (S[i] != NULL)
			delete S[i];
		if (SigmaR[i] != NULL)
			delete SigmaR[i];
		if (SigmaL[i] != NULL)
			delete SigmaL[i];
		if (X0[i] != NULL)
			delete X0[i];
	}

	TopLevelModels.clear();
	ModelBeforeConstraint.clear();
	Constraint.clear();
	TopLevelYields.clear();

	NormalizedYields.clear();
	NormalizedNegativeYields.clear();

	Models.clear();
	Yields.clear();
	S.clear();
	SigmaR.clear();
	SigmaL.clear();
	X0.clear();

}
