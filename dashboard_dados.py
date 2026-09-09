import glob
import os


arquivo_mais_recente = glob.glob(
    r'C:\Users\Kevin Rosa\PycharmProjects\PythonProject\ADEUS FAB\coletor-trafego-aereo-sul\voos_sul_*.json'
)
print(max(arquivo_mais_recente, key=os.path.getmtime))

