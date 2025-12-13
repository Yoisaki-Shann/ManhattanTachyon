import discord
from discord.ext import commands
from Database import Db_Handler

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Check if the user has permission to use the command
    def is_manager(ctx):
        if ctx.author.guild_permissions.administrator: return True
        allowed_roles = ["mod", "staff", "ls uma officer", "umaclover leader"]
        for role in ctx.author.roles:
            if role.name.lower() in allowed_roles: return True
        return False
    
    # Error handling for the cog
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
        else:
            print(f"Error in {ctx.command}: {error}") # Optional: Log other errors to console

    @commands.command()
    @commands.check(is_manager)
    async def bind(self, ctx, *, name): # Use *, name to capture full name with spaces
        print(f"Bind command invoked by {ctx.author} for {name}")
        binding = await Db_Handler.bind(ctx.author.id, name)
        await ctx.send(binding)

    
    @commands.command()
    @commands.check(is_manager)
    async def unbind(self, ctx, *, name):
        # unbinding = await Db_Handler.unbind(ctx.author.id, name)
        # await ctx.send(un binding)
        pass

async def setup(bot):
    await bot.add_cog(Staff(bot))