cd `dirname $0`
conda create -y -n venv-prtgen python=2.7.13
source activate venv-prtgen
pip install -r requirements_darwin.txt