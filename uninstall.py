import os
from sys import platform

if platform == 'win32':
    os.system('conda remove --name venv-prtgen --all -y')
elif platform == 'darwin':
    os.system('conda remove --name venv-prtgen --all -y')