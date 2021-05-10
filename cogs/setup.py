from discord.ext import commands
import discord


class Setup(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.liste_modules = client.liste_modules
    
    @commands.command(
        name="setup",
        description="Permet d'activer ou désactiver les modules du bot",
        usage="setup (desactive|active) (nom_du_module)"
    )
    async def _setup(self, ctx, *args):
        emoji_activé = "✅"
        emoji_désactivé  = "❌"
        
        if len(args) == 0:
            embed = discord.Embed(title="Status des modules", color=0xF5DF4D)
            status_modules = self.client.modules_db.get_modules_status(ctx.guild)
            for nom_module, status in status_modules.items():  
                embed.add_field(name=f"Status du module {self.client.dico_nom_modules_jolis[nom_module]}", value=emoji_activé if status else emoji_désactivé)
            embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
    
def setup(client):
    client.add_cog(Setup(client))