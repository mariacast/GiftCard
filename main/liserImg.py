import sys
import subprocess as spp

upName = sys.argv[1]
spp.getstatusoutput("base64 -d /tmp/"+upName+" > /var/www/html/pool/"+upName)
spp.getstatusoutput("rm -frv /tmp/"+upName)
#spp.getstatusoutput("ffmpeg -i /tmp/ci_"+upName+" -vcodec h264 -acodec aac -strict -2 /var/www/html/pool/"+upName)
#spp.getstatusoutput("rm -frv /tmp/ci_"+upName)

