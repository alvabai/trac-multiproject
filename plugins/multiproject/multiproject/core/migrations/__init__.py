import os


def list_migrations():
    files = []
    path  = __file__.rsplit('/',1)[0]
    for file in os.listdir(path):
        if file.endswith('.py') and file != '__init__.py':
            files.append(file[:-3])
    return files

__all__ = list_migrations()
