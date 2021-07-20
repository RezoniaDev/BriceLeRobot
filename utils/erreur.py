import discord
from discord.ext import commands
import sqlite3
from datetime import datetime


class Erreur:
    
    def __init__(self, client: commands.AutoShardedBot, identifiant: int, id_envoyeur: int, nom_guilde: str, id_guilde: int, description: str, date: datetime):
        self.client = client
        self.identifiant = identifiant
        self.id_envoyeur = id_envoyeur
        self.envoyeur = self.client.get_user(self.id_envoyeur)
        self.id_guilde = id_guilde
        self.guilde = self.client.get_guild(self.id_guilde)
        self.nom_guilde = nom_guilde
        self.description = description
        self.date = date
        
    def avoir_client(self):
        return self.client
    
    def avoir_identifiant(self):
        return self.identifiant
    
    def avoir_guilde(self):
        return self.guilde
    
    def avoir_envoyeur(self):
        return self.envoyeur
    
    def avoir_description(self):
        return self.description
    
    def avoir_date(self):
        return self.date

    def modifier_identifiant(self, identifiant):
        self.identifiant = identifiant
        
    def modifier_envoyeur(self, envoyeur):
        self.envoyeur = envoyeur
        self.id_envoyeur = self.envoyeur.id
    
    def modifier_guilde(self, guilde):
        self.guilde = guilde
        self.id_guilde = guilde.id
        self.nom_guilde = guilde.name
    
    def modifier_description(self, description):
        self.description = description
    
    def modifier_date(self, date):
        self.date = date
        
    def avoir_embed(self):
        a_embed = discord.Embed(
        color=0xF5DF4D,
        )
        a_embed.add_field(name="Numéro de l'erreur : ", value=self.identifiant, inline=False)
        a_embed.add_field(name="Soumetteur :", value=f"<@{self.envoyeur.id}> (*{self.id_envoyeur}*)", inline=False)
        a_embed.add_field(name="Description :", value=self.description, inline=False)
        a_embed.add_field(name="Nom de la guilde :", value=self.guilde.name, inline=False)
        a_embed.add_field(name="Identifiant de la guilde :", value=self.guilde.id, inline=False)
        a_embed.add_field(name="Date :", value=self.date.strftime("le %x à %X"), inline=False)
        a_embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar)
        return a_embed

class ErreurBDD:

    def __init__(self, client) -> None:
        self.client = client
        self.base_de_données = sqlite3.connect("./données/erreur.db")
        self.__créer_les_tables__()
        
    def __créer_les_tables__(self) -> None:
        curseur = self.base_de_données.cursor()
        curseur.execute(
            """CREATE TABLE IF NOT EXISTS erreur (identifiant INTEGER PRIMARY KEY AUTOINCREMENT, id_envoyeur BIGINT NOT NULL
            , nom_guilde TEXT NOT NULL, id_guilde BIGINT NOT NULL,  description TEXT NOT NULL, date timestamp)""")
        self.base_de_données.commit()
        curseur.close()    

    def __est_dans_la_table__(self, identifiant: int) -> None:
        curseur = self.base_de_données. cursor()
        curseur.execute("""SELECT * FROM erreur WHERE identifiant = ?""", (identifiant,))
        result = curseur.fetchall()
        if len(result) == 0:
            curseur.close()
            return False
        else:
            curseur.close()
            return True

    def avoir_une_erreur(self, identifiant: int) -> Erreur:
        curseur = self.base_de_données.cursor()
        if not self.__est_dans_la_table__(identifiant):
            curseur.close()
            return None
        else:
            curseur.execute("""SELECT * FROM erreur WHERE identifiant = ?""", (identifiant, ))
            réponse = curseur.fetchone()
            self.base_de_données.commit()
            curseur.close()
            return Erreur(self.client, réponse[0], réponse[1], réponse[3], réponse[2], réponse[4], réponse[5])

    def avoir_toutes_les_erreurs(self) -> set:
        curseur = self.base_de_données.cursor()
        curseur.execute("""SELECT * FROM erreur""")
        colonnes = curseur.fetchall()
        erreurs = set()
        for réponse in colonnes:
            erreurs.add(Erreur(self.client, réponse[0], réponse[1], réponse[3], réponse[2], réponse[4], réponse[5]))
        self.base_de_données.commit()
        curseur.close()
        return erreurs

    def ajouter_une_erreur(self, envoyeur: discord.User, guilde: discord.Guild, description: str, date: datetime):
        curseur = self.base_de_données.cursor()
        curseur.execute("""INSERT INTO erreur (id_envoyeur, nom_guilde, id_guilde, description, date) VALUES (?, ?, ?, ?, ?)
        """, (envoyeur.id , guilde.id, guilde.name, description, date))
        identifiant = curseur.lastrowid
        self.base_de_données.commit()
        curseur.close()
        return Erreur(self.client, identifiant, envoyeur.id, guilde.name, guilde.id, description, date)

    def enlever_une_erreur(self, identifiant):
        curseur = self.base_de_données.cursor()
        if not self.__est_dans_la_table__(identifiant):
            return
        else:
            curseur.execute("""DELETE FROM erreur WHERE identifiant = ?""", (identifiant, ))
            self.base_de_données.commit()
            curseur.close()