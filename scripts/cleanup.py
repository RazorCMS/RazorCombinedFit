import os, sys

box = sys.argv[1]
neutralinopoint = int(sys.argv[2])
outputDir = "/afs/cern.ch/work/s/salvati/private/workspace/RazorStops/ScanHybrid_" + box + "_" + str(neutralinopoint)
print outputDir

logFiles = outputDir+"/logs_*/*"

for i in range(100):
	os.system("sleep 60; rm -r core*; rm -rf LSFJOB*; rm -r %s"%logFiles)