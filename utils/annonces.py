import sqlite3

class AnnoncesDB:

    def __init__(self, accès_dossier):
        self.database = sqlite3.connect(accès_dossier + "annonces.db")
        self.create_table()

    def create_table(self):
        curseur = self.database.cursor()
        curseur.execute("""CREATE TABLE IF NOT EXISTS annonces (guild_id BIGINT PRIMARY KEY NOT NULL, annonces_channel BIGINT NOT NULL)""")
        self.database.commit()
        curseur.close()

    def est_dans_la_table(self, guild_id):
        curseur = self.database.cursor()
        curseur.execute("""SELECT * FROM annonces WHERE guild_id = ?""", (guild_id,))
        résultat = curseur.fetchall()
        return not(résultat is None)

    def select_one_annonce_channel(self, guild_id):
        curseur = self.database.cursor()
        if not self.est_dans_la_table(guild_id):
            curseur.close()
            return None
        else:
            curseur.execute("""SELECT annonces_channel FROM annonces WHERE guild_id = ?""", (guild_id, ))
            réponse = curseur.fetchone()
            self.database.commit()
            curseur.close()
            return réponse[0] if réponse is not None else réponse

    def select_all_annonces_channel(self):
        curseur = self.database.cursor()
        curseur.execute("""SELECT * FROM annonces""")
        colonnes = curseur.fetchall()
        dictionnaire = dict()
        print(colonnes)
        for id_guilde, id_salon in colonnes:
            dictionnaire[id_guilde] = id_salon
        self.database.commit()
        curseur.close()
        return dictionnaire

    def insert_element(self, guild_id, annonces_channel):
        if self.est_dans_la_table(guild_id):
            self.update_element(guild_id, annonces_channel)
        curseur = self.database.cursor()
        curseur.execute("""INSERT INTO annonces (guild_id, annonces_channel) VALUES (?, ?)""",(guild_id, annonces_channel))
        self.database.commit()
        curseur.close()

    def update_element(self, guild_id, annonces_channel):
        if not self.est_dans_la_table(guild_id):
            self.insert_element(guild_id, annonces_channel)
        curseur = self.database.cursor()
        curseur.execute("""UPDATE annonces SET annonces_channel = ? WHERE guild_id = ?""", (annonces_channel, guild_id))
        self.database.commit()
        curseur.close()