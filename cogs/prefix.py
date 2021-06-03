from discord.ext import commands
from discord.ext.commands import has_permissions, when_mentioned_or
from utils.prefix import PrefixDB

class Prefix(commands.Cog, name="Préfixe"):
    
    def __init__(self, client):
        self.client = client
        self.prefix = client.prefix_db       
    
    @commands.command(
        name="test"
    )
    async def _test(self, ctx):
        self.client.modules_db.__add_module__("log")
        await ctx.send("TEST OK !")
            
    @commands.command(
        name="prefix"
    )
    async def _prefix(self, ctx):
        await ctx.send(f"Le préfixe de la guilde est : `{self.prefix.get_prefix(ctx.guild)}`")

    @commands.command(
        name="change_prefix"
    )
    @has_permissions(administrator=True)
    async def _change_prefix(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("Vous devez renseigner un préfixe si vous voulez le changer !")
            return
        self.prefix.modify_prefix(ctx.guild, args[0])
        await ctx.send(f"Le préfixe est maintenant : `{args[0]}`.")

    @commands.Cog.listener()
    async def on_guild_join(self, guilde):
        self.prefix.ajoute_guilde(guilde)

    @commands.Cog.listener()
    async def on_guild_remove(self, guilde):
        self.prefix.delete_prefix(guilde)
        
    

def setup(client):
    client.add_cog(Prefix(client))
    print("Le cog Préfixe est prêt !")