import pandas as pd
import sqlite3
import os
import numpy as np
from datetime import datetime

# Database path
# DB_PATH = 'C:\\Users\\mRemfort\\PycharmProjects\\data_workspace - Database\\linkedin_analytics.db'
DB_PATH = './linkedin_analytics.db'

def db_exists():
    """Check if the database file exists"""
    return os.path.exists(DB_PATH)


def init_db():
    """Initialize the database with required tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create tables for each data type
    c.execute('''
    CREATE TABLE IF NOT EXISTS new_followers (
        workspace TEXT,
        date TEXT,
        total_followers INTEGER,
        PRIMARY KEY (workspace, date)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS visitor_metrics (
        workspace TEXT,
        date TEXT,
        total_unique_visitors INTEGER,
        total_page_views INTEGER,
        PRIMARY KEY (workspace, date)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS content_metrics (
        workspace TEXT,
        date TEXT,
        unique_impressions INTEGER,
        clicks_total INTEGER,
        reactions_total INTEGER,
        reposts_total INTEGER,
        engagement_rate REAL,
        PRIMARY KEY (workspace, date)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        workspace TEXT,
        post_title TEXT,
        post_link TEXT,
        created_date TEXT,
        impressions INTEGER,
        clicks INTEGER,
        click_through_rate REAL,
        likes INTEGER,
        comments INTEGER,
        reposts INTEGER,
        follows INTEGER,
        engagement_rate REAL,
        PRIMARY KEY (workspace, post_title)
    )
    ''')

    conn.commit()
    conn.close()


# Helper function to safely convert values to integers or 0 if NaN
def safe_int(value):
    if pd.isna(value) or np.isnan(value) if isinstance(value, float) else False:
        return 0
    return int(value)


# Helper function to safely convert values to floats or 0 if NaN
def safe_float(value):
    if pd.isna(value) or np.isnan(value) if isinstance(value, float) else False:
        return 0.0
    return float(value)


def save_followers_data(df, workspace):
    """Save followers data to database"""
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)

    # Convert dataframe to format expected by database
    db_data = []
    for idx, row in df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        db_data.append((workspace, date_str, safe_int(row['Total followers'])))

    c = conn.cursor()
    c.executemany(
        'INSERT OR REPLACE INTO new_followers (workspace, date, total_followers) VALUES (?, ?, ?)',
        db_data
    )

    conn.commit()
    conn.close()


def save_visitor_metrics(df, workspace):
    """Save visitor metrics data to database"""
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)

    # Convert dataframe to format expected by database
    db_data = []
    for idx, row in df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        db_data.append((
            workspace,
            date_str,
            safe_int(row['Total unique visitors (total)']),
            safe_int(row['Total page views (total)'])
        ))

    c = conn.cursor()
    c.executemany(
        'INSERT OR REPLACE INTO visitor_metrics (workspace, date, total_unique_visitors, total_page_views) VALUES (?, ?, ?, ?)',
        db_data
    )

    conn.commit()
    conn.close()


def save_content_metrics(df, workspace):
    """Save content metrics data to database"""
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)

    # Convert dataframe to format expected by database
    db_data = []
    for idx, row in df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        db_data.append((
            workspace,
            date_str,
            safe_int(row['Unique impressions (organic)']),
            safe_int(row['Clicks (total)']),
            safe_int(row['Reactions (total)']),
            safe_int(row['Reposts (total)']),
            safe_float(row['Engagement rate (total)'])
        ))

    c = conn.cursor()
    c.executemany(
        '''INSERT OR REPLACE INTO content_metrics 
           (workspace, date, unique_impressions, clicks_total, reactions_total, reposts_total, engagement_rate) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        db_data
    )

    conn.commit()
    conn.close()


def save_posts_data(df, workspace):
    """Save posts data to database"""
    if df.empty:
        return

    conn = sqlite3.connect(DB_PATH)

    # Convert dataframe to format expected by database
    db_data = []
    for idx, row in df.iterrows():
        post_title = idx
        created_date = row['Created date'].strftime('%Y-%m-%d') if isinstance(row['Created date'], datetime) else row[
            'Created date']

        db_data.append((
            workspace,
            post_title,
            str(row['Post link']),
            created_date,
            safe_int(row['Impressions']),
            safe_int(row['Clicks']),
            safe_float(row['Click through rate (CTR)']),
            safe_int(row['Likes']),
            safe_int(row['Comments']),
            safe_int(row['Reposts']),
            safe_int(row['Follows']),
            safe_float(row['Engagement rate'])
        ))

    c = conn.cursor()
    c.executemany(
        '''INSERT OR REPLACE INTO posts 
           (workspace, post_title, post_link, created_date, impressions, clicks, click_through_rate, 
            likes, comments, reposts, follows, engagement_rate) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        db_data
    )

    conn.commit()
    conn.close()


def load_followers_data(workspace):
    """Load followers data from database"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, total_followers FROM new_followers WHERE workspace = ?"
    df = pd.read_sql(query, conn, params=(workspace,))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Format dataframe to match expected structure
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.rename(columns={'total_followers': 'Total followers'}, inplace=True)

    return df


