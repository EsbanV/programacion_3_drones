import subprocess
import sys

# Ejecuta el dashboard
dashboard = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "visual/dashboard.py"])

# Ejecuta la API (espera a que dashboard inicie primero si quieres)
api = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--reload"])

try:
    dashboard.wait()
    api.wait()
except KeyboardInterrupt:
    dashboard.terminate()
    api.terminate()
