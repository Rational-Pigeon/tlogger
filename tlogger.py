#!/usr/bin/env python3

import sqlite3
import datetime
import argparse
import os

# Get the directory where the original script is located
script_dir = os.path.dirname(os.path.realpath(__file__))# Get the directory where the script is located
db_path = os.path.join(script_dir, 'logger.db')

# Setup the database
def setup_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mydat (
        id INTEGER PRIMARY KEY,
        category_id INTEGER,
        action TEXT,
        date TEXT,
        day_of_week TEXT,
        hours REAL,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    ''')
    conn.commit()
    conn.close()

setup_database()

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Time Logger')
    subparsers = parser.add_subparsers(dest='command')

    # new_category command
    parser_new_category = subparsers.add_parser('new_category', help='Add a new category')
    parser_new_category.add_argument('category', help='Name of the category to add')

    # edit_category command
    parser_edit_category = subparsers.add_parser('edit_category', help='Edit an existing category')
    parser_edit_category.add_argument('category', help='Name of the existing category')
    parser_edit_category.add_argument('new_category', help='New name for the category')

    # add command
    parser_add = subparsers.add_parser('add', help='Add a new log entry')
    parser_add.add_argument('category', help='Category of the activity')
    parser_add.add_argument('action', help='Description of the activity')
    parser_add.add_argument('hours', type=float, help='Number of hours spent')
    parser_add.add_argument('date', nargs='?', default='today', help='Date of the activity (default: today)')

    # list command
    parser_list = subparsers.add_parser('list', help='List entries for a specific date or date interval')
    parser_list.add_argument('date', nargs='?', default='today', help="Date or date interval (e.g., 'today', 'yesterday', '3-days-ago', 'this-week')")

    # edit command
    parser_edit = subparsers.add_parser('edit', help='Edit a specific column of an entry')
    parser_edit.add_argument('id', type=int, help='ID of the entry to edit')
    parser_edit.add_argument('column', help='Column to edit (category_id, action, date, day_of_week, hours)')
    parser_edit.add_argument('new_input', help='New value for the specified column')

    # delete command
    parser_delete = subparsers.add_parser('delete', help='Delete an entry by ID')
    parser_delete.add_argument('id', type=int, help='ID of the entry to delete')

    # report command
    parser_report = subparsers.add_parser('report', help='Generate a report of hours spent per category')
    parser_report.add_argument('date_interval', nargs='?', default='this-week', help="Date interval (e.g., 'this-week', 'last-month', '3-weeks-ago')")
    parser_report.add_argument('category', nargs='?', default=None, help='Specific category to limit the report to')

    return parser.parse_args()

# Handle single date strings
def parse_single_date(date_str):
    today = datetime.date.today()
    if date_str == 'today':
        return today
    elif date_str == 'yesterday':
        return today - datetime.timedelta(days=1)
    elif date_str.endswith('-days-ago'):
        n = int(date_str.split('-')[0])
        return today - datetime.timedelta(days=n)
    else:
        # Try parsing the date string directly
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format or unsupported date string")

# Handle date intervals
def get_date_range(interval):
    today = datetime.date.today()
    if interval == 'today':
        return today, today
    elif interval == 'yesterday':
        yesterday = today - datetime.timedelta(days=1)
        return yesterday, yesterday
    elif interval.endswith('-days-ago'):
        n = int(interval.split('-')[0])
        end_date = today - datetime.timedelta(days=n)
        return end_date, end_date
    elif interval == 'this-month':
        start_date = today.replace(day=1)
        end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        return start_date, end_date
    elif interval == 'last-month':
        end_date = today.replace(day=1) - datetime.timedelta(days=1)
        start_date = end_date.replace(day=1)
        return start_date, end_date
    elif interval.endswith('-months-ago'):
        n = int(interval.split('-')[0])
        end_date = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) - datetime.timedelta(days=30*(n-1))
        start_date = end_date.replace(day=1)
        return start_date, end_date
    elif interval == 'this-week':
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = start_date + datetime.timedelta(days=6)
        return start_date, end_date
    elif interval == 'last-week':
        end_date = today - datetime.timedelta(days=today.weekday() + 1)
        start_date = end_date - datetime.timedelta(days=6)
        return start_date, end_date
    elif interval.endswith('-weeks-ago'):
        n = int(interval.split('-')[0])
        end_date = today - datetime.timedelta(weeks=n)
        start_date = end_date - datetime.timedelta(days=end_date.weekday())
        end_date = start_date + datetime.timedelta(days=6)
        return start_date, end_date
    else:
        raise ValueError("Invalid date interval")

# Execute the command
def execute_command(args):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if args.command == 'new_category':
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (args.category,))
    elif args.command == 'edit_category':
        cursor.execute('UPDATE categories SET name = ? WHERE name = ?', (args.new_category, args.category))
        cursor.execute('UPDATE mydat SET category_id = (SELECT id FROM categories WHERE name = ?) WHERE category_id = (SELECT id FROM categories WHERE name = ?)', (args.new_category, args.category))
    elif args.command == 'add':
        cursor.execute('SELECT id FROM categories WHERE name = ?', (args.category,))
        category_id = cursor.fetchone()
        if not category_id:
            if input(f"Category '{args.category}' does not exist. Add it? (y/n) ").strip().lower() == 'y':
                cursor.execute('INSERT INTO categories (name) VALUES (?)', (args.category,))
                category_id = cursor.lastrowid
            else:
                print("Action discarded.")
                return
        else:
            category_id = category_id[0]
        date = parse_single_date(args.date)
        day_of_week = date.strftime('%A')
        cursor.execute('INSERT INTO mydat (category_id, action, date, day_of_week, hours) VALUES (?, ?, ?, ?, ?)', (category_id, args.action, date.strftime('%Y-%m-%d'), day_of_week, args.hours))
    elif args.command == 'list':
        start_date, end_date = get_date_range(args.date)
        cursor.execute('SELECT mydat.id, categories.name, action, date, day_of_week, hours FROM mydat JOIN categories ON mydat.category_id = categories.id WHERE date BETWEEN ? AND ?', (start_date, end_date))
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    elif args.command == 'edit':
        cursor.execute(f'UPDATE mydat SET {args.column} = ? WHERE id = ?', (args.new_input, args.id))
    elif args.command == 'delete':
        if input(f"Are you sure you want to delete entry with ID {args.id}? (y/n) ").strip().lower() == 'y':
            cursor.execute('DELETE FROM mydat WHERE id = ?', (args.id,))
    elif args.command == 'report':
        start_date, end_date = get_date_range(args.date_interval)
        if args.category:
            cursor.execute('SELECT categories.name, SUM(hours) FROM mydat JOIN categories ON mydat.category_id = categories.id WHERE date BETWEEN ? AND ? AND categories.name = ? GROUP BY categories.name', (start_date, end_date, args.category))
        else:
            cursor.execute('SELECT categories.name, SUM(hours) FROM mydat JOIN categories ON mydat.category_id = categories.id WHERE date BETWEEN ? AND ? GROUP BY categories.name', (start_date, end_date))
        rows = cursor.fetchall()
        print(f"Report from {start_date} to {end_date}:")
        for row in rows:
            print(f"Category: {row[0]}, Hours: {row[1]}")

    conn.commit()
    conn.close()

# Main entry point
if __name__ == '__main__':
    args = parse_args()
    if args.command:
        execute_command(args)
    else:
        print("Use -h or --help for available commands and their usage.")
