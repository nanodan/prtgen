import os
from sys import platform

if platform == 'win32':
	os.system('run.bat')
elif platform == 'darwin':
	os.system('./run.sh')