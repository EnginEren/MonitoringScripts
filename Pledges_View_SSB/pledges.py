#!/usr/bin/python
import os, sys
import simplejson
import json
import time
import urllib, httplib
import string

#_____________________________________________________________________________

# function needed to fetch a list of all pledges values from siteDB
def fetch_all_pledges(url,api):
  headers = {"Accept": "application/json"}
  if 'X509_USER_PROXY' in os.environ:
      print 'X509_USER_PROXY found'
      conn = httplib.HTTPSConnection(url, cert_file = os.getenv('X509_USER_PROXY'), key_file = os.getenv('X509_USER_PROXY'))
  elif 'X509_USER_CERT' in os.environ and 'X509_USER_KEY' in os.environ:
      print 'X509_USER_CERT and X509_USER_KEY found'
      conn = httplib.HTTPSConnection(url, cert_file = os.getenv('X509_USER_CERT'), key_file = os.getenv('X509_USER_KEY'))
  else:
      print 'You need a valid proxy or cert/key files'
      sys.exit()
  print 'conn found in if else structure'
  r1=conn.request("GET",api, None, headers)
  print 'r1 passed'
  r2=conn.getresponse()
  print 'r2 passed'
  inputjson=r2.read()
  print '-------------------------------------------------------------'
  jsn = simplejson.loads(inputjson)
  pledges= {}
  pledgesSites = {}
  count = 0
  for i in jsn['result']:
    #_____________________________
    pledgeDate     = i[2]
    pledgeTime     = i[1]
    pledgeSiteName = i[0]
    #pledgeCpuValue = i[3]
    #_____________________________
    if pledgeDate == 2014:
      current = time.time()
      diff = current - pledgeTime
      if pledges.has_key(pledgeSiteName):
        pledges[pledgeSiteName][diff] = {"time":i[1], "cpu":i[3] * 100}
      else:
        pledges[pledgeSiteName] = {diff:{"time":i[1], "cpu":i[3] * 100}}
  for site in pledges.keys():
    min_site = min(pledges[site].keys())
    pledgesSites[site] = pledges[site][min_site]['cpu']
  return pledgesSites
#_____________________________________________________________________________

# function matchs pledges values gets from siteDB with SiteName

