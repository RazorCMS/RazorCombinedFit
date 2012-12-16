#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: Sezen2DatasetWithUnweighting.py
# Created: 14-Dec-2012 Sezen & HBP
#------------------------------------------------------------------------------
import os, sys, re
from string import *
from math import *
from time import sleep
from optparse import OptionParser # replaces getopt

from ROOT import *
from RootTools.RootFile import Ntuple, pickEventAtRandom
from RootTools.Utils import RED, BLUE, RESETCOLOR, nameonly
#------------------------------------------------------------------------------
BOX_NUM = {'Had': 0}

# Command line options

OPTIONS = \
		[('-c', '--config',  'config',  'string', "razor_cfg.py",
		  'name of config file'),
		 ('-x', '--box',     'box',     'string', None, 'name of box'),
		 ('-d', '--dir',     'outdir',  'string', "./", 'output directory'),
		 ('-u', '--unweight','unweight', None,    False,'unweight events')]


#------------------------------------------------------------------------------
def mkhist1(hname, xtitle, ytitle, nbins, xmin, xmax, color=kBlack):
	h = TH1F(hname, "", nbins, xmin, xmax)
	
	h.SetLineColor(color)
	h.SetMarkerSize(1.0)
	h.SetMarkerColor(color)
	h.SetMarkerStyle(20)
	
	h.GetXaxis().SetTitle(xtitle)
	h.GetXaxis().SetTitleOffset(1.3)
	h.SetNdivisions(510, "X")
	h.SetMarkerSize(1.0)
	
	h.GetYaxis().SetTitle(ytitle)
	h.GetYaxis().SetTitleOffset(1.4)
	h.SetNdivisions(510, "Y")
	
	return h

findcolon = re.compile("(?<=\w):")

def scream(message):
	from random import randint
	i = randint(0,4)
	random_phrases = {0: 'Twas brillig and the slithy tothes',
					  1: 'Let all the evil that lurks in the mud hatch out',
					  2: 'Alas poor CMS I new them well!',
					  3: 'Lies, damned lies, and statistics',
					  4: 'Speak severely to your little boy and beat him '\
					  'when he sneezes'}
	print "\n** %s\n** %s%s%s\n" % (random_phrases[i], BLUE, message,
									RESETCOLOR)
	sys.exit(0)
