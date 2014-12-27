"""Script to combine data cards with different b-tags"""
import glob
from optparse import OptionParser
import os
import re

if __name__ == '__main__':

    PARSER = OptionParser()
    (options, args) = PARSER.parse_args()

    cards_dir = args[0]
    btag1 = sorted(glob.glob('%s/*_1.txt' % cards_dir))
    btag2 = sorted(glob.glob('%s/*_2.txt' % cards_dir))
    btag3 = sorted(glob.glob('%s/*_3.txt' % cards_dir))

    print len(btag1), len(btag2), len(btag3)
    for i in range(0, len(btag1)):
        os.system('combineCards.py b1=%s b2=%s b3=%s > %s' %
                  (btag1[i], btag2[i], btag3[i],
                   btag1[i][:-6] + '.txt'))

        match = re.search(r'(razor_combine)_(.+)', cards_dir+btag1[i][:-6])
        print match.group(2)
        os.system('combine -M Asymptotic %s.txt -n %s' %
                  (btag1[i][:-6], match.group(2)))
        os.system('mv higgsCombine* %s' % cards_dir)
        os.system('rm roostats*')
