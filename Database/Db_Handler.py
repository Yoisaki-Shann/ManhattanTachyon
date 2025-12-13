import aiosqlite
import os
import json

# Get Circle/club Data
async def get_circle_data(input_data=None):
    async with aiosqlite.connect("Database/AlmondData.db") as db:
        
        # Base Query
        sql = '''SELECT 
        c.name,
        c.leader_name,
        c.monthly_rank,
        c.monthly_point,
        c.member_count,
        c.last_month_rank,
        c.last_month_point,
        c.last_updated
        FROM circles c'''

        args = ()

        # Logic: If int -> Discord ID search. If str -> Name search.
        if isinstance(input_data, int):
            sql += " JOIN members m ON c.circle_id = m.circle_id WHERE m.discord_id = ?"
            args = (input_data,)
        elif isinstance(input_data, str):
            sql += " WHERE c.name LIKE ?"
            args = (f"%{input_data}%",)

        async with db.execute(sql, args) as cursor:
            rows = await cursor.fetchall()

            if not rows:
                return None

            name, leader_name, monthly_rank, monthly_point, member_count, last_month_rank, last_month_point, last_updated = rows[0]

            return {
                "name": name,
                "leader_name": leader_name,
                "monthly_rank": monthly_rank,
                "monthly_fans": monthly_point,
                "member_count": member_count,
                "last_month_rank": last_month_rank,
                "last_month_fans": last_month_point,
                "last_updated": last_updated
            }
# Bind
async def bind(discord_id: int, UserInputs: str):
    async with aiosqlite.connect("Database/AlmondData.db") as db:

        rows = None

        # If a number, try to match the trainer_id
        if UserInputs.isdigit():
            async with db.execute('''SELECT name, trainer_id, discord_id FROM members WHERE trainer_id = ?''', (int(UserInputs),)) as cursor:
                rows = await cursor.fetchall()
        # If not a number, try to match the name        
        if not rows:
            async with db.execute('''SELECT name, trainer_id, discord_id FROM members WHERE name LIKE ?''', (UserInputs,)) as cursor:
                rows = await cursor.fetchall()
        # If not found, return None
        if not rows:
            return "No match found for **{}**".format(UserInputs)
        
        # Taking the first match found
        name, trainer_id, check_link = rows[0]

        # check if the trainer_id is already linked to a discord_id
        if check_link and check_link != discord_id:
             return "**{}** is already linked to different Account".format(name)
        
        elif check_link == discord_id:
             return "**{}** is already linked to You".format(name)

        # update the discord_id in the members table
        async with db.execute('''UPDATE members SET discord_id = ? WHERE trainer_id = ?''', (discord_id, trainer_id)) as cursor:
            await db.commit()
            return "**{}** is linked to **{}** : **{}**".format(UserInputs, name, trainer_id)
        