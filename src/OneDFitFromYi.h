#ifndef ONEDFITFROMYI_H_
#define ONEDFITFROMYI_H_

#include "RooWorkspace.h"
#include "TObject.h"

#include <string>
#include <vector>

class OneDFitFromYi : public TObject{
	/**
	 * This class is a straight copy and paste from Yi's
	 * C++ code (see FitMRDistribution_Cleaned.cc
	 *
	 * However, we make it callable from python
	 */

public:
	OneDFitFromYi();
	OneDFitFromYi(RooWorkspace* workspace, const int strategy);
	virtual ~OneDFitFromYi();
	void define(const std::string& fileName, std::vector<double>& rCuts);

	static const int Strategy_Normal=100;
	static const int Strategy_IgnoreLeft=101;
	static const int Strategy_IgnoreGaussian=102;

	struct SingleFitResult{
	public:
		double X0;
		double X0Error;
		double SigmaL;
		double SigmaLError;
		double SigmaR;
		double SigmaRError;
		double S;
		double SError;
		int Strategy;
		int Status;
		int Quality;
		SingleFitResult():
			X0(0),X0Error(0),
			SigmaL(0),SigmaLError(0),
			SigmaR(0),SigmaRError(0),
			S(0),SError(0),
			Strategy(Strategy_Normal),
			Status(-1),
			Quality(-1){
		}
	};

private:

	SingleFitResult FitWithRCut(const std::string& fileName, double rCut, const int strategy);

	RooWorkspace* workspace_;
	const int strategy_;

	ClassDef(OneDFitFromYi,1);
};

#endif /* ONEDFITFROMYI_H_ */
