import sqlite3
import discord

class ModulesDB:
    
    def __init__(self, liste_modules: list[str]):
        self.database = sqlite3.connect(".\données\modules.db")
        self.__créer_la_table__()
        self.liste_modules = liste_modules
        
    def __créer_la_table__(self):
        curseur = self.database.cursor()
        curseur.execute("CREATE TABLE IF NOT EXISTS modules (guild_id BIGINT  NOT NULL, level TINYINT NOT NULL DEFAULT 0, log TINYINT NOT NULL DEFAULT 0, PRIMARY KEY (guild_id));")
        curseur.close()
        self.database.commit()
        
    def __ajouter_extension__(self, nom_module: str):
        curseur = self.database.cursor()
        curseur.execute(f"ALTER TABLE modules ADD {nom_module} TINYINT NOT NULL DEFAULT 0")
        curseur.close()
        self.database.commit()    
    
    def __est_dans_la_table__(self, guilde: discord.Guild):
        curseur = self.database.cursor()
        curseur.execute("SELECT * FROM modules WHERE guild_id = ?", (guilde.id,))
        résultat = curseur.fetchone()
        curseur.close()
        return résultat is not None   

    def ajoute_guilde(self, guilde: discord.Guild):
        if self.__est_dans_la_table__(guilde):
            return
        curseur = self.database.cursor()
        curseur.execute("INSERT INTO modules (guild_id, level) VALUES ( ?, ?)", (guilde.id, 0))
        curseur.close()
        self.database.commit()

    def avoir_status_extensions(self, guilde: discord.Guild):
        if not self.__est_dans_la_table__(guilde):
            self.ajoute_guilde(guilde)
            return {i: 0 for i in self.liste_modules}
        else:
            curseur = self.database.cursor()
            curseur.execute("SELECT * FROM modules WHERE guild_id = ?", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            résultat_sans_id_guilde = [résultat[i] for i in range(1, len(résultat))]
            return {
                nom_module: bool(status)
                for nom_module, status in zip(self.liste_modules, résultat_sans_id_guilde)
            }
        
    def avoir_status_extension(self, guilde: discord.Guild,  nom_module: str) -> bool:
        if nom_module not in self.liste_modules:
            return False
        if not self.__est_dans_la_table__(guilde):
            self.ajoute_guilde(guilde)
            return False
        else:
            curseur = self.database.cursor()
            curseur.execute(f"SELECT {nom_module} FROM modules WHERE guild_id = ?", (guilde.id,))
            résultat = curseur.fetchone()
            curseur.close()
            return bool(résultat[0])
                
    def modifier_status_extension(self, guilde: discord.Guild, nom_module: str, status: bool):
        if nom_module not in self.liste_modules:
            return None        
        if not self.__est_dans_la_table__(guilde):
            self.ajoute_guilde(guilde)
            self.modifier_status_extension(guilde, nom_module, status)
        curseur = self.database.cursor()
        curseur.execute(f"UPDATE modules SET {nom_module} = ? WHERE guild_id = ?", (1 if status else 0, guilde.id))
        curseur.close()
        self.database.commit()
            
    def supprimer_extension(self, guilde: discord.Guild):
        curseur = self.database.cursor()
        curseur.execute("DELETE FROM modules WHERE guild_id = ?", (guilde.id))
        curseur.close()
        self.database.commit()