def matchPledges(pledgeList):
  pledges = {}
  sitesList =  ['T1_TW_ASGC','T1_FR_CCIN2P3','T1_CH_CERN','T1_IT_CNAF','T1_US_FNAL','T1_US_FNAL_Disk','T1_RU_JINR','T1_RU_JINR_Disk','T1_DE_KIT','T1_ES_PIC','T1_UK_RAL','T1_UK_RAL_Disk','T2_IT_Bari','T2_CN_Beijing','T2_K_SGrid_Bristol','T2_K_London_Brunel','T2_FR_CCIN2P3','T2_CH_CERN','T2_CH_CERN_AI','T2_CH_CERN_HLT','T2_CH_CERN_T0','T2_ES_CIEMAT','T2_CH_CSCS','T2_TH_CUNSTDA','T2_S_Caltech','T2_DE_DESY','T2_EE_Estonia','T2_S_Florida','T2_FR_GRIF_IRFU','T2_FR_GRIF_LLR','T2_BR_UERJ','T2_FI_HIP','T2_AT_Vienna','T2_HU_Budapest','T2_UK_London_IC','T2_ES_IFCA','T2_RU_IHEP','T2_BE_IIHE','T2_RU_INR', 'T2_FR_IPHC','T2_RU_ITEP','T2_GR_Ioannina','T2_RU_JINR','T2_UA_KIPT','T2_KR_KNU','T2_IT_Legnaro','T2_BE_UCL','T2_TR_METU','T2_US_MIT','T2_PT_NCG_Lisbon','T2_PK_NCP','T2_US_Nebraska','T2_RU_PNPI','T2_IT_Pisa','T2_US_Purde', 'T2_RU_RRC_KI','T2_DE_RWTH','T2_IT_Rome','T2_UK_SGrid_RALPP','T2_RU_SINP','T2_BR_SPRACE','T2_IN_TIFR','T2_TW_Taiwan','T2_US_UCSD','T2_MY_UPM_BIRUNI', 'T2_US_Vanderbilt','T2_PL_Warsaw','T2_US_Wisconsin']
  matchList =  {"T1_TW_ASGC": "ASGC", "T1_FR_CCIN2P3": "CC-IN2P3", "T1_CH_CERN": "CERN","T1_IT_CNAF": "CNAF","T1_US_FNAL": "FNAL","T1_US_FNAL_Disk": "n/a","T1_RU_JINR": "JINR-T1","T1_RU_JINR_Disk": "JINR-T1DISK","T1_DE_KIT": "KIT","T1_ES_PIC": "PIC","T1_UK_RAL": "RAL","T1_UK_RAL_Disk": "n/a","T2_IT_Bari": "Bari","T2_CN_Beijing": "Beijing","T2_K_SGrid_Bristol": "Bristol","T2_K_London_Brunel": "Brunel","T2_FR_CCIN2P3": "CC-IN2P3 AF","T2_CH_CERN": "n/a","T2_CH_CERN_AI": "n/a","T2_CH_CERN_HLT": "n/a","T2_CH_CERN_T0": "n/a","T2_ES_CIEMAT": "CIEMAT","T2_CH_CSCS": "CSCS","T2_TH_CUNSTDA": "CUNSTDA","T2_S_Caltech": "Caltech","T2_DE_DESY": "DESY","T2_EE_Estonia": "Estonia","T2_S_Florida": "Florida","T2_FR_GRIF_IRFU": "GRIF_IRFU","T2_FR_GRIF_LLR": "GRIF_LLR","T2_BR_UERJ": "HEPGRID_UERJ","T2_FI_HIP": "Helsinki Institute of Physics","T2_AT_Vienna": "Hephy-Vienna","T2_HU_Budapest": "Hungary","T2_UK_London_IC": "IC","T2_ES_IFCA": "IFCA","T2_RU_IHEP": "IHEP","T2_BE_IIHE": "IIHE","T2_RU_INR": "INR","T2_FR_IPHC": "IPHC","T2_RU_ITEP": "ITEP","T2_GR_Ioannina": "Ioannina","T2_RU_JINR": "JINR","T2_UA_KIPT": "KIPT", "T2_KR_KNU": "KNU","T2_IT_Legnaro": "Legnaro","T2_BE_UCL": "Louvain","T2_TR_METU": "METU", "T2_US_MIT": "MIT", "T2_PT_NCG_Lisbon": "NCG-INGRID-PT","T2_PK_NCP": "NCP-LCG2","T2_US_Nebraska": "Nebraska","T2_RU_PNPI": "PNPI","T2_IT_Pisa": "Pisa","T2_US_Purde": "Purdue","T2_RU_RRC_KI": "RRC_KI","T2_DE_RWTH": "RWTH","T2_IT_Rome": "Rome","T2_UK_SGrid_RALPP": "Rutherford PPD","T2_RU_SINP": "SINP","T2_BR_SPRACE": "SPRACE","T2_IN_TIFR": "TIFR","T2_TW_Taiwan": "Taiwan","T2_US_UCSD": "UCSD","T2_MY_UPM_BIRUNI": "n/a","T2_US_Vanderbilt": "n/a","T2_PL_Warsaw": "Warsaw","T2_US_Wisconsin": "Wisconsin"}
  for site in matchList:
    if pledgeList.has_key(matchList[site]):
    	valPos = str(pledgeList[matchList[site]]).find('.') 
    	pledges[site] = int(str(pledgeList[matchList[site]])[0:valPos])
    else:
      	pledges[site] = "n/a"
  return pledges
#_______________________________________________________________________
#____________________function creates JSON TXT HTML file________________
def savetoFile(pledges, year,outputfile_txt):
  saveTime = time.strftime('%Y-%m-%d %H:%M:%S')
  url = " https://cmsweb.cern.ch/sitedb/prod/pledges "
  #_______________JSON__________________________________________________
  filename = year + outputfile_txt + ".json"
  fileOp = open(filename, "w")
  fileOp.write(unicode(simplejson.dumps(pledges, ensure_ascii=False)))
  fileOp.close()

  #_______________the List_____________________________________________
  filename = year + outputfile_txt + ".txt"
  fileOp = open(filename, "w")
  fileOp.write("Pledges[" + year + "]\n")
  for tmpPledges in pledges:
      if (pledges[tmpPledges]      == 0)     : color = 'yellow'
      if (pledges[tmpPledges]      > 0)      : color = 'green'
      if (str(pledges[tmpPledges]) == 'n/a') : color = 'white'
      fileOp.write('%-0s %20s %10s %10s %10s\n' % (saveTime, tmpPledges, str(pledges[tmpPledges]), color, url ))

  fileOp.close()

  #_______________html________________________________________________
  filename = year + outputfile_txt + ".html"
  fileOp = open(filename, "w")
  html = ''
  htmlTag    = '<html><body><h3>Pledges[' + year  + ']</h3><table>'
  htmlBody   = ''
  htmlEndTag = '</table></body></html>'

  for tmpPledges in pledges:
    htmlBody = htmlBody + "<tr><td>" + tmpPledges + "</td>" + "<td>" + str(pledges[tmpPledges]) + "</td></tr>";
  html = htmlTag + htmlBody + htmlEndTag
  fileOp.write(html) 
  fileOp.close()

# run program for last month, last 2 months and last 3 months
if __name__ == '__main__':
  outputfile_txt=sys.argv[1]
  year = sys.argv[2]
  print 'starting to fetch all pledges from siteDB'
  allPledgeList = fetch_all_pledges('cmsweb.cern.ch','/sitedb/data/prod/resource-pledges')
  pledges       = matchPledges(allPledgeList)
  savetoFile(pledges, year, outputfile_txt)
