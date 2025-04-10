import subprocess
from Beatrice_Advisors import display_beatrice
from Christina_Lewis import display_christina

# Full path to the app.py file
subprocess.call("streamlit run app.py --server.port=8080")
