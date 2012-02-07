import ROOT as rt

def getColorList():
    return [rt.kBlue+3,rt.kMagenta+1,rt.kGreen-6,\
            rt.kRed+1,rt.kBlue-1,rt.kGreen+3,\
            rt.kYellow+1,rt.kCyan+3,rt.kSpring,rt.kOrange-9,rt.kOrange,rt.kAzure,rt.kGray]

def setStyle():
    """Copy and paste from Chris's macro"""
    
    from ROOT import gStyle
    
    # For the canvas:
    gStyle.SetCanvasBorderMode(0);
    gStyle.SetCanvasColor(rt.kWhite);
    gStyle.SetCanvasDefH(300); #Height of canvas
    gStyle.SetCanvasDefW(600); #Width of canvas
    gStyle.SetCanvasDefX(0);   #POsition on screen
    gStyle.SetCanvasDefY(0);
    
    # For the Pad:
    gStyle.SetPadBorderMode(0);
    # gStyle.SetPadBorderSize(Width_t size = 1);
    gStyle.SetPadColor(rt.kWhite);
    gStyle.SetPadGridX(False);
    gStyle.SetPadGridY(False);
    gStyle.SetGridColor(0);
    gStyle.SetGridStyle(3);
    gStyle.SetGridWidth(1);
    
    # For the frame:
    gStyle.SetFrameBorderMode(0);
    gStyle.SetFrameBorderSize(1);
    gStyle.SetFrameFillColor(0);
    gStyle.SetFrameFillStyle(0);
    gStyle.SetFrameLineColor(1);
    gStyle.SetFrameLineStyle(1);
    gStyle.SetFrameLineWidth(1);
    
    # set the paper & margin sizes
    gStyle.SetPaperSize(20,26);
    gStyle.SetPadTopMargin(0.065);
    gStyle.SetPadRightMargin(0.065);
    gStyle.SetPadBottomMargin(0.15);
    gStyle.SetPadLeftMargin(0.17);
    
    # use large Times-Roman fonts
    gStyle.SetTitleFont(132,"xyz");  # set the all 3 axes title font
    gStyle.SetTitleFont(132," ");    # set the pad title font
    gStyle.SetTitleSize(0.06,"xyz"); # set the 3 axes title size
    gStyle.SetTitleSize(0.06," ");   # set the pad title size
    gStyle.SetLabelFont(132,"xyz");
    gStyle.SetLabelSize(0.05,"xyz");
    gStyle.SetLabelColor(1,"xyz");
    gStyle.SetTextFont(132);
    gStyle.SetTextSize(0.08);
    gStyle.SetStatFont(132);
    
    # use bold lines and markers
    gStyle.SetMarkerStyle(8);
    gStyle.SetHistLineWidth(2);
    gStyle.SetLineStyleString(2,"[12 12]"); # postscript dashes
    
    #..Get rid of X error bars
    gStyle.SetErrorX(0.001);
    
    # do not display any of the standard histogram decorations
    gStyle.SetOptTitle(0);
    gStyle.SetOptStat(0);
    gStyle.SetOptFit(11111111);
    
    # put tick marks on top and RHS of plots
    gStyle.SetPadTickX(1);
    gStyle.SetPadTickY(1);
    
    # set a decent palette
    gStyle.SetPalette(1);
    
    gStyle.cd();
