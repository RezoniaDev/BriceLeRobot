import discord
from utils.modules import ModulesDB
from discord.ext import commands
from utils.util import get_message, a_un_salon, est_activé, avoir_préfixe_guilde
from discord.ext.commands.core import has_permissions


class Spoil(commands.Cog, name="Spoil"):
    
    
    def __init__(self, client) -> None:
        self.client = client
        self.base_de_données = client.spoil_bdd
        self.setup_bdd = client.modules_db
        
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        guilde = message.channel.guild
        salon_spoil = await self.base_de_données.avoir_le_salon_spoil(guilde)
        if (
            est_activé(self.setup_bdd, guilde, "spoil") 
            and salon_spoil is not None 
            and (salon_spoil.id == message.channel.id)
            and not message.author.bot
        ):
            message_content = message.content
            await message.delete()
            if message_content == "":
                message_content = " "
            await message.channel.send(f"Spoil de <@{message.author.id}> : \n||"+ message_content +"||")
        
            
    @commands.command(
        name="spoil",
        description="""Permet de cacher un "spoil" pour que seulement les gens qui veulent se faire "spoil" le voient.""",
        usage="spoil <text>"
    )        
    async def __spoil(self, ctx, *args):
        guilde = ctx.guild
        if not est_activé(self.setup_bdd, guilde, "spoil"):
            await ctx.send(f"Le module **Spoil** n'est pas activé ! Si vous voulez l'activer, faîtes `{avoir_préfixe_guilde(self.client, guilde)}setup` !")
            return
        else:
            arguments = list(args)
            if len(arguments) == 0:
                await ctx.send(f"Vous devez écrire un message ! Usage de la commande : `{avoir_préfixe_guilde(self.client, guilde)}spoil <texte>`.")
                return
            message = " ".join(*args)
            await ctx.send(f"Spoil de <@{ctx.author.id}> : \n||"+ message +"||")
                
    @has_permissions(administrator=True)
    @commands.command(
        name="register_spoil",
        description="Permet d'enregister le salon où a été envoyé la commande comme un salon `spoil`.",
        usage="&register_spoil (channel)"
    )
    async def __register_spoil(self, ctx, salon: discord.TextChannel):
        guilde = ctx.guild
        if not est_activé(self.setup_bdd, guilde, "spoil"):
            await ctx.send(f"Le module **Spoil** n'est pas activé ! Si vous voulez l'activer, faîtes `{avoir_préfixe_guilde(self.client, guilde)}setup` !")
            return
        else:
            if salon is None:
                salon = ctx.channel
            self.base_de_données.insérer_un_salon(guilde, salon)
            await ctx.send(f"Le salon `{salon.name}` est maintenant le salon à spoil !")

    @commands.Cog.listener()
    async def on_guild_remove(self, guilde:discord.Guild):
        self.setup_bdd.modifier_status_extension(guilde, "spoil", False)
        
    
async def setup_spoil(client: commands.Bot, ctx):
    message = await get_message(client, ctx, "Voulez-vous un salon `spoil` ?", "Si oui, mentionnez-le, sinon mettez `None`.")
    if len(a_un_salon(message)):
        salon = await client.fetch_channel(int(a_un_salon(message)[0].lstrip("<#").rstrip(">")))
        client.spoil_bdd.insérer_un_salon(salon.guild, salon)
    client.modules_db.modifier_status_extension(salon.guild if salon is not None else ctx.guild, "spoil", True)
    await ctx.send("L'extension **Spoil** a bien été activée !")    

def setup(client):
    client.add_cog(Spoil(client))
    print("L'extension Spoil a bien été activée")    