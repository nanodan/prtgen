import os
from sys import platform

if platform == 'win32':
    os.system('activate venv-prtgen & cd prtApp & python prtGen.py')
elif platform == 'darwin':
    os.system('source activate venv-prtgen & cd prtApp & python prtGen.py')