#------------------------------------------------------------------------------
def main():
	if len(sys.argv) < 2:
		print '''
Usage:
	 ./Sezen2DatasetWithUnweighting.py %s<options>%s %s<root-file-name>%s

	 options:
	 -c config-file
	 -x box-name
	 -d output-directory
	 [-u unweight events]
		''' % (BOLDRED, RESETCOLOR, BOLDBLUE, RESETCOLOR)
		sys.exit(0)

	# ---------------------------------------
	# decode command line
	# ---------------------------------------
	parser = OptionParser()
	for shortOption, longOption, field, fieldtype, default, help in OPTIONS:
		if fieldtype != None:
			parser.add_option(shortOption, longOption,
							  dest=field,
							  type=fieldtype,
							  default=default,
							  help=help)
		else:
			parser.add_option(shortOption, longOption,
							  dest=field,
							  default=False,
							  action='store_true',
							  help=help)

	options, args = parser.parse_args()

	rootfilename  = args[0]
	if not os.path.exists(rootfilename):
		scream("can't find root file %s" % rootfilename)
		
	configname= options.config
	if not os.path.exists(configname):
		scream("can't find config file %s" % configname)

	box       = options.box
	if box == None:
		scream("use -x or --box to specify box name")
		
	prefix    = "%s%s" % (options.outdir, nameonly(rootfilename))
	treename  = "EVENTS"
	unweight  = options.unweight
		
	print
	print "Root filename: ", rootfilename
	print "Root treename: ", treename
	print "config:        ", configname
	print "box:           ", box
	print "unweight:      ", unweight
	print "prefix:        ", prefix

	# ---------------------------------------
	# read config file and find box block
	# and make objects known to python
	# ---------------------------------------
	token = '[%s]' % box
	records = open(configname).readlines()
	record = ''
	blockFound = False
	for line in records:
		t = strip(line)
		if blockFound:
			record += line
			if t == '':break
		elif t == token:
			blockFound = True

	record = findcolon.sub(' = ',record)
	exec(record)

	# ---------------------------------------
	# use workspace as a utility for creating
	# Roo stuff
	# ---------------------------------------
	print "\nbox name: %s\n" % box

	# create variables
	
	workspace = RooWorkspace(box)
	print "===> variables:"
	workspace.defineSet("variables", '')
	for v in variables:
		r = workspace.factory(v)
		print "\t%s\t%s" % (v, r.GetName())
		workspace.extendSet("variables", r.GetName())

	# create different ranges for the variables
	
	print
	print "===> variables_range:"
	wtmp = RooWorkspace("Boris") # so we don't pollute first workspace
	for v in variables_range:
		r = wtmp.factory(v)
		varname, rangename = split(v, '_')
		print "\t%s\t%s" % (varname, rangename)
		if workspace.var(varname):
			workspace.var(varname).setRange(rangename,
											r.getMin(),
											r.getMax())
		else:
			print "** can't find variable %s in variables" % varname
			sys.exit(0)

	# create more variables
	
	workspace.factory('W[0,0,+INF]')
	workspace.factory('nb[0,0,10]')
	workspace.factory('nW[0,0,+10]')
	workspace.factory('naW[0,0,+10]')

	print
	print "===> args:"
	args = workspace.allVars()
	args.Print()
	
	# get boundaries of MR window
	
	MRmin = args['MR'].getMin()
	MRmax = args['MR'].getMax()

	# get boundaries of Rsq window

	RSQmin = args['Rsq'].getMin()
	RSQmax = args['Rsq'].getMax()
	
	# ---------------------------------------
	# loop over events
	# ---------------------------------------

	# open ntuple
	
	ntuple = Ntuple(rootfilename, treename)
	
	count = 0
	sumw1 = 0.0
	sumw2 = 0.0
	selectedevents = []
	wcdf  = [] # cumulative distribution function of weights

	MRbins = 25
	hMR  = mkhist1("hMR", "MR", "", MRbins, MRmin, MRmax)
	cMR  = TCanvas("fig_MR", "fig_MR", 10, 10, 500, 500)

	RSQbins= 25
	hRSQ = mkhist1("hRSQ", "R^{2}", "", RSQbins, RSQmin, RSQmax)
	cRSQ = TCanvas("fig_RSQ", "fig_RSQ", 520, 10, 500, 500)
	
	for rownumber, event in enumerate(ntuple):
		
		if rownumber % 50000 == 0: print rownumber
		
		# apply cuts

		if not (event.MR >= MRmin):    continue
		if not (event.MR <= MRmax):    continue
		if not (event.RSQ >= RSQmin):  continue
		if not (event.RSQ <= RSQmax):  continue
		if not (event.BOX_NUM == BOX_NUM[box]): continue
		if not (event.WTAG_NUM > 0):   continue
		if not (event.BTAG_NUM > 0):   continue

		# sum weights

		count += 1
		sumw1 += event.WXSEC
		sumw2 += event.WXSEC * event.WXSEC

		# compute cumulative distribution function of weights

		if count == 1:
			wcdf.append(event.WXSEC)
		else:
			wcdf.append(wcdf[-1] + event.WXSEC)

		# plot some stuff
		
		hMR.Fill(event.MR,  event.WXSEC)
		hRSQ.Fill(event.RSQ, event.WXSEC)
		
		if count % 100 == 0:
			cMR.cd()
			hMR.Draw("hist")
			cMR.Update()

			cRSQ.cd()
			hRSQ.Draw("hist")
			cRSQ.Update()			
			
		# save event (NB: use clone method to ensure deep copying)
		
		selectedevents.append(event.clone())

	cMR.cd()
	hMR.Draw("hist")
	cMR.Update()

	cRSQ.cd()
	hRSQ.Draw("hist")
	cRSQ.Update()	
	
	effcount = int(0.5+sumw1*sumw1 / sumw2)
	print
	print "Weighted count:     %10.2f +/- %-10.2f" % (sumw1, sqrt(sumw2))
	print "Weighted count (2): %10.2f" %  wcdf[-1]
	print "Unweighted count:   %7d" % count
	print "Effective count:    %7d" % effcount
	
	# ---------------------------------------
	# create empty dataset, loop over selected
	# events and fill dataset
	# ---------------------------------------
	
	dataset = RooDataSet('RMRTree','Selected R and MR', args)

	if unweight: count = effcount

	hMRu  = mkhist1("hMRu", "MR", "", MRbins, MRmin, MRmax, kBlue+1)
	hRSQu = mkhist1("hRSQu", "R^{2}", "", RSQbins, RSQmin, RSQmax,kBlue+1)
		
	for ii in xrange(count):
	
		if unweight:
			jj = pickEventAtRandom(wcdf)
		else:
			jj = ii			
		event = selectedevents[jj]
		
		# set the variable values and add variables
		# to dataset
		a = RooArgSet(args)
		a.setRealValue('MR', event.MR)
		a.setRealValue('Rsq',event.RSQ)
		a.setRealValue('nb', event.BTAG_NUM)
		a.setRealValue('nW', event.WTAG_NUM)
		a.setRealValue('naW',event.AWTAG_NUM)
		a.setRealValue('R',  sqrt(event.RSQ))
		dataset.add(a)

		hMRu.Fill(event.MR)
		hRSQu.Fill(event.RSQ)
		
		if ii % 500 == 0:
			cMR.cd()
			hMRu.Draw("ep")
			cMR.Update()

			cRSQ.cd()
			hRSQu.Draw("ep")
			cRSQ.Update()			

	# normalize histograms to the same area
	
	ymax = 50 * (1 + int(1.1*hMR.GetMaximum()/50))
	hMR.SetMaximum(ymax)
	hMRu.SetMaximum(ymax)
	hMRu.Scale(hMR.Integral()/hMRu.Integral())

	ymax = 50 * (1 + int(1.1*hRSQ.GetMaximum()/50))
	hRSQ.SetMaximum(ymax)
	hRSQu.SetMaximum(ymax)
	hRSQu.Scale(hRSQ.Integral()/hRSQu.Integral())
	
	# plot
	
	cMR.cd()
	hMR.Draw("hist")
	hMRu.Draw("ep same")
	cMR.Update()
	
	cRSQ.cd()
	hRSQ.Draw("hist")
	hRSQu.Draw("ep same")
	cRSQ.Update()	

	# Save RooDataSet to Root file
	
	filename = "%(prefix)s_MR%(MRmin)s_R%(Rmin)s_%(box)s.root" % \
			   {'prefix': prefix,
				'MRmin' : MRmin,
				'Rmin'  : sqrt(RSQmin),
				'box'   : box}

	print "\nwrite:"
	print filename
	output = TFile(filename, "recreate")
	dataset.Write()
	output.Close()

	sleep(3)
	#gApplication.Run()
#------------------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print
	print "goodbye cruel world!"
