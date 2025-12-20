import discord
from discord.ext import commands
import Database.Db_Handler as Db

class Members_Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx, *, query=None):
        search_query = None

        # 1. Determine Search Query
        if query is None:
            # Case: !profile (Self)
            search_query = ctx.author.id
        elif ctx.message.mentions:
            # Case: !profile @User
            search_query = ctx.message.mentions[0].id
        elif query.isdigit():
            # Case: !profile 123456789 (TrainerID)
            search_query = int(query)
        else:
            # Case: !profile PlayerName
            search_query = query

        # 2. Fetch Data
        data = await Db.get_member_data(search_query)

        # 3. Handle Results
        if data:
            embed = discord.Embed(
                title=f"📊 Profile: {data['name']}",
                color=discord.Color.blue()
            )

            embed.add_field(name="🆔 Trainer ID", value=data['trainer_id'], inline=True)
            embed.add_field(name="🏆 Rank", value=f"#{data['rank']} ({data['circle_name']})", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  
            
            embed.add_field(name="🌟 Total Fans", value=f"{data['fan_count'] or 0:,}", inline=True)
            embed.add_field(name="📊 Weekly Gain", value=f"{data['weekly_gain'] or 0:,}", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  
            
            embed.add_field(name="📈 Monthly Gain", value=f"{data['monthly_gain'] or 0:,}", inline=True)
            embed.add_field(name="🔗 Discord", value=f"<@{data['discord_id']}>" if data.get('discord_id') else "Not Linked", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  
            embed.set_footer(text=f"Last Updated: {data['last_updated']}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Could not find profile for **{query or ctx.author.name}**.")

    @commands.command(name="member", aliases=["members"])
    async def leaderboard(self, ctx, *, club_name):

        # Determine sort type
        if "weekly" in club_name.lower():
            sort_by = "weekly_gain"
            sort_label = "Weekly Gain"
            club_name = club_name.lower().replace("weekly", "").strip()
        elif "monthly" in club_name.lower():
            sort_by = "monthly_gain"
            sort_label = "Monthly Gain"
            club_name = club_name.lower().replace("monthly", "").strip()
        else:
            sort_by = "fan_count"
            sort_label = "Total Fans"
        
        data = await Db.get_club_leaderboard(club_name, sort_by)
        
        if not data:
            await ctx.send(f"Could not find club **{club_name}**.")
            return
        if not club_name:
            club_name = "Umaclover"
            
        # Create embed
        title = f"🏆 {club_name.title()} - {sort_label} Leaderboard"
        embed = discord.Embed(title=title, color=discord.Color.gold())
        
        # Add top members
        description = ""
        for idx, (name, fans, monthly, weekly) in enumerate(data, 1):
            if idx == 1:
                rank_display = "🥇"
            elif idx == 2:
                rank_display = "🥈"
            elif idx == 3:
                rank_display = "🥉"
            else:
                rank_display = f"**#{idx}**"
            
            # Select the correct value based on sort type
            if sort_by == "weekly_gain":
                value = f"{weekly:,}"
            elif sort_by == "monthly_gain":
                value = f"{monthly:,}"
            else:
                value = f"{fans:,}"
                
            description += f"{rank_display} {name} - {value}\n"
        
        embed.description = description
        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Members_Stats(bot))
