import sys
import ROOT as rt
from array import *
import os
from math import *
pwd = os.environ['PWD']
def fillGapsVertical(histo, ix, iy):
    return (histo.GetBinContent(ix,iy+1)+histo.GetBinContent(ix,iy-1))/2.

def fillGapsVertical2(histo, ix, iy):
    return (histo.GetBinContent(ix,iy+1)+histo.GetBinContent(ix,iy-1)+histo.GetBinContent(ix,iy))/3.

def smear(histo, ix, iy):
    return (histo.GetBinContent(ix,iy+1)+histo.GetBinContent(ix,iy)+histo.GetBinContent(ix,iy-1)+
            histo.GetBinContent(ix-1,iy+1)+histo.GetBinContent(ix-1,iy)+histo.GetBinContent(ix-1,iy-1)+
            histo.GetBinContent(ix+1,iy+1)+histo.GetBinContent(ix+1,iy)+histo.GetBinContent(ix+1,iy-1))/9.

def get1DHist(hin,m0):
    iy = int(38)
    minY = 10.
    maxY = 770.
    h1d = rt.TH1D("h1d_m0_%i"%m0,"h1d_m0_%i"%m0,iy,minY,maxY)
    for j in range(1,iy+1):
        # invert this : m0 =  i*hin.GetXaxis().GetBinWidth(1)
        i = int(float(m0) / hin.GetXaxis().GetBinWidth(1))
        m12 = j*h.GetYaxis().GetBinWidth(1)
        if os.path.exists("%s/CLs_m0_%i_m12_%i.root"%(pwd,m0,m12)):
            h1d.SetBinContent(j,hin.GetBinContent(i,j))                  
    return h1d         
                    
def getLog1DHist(hin,m0):
    iy = int(38)
    minY = 10.
    maxY = 770.
    h1d = rt.TH1D("h1d_m0_%i"%m0,"h1d_m0_%i"%m0,iy,minY,maxY)
    for j in range(1,iy+1):
        # invert this : m0 =  i*hin.GetXaxis().GetBinWidth(1)
        i = int(float(m0) / hin.GetXaxis().GetBinWidth(1))
        m12 = j*h.GetYaxis().GetBinWidth(1)
        if os.path.exists("%s/CLs_m0_%i_m12_%i.root"%(pwd,m0,m12)):
            if hin.GetBinContent(i,j) > 0: lb = log10(hin.GetBinContent(i,j))
            else: lb = log10(0.000001)            
            h1d.SetBinContent(j,lb)
    return h1d         

def cleanUpHist(hin):
    #remove spikes
    for i in range(1,ix+1):
        for j in range(1,iy+1):
            if hin.GetBinContent(i,j) > 1: hin.SetBinContent(i,j,0)
            if hin.GetBinContent(i,j) < 0: hin.SetBinContent(i,j,0)
    h = hin.Clone()        
    # fill the gaps
    for i in range(2,ix):
        for j in range(2,iy):
            if h.GetBinContent(i,j) == 0:
                h.SetBinContent(i,j,fillGapsVertical(h,i,j))
                
    # fill the gaps
    for i in range(2,ix):
        for j in range(2,iy):
            if h.GetBinContent(i,j) == 0:
                h.SetBinContent(i,j,fillGapsVertical2(h,i,j))
                
    # smear
    for iSmear in range(0,0):
        for i in range(2,ix):
            for j in range(2,iy):
                h.SetBinContent(i,j,smear(hin,i,j))
    return hin, h            
    
def getBestArrays(h):
    m0best = []
    m12best = []
    for i in range(1,ix+1):
        m12min = 800
        m0min = 2000
        for j in range(1,iy+1):
            m0 =  i*h.GetXaxis().GetBinWidth(1) 
            m12 = j*h.GetYaxis().GetBinWidth(1)
            if os.path.exists("%s/CLs_m0_%i_m12_%i.root"%(pwd,m0,m12)) and h.GetBinContent(i,j)>=0.05:
                if m12 < m12min:
                    m12min = m12
                    m0min = m0 
        if not m12min == 800:
            m12best.append(m12min)
            m0best.append(m0min)
    print "m0best  = ", m0best         
    print "m12best = ", m12best
  
    return m0best,m12best

