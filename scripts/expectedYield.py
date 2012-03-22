from optparse import OptionParser
import ROOT as rt
import sys
from RazorCombinedFit.Framework import Config

def defineParser():
    
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default=None,
                  help="Name of the config file to use")
    parser.add_option('--box',dest="box",type="string",default='Had',
                  help="Name of the box to use when reading the config")
    parser.add_option('--scale-lumi',dest="scale_lumi",type="int", default=1,
                  help="The lumi scale factor used when genrating the toys")
    parser.add_option('-o','--output',dest="output",type="string", default='expected_Had.root',
                  help="Name of the root file to store everything in")
    parser.add_option('--options',dest="options", default=False,action='store_true',
                  help="Use the options parser output")
    parser.add_option('--store-cuts',dest="store_cuts", default=False,action='store_true',
                  help="Write the cuts to a pickle file")    
    return parser

if __name__ == '__main__':

    parser = defineParser()
    (options,args) = parser.parse_args()
    
    if options.options:
        ScaleFactor = options.scale_lumi
        Box = options.box
        label = options.output
        inputFiles = args
        
        cfg = Config.Config(options.config)
        
        binning = cfg.getBinning(Box)
        MRbins = binning[0]
        Rsqbins = binning[1]
        
    else:
        
        ScaleFactor = int(sys.argv[1])
        label = sys.argv[2]
        Box = sys.argv[3]
        inputFiles = sys.argv[4:]
        
        # bins in mR
        MRbins = [300, 350, 400, 450, 650, 800, 1000, 1250, 1500, 7000]
        # bins in R^2
        Rsqbins = [0.09, 0.16, 0.20, 0.30, 0.40, 0.45, 0.50]
    
    myTree = rt.TTree("myTree", "myTree")

    # create magic string
    magicString= "struct MyStruct{"
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            magicString += "Double_t bin_%i_%i;"%(ix,iy)
    magicString += "};"
    #print magicString

    # THIS IS CRAZY !!!!
    rt.gROOT.ProcessLine(magicString)
    from ROOT import MyStruct

    cuts = {}
    # associate the bins to the corresponding variables in the structure
    s = MyStruct()
    for ix in range(0, len(MRbins)-1):
        for iy in range(0, len(Rsqbins)-1):
            myBin = ["b%s_%i_%i" %(Box,ix,iy), MRbins[ix], MRbins[ix+1], Rsqbins[iy], Rsqbins[iy+1]]
            varName = "bin_%i_%i" %(ix, iy) 
            cuts[myBin[0]] = "MR>%f && MR<=%f && Rsq>%f && Rsq<=%f" % (MRbins[ix],MRbins[ix+1], Rsqbins[iy],Rsqbins[iy+1])
            # only the signal-region bins go in the Tree
            myTree.Branch(myBin[0], rt.AddressOf(s,varName),'%s/D' %varName)
    
    #write out a map of cuts for later
    if options.store_cuts:
        import pickle
        output = options.output.replace('.root','.pkl')
        pickle.dump(cuts, file(output,'wb'))
    
    treeName = "RMRTree"
    for i in xrange(len(inputFiles)):
        print "processing file: ", inputFiles[i]
        myfile = rt.TFile.Open(inputFiles[i])
        gdata = myfile.Get(treeName)
        if gdata == None: continue
        if gdata.InheritsFrom("RooDataSet") != True: continue
        for ix in range(0, len(MRbins)-1):
            for iy in range(0, len(Rsqbins)-1):
                # fill the tree. THIS SUCKS!!!
                dataTMP = gdata.reduce("MR>%f && MR<=%f && Rsq>%f && Rsq<=%f" % (MRbins[ix],MRbins[ix+1], Rsqbins[iy],Rsqbins[iy+1]))
                setattr(s,"bin_%i_%i"%(ix,iy), float(dataTMP.numEntries())/ScaleFactor )
                del dataTMP
        myTree.Fill()
        del gdata
        myfile.Close()        
        continue

    
    fileOut = rt.TFile.Open("%s" %label, "recreate")
    #data.Write()
    #hadHistDataset.Write()
    myTree.Write()
    fileOut.Close()

        
        
