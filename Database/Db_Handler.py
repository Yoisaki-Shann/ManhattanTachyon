import aiosqlite

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

        # Get Circle Data
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
# Get Member Data
async def get_member_data(query):
    async with aiosqlite.connect("Database/AlmondData.db") as db:
        sql = '''
            SELECT 
                m.name, 
                m.trainer_id,
                m.discord_id,
                c.name as circle_name, 
                s.fan_count, 
                s.monthly_gain,
                s.seven_day_avg,
                s.recorded_at
            FROM members m
            LEFT JOIN circles c ON m.circle_id = c.circle_id
            LEFT JOIN members_stats s ON m.trainer_id = s.trainer_id
            WHERE 
        '''
        
        args = ()
        
        if isinstance(query, int):
            # Check if it's a Discord ID or Trainer ID
            sql += " (m.discord_id = ? OR m.trainer_id = ?)"
            args = (query, query)
        else:
            # Assume Name
            sql += " m.name LIKE ?"
            args = (f"%{query}%",)
            
        # Get the LATEST stats entry for this user
        sql += " ORDER BY s.id DESC LIMIT 1"

        # Get the latest stats entry for this user
        async with db.execute(sql, args) as cursor:
            row = await cursor.fetchone()
            if row:
                # Calculate rank within circle based on fan_count
                rank = None
                if row[3]:  # if circle_name exists (index changed due to discord_id)
                    # Get circle_id first
                    async with db.execute("SELECT circle_id FROM circles WHERE name = ?", (row[3],)) as c_cursor:
                        c_row = await c_cursor.fetchone()
                        if c_row:
                            circle_id = c_row[0]
                            # Count how many have higher fan_count in same circle
                            rank_sql = '''
                                SELECT COUNT(*) + 1 FROM members m
                                JOIN members_stats s ON m.trainer_id = s.trainer_id
                                WHERE m.circle_id = ? AND s.fan_count > ?
                                AND m.is_active = 1
                                AND s.id IN (SELECT MAX(id) FROM members_stats GROUP BY trainer_id)
                            '''
                            # Get rank
                            async with db.execute(rank_sql, (circle_id, row[4])) as r_cursor:
                                rank_row = await r_cursor.fetchone()
                                rank = rank_row[0] if rank_row else None
                
                return {
                    "name": row[0],
                    "trainer_id": row[1],
                    "discord_id": row[2],
                    "circle_name": row[3],
                    "fan_count": row[4],
                    "monthly_gain": row[5],
                    "weekly_gain": row[6],
                    "last_updated": row[7],
                    "rank": rank
                }
            return None

