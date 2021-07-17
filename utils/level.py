import sqlite3

class LevelDB:
    
    def __init__(self, accès_dossier):
        self.database = sqlite3.connect(accès_dossier + "level.db")
        
    def __créer_une_table__(self, id_guilde):
        curseur = self.database.cursor()
        curseur.execute(f"""CREATE TABLE IF NOT EXISTS "{id_guilde}" (user_id INT PRIMARY KEY, xp BIGINT DEFAULT 0, level INT DEFAULT 0)""")
        curseur.close()
        self.database.commit()
        
    def __est_dans_la_table__(self, guilde, utilisateur):
        self.__créer_une_table__(guilde.id)
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT * FROM "{guilde.id}" WHERE user_id = ?""", (utilisateur.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return résultat is not None

    def ajouter_guilde(self, guilde):
        self.__créer_une_table__(guilde.id)

    def ajouter_utilisateur(self, guilde, utilisateur):
        self.ajouter_guilde(guilde)
        if self.__est_dans_la_table__(guilde, utilisateur):
            return
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""INSERT INTO "{guilde.id}" (user_id, xp, level) VALUES (?, ?, ?)""", (utilisateur.id, 0, 0))
            curseur.close()
            self.database.commit()           
            
    def avoir_informations_utilisateur(self, guilde, utilisateur):
        self.__créer_une_table__(guilde.id)
        if not self.__est_dans_la_table__(guilde, utilisateur):
            self.ajouter_utilisateur(guilde, utilisateur)
            return (0, 0)
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""SELECT xp, level FROM "{guilde.id}" WHERE user_id = ?""", (utilisateur.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return tuple(résultat)     
    
    def retourne_liste_rangs(self, guilde):
        self.__créer_une_table__(guilde.id)
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT user_id FROM "{guilde.id}" ORDER BY xp DESC""")
        return [item[0] for item in curseur.fetchall()]
    
    def __modifie_BDD__(self, guilde, utilisateur, xp, level):
        curseur = self.database.cursor()
        curseur.execute(f"""UPDATE "{guilde.id}" SET xp = ?, level = ? WHERE user_id = ?""",(xp, level, utilisateur.id))
        curseur.close()
        self.database.commit()
        
    def modifier_expérience(self, guilde, utilisateur, xp, level):
        self.ajouter_guilde(guilde)
        
        if not self.__est_dans_la_table__(guilde, utilisateur):
            self.ajouter_utilisateur(guilde, utilisateur)
            self.__modifie_BDD__(guilde, utilisateur, xp, level)
        else:
            self.__modifie_BDD__(guilde, utilisateur, xp, level)
            
    def supprimer_utilisateur(self, guilde, utilisateur):
        curseur = self.database.cursor()
        curseur.execute(f"""DELETE FROM "{guilde.id}" WHERE user_id = ?""", (utilisateur.id))
        curseur.close()
        self.database.commit()
        
    def supprimer_guilde(self, guilde):
        curseur = self.database.cursor()
        curseur.execute(f"""DROP TABLE "{guilde.id}" """)
        curseur.close()
        self.database.commit()