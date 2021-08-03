import datetime,time
import os,sys
import configparser as  ConfigParser
#import pymssql
import splunklib.results as results
from time import sleep
from splunklib.binding import HTTPError
import splunklib.client as client
import logging 

class util():

#############################
 def __init__(self):
#############################
  self.logfile = ""
  self.logger=logging.getLogger('-')
 
 ##########################################
 def setlogger(self):
 ##########################################
  self.logger.setLevel(logging.DEBUG)
  # create file handler which logs even debug messages
  fh = logging.FileHandler(self.logfile )
  fh.setLevel(logging.DEBUG)
  self.logger.addHandler(fh)


 ##########################################
 def getsplunkdaterange(self,dt1, hr1 ):
 ##########################################
 #os.environ["TZ"]="UTC"
  pull_from = datetime.datetime.strptime(dt1, '%Y-%m-%d %H:%M:%S')
  pull_to =  pull_from + datetime.timedelta(hours=hr1)
  #print pull_from, pull_to
  pattern='%Y-%m-%d %H:%M:%S' 
  earliest=int(time.mktime(time.strptime(str(pull_from),pattern)))
  latest=int(time.mktime(time.strptime(str(pull_to),pattern)))
  return [earliest,latest]   

 ##################################
 def load_config(self,prop_file):
 ##################################
  config = ConfigParser.RawConfigParser()
  if os.path.isfile(prop_file):
      config.read(prop_file)
  else:
      print ("WARN : file not found "+prop_file)
      self.logger.error("WARN : file not found "+prop_file)

  return config 


 ###################################
 def getconfigkeys(self,vconfig,vsection):
 ###################################

  try:
     return dict(vconfig.items(vsection))
  except:
     print ("WARN  : unable to get config keys for section "+vsection ) 
     self.logger.error( "WARN  : unable to get config keys for section "+vsection)
     return {}


 ##################################
 def get_ssconn(self,cfgfile,dbname):
 ##################################

  cfg=self.load_config(cfgfile )
  if cfg.has_section(dbname):
     pass        
  else:
     print ("ERROR : No section found "+"cccm" )
     self.logger.error( "ERROR : No section found "+dbname )
     sys.exit(1)

  mydict=self.getconfigkeys(cfg,dbname )
  username=mydict['username']        
  pwd_env_var=mydict['pwd_env_var']
  try:
     password=os.environ[pwd_env_var]             

  except:
     print ("ERROR : Environment variable ",pwd_env_var," Not defined ")
     self.logger.error( "ERROR : Environment variable ",pwd_env_var," Not defined ")
     sys.exit(1)

  server=mydict['server']
  dbname=dbname 
  conn=""
  try:
    conn = pymssql.connect(server=server , user=username, password=password , database=dbname )
  except Exception as e:
    print ("ERROR : unable to connect to databsae "+dbname)
    self.logger.error( "ERROR : unable to connect to databsae "+dbname)
    print (str(e))
    self.logger.error( str(e))
    sys.exit(1)

  return conn 

 ############################
 def splunk_conn(self,cfgfile):
 ############################


  cfg=self.load_config(cfgfile )
  mydict=self.getconfigkeys(cfg,'splunk' )

  USERNAME=mydict['username']
  try:
    PASSWORD=os.environ['SPLUNK_PASSWORD']
  except:
    print ("# INFO : Environment Variable SPLUNK_PASSWORD not set ")
    self.logger.error( "# INFO : Environment Variable SPLUNK_PASSWORD not set " )
    sys.exit(1)


  PORT=mydict['port']
  HOST=mydict['host']
  
  # Create a Service instance and log in
  try:
    service = client.connect( host=HOST, port=PORT, username=USERNAME, password=PASSWORD, scheme="https")
    print ("# Connected to Splunk ")
    self.logger.info( "# Connected to Splunk ")
  except Exception as e:
    print ("# ERROR : Unable to connect to Splunk ")
    self.logger.error( "# ERROR : Unable to connect to Splunk ")
    sys.exit(1)

  return service


 ##################################################
 def splunk_search(self,service,search,kwargs_export ):
 ###################################################

  
  try:
      service.parse(search, parse_only=True)
  except HTTPError as e:
      self.logger.error( str(e) )
      print (str(e))


  job = service.jobs.create(search, **kwargs_export )


  while True:
      while not job.is_ready():
        pass
      stats = {"isDone": job["isDone"],
	      "doneProgress": float(job["doneProgress"])*100,
		"scanCount": int(job["scanCount"]),
		"eventCount": int(job["eventCount"]),
		"resultCount": int(job["resultCount"])}

      status = ("\r%(doneProgress)03.1f%%  %(scanCount)d scanned  "
		"%(eventCount)d matched  %(resultCount)d results") % stats

      sys.stdout.write(status)
      self.logger.info(status)
      sys.stdout.flush()
      if stats["isDone"] == "1":
         sys.stdout.write("\n\nDone!\n\n")
         self.logger.info("\n\nDone!\n\n")
         break
      sleep(2)

  return(job)








