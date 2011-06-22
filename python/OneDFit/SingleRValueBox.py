from RazorCombinedFit.Framework import Box
import RootTools
import ROOT as rt

class SingleRValueBox(Box.Box):
    
    def __init__(self, name, variables):
        super(SingleRValueBox,self).__init__(name, variables)
        
    def defineCpp(self, inputFile, cuts):
        """Call Yi's C++ code directly"""
        
        rcuts = cuts.get('rcuts',[])
        rcuts.sort()
        
        rcuts_vec = rt.std.vector('double')()
        for r in rcuts:
            rcuts_vec.push_back(rt.Double(r))
            
        from ROOT import OneDFitFromYi
        yiFit = OneDFitFromYi(self.workspace,OneDFitFromYi.Strategy_Normal)
        yiFit.define(inputFile, rcuts_vec)
        
        self.workspace.Print("V")
        
    def define(self, inputFile, cuts):
        
        if cuts.get('useC++',False):
            return self.defineCpp(inputFile, cuts)
        
        rcuts = cuts.get('rcuts',[])
        rcuts.sort()
        
        if len(rcuts) < 1:
            self.workspace.factory("RooTwoSideGaussianWithAnExponentialTail::fitmodel(MR,X0[0,400],SigmaL[0,500],SigmaR[0,500],S[0,0.5])")
        else:
            
            #get the dataset to play with
            reduce = cuts.get('reduce',None)
            data = RootTools.getDataSet(inputFile,'RMRTree', reduce)
            
            #our parameters of interest
            self.workspace.factory('A[0,0.1]')
            self.workspace.factory('B[0,0.1]')
            
            nrcuts = len(rcuts)
            
            #the full blooded fit from Yi
            for i in xrange(nrcuts):
                
                #estimate the bin yield to help the fit
                cut = 'R > %f' % rcuts[i]
                if(i != len(rcuts) -1):
                    cut = '%s && R <= %f' % (cut, rcuts[i+1])
                guessYield = data.reduce(rt.RooFit.Cut(cut)).sumEntries()
                
                #create the yield variables
                print 'Yield guessed for bin %d is %d' % (i, guessYield)
                self.workspace.factory('SingleBinYield_%d[%d,0,%d]' % (i,guessYield,guessYield*10) )
                
                #now add the PDF
                self.workspace.factory("""RooTwoSideGaussianWithAnExponentialTail::Model_%(index)d(
                    MR,
                    X0_%(index)d[0,400],
                    SigmaL_%(index)d[0,500],
                    SigmaR_%(index)d[50,0,500],
                    expr::S_%(index)d('@0 + %(r2)f * @1',A,B)
                    )""" % {'index':i,'r2':rcuts[i]*rcuts[i]}
                ) 
                
            # the yields need to be in a seperate loop so everything is defined
            for i in reversed(xrange(nrcuts)):
                if(i == nrcuts -1):
                    #last bin
                    self.workspace.factory("expr::Yield_%d('@0',SingleBinYield_%d)" % (i,i))
                else:
                    self.workspace.factory("expr::Yield_%d('@0 + @1',Yield_%d,SingleBinYield_%d)" % (i,i+1,i))
                self.workspace.factory("expr::NYield_%d('-@0',Yield_%d)" % (i,i))
            
            for i in xrange(nrcuts):
                if(i == nrcuts -1):
                    self.workspace.factory("RooAtLeast::Constraint_%d(R,RooConstVar(%f))" % (i,rcuts[i]))
                    self.workspace.factory("PROD::TopLevelModel_%d)")
                    
                else:
                    self.workspace.factory("expr::NormalizedYield_%d('@0 / (@0 - @1)',Yield_%d,Yield_%d)" % (i,i,i+1) ) 
                    self.workspace.factory("expr::NormalizedNegativeYield_%d('-@0 / (@0 - @1)',Yield_%d,Yield_%d)" % (i,i,i+1) ) 
                    
                    self.workspace.factory("SUM::ModelBeforeConstraint_%d(NormalizedYield_%d*Model_%d,NormalizedNegativeYield_%d*Model_%d)" % (i,i,i,i,i+1))
                
                    self.workspace.factory("RooSameAs::Constraint_%d(R,RooConstVar(%f),RooConstVar(%f))" % (i,0.5*(rcuts[i+1]+rcuts[i]),0.5*(rcuts[i+1]-rcuts[i])) )
            
                
#                
#     if(i == RCuts.size() - 1)
#         ModelBeforeConstraint.push_back(Models[i]);
#      else
#         ModelBeforeConstraint.push_back(new RooAddPdf(Form("ModelBeforeConstraint_%d", i),
#            Form("Model before constraint (bin %d)", i), RooArgList(*Models[i], *Models[i+1]),
#            RooArgList(*NormalizedYields[i], *NormalizedNegativeYields[i])));
#
#      if(i == RCuts.size() - 1)
#         Constraint.push_back(new RooAtLeast(Form("Constraint_%d", i), "Last bin constraint", R, RCuts[i]));
#      else
#         Constraint.push_back(new RooSameAs(Form("Constraint_%d", i),
#            Form("Constraint R = %f - %f", RCuts[i], RCuts[i+1]), R,
#            (RCuts[i+1] + RCuts[i]) / 2, (RCuts[i+1] - RCuts[i]) / 2));
#
#      if(i == RCuts.size() - 1)
#         TopLevelModels.push_back(new RooProdPdf(Form("TopLevelModel_%d", i),
#            Form("Top level model for bin with R > %f", RCuts[i]),
#            RooArgList(*ModelBeforeConstraint[i], *Constraint[i])));
#      else
#         TopLevelModels.push_back(new RooProdPdf(Form("TopLevelModel_%d", i),
#            Form("Top level model for bin with R = %f - %f", RCuts[i], RCuts[i+1]),
#            RooArgList(*ModelBeforeConstraint[i], *Constraint[i])));
#
#      if(i == RCuts.size() - 1)
#         TopLevelYields.push_back(Yields[i]);
#      else
#         TopLevelYields.push_back(new RooFormulaVar(Form("BinYield_%d", i), "Bin yield variable",
#            "@0 - @1", RooArgList(*Yields[i], *Yields[i+1])));
                


                    

            
        
        

