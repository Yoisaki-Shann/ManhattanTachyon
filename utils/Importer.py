import json
import sqlite3
import os
from datetime import datetime



def CreateDB():
    Connection = sqlite3.connect("Database/AlmondData.db")
    Cursor = Connection.cursor()
    Cursor.execute("PRAGMA foreign_keys = ON;")
    # Create Table circle data
    Circle = ''' 
    CREATE TABLE IF NOT EXISTS circles (
        circle_id INTEGER PRIMARY KEY,
        name TEXT,
        leader_name TEXT,
        member_count INTEGER,
        monthly_rank INTEGER,
        monthly_point INTEGER,
        last_month_rank INTEGER,
        last_month_point INTEGER,
        last_updated TEXT
    ) '''

    # Create Table members data
    Members = ''' 
    CREATE TABLE IF NOT EXISTS members (
        trainer_id INTEGER PRIMARY KEY,
        circle_id INTEGER,
        name TEXT,
        role TEXT,
        is_active INTEGER,
        discord_id INTEGER,
        FOREIGN KEY(circle_id) REFERENCES circles(circle_id)
    ) '''
    members_Stats = ''' 
    CREATE TABLE IF NOT EXISTS members_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_id INTEGER,
        fan_count INTEGER,
        monthly_gain INTEGER,
        daily_gain INTEGER,
        seven_day_avg INTEGER,
        projected_monthly INTEGER,
        daily_fans_list TEXT,
        recorded_at TEXT,
        FOREIGN KEY(trainer_id) REFERENCES members(trainer_id)
    ) '''
    Cursor.execute(Circle)
    Cursor.execute(Members)
    Cursor.execute(members_Stats)
    Connection.commit()
    return Connection

def Importjson(connection, filepath):
    cursor = connection.cursor()
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Import Circle Data
        c_data = data.get('circle', {})
        if c_data:
            cursor.execute('''
                INSERT OR REPLACE INTO circles (
                    circle_id, name, leader_name, member_count, monthly_rank, monthly_point, last_month_rank, last_month_point, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                c_data.get('circle_id'),
                c_data.get('name'),
                c_data.get('leader_name'),
                c_data.get('member_count'),
                c_data.get('monthly_rank'),
                c_data.get('monthly_point'),
                c_data.get('last_month_rank'),
                c_data.get('last_month_point'),
                c_data.get('last_updated')
            ))
            
            circle_id = c_data.get('circle_id')

        # Import Member Data
        members_data = data.get('members', [])
        for m in members_data:
            # Upsert Member (Preserve discord_id)
            is_active = 1 if m.get('isActive') else 0
            
            cursor.execute('''
                INSERT INTO members (trainer_id, circle_id, name, role, is_active)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(trainer_id) DO UPDATE SET
                    circle_id=excluded.circle_id,
                    name=excluded.name,
                    role=excluded.role,
                    is_active=excluded.is_active
            ''', (
                m.get('trainer_id'),
                circle_id,
                m.get('name'),
                m.get('role'),
                is_active
            ))

            # Insert Stats Snapshot
            cursor.execute('''
                INSERT INTO members_stats (
                    trainer_id, fan_count, monthly_gain, daily_gain, 
                    seven_day_avg, projected_monthly, daily_fans_list, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                m.get('trainer_id'),
                m.get('fan_count'),
                m.get('monthly_gain'),
                m.get('daily_gain'),
                int(m.get('seven_day_avg', 0)),
                int(m.get('projected_monthly', 0)),
                json.dumps(m.get('daily_fans', [])),
                m.get('last_updated')
            ))

        connection.commit()
        print("Import successful.")
        
    except Exception as e:
        print(f"Error importing JSON: {e}")
        connection.rollback()

if __name__ == "__main__":
    conn = CreateDB()
    
    # Run 1: First Club
    print("--- Importing Club A ---")
    #Importjson(conn, "Database/club_A.json")
    
    # Run 2: Second Club
    print("--- Importing Club B ---")
    #Importjson(conn, "Database/club_B.json")
    
    conn.close()