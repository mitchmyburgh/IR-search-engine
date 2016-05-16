import os
from datetime import datetime

from index import index

try:
	os.mkdir ("indexes")
except:
	pass

startTime = datetime.now()
for i in range(1, 17):
	index("testbeds/testbed"+str(i), i)

print ("Time taken: "+str(datetime.now() - startTime))