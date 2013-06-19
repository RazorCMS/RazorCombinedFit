import sys
import subprocess
import re

if __name__ == '__main__':
	"""This little macro is just to find what signal files are missing in each box (one by one)
	from Lucie's T2tt samples"""

	box = sys.argv[1]
	directory = sys.argv[2]

	massPairDict = {}
	for mLSP in range(25, 825, 25):
		
		theDir = '%s/mLSP%s.0/'%(directory,str(mLSP))
		proc = subprocess.Popen(["ls %s | grep %s"%(theDir, box)], stdout=subprocess.PIPE, shell=True)
		(dirmLSP, err) = proc.communicate()

		# print dirmLSP
		massTuple = ()

		# dump all signal files into signalFile
		signalFile = re.split("\n", dirmLSP)
		for mstop in range(mLSP+100, 825, 25):
			findCounter = 0
			for line in signalFile[:-1]:
				massPoint = massPoint = "%.1f_%.1f"%(mstop, mLSP)
				themass = re.findall(str(massPoint) + "_" + box, line)
				if len(themass) > 0:
					thestopmass = float(re.split("_", themass[0])[0])
					massTuple = massTuple + (thestopmass,)
					findCounter += 1
			if findCounter == 0:
				print 'Could not find:', ('mLSP', 'mStop'), '=', (mLSP, mstop)

		massPairDict[mLSP] = massTuple

	mLSPlist = massPairDict.keys()
	mLSPlist.sort()
	for lsp in mLSPlist:
		print "%s: %s"%(lsp,massPairDict[lsp])

