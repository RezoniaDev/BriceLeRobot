import discord
import sqlite3

class HistoriqueDB:
    
    def __init__(self, accès_dossier, client, setup_bdd):
        self.database = sqlite3.connect(accès_dossier + "log.db")
        self.client = client
        self.setup_bdd = setup_bdd
        self.__créer_une_table__()
        
    def avoir_bdd_setup(self):
        return self.setup_bdd    
    
    def __créer_une_table__(self):
        curseur = self.database.cursor()
        curseur.execute(f"""CREATE TABLE IF NOT EXISTS logs (id_guilde INT PRIMARY KEY, id_salon_historique INT, id_catégorie INT)""")
        curseur.close()
        self.database.commit()
        
    def est_dans_la_table(self, guilde: discord.Guild) -> bool:
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT * FROM logs WHERE id_guilde = ? """, (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)

    def ajouter_une_guilde(self, guilde: discord.Guild, catégorie: discord.CategoryChannel, salon: discord.TextChannel):
        if not self.est_dans_la_table(guilde):
            curseur = self.database.cursor()
            curseur.execute(f"""INSERT INTO logs (id_guilde, id_catégorie, id_salon_historique) VALUES (?, ?, ?)""", (guilde.id, catégorie.id, salon.id))
            curseur.close()
            self.database.commit()
        else:
            self.modifie_catégorie(guilde, catégorie)
            self.modifie_salon(guilde, salon)           
            
    def avoir_identifiant_salon(self, guilde: discord.Guild):
        if self.est_dans_la_table(guilde):
            curseur = self.database.cursor()
            curseur.execute(f"""SELECT id_salon_historique FROM logs WHERE id_guilde = ?""", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return résultat[0]    
        else:
            return -1
    
    def ajouter_catégorie(self, guilde:discord.Guild, catégorie: discord.CategoryChannel):
        if not self.__catégorie_est_dans_la_table__(guilde):
            curseur = self.database.cursor()
            curseur.execute(f"""INSERT INTO logs (id_guilde, id_catégorie VALUES (?, ?)""", (guilde.id, catégorie.id))
            curseur.close()
            self.database.commit()
        else:
            self.modifie_catégorie(guilde, catégorie)

    def ajouter_salon(self, guilde:discord.Guild, salon: discord.TextChannel):
        if not self.__salon_est_dans_la_table__(guilde):
            curseur = self.database.cursor()
            curseur.execute(f"""INSERT INTO logs (id_guilde, id_salon_historique VALUES (?, ?)""", (guilde.id, salon.id))
            curseur.close()
            self.database.commit()
        else:
            self.modifie_salon(guilde, salon)

    def avoir_identifiant_catégorie(self, guilde: discord.Guild):
        if not self.est_dans_la_table(guilde):
            return -1
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""SELECT id_catégorie FROM logs WHERE id_guilde = ?""", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return résultat[0]

    def __catégorie_est_dans_la_table__(self, guilde):
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT id_catégorie FROM logs WHERE id_guilde = ? """, (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)

    def __salon_est_dans_la_table__(self, guilde):
        curseur = self.database.cursor()
        curseur.execute(f"""SELECT id_salon_historique FROM logs WHERE id_guilde = ? """, (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)


    def modifie_salon(self, guilde: discord.Guild, salon: discord.TextChannel):
        if not self.__salon_est_dans_la_table__(guilde):
            self.ajouter_salon(guilde, salon)
        else:
            curseur = self.database.cursor()
            curseur.execute(f"""UPDATE logs SET id_salon_historique = ? WHERE id_guilde = ?""",(salon.id, guilde.id))
            curseur.close()
            self.database.commit()
            
    def modifie_catégorie(self, guilde: discord.Guild, catégorie: discord.CategoryChannel):
        curseur = self.database.cursor()
        curseur.execute(f"""UPDATE logs SET id_catégorie = ? WHERE id_guilde = ?""",(catégorie.id, guilde.id))
        curseur.close()
        self.database.commit()
    
    def supprimer_guilde(self, guilde: discord.Guild):
        curseur = self.database.cursor()
        curseur.execute(f"""DELETE FROM logs WHERE id_guilde = ?""", (guilde.id, ))
        curseur.close()
        self.database.commit()