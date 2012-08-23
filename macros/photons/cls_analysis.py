# Max Horton
# CERN summer student 2012
# Caltech Class of 2014
# Maxwell.Christian.Horton@gmail.com
#
# Entry point for the CLs calculator.  Note that the CLs calculator in
# this case is the StandardHypoTestInvDemo() program, from RooStats.  It
# will frequently be referred to as simply "the calculator", because
# that's what it is.
#
# The program is called from the command line using
# "python cls_analysis.py" with optional flags.
#

from ROOT import *
import os
from optparse import OptionParser

# Set up an OptionParser with desired options, and return it.
def define_parser():
    # Note that we are using the options as values in calls to the system.
    # So we might as well just store them as strings (thus all of them are
    # strings.
    parser = OptionParser()
    # Type of calculator.  See StandardHypo...C
    parser.add_option("-c", "--calculatorType", action="store", type="string", dest="calculatorType")
    # Test statistic type.  Use -t 1 for tevatron
    parser.add_option("-t", "--test_statistic_type", action="store", type="string", dest="testStatType")
    # Number of points to scan
    parser.add_option("-p", "--points", action="store", type="string", dest="npoints")
    # Number of toys to use
    parser.add_option("-n", "--num_toys", action="store", type="string", dest="ntoys")
    # File with 4 input histograms
    parser.add_option("--histfile", "--signal_histogram_file", action="store", type = "string", dest = "input_sig")
    # Background histogram name
    parser.add_option("--bkgname", action="store", type = "string", dest = "bkgname")
    # Name of data set in the workspace
    parser.add_option("--datname", action="store", type = "string", dest = "datname")
    # Leave this flag in to prevent windows from popping up.
    parser.add_option("-b", action="store_true", dest = "suppress")
    # Name of file containing the workspace
    parser.add_option("-w", "--ws_container_name", type = "string", dest = "ws_container_name")
    return parser


# Main function.  It will read the input options, creating values for
# strings to correspond to the user's requested options.  Then, the
# workspace_preparer will be called, to prepare the model for the 
# calculation.  Then, the actual CLs calculator will be called.
if __name__ == "__main__":
    parser = define_parser()
    (options, args) = parser.parse_args()

    # Set defaults for optional values
    # Note that some of these aren't available as flags, because they
    # aren't likely to be changed by the user.  (Ex: useCLs should always
    # be set to true because we are doing CLs!)
    # These \\" ... \\" are needed because we perform an os.system call
    # to run the calculator (see comment below explaining why).  When
    # a system call is performed in this way, ROOT requires that all
    # string arguments to the call be surrounded by \".  So, we need
    # \\" on either side (since printing a backslash requires the 
    # backslash escape character.
    #
    # See StandardHypoTestInvDemo() for explanation of parameters such
    # as calculatorType or testStatType
    wsName = '\\"newws\\"'
    modelSBName = '\\"SbModel\\"'
    modelBName = '\\"BModel\\"'
    dataName = '\\"data\\"'
    calculatorType = "0" 
    testStatType = "3" 
    useCLs = "true"
    npoints = "4"
    poimin = "0"
    poimax = "1000"
    ntoys = "1000"
    useNumberCounting = "false"
    nuisPriorName = '\\"0\\"'

    # When we call the workspace_preparer, we aren't doing an os.system()
    # call, so we don't need the \\" characters.
    input_sig = "signal.root"
    bkgname = "background"
    datname = "data"
    ws_container_name = "razor_output.root"

    graphics_string = ''

    # Set up all values according to the input parser
    if (options.calculatorType != None):
        calculatorType = options.calculatorType

    if (options.testStatType != None):
        testStatType = options.testStatType

    if (options.npoints != None):
        npoints = options.npoints

    if (options.ntoys != None):
        ntoys = options.ntoys

    if (options.input_sig != None):
        input_sig = options.input_sig

    if (options.bkgname != None):
        bkgname = options.bkgname

    if (options.ws_container_name != None):
        ws_container_name = options.ws_container_name


    if (options.datname != None):
        datname = options.datname
        dataName = '\\"' + options.datname + '\\"'

    if (options.suppress):
        graphics_string = '-b -q '

    workspace = "_workspacefrom_" + input_sig
    infile = '\\"' + workspace + '\\"'



    cls_name = '\\"' + input_sig + '_cls.ps\\"'
    bells_name = '\\"' + input_sig + '_bells.ps\\"'
    # Unfortunately, the StandardHypoTestInvDemo() method, which is used
    # to perform the calculations, has an issue: if we try to load it
    # running the workspace_preparer, it won't load all of its packages.
    # So, we have to resort to an os.system() call to get the function to
    # work.  Thus, we need to create a large, ROOT-formatted string to
    # contain the information we need to pass in the system call.  This is
    # the hypotest_call_string below.

    hypotest_call_string =  infile + ',' + wsName + ',' + modelSBName + ',' + modelBName + ',' + dataName + ',' + calculatorType + ',' + testStatType + ',' + useCLs + ',' + npoints + ',' + poimin + ',' + poimax + ',' + ntoys + ',' + useNumberCounting + ',' + nuisPriorName + ','  + cls_name + "," + bells_name

    # Now that we have set up for the calls, let's make them.  First, load
    # the workspace_preparer, which sets up a file for the StandardHypo-
    # TestInvDemo() to read values / pdfs from.
    gROOT.ProcessLine('.L workspace_preparer.C')

    # Now we can prepare the workspace.
    # workspace is the write workspace name
    workspace_preparer(input_sig, bkgname, datname, workspace, ws_container_name)

    # As mentioned, gROOT.ProcessLine('.L StandardHypoTestInvDemo.C')
    # and then StandardHypoTestInvDemo() will cause errors because the 
    # packages needed won't load.  So, we resort to a different method of
    # calling the function - a simple os.system call.
    os.system('root -l ' + graphics_string  + ' "StandardHypoTestInvDemo.C(' + hypotest_call_string  + ')" -q')