def load_visitor_metrics(workspace):
    """Load visitor metrics from database"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, total_unique_visitors, total_page_views FROM visitor_metrics WHERE workspace = ?"
    df = pd.read_sql(query, conn, params=(workspace,))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Format dataframe to match expected structure
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.rename(columns={
        'total_unique_visitors': 'Total unique visitors (total)',
        'total_page_views': 'Total page views (total)'
    }, inplace=True)

    return df


def load_content_metrics(workspace):
    """Load content metrics from database"""
    conn = sqlite3.connect(DB_PATH)
    query = '''SELECT date, unique_impressions, clicks_total, reactions_total, reposts_total, engagement_rate 
              FROM content_metrics WHERE workspace = ?'''
    df = pd.read_sql(query, conn, params=(workspace,))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Format dataframe to match expected structure
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.rename(columns={
        'unique_impressions': 'Unique impressions (organic)',
        'clicks_total': 'Clicks (total)',
        'reactions_total': 'Reactions (total)',
        'reposts_total': 'Reposts (total)',
        'engagement_rate': 'Engagement rate (total)'
    }, inplace=True)

    return df


def load_posts_data(workspace):
    """Load posts data from database"""
    conn = sqlite3.connect(DB_PATH)
    query = '''SELECT post_title, post_link, created_date, impressions, clicks, click_through_rate, 
               likes, comments, reposts, follows, engagement_rate 
               FROM posts WHERE workspace = ?'''
    df = pd.read_sql(query, conn, params=(workspace,))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Format dataframe to match expected structure
    df.set_index('post_title', inplace=True)
    df.rename(columns={
        'created_date': 'Created date',
        'post_link': 'Post link',
        'impressions': 'Impressions',
        'clicks': 'Clicks',
        'click_through_rate': 'Click through rate (CTR)',
        'likes': 'Likes',
        'comments': 'Comments',
        'reposts': 'Reposts',
        'follows': 'Follows',
        'engagement_rate': 'Engagement rate'
    }, inplace=True)

    # Convert date strings to datetime objects
    df['Created date'] = pd.to_datetime(df['Created date'])

    return df


def has_workspace_data(workspace):
    """Check if data exists for a given workspace"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if any data exists for this workspace
    c.execute("SELECT COUNT(*) FROM new_followers WHERE workspace = ?", (workspace,))
    followers_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM visitor_metrics WHERE workspace = ?", (workspace,))
    visitors_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM content_metrics WHERE workspace = ?", (workspace,))
    content_count = c.fetchone()[0]

    conn.close()

    # Return True if at least one table has data for this workspace
    return followers_count > 0 or visitors_count > 0 or content_count > 0


