from discord.ext import tasks
from pandas import DataFrame

@tasks.loop(minutes=1440.0)
async def csv_guild(self):
    nom_colonnes = ["nom_guilde","identifiant_guilde","nom_propriétaire","identifiant_propriétaire","nombre_membres","nombres_membres_réels","nombres_roles","nom_roles","identifiant_roles","noms_membres","nombre_salons","noms_salons","identifiants_salons","nombre_catégories", "noms_catégories","identifiants_catégorie","nombre_salons_vocaux", "noms_salons_vocaux","identifiants_salons_vocaux"]
    données = {a: [] for a in nom_colonnes}
    for guilde in self.client.guilds:
        données["nom_guilde"].append(guilde.name)
        données["identifiant_guilde"].append(guilde.id)
        données["nom_propriétaire"].append(guilde.owner.name)
        données["identifiant_propriétaire"].append(guilde.owner.id)
        données["nombre_membres"].append(len(guilde.members))
        données["nombre_membres_réels"].append(len([a for a in guilde.members if not a.bot]))
        données["nombres_roles"].append(len(guilde.roles))
        données["nom_roles"].append("/".join(role.name for role in guilde.roles))
        données["identifiants_roles"].append("/".join(str(role.id) for role in guilde.roles))

        données["noms_membres"].append("/".join(membre.id for membre in guilde.members))
        données["nombre_salons"].append(len(guilde.text_channels) + len(guilde.stage_channels))  
        salons = guilde.text_channels.extend(guilde.stage_channels)
        données["noms_salons"].append("/".join(salon.name for salon in salons))
        données["identifiants_salons"].append("/".join(str(salon.id) for salon in salons))
        données["nombre_catégories"].append(len(guilde.categories))
        données["noms_catégories"].append("/".join(catégorie.name for catégorie in guilde.categories))
        données["identifiants_catégorie"].append("/".join(str(catégorie.id) for catégorie in guilde.categories)) 
        données["nombre_salons_vocaux"].append(len(guilde.voice_channels))
        données["noms_salons_vocaux"].append("/".join(salon_vocal.name for salon_vocal in guilde.vocal_channels))
        données["identifiants_salons_vocaux"].append("/".join(str(salon_vocal.id) for salon_vocal in guilde.vocal_channels))
        données_dataframe = DataFrame(données, columns=nom_colonnes)
        print(données_dataframe)