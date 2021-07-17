from utils.modules import ModulesDB
import os
import discord
from utils.util import a_un_rôle, a_un_salon, get_message, est_activé, avoir_préfixe_guilde
from discord import Permissions
from discord.ext import commands
from multicolorcaptcha import CaptchaGenerator


class Vérification(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.base_de_données = client.vérification_bdd
        self.captcha_generator = CaptchaGenerator(2)

    @commands.Cog.listener()
    async def on_member_join(self, membre: discord.Member):
        if est_activé(self.base_de_données.avoir_base_de_données_setup(), membre.guild, "vérification"):
            guilde = membre.guild
            inforamtions_vérifications_guilde = self.base_de_données.avoir_les_informations(guilde)
            lien_invitation = inforamtions_vérifications_guilde[0]
            rôle_non_vérifiée = guilde.get_role(inforamtions_vérifications_guilde[1])
            rôle_vérifiée = guilde.get_role(inforamtions_vérifications_guilde[2])
            await membre.add_roles(rôle_non_vérifiée)
            salon_vérificaiton = await guilde.create_text_channel(f"vérification-{membre.display_name}", overwrites={guilde.me: discord.PermissionOverwrite(read_messages=True, send_messages=True), membre: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
            captcha = self.captcha_generator.gen_captcha_image(difficult_level=5, multicolor=True)
            self.base_de_données.ajouter_dans_les_captcha(guilde, membre, captcha["characters"], salon_vérificaiton)
            await salon_vérificaiton.send("Vous **devez** résoudre le captcha suivant : ")
            image = captcha["image"]
            image.save("captcha.png", "png")
            await salon_vérificaiton.send(file=discord.File("captcha.png"))
            os.remove("captcha.png")
            
    @commands.Cog.listener() 
    async def on_message(self, message: discord.Message):
        if est_activé(self.base_de_données.avoir_base_de_données_setup(), message.channel.guild, "vérification"):
            
            guilde = message.guild
            auteur = message.author
            inforamtions_vérifications_guilde = self.base_de_données.avoir_les_informations(guilde)
                
            if inforamtions_vérifications_guilde != None:   
                lien_invitation = inforamtions_vérifications_guilde[0]
                rôle_non_vérifiée = guilde.get_role(inforamtions_vérifications_guilde[1])
                rôle_vérifiée = guilde.get_role(inforamtions_vérifications_guilde[2])
                
                if self.base_de_données.__est_dans_la_table_captcha__(guilde, auteur):
                    code, id_salon = self.base_de_données.avoir_le_code(guilde, auteur)
                    salon = self.client.get_channel(id_salon)
                    if message.content == code:      
                        await salon.delete()
                        await auteur.remove_roles(rôle_non_vérifiée)
                        await auteur.add_roles(rôle_vérifiée)
                    else:
                        await salon.delete()
                        await auteur.send(f"Vous avez raté le captcha ! Réessayez avec ce lien : {lien_invitation}.")
                        await auteur.kick(reason="Captcha raté !")
                    self.base_de_données.retirer_une_personne(guilde, auteur)
                    
                
async def setup_vérification(client: commands.Bot, ctx):
    guilde = ctx.guild
    réponse_message = await get_message(client, ctx, "Quel est le salon où les gens rejoignent ?", "Mentionnez-le après ce message", 0xF5DF4D, 120)
    if len(a_un_salon(réponse_message)) == 0:
        await ctx.send("Il faut que vous mentionnez un salon")
        return
    else:
        id_salon_caractères = a_un_salon(réponse_message)[0]
        identifiant_salon = int(id_salon_caractères.lstrip("<#").rstrip(">"))
        salon = client.get_channel(identifiant_salon)
        lien_invitation = await salon.create_invite(reason="Invitation pour le robot.")
        lien_invitation = lien_invitation.url
    réponse_rôle = await get_message(client, ctx, "Quel est le rôle donné à tout le monde ?", "Mentionnez-le après ce message (si il y a aucun rôle, mettez None)", 0xF5DF4D, 120)
    rôle_vérifié = None
    if réponse_rôle.lower() != "none":
        if (len(a_un_rôle(réponse_rôle)) == 0):
            await ctx.send("Il faut que vous mentionnez un rôle ou mettre None si vous voulez mettre aucun message !")
            return
        else:
            id_rôle_caractères = a_un_rôle(réponse_rôle)[0]
            identifiant_rôle = int(id_rôle_caractères.lstrip("<@&").rstrip(">"))
            rôle_vérifié = guilde.get_role(identifiant_rôle)
    rôle_non_vérifié = await guilde.create_role(name="Non vérifié", permissions=Permissions.none())
    
    for salon_temporaire in guilde.channels:
        await salon_temporaire.set_permissions(rôle_non_vérifié, read_messages=False, send_messages=False)
    
    client.vérification_bdd.ajouter_dans_la_table(guilde, rôle_non_vérifié, rôle_vérifié, lien_invitation)
    client.modules_db.modifier_status_extension(guilde, "vérification", True)
    await ctx.send("L'extension Vérification est bien paramétrée ! :white_check_mark:")
    
def setup(client):
    print("L'extension Vérification est activée !")
    client.add_cog(Vérification(client))