if __name__ == '__main__':
    fileIn = rt.TFile.Open(sys.argv[1])
    CLsVar = sys.argv[2]
    tree = fileIn.Get("clTree")
           
    ix = int(100)
    minX = 10.
    maxX = 2010.
    iy = int(38)
    minY = 10.
    maxY = 770.

    tanB = 10
    h = rt.TH2D("mSUGRAplot", "CMSSM CL_{s} tan#beta=%i %s"%(tanB,CLsVar),ix, minX, maxX, iy, minY, maxY)

    tree.Project("mSUGRAplot", "m12:m0",CLsVar)

    # for each m0, find the min m12 that is NOT excluded 
    m0best, m12best = getBestArrays(h)
    # get rid of certain values
    if tanB == 10:
        if CLsVar == "CLs_Had" or CLsVar == "CLs_Tot_ExpPlus": 
            m12best.pop(m0best.index(120))
            m0best.remove(120)

            if CLsVar == "CLs_Tot" or CLsVar == "CLs_Tot_Exp" or CLsVar == "CLs_Tot_ExpMinus": 
                m12best.pop(m0best.index(120))
                m0best.remove(120)
                m12best.pop(m0best.index(140))
                m0best.remove(140)


    m0values = list(m0best)
       
    hin, h = cleanUpHist(h)
    
    h1dlist = [getLog1DHist(hin, m0) for m0 in m0values] 

    # define markers
    markersbest = []
    for i in range(0,len(m0best)):
        marker = rt.TMarker(m0best[i],m12best[i],29)
        markersbest.append(marker)
        
    c = rt.TCanvas("c","c",700, 600)
    rt.gStyle.SetPalette(1)
    c.SetLogz()
    
    hin.SetMaximum(0.1)
  
    # drawing for real
    hin.Draw("colz")

  
    grbest = rt.TGraph(len(m0best),array('f',m0best),array('f',m12best))
    
    m0fit = list(m0values) 
    m12fit = []    

    for h1d in h1dlist:
        fr = h1d.Fit("pol1","SNO")
        m12 = 0
        if fr.Parameter(1) !=0: m12 = (log10(0.05) - fr.Parameter(0) )/ fr.Parameter(1)
        m12fit.append(m12)

    markersfit = []
    for i in range(0,len(m0fit)):
        marker = rt.TMarker(m0fit[i],m12fit[i],29)
        markersfit.append(marker)
       
    grfit = rt.TGraph(len(m0fit),array('f',m0fit),array('f',m12fit))
    for marker in markersbest:
        marker.Draw("same")

    glsq = rt.TF1("glsq","[0]*sqrt([1]-x*x*[2]+[3])+[4]*([5]+[6]*x)")

    poly4 = rt.TF1("poly4","[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x*x")
    # FIT CONFIGURATION
    # for Had:
    # Using the output of the fit to the TOTAL
    #     PARAMETER                                   STEP         FIRST
    # NO.   NAME      VALUE            ERROR          SIZE      DERIVATIVE
    # 1  p0           3.68547e-01   4.13885e-03   1.82782e-06   6.28218e-03
    # 2  p1           1.95737e+05     fixed
    # 3  p2           2.67367e-01   5.24430e-04   2.57415e-07  -8.68363e-03
    # 4  p3           1.04851e+05   1.03486e+03  -9.78660e-02   1.47698e-08
    # 5  p4           1.30206e+00   9.38195e-03  -5.59329e-06  -8.90962e-03
    # 6  p5           3.11027e+02     fixed
    # 7  p6          -3.39352e-02   1.13664e-03   1.02656e-06  -1.15377e-01
    if CLsVar == "CLs_Had":	   
    	glsq.SetParameters(0.9*3.68547e-01,1.95737e5,2.67367e-01,1.04851e+05,0.9*1.30206e+00,311.027,-3.39352e-02)
    	glsq.SetParLimits(0, 1, 1)
    	glsq.SetParLimits(4, 1, 1)
    	glsq.SetParLimits(1, 1, 1)
    	glsq.SetParLimits(5, 1, 1)

    # FIT CONFIGURATION
    # for Tot (Obs, ExpPlus, ExpMinus):

    if CLsVar == "CLs_Tot" or CLsVar == "CLs_Tot_ExpMinus":	       
    	glsq.SetParameters(3.26206e-01,1.95737e5,2.39535e-1,1.95736e5,0.8,311.027,-0.0167)
    	glsq.SetParLimits(1, 1, 1)
   	glsq.SetParLimits(5, 1, 1)

    # FIT CONFIGURATION
    # for Tot (Exp):
    
    if CLsVar == "CLs_Tot_Exp":	     
    	glsq.SetParameters(0.9*3.68547e-01,1.95737e5,2.67367e-01,1.04851e+05,0.9*1.30206e+00,311.027,-3.39352e-02)
    	glsq.SetParLimits(1, 1, 1)
    	glsq.SetParLimits(5, 1, 1)
    	glsq.SetParLimits(6, 1, 1)

    if CLsVar == "CLs_Tot_ExpPlus":	       
    	glsq.SetParameters(3.26206e-01,1.95737e5,2.39535e-1,1.95736e5,0.9,315.027,-0.0167)
    	glsq.SetParLimits(1, 1, 1)
   	glsq.SetParLimits(5, 1, 1)

    grbest.Fit(glsq)
    grbest.Fit(poly4) 
    poly4.SetLineWidth(3)
    poly4.SetLineColor(rt.kBlack)
    poly4.Draw("csame")
    m12smooth = []
    m0smooth = list(m0values)

    for m0 in m0smooth:
        if CLsVar == "CLs_Tot_ExpPlus": m12smooth.append(poly4.Eval(m0)+5)
	else: m12smooth.append(glsq.Eval(m0))

    m0smooth.reverse()
    m0smooth.append(0)
    m12smooth.reverse()
    if CLsVar == "CLs_Tot_ExpPlus": m12smooth.append(poly4.Eval(120)+5)
    else: m12smooth.append(glsq.Eval(0))
    m0smooth.reverse()
    m12smooth.reverse()

    m0smooth.append(3000)
    m12smooth.append(glsq.Eval(3000))
    m0smooth.append(4000)
    m12smooth.append(glsq.Eval(4000))
    if tanB == 10:
        if CLsVar == "CLs_Tot_Exp": 
            m12smooth[7] = m12best[6]
            m12smooth[8] = m12best[7]
            m12smooth[9] = m12best[8]
            m12smooth[10] = m12best[9]

        if CLsVar == "CLs_Had": 
            m12smooth[7] = m12best[6]
            m12smooth[8] = m12smooth[8]-5
            m12smooth[9] = m12smooth[9]-5
            m12smooth[10] = m12smooth[10]-5
            m12smooth[11] = m12smooth[11]-5
            m12smooth[12] = m12smooth[12]-5
            m12smooth[13] = m12smooth[13]-5
    print "m0smooth = ", m0smooth
    print "m12smooth = ", m12smooth

    grfinal = rt.TGraph(len(m0smooth),array('f',m0smooth),array('f',m12smooth))
    grfinal.SetLineWidth(3)
    grfinal.SetLineColor(rt.kBlue+2)
    grfinal.Draw("csame")
    c.SaveAs("2dCLs.gif")
    c.SaveAs("2dCLs.C")

    fileOut = rt.TFile.Open("1d_2d_CLs.root","recreate")
    hin.Write()
    h.Write()
    grfinal.Write()
    for h1d in h1dlist:
        h1d.Write()
    fileOut.Close()
                            
