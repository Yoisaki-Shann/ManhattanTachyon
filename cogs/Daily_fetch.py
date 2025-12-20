import Service.ApiWrapper as Api
import Database.Db_Handler as Db
from discord.ext import tasks
from datetime import datetime, time
from discord.ext import commands

class DailyFetch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_fetch_task.start()
    
    # Daily Fetch auto fetch
    @tasks.loop(time=time(hour=17, minute=0))
    async def daily_fetch_task(self):
        await self.run_daily_fetch()

    @commands.command(name="dailyfetch")
    @commands.has_role("Mod")
    async def force_daily_fetch(self, ctx):
        await ctx.send("Starting Manual Fetch...") # Visual feedback in chat
        await self.run_daily_fetch()
        await ctx.send("Manual Fetch Completed.")

    @force_daily_fetch.error
    async def force_daily_fetch_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("You do not have the required 'Mod' role to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")

    async def run_daily_fetch(self):
        print("Starting daily fetch...")
        clubs = await Db.get_circle_id()

        if not clubs:
            print("No clubs found.")
            return 0
        
        print(f"Found {len(clubs)} clubs to update.")
        
        for circle_id in clubs:
            print(f"Updating Circle ID: {circle_id}...")
            try:
                data = await Api.fetch_and_process(circle_id)
                if data:
                    await Db.update_db(data)
                    print(f"Successfully updated Circle ID: {circle_id}")
                else:
                    print(f"Failed to fetch data for Circle ID: {circle_id}")
            except Exception as e:
                print(f"Error updating Circle ID {circle_id}: {e}")

async def setup(bot):
    await bot.add_cog(DailyFetch(bot))

