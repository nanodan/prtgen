import os
from sys import platform

if platform == 'win32':
	os.system('pip install virtualenv')
	os.system('virtualenv venv')
	os.system('setup_venv.bat')
elif platform == 'darwin':
	os.system('conda create -y -n venv-prtgen python=2.7.13')
	os.system('./setup_venv.sh')