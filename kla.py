import zipfile
import subprocess
import requests
import urllib
import io
import json
import base64
import os
import sys
import stat
from pathlib import Path

# Params used in the call to the baseline analysis.
args = sys.argv
PARAM_KLA_BASEURL = args[1]
PARAM_KLA_SCOPE = args[2]
PARAM_KLA_USERNAME = '$KIUWAN_USER' 
PARAM_KLA_PASSWORD = '$KIUWAN_PASS'
PARAM_KLA_APPNAME = '$BITBUCKET_PROJECT_KEY'
PARAM_KLA_SOURCEDIR = '$BITBUCKET_CLONE_DIR'
PARAM_KLA_LABEL = '$BITBUCKET_BUILD_NUMBER'
PARAM_KLA_DATABASETYPE = '$KIUWAN_SQL_TYPE'
PARAM_KLA_ADVANCEDPARAMS = '$KIUWAN_ADVANCED_PARAMS'

KLA_URL = PARAM_KLA_BASEURL + '/pub/analyzer/KiuwanLocalAnalyzer.zip'
TMP_EXTRACTION_DIR = '/tmp' + '/kla'
KLA_EXE_DIR = TMP_EXTRACTION_DIR + "/KiuwanLocalAnalyzer/bin"

# Function to create the Kiuwan KLA line command.
# It is created with the minimum amount of parameters. Then the advanced parameters are passed in, the User is responsible for a good format
# Note the memory parameter has been already created properly
def getKLACmd(tmp_dir=TMP_EXTRACTION_DIR,
              appname=PARAM_KLA_APPNAME,
              sourcedir=PARAM_KLA_SOURCEDIR,
              scope=PARAM_KLA_SCOPE,
              label=PARAM_KLA_LABEL,
              user=PARAM_KLA_USERNAME,
              password=PARAM_KLA_PASSWORD,
              dbtype=PARAM_KLA_DATABASETYPE,
              advanced=PARAM_KLA_ADVANCEDPARAMS):
    prefix = tmp_dir + '/KiuwanLocalAnalyzer/bin/'
    agent = prefix + 'agent.sh'
    os.chmod(agent, stat.S_IRWXU)

    klablcmd = '{} -c -n {} -s {} -as {} -l {} --user {} --pass {} transactsql.parser.valid.list={} {}'.format(agent, appname, sourcedir, scope, label, user, password, dbtype, advanced)
    return klablcmd

# Function to download and extract the Kiuwan Local Analyzer from kiuwan server
# TODO: parametrize the URL to support Kiuwan on premises installations
def downloadAndExtractKLA(tmp_dir=TMP_EXTRACTION_DIR, klaurl=KLA_URL):
    print('Downloading KLA zip from ', klaurl, ' at [', os.getcwd(), ']', '...')
    resp = urllib.request.urlopen(klaurl)
    zipf = zipfile.ZipFile(io.BytesIO(resp.read()))
    for item in zipf.namelist():
        print("\tFile in zip: ", item)

    print('Extracting zip to [', tmp_dir, ']', '...')
    # Luis: para probar crear dirs
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    zipf.extractall(tmp_dir)

# Parse the output of the analysis resutl to get the analysis code
def getBLAnalysisCodeFromKLAOutput(output_to_parse):
    return output_to_parse.split("Analysis created in Kiuwan with code:", 1)[1].split()[0]

# Function to excetute the actual Kiuwan Local Analyzer command line and get the resutls.
def executeKLA(cmd):
    print('Executing [', cmd, '] ...')
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # (output, err) = pipe.communicate()
    output_text = ''
    try:
      nextline = pipe.stdout.readline()
      while (pipe.poll() == None):
            output_text = output_text + nextline.decode('utf-8')
            sys.stdout.write(nextline.decode('utf-8'))
            sys.stdout.flush()
            nextline = pipe.stdout.readline()
    except KeyboardInterrupt:
        print("Keyboard interrupt... why??")
        return output_text, pipe.returncode
        
    #return_code = pipe.wait()
    return output_text, pipe.returncode

# Actual executing code after defining the functions
# Extract and download KLA from kiuwan.com (or from on-premise site)
downloadAndExtractKLA(tmp_dir=TMP_EXTRACTION_DIR)

# Build the KLA CLI command
kla_bl_cmd = getKLACmd(tmp_dir=TMP_EXTRACTION_DIR)

# Execute CLA KLI and set results as outputs
output, rc = executeKLA(kla_bl_cmd)
print('{}{}'.format('KLA return code: ', rc))
if rc==0:
  analysis_code = getBLAnalysisCodeFromKLAOutput(output)
  print('Analysis code [', analysis_code, ']')
  print('Analysis successful')
elif rc == 1:
  print('::set-output name=message::Analyzer execution error.')
elif rc == 10:
  print('::set-output name=message::Audit overall result = FAIL.')
elif rc == 11:
  print('::set-output name=message::Invalid analysis configuration.')
elif rc == 12:
  print('::set-output name=message::The downloaded model does not support any of the discovered languages.')
elif rc == 13:
  print('::set-output name=message::Timeout waiting for analysis results.')
elif rc == 14:
  print('::set-output name=message::Analysis finished with an error in Kiuwan.')
elif rc == 15:
  print('::set-output name=message::Timeout: killed the subprocess.')
elif rc == 16:
  print('::set-output name=message::Baseline analysis not permitted for current user.')
elif rc == 17:
  print('::set-output name=message::Delivery analysis not permitted for current user.')
elif rc == 18:
  print('::set-output name=message::No analyzable extensions found.')
elif rc == 19:
  print('::set-output name=message::Error checking license.')
elif rc == 21:
  print('::set-output name=message::Invalid CLI parameter	.')
elif rc == 22:
  print('::set-output name=message::Access denied.')
elif rc == 23:
  print('::set-output name=message::Bad Credentials.')
elif rc == 24:
  print('::set-output name=message::Application Not Found.')
elif rc == 25:
  print('::set-output name=message::Limit Exceeded for Calls to Kiuwan API.')
elif rc == 26:
  print('::set-output name=message::Quota Limit Reached	.')
elif rc == 27:
  print('::set-output name=message::Analysis Not Found.') 
elif rc == 28:
  print('::set-output name=message::Application already exists.')
elif rc == 30:
  print('::set-output name=message::Delivery analysis not permitted: baseline analysis not found.')
elif rc == 31:
  print('::set-output name=message::No engine available.')
elif rc == 32:
  print('::set-output name=message::Unexpected error	.')
elif rc == 33:
  print('::set-output name=message::Out of Memory.')
elif rc == 34:
  print('::set-output name=message::JVM Error	.')
else:
  print('::set-output name=message::No error message found.')

