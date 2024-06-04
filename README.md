# MsSQL Database Backup App

Database Backup App provides a simple PyQt5-based interface to back up an SQL Server database. This application allows users to connect to a specified SQL Server, list databases, and back up the selected database.

## Features

- Connect to SQL Server
- List databases
- Back up the selected database
- Grant permissions for the backup directory

## Requirements

- Python 3.x
- PyQt5
- pyodbc

## Installation

1. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

2. Clone or download this repository.

3. Run the `sql_backup_gui.py` file:

    ```sh
    python sql_backup_gui.py
    ```

## Usage

1. Upon starting the application, you will be presented with an interface.
2. Enter the Host/IP address, username, and password of the SQL Server you want to connect to.
3. Click the `Connect` button.
4. Once the connection is successful, select the database you want to back up.
5. Click the `Backup` button to start the backup process.

## Code Explanation

- `initUI()`: Creates the application's user interface.
- `setupLogging()`: Configures logging for the application.
- `connectToServer()`: Connects to the SQL Server and lists databases.
- `listDatabases()`: Lists the databases on the connected SQL Server.
- `grantBackupDirectoryAccess()`: Grants access permissions to the backup directory.
- `backupDatabase()`: Backs up the selected database, logs the outcome, and notifies the user.

## Logging

All significant events are logged in the `backup_log.txt` file. This is useful for debugging and tracking the history of operations.

## Contributing

If you wish to contribute, please create a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
