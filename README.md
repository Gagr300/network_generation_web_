# network_generation_web

windows powershell
```
python -m venv .venv
.\\.venv\\Scripts\\activate.ps1
python.exe -m pip install --upgrade pip  setuptools wheel
pip install -r .\backend\requirements.txt
pip install pandas --upgrade --only-binary :all:
```