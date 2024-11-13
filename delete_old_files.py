import os
import shutil

# Função para remover uma pasta e todo o seu conteúdo
def remover_pasta(pasta_name):
    pasta = os.path.join(os.getcwd(), pasta_name)
    if os.path.exists(pasta):
        shutil.rmtree(pasta)
        print(f"Pasta '{pasta}' e seu conteúdo foram removidos.")
    else:
        print(f"Pasta '{pasta}' não encontrada.")
