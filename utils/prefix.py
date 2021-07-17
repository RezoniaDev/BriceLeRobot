import sqlite3

class PrefixDB:
    
    def __init__(self, accès_dossier):
        self.database = sqlite3.connect(accès_dossier + "prefix.db")
        self.__create_table__()
        
    def __create_table__(self):
        curseur = self.database.cursor()
        curseur.execute("CREATE TABLE IF NOT EXISTS prefix (guild_id INT PRIMARY KEY, prefix TEXT DEFAULT '&')")
        curseur.close()
        self.database.commit()
        
    def __est_dans_la_table__(self, guilde):
        curseur = self.database.cursor()
        curseur.execute("SELECT * FROM prefix WHERE guild_id = ?", (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not résultat is None   

    def ajoute_guilde(self, guilde):
        if self.__est_dans_la_table__(guilde):
            return
        else:
            curseur = self.database.cursor()
            curseur.execute("INSERT INTO prefix VALUES (?, ?)", (guilde.id, "&"))
            curseur.close()
            self.database.commit()

    def get_prefix(self, guilde):
        if not self.__est_dans_la_table__(guilde):
            self.ajoute_guilde(guilde)
            return "&"
        else:
            curseur = self.database.cursor()
            curseur.execute("SELECT prefix FROM prefix WHERE guild_id = ?", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return résultat[0]     
            
        
    def modify_prefix(self, guilde, préfixe):
        curseur = self.database.cursor()
        curseur.execute("UPDATE prefix SET prefix = ? WHERE guild_id = ?", (préfixe, guilde.id))
        curseur.close()
        self.database.commit()
            
    def delete_prefix(self, guilde):
        curseur = self.database.cursor()
        curseur.execute("DELETE FROM prefix WHERE guild_id = ?", (guilde.id))
        curseur.close()
        self.database.commit()