def add_manual_entry(table_name, data_dict, workspace):
    """
    Add a manual entry to a specific table in the database

    Parameters:
    table_name (str): The name of the table to add data to
    data_dict (dict): Dictionary containing the data to add
    workspace (str): The workspace name

    Returns:
    bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Handle different table types
        if table_name == "new_followers":
            c.execute(
                'INSERT OR REPLACE INTO new_followers (workspace, date, total_followers) VALUES (?, ?, ?)',
                (workspace, data_dict['date'], data_dict['total_followers'])
            )
        elif table_name == "visitor_metrics":
            c.execute(
                '''INSERT OR REPLACE INTO visitor_metrics 
                   (workspace, date, total_unique_visitors, total_page_views) 
                   VALUES (?, ?, ?, ?)''',
                (workspace, data_dict['date'], data_dict['total_unique_visitors'],
                 data_dict['total_page_views'])
            )
        elif table_name == "content_metrics":
            c.execute(
                '''INSERT OR REPLACE INTO content_metrics 
                   (workspace, date, unique_impressions, clicks_total, reactions_total, 
                    reposts_total, engagement_rate) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (workspace, data_dict['date'], data_dict['unique_impressions'],
                 data_dict['clicks_total'], data_dict['reactions_total'],
                 data_dict['reposts_total'], data_dict['engagement_rate'])
            )
        elif table_name == "posts":
            c.execute(
                '''INSERT OR REPLACE INTO posts 
                   (workspace, post_title, post_link, created_date, impressions, clicks, 
                    click_through_rate, likes, comments, reposts, follows, engagement_rate) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (workspace, data_dict['post_title'], data_dict['post_link'],
                 data_dict['created_date'], data_dict['impressions'], data_dict['clicks'],
                 data_dict['click_through_rate'], data_dict['likes'], data_dict['comments'],
                 data_dict['reposts'], data_dict['follows'], data_dict['engagement_rate'])
            )
        else:
            conn.close()
            return False

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if conn:
            conn.close()
        return False


def get_table_structure(table_name):
    """
    Get the structure of a table to guide manual entry form creation

    Parameters:
    table_name (str): The name of the table

    Returns:
    list: List of column information (name, type, etc.)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table_name})")
    columns = c.fetchall()
    conn.close()
    return columns


def get_entries(table_name, workspace, limit=100):
    """
    Get entries from a specific table for a workspace

    Parameters:
    table_name (str): The name of the table
    workspace (str): The workspace name
    limit (int): Maximum number of entries to return

    Returns:
    list: List of tuples with entry data
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if table_name == "new_followers":
            c.execute(
                "SELECT rowid, date, total_followers FROM new_followers WHERE workspace = ? ORDER BY date DESC LIMIT ?",
                (workspace, limit)
            )
        elif table_name == "visitor_metrics":
            c.execute(
                "SELECT rowid, date, total_unique_visitors, total_page_views FROM visitor_metrics WHERE workspace = ? ORDER BY date DESC LIMIT ?",
                (workspace, limit)
            )
        elif table_name == "content_metrics":
            c.execute(
                "SELECT rowid, date, unique_impressions, clicks_total, reactions_total, reposts_total, engagement_rate FROM content_metrics WHERE workspace = ? ORDER BY date DESC LIMIT ?",
                (workspace, limit)
            )
        elif table_name == "posts":
            c.execute(
                "SELECT rowid, post_title, created_date FROM posts WHERE workspace = ? ORDER BY created_date DESC LIMIT ?",
                (workspace, limit)
            )
        else:
            conn.close()
            return []

        entries = c.fetchall()
        conn.close()
        return entries
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return []


def delete_entry(table_name, entry_id):
    """
    Delete a specific entry from a table

    Parameters:
    table_name (str): The name of the table
    entry_id (int): The rowid of the entry to delete

    Returns:
    bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute(f"DELETE FROM {table_name} WHERE rowid = ?", (entry_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return False


def delete_entries_by_date_range(table_name, workspace, start_date, end_date):
    """
    Delete entries in a date range from a table

    Parameters:
    table_name (str): The name of the table
    workspace (str): The workspace name
    start_date (str): Start date in 'YYYY-MM-DD' format
    end_date (str): End date in 'YYYY-MM-DD' format

    Returns:
    int: Number of entries deleted
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if table_name == "posts":
            date_column = "created_date"
        else:
            date_column = "date"

        c.execute(f"SELECT COUNT(*) FROM {table_name} WHERE workspace = ? AND {date_column} BETWEEN ? AND ?",
                  (workspace, start_date, end_date))
        count = c.fetchone()[0]

        c.execute(f"DELETE FROM {table_name} WHERE workspace = ? AND {date_column} BETWEEN ? AND ?",
                  (workspace, start_date, end_date))

        conn.commit()
        conn.close()
        return count
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return 0