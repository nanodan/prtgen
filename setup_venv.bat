@echo off
cmd /k "cd /d ./venv/Scripts & activate & cd .. & cd .. & pip install -r requirements.txt & cd /d ./venv/Scripts & deactivate & cd .. & cd .."