# Get Club Leaderboard
async def get_club_leaderboard(circle_name, sort_by="fan_count"):
    async with aiosqlite.connect("Database/AlmondData.db") as db:
        
        # Find circle_id
        async with db.execute("SELECT circle_id FROM circles WHERE name LIKE ?", (f"%{circle_name}%",)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            circle_id = row[0]
        
        # Sort by fan_count, weekly_gain, or monthly_gain
        if sort_by == "fan_count":
            order_col = "s.fan_count"
        elif sort_by == "weekly_gain":
            order_col = "s.seven_day_avg"
        else:  # monthly_gain
            order_col = "s.monthly_gain"
        
        # Get members with latest stats
        sql = f'''
            SELECT m.name, s.fan_count, s.monthly_gain, s.seven_day_avg
            FROM members m
            JOIN members_stats s ON m.trainer_id = s.trainer_id
            WHERE m.circle_id = ?
            AND m.is_active = 1
            AND s.id IN (SELECT MAX(id) FROM members_stats GROUP BY trainer_id)
            ORDER BY {order_col} DESC
        '''
        
        async with db.execute(sql, (circle_id,)) as cursor:
            return await cursor.fetchall()

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

# Get Circle ID
async def get_circle_id():
    async with aiosqlite.connect("Database/AlmondData.db") as db:
        async with db.execute("SELECT circle_id FROM circles") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
            
# Unbind
async def unbind(discord_id: int):
    async with aiosqlite.connect("Database/AlmondData.db") as db:
        async with db.execute("UPDATE members SET discord_id = NULL WHERE discord_id = ?", (discord_id,)) as cursor:
            await db.commit()
            if cursor.rowcount > 0:
                return "Successfully unlinked your profile."
            else:
                return "You are not currently linked to any profile."

# Update DB
async def update_db(data):
    # data is expected to be { 'circle': {...}, 'members': [...] }
    circle_info = data.get('circle')
    members_list = data.get('members')

    if not circle_info:
        return

    async with aiosqlite.connect("Database/AlmondData.db") as db:
        # Update Circle
        await db.execute('''
            UPDATE circles SET 
            monthly_rank = ?,
            monthly_point = ?,
            member_count = ?,
            last_month_rank = ?,
            last_month_point = ?,
            last_updated = ?
            WHERE circle_id = ?
        ''', (
            circle_info.get('monthly_rank'),
            circle_info.get('monthly_point'),
            circle_info.get('member_count'),
            circle_info.get('last_month_rank'),
            circle_info.get('last_month_point'),
            circle_info.get('last_updated'),
            circle_info.get('circle_id')
        ))

        # Mark all current members of this circle as inactive first
        circle_id = circle_info.get('circle_id')
        await db.execute("UPDATE members SET is_active = 0 WHERE circle_id = ?", (circle_id,))

        # Update Members & Stats
        for member in members_list:
            # Get Member Info ( for checking if the member is already in the database)
            trainer_id = member.get('viewer_id')
            name = member.get('trainer_name') 
            circle_id = circle_info.get('circle_id')
            last_updated = circle_info.get('last_updated')
            
            # remove 0 from placeholder data from api daily_fans[1000, 1100, 1200, 1500, 0, 0, 0...]
            daily_fans_raw = member.get('daily_fans', [])
            valid_stats = [x for x in daily_fans_raw if x > 0]
            
            latest_total = 0
            month_diff = 0
            week_diff = 0
            
            # Calculate Fans
            if valid_stats:
                latest_total = valid_stats[-1]
                start_fans = valid_stats[0]
                month_diff = latest_total - start_fans
                
                # Calculate weekly gain (today vs 7 days ago)
                # If we have at least 8 days of data, compare latest vs 7 days back
                if len(valid_stats) >= 8:
                    week_ago_fans = valid_stats[-8]
                    week_diff = latest_total - week_ago_fans
                elif len(valid_stats) > 1:
                    # If less than 7 days, use available data
                    week_diff = latest_total - valid_stats[0]
            
            # Update Members Table (Profile Info)
            cursor = await db.execute("SELECT 1 FROM members WHERE trainer_id = ?", (trainer_id,))
            exists = await cursor.fetchone()
            await cursor.close()

            # If the member is already in the database, update their info
            if exists:
                await db.execute('''
                    UPDATE members SET 
                    name = ?,
                    circle_id = ?,
                    is_active = 1
                    WHERE trainer_id = ?
                ''', (name, circle_id, trainer_id))
            # If the member is not in the database, add them
            else:
                await db.execute('''
                    INSERT INTO members (trainer_id, circle_id, name, discord_id, is_active)
                    VALUES (?, ?, ?, NULL, 1)
                ''', (trainer_id, circle_id, name))

            # Insert Stats (Daily Fans)
            import json
            daily_fans_json = json.dumps(daily_fans_raw)
            
            await db.execute('''
                INSERT INTO members_stats (
                    trainer_id, 
                    fan_count, 
                    monthly_gain,
                    seven_day_avg,
                    daily_fans_list, 
                    recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                trainer_id, 
                latest_total, 
                month_diff,
                week_diff,
                daily_fans_json, 
                last_updated
            ))

        await db.commit()


        
        
       
                
            