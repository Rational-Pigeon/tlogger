# tlogger - A Simple Time Logging Tool

tlogger is a command-line tool for logging and reporting time spent on various activities. It allows you to manage categories, add and edit logs, and generate reports of your activities over specific time intervals.

## Features

- Add and edit categories of activities
- Log activities with time spent and dates
- List entries for specific dates or intervals
- Edit and delete entries by ID
- Generate reports of time spent per category over specified intervals

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tlogger.git
    ```
2. Navigate to the project directory:
    ```bash
    cd tlogger
    ```
3. Make the script executable:
    ```bash
    chmod +x tlogger.py
    ```

## Usage

### Commands

1. **new_category**: Add a new category
    ```bash
    ./tlogger.py new_category <category>
    ```

2. **edit_category**: Edit an existing category
    ```bash
    ./tlogger.py edit_category <category> <new_category>
    ```

3. **add**: Add a new log entry
    ```bash
    ./tlogger.py add <category> <action> <hours> [date]
    ```

4. **list**: List entries for a specific date or date interval
    ```bash
    ./tlogger.py list [date]
    ```

5. **edit**: Edit a specific column of an entry
    ```bash
    ./tlogger.py edit <id> <column> <new_input>
    ```

6. **delete**: Delete an entry by ID
    ```bash
    ./tlogger.py delete <id>
    ```

7. **report**: Generate a report of hours spent per category
    ```bash
    ./tlogger.py report [date_interval] [category]
    ```

### Date Formats and Intervals

The following date formats and intervals are supported:

- `today`: Current date
- `yesterday`: Previous date
- `n-days-ago`: n days before today (e.g., `3-days-ago`)
- `this-week`: Current week (Monday to Sunday)
- `last-week`: Previous week (Monday to Sunday)
- `n-weeks-ago`: n weeks before the current week (e.g., `2-weeks-ago`)
- `this-month`: Current month
- `last-month`: Previous month
- `n-months-ago`: n months before the current month (e.g., `1-months-ago`)

### Examples

```bash
# Add a new category
./tlogger.py new_category Development

# Add a new entry
./tlogger.py add Development "working on tlogger" 2.5

# Add a new entry with a date 2-days-ago
./tlogger.py add Reflection "went for a long walk, read LAEL and came up with improvement plan" 1 2-days-ago

# List today's entries
./tlogger.py list

# Edit an entry
./tlogger.py edit 1 hours 3.0

# Delete an entry
./tlogger.py delete 1

# Generate a report
./tlogger.py report this-week Development
```
