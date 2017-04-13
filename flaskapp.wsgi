import sys,os
sys.path.insert(0,'/var/www/bigdata')
os.chdir("/var/www/bigdata")
from flaskapp import app as application
