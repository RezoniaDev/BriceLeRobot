import sqlite3
import discord
from discord.ext import commands

class SpoilDB:

    def __init__(self, accès_dossier, client: commands.Bot) -> None:
        self.client = client
        self.base_de_données = sqlite3.connect(accès_dossier + "spoil.db")
        self.__créer_la_table__()

    def __créer_la_table__(self) -> None:
        curseur = self.base_de_données.cursor()
        curseur.execute("""CREATE TABLE IF NOT EXISTS spoil (id_guilde BIGINT PRIMARY KEY NOT NULL, salon_spoil BIGINT NOT NULL)""")
        self.base_de_données.commit()
        curseur.close()

    def __est_dans_la_table__(self, guilde: discord.Guild) -> bool:
        curseur = self.base_de_données.cursor()
        curseur.execute("""SELECT * FROM spoil WHERE id_guilde = ?""", (guilde.id,))
        result = curseur.fetchall()
        if len(result) == 0:
            curseur.close()
            return False
        else:
            curseur.close()
            return True

    async def avoir_le_salon_spoil(self, guilde: discord.Guild):
        curseur = self.base_de_données.cursor()
        if not self.__est_dans_la_table__(guilde):
            curseur.close()
            return None
        else:
            curseur.execute("""SELECT salon_spoil FROM spoil WHERE id_guilde = ?""", (guilde.id, ))
            réponse = curseur.fetchone()
            self.base_de_données.commit()
            curseur.close()
            salon = await self.client.fetch_channel(réponse[0])
            return salon
            
    def avoir_tous_les_salons_spoil(self) -> dict:
        curseur = self.base_de_données.cursor()
        curseur.execute("""SELECT * FROM spoil""")
        colonnes = curseur.fetchall()
        dictionnaire = dict()
        for colonne in colonnes:
            salon = self.client.fetch_channel(colonne[1])
            print(salon)
            dictionnaire[colonne[0]] = salon 
        self.base_de_données.commit()
        curseur.close()
        return dictionnaire

    def insérer_un_salon(self, guilde: discord.Guild, salon_spoil: discord.TextChannel) -> None:
        if self.__est_dans_la_table__(guilde):
            self.modifier_un_salon(guilde, salon_spoil)
            return
        curseur = self.base_de_données.cursor()
        curseur.execute("""INSERT INTO spoil (id_guilde, salon_spoil) VALUES (?, ?)""",(guilde.id, salon_spoil.id))
        self.base_de_données.commit()
        curseur.close()

    def modifier_un_salon(self, guilde: discord.Guild, salon_spoil: discord.TextChannel) -> None:
        if not self.__est_dans_la_table__(guilde):
            self.insérer_un_salon(guilde, salon_spoil)
            return
        else:
            curseur = self.base_de_données.cursor()
            curseur.execute("""UPDATE spoil SET salon_spoil = ? WHERE id_guilde = ?""", (salon_spoil.id, guilde.id))
            self.base_de_données.commit()
            curseur.close()
    
    def supprimer_la_guilde(self, guilde: discord.Guild) -> None:
        if not self.__est_dans_la_table__(guilde):
            return
        else:
            curseur = self.base_de_données.cursor()
            curseur.execute("""DELETE FROM spoil WHERE id_guilde = ?""", tuple({guilde.id}))
            curseur.close()
            self.base_de_données.commit()