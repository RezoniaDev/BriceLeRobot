from pathlib import Path
       
def get_path():
    """
    Cette fonction donne le chemin de `bot.py`

    :return: cwd (str) : Le chemin du dossier de `bot.py`
    """
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd

