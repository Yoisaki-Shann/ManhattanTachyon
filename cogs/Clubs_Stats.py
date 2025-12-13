import discord
from discord.ext import commands
from Database.Db_Handler import get_circle_data  
# Clubs_Stats.py
class Clubs_Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Clubs_Stats.py
    @commands.command(name="clubprofile")
    async def clubprofile(self, ctx, *, input_name = None):
        target = input_name if input_name else ctx.author.id
        circle_data = await get_circle_data(target)
        if circle_data:
            await ctx.send(f"📊 Analyzing **{circle_data['name']}**...")
            embed = discord.Embed(title="📈 Club Profile", color=discord.Color.dark_purple())
            embed.add_field(name="🏰 Name", value=circle_data['name'], inline=True)
            embed.add_field(name="👑 Leader", value=circle_data['leader_name'], inline=True)
            embed.add_field(name="👥 Member Count", value=circle_data['member_count'], inline=True)
            embed.add_field(name="📈 Monthly Rank", value=circle_data['monthly_rank'], inline=True)
            embed.add_field(name="🌟 Monthly Fans", value=f"{circle_data['monthly_fans']:,}", inline=True)
            embed.add_field(name="📉 Last Month Rank", value=circle_data['last_month_rank'], inline=True)
            embed.add_field(name="✨ Last Month Fans", value=f"{circle_data['last_month_fans']:,}", inline=True)
            embed.add_field(name="⏰ Last Updated", value=circle_data['last_updated'], inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Club data not found.")

async def setup(bot):
    await bot.add_cog(Clubs_Stats(bot))
        