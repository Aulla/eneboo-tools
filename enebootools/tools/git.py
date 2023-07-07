import os

def resolve_current_branch(folder_path):
    # obtener la rama actual de una carpeta git
    os.chdir(folder_path)
    return os.popen("git branch --show-current").read().strip()