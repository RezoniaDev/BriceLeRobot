import sqlite3
import discord

class VérificationDB:
    
    nom_table = "vérification"
    
    def __init__(self, accès_dossier, setup_bdd) -> None:
        self.base_de_données= sqlite3.connect(accès_dossier + "vérification.db")
        self.setup_bdd = setup_bdd
        self.__créer_la_table__()
    
    def avoir_base_de_données_setup(self):
        return self.setup_bdd
    
    def __créer_la_table__(self) -> None:
        curseur = self.base_de_données.cursor() 
        curseur.execute("CREATE TABLE IF NOT EXISTS vérification ( id_guilde INT PRIMARY KEY, invitation VARCHAR, role_non_vérifié INT, role_par_défaut INT)")
        curseur.execute("CREATE TABLE IF NOT EXISTS vérification_captacha ( id_guilde INT PRIMARY KEY, id_auteur INT, id_salon INT, code VARCHAR)")
        curseur.close()
        self.base_de_données.commit()     
    
    def __est_dans_la_table__(self, guilde: discord.Guild) -> bool:
        curseur = self.base_de_données.cursor()
        curseur.execute(f"""SELECT * FROM {self.nom_table} WHERE id_guilde = ? """, (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)

    def ajouter_dans_la_table(self, guilde: discord.Guild, rôle_non_vérifié: discord.Role, rôle_par_défault: discord.Role, lien_invitation: str) -> None:
        curseur = self.base_de_données.cursor()
        if not self.__est_dans_la_table__(guilde):
            curseur.execute(f"""INSERT INTO {self.nom_table} (id_guilde, invitation, role_non_vérifié, role_par_défaut) VALUES (?,?,?,?)""", (guilde.id, lien_invitation, rôle_non_vérifié.id, -1 if rôle_par_défault is None else rôle_par_défault.id))
        else:
            curseur.execute(f"""UPDATE {self.nom_table} SET invitation = ?, role_non_vérifié = ?, role_par_défaut = ? WHERE id_guilde = ? """, (lien_invitation, rôle_non_vérifié.id, -1 if rôle_par_défault is None else rôle_par_défault.id, guilde.id))
        curseur.close()
        self.base_de_données.commit()
    
    def __est_dans_la_table_captcha__(self, guilde: discord.Guild, auteur: discord.Member) -> bool:
        curseur = self.base_de_données.cursor()
        curseur.execute(f"""SELECT * FROM {self.nom_table}_captacha WHERE id_guilde = ? AND id_auteur = ? """, (guilde.id, auteur.id))
        résultat = curseur.fetchone()
        curseur.close()
        return not(résultat == None)
    
    def ajouter_dans_les_captcha(self, guilde: discord.Guild, auteur: discord.Member, code: str, salon: discord.TextChannel) -> None:
        curseur = self.base_de_données.cursor()
        
        if not self.__est_dans_la_table_captcha__(guilde, auteur):
            curseur.execute("""INSERT INTO vérification_captacha (id_guilde, id_auteur, id_salon, code) VALUES (?,?, ?, ?)""", (guilde.id, auteur.id, salon.id, code))
            curseur.close()
            self.base_de_données.commit()
    
    def avoir_le_code(self, guilde: discord.Guild, auteur: discord.Member) -> tuple:
        if not self.__est_dans_la_table_captcha__(guilde, auteur):
            return None
        else:
            curseur = self.base_de_données.cursor()
            curseur.execute("""SELECT code, id_salon FROM vérification_captacha WHERE id_guilde = ? AND id_auteur = ?""", (guilde.id, auteur.id))
            résultat = curseur.fetchone()
            curseur.close()
            self.base_de_données.commit()
            return tuple(résultat)
    
    def retirer_une_personne(self, guilde: discord.Guild, auteur: discord.Member) -> None:
        if not self.__est_dans_la_table_captcha__(guilde, auteur):
            return
        else:
            curseur = self.base_de_données.cursor()
            curseur.execute("""DELETE FROM vérification_captacha WHERE id_guilde = ? AND id_auteur = ?""", (guilde.id, auteur.id))
            curseur.close()
            self.base_de_données.commit()
            
    def avoir_les_informations(self, guilde: discord.Guild) -> list:
        curseur = self.base_de_données.cursor()
        if not self.__est_dans_la_table__(guilde):
            return None
        else:
            curseur.execute(f"""SELECT invitation, role_non_vérifié, role_par_défaut FROM {self.nom_table} WHERE id_guilde = ?""", (guilde.id, ))
            résultat = list(curseur.fetchone())
            if résultat[2] == -1:
                résultat[2] = None
            return résultat
        curseur.close()