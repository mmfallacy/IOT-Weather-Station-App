@echo off
pip install -r requirements.txt

echo @echo off >> "Start Web App.cmd"
echo start "" http://localhost:35223 >>"Start Web App.cmd"
echo python main.py >>"Start Web App.cmd"
