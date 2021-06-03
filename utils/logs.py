import sqlite3

class LogDB:
    
    def __init__(self):
        self.database = sqlite3.connect(".\données\log.db")
        self.__create_table__()
        
    def __create_table__(self):
        curseur = self.database.cursor()
        curseur.execute(f"""CREATE TABLE IF NOT EXISTS logs (guild_id INT PRIMARY KEY, log_channel INT, category_id INT)""")
        curseur.close()
        self.database.commit()
        
    def est_dans_la_table(self, guilde):
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT * FROM logs WHERE guild_id = ? """, (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)

    def ajouter_log_channel(self, guilde, catégorie, salon):
        if self.est_dans_la_table(guilde):
            return
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""INSERT INTO logs (guild_id, category_id, log_channel) VALUES (?, ?, ?)""", (guilde.id, catégorie.id, salon.id))
            curseur.close()
            self.database.commit()           
            
    def get_log_channel(self, guilde):
        if not self.est_dans_la_table(guilde):
            return -1
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""SELECT log_channel FROM logs WHERE guild_id = ?""", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return résultat[0]    
    
    def get_category_id(self, guilde):
        if not self.est_dans_la_table(guilde):
            return -1
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""SELECT caterogy_id FROM logs WHERE guild_id""", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return résultat[0]
    
    def modifie_salon(self, guilde, salon):
        curseur = self.database.cursor()
        curseur.execute(f"""UPDATE logs SET log_channel = ? WHERE guild_id = ?""",(salon.id, guilde.id))
        curseur.close()
        self.database.commit()
            
    def modifie_catégorie(self, guilde, catégorie):
        curseur = self.database.cursor()
        curseur.execute(f"""UPDATE logs SET category_id = ? WHERE guild_id = ?""",(catégorie.id, guilde.id))
        curseur.close()
        self.database.commit()
    
    def supprimer_guilde(self, guilde, utilisateur):
        curseur = self.database.cursor()
        curseur.execute(f"""DELETE FROM logs WHERE guild_id = ?""", (guilde.id))
        curseur.close()
        self.database.commit()