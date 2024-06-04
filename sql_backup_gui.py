import sys
import os
import logging
import pyodbc
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
)

class BackupDatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.default_backup_dir = "C:\\Backup\\" # Backup Directory
        self.initUI()
        self.setupLogging()
        self.connection = None
        self.databases = []

    def initUI(self):
        self.setWindowTitle('Database Backup App')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.server_label = QLabel('Host/IP:')
        self.server_input = QLineEdit()
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)

        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connectToServer)
        layout.addWidget(self.connect_button)

        self.backup_combo = QComboBox()
        layout.addWidget(self.backup_combo)

        self.backup_button = QPushButton('Backup')
        self.backup_button.clicked.connect(self.backupDatabase)
        self.backup_button.setEnabled(False)
        layout.addWidget(self.backup_button)

        self.setLayout(layout)
        self.resize(1280, 720)

    def setupLogging(self):
        logging.basicConfig(
            filename='backup_log.txt',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8',
        )

    def connectToServer(self):
        server = self.server_input.text()
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            connection_string = f"Driver={{SQL Server}};Server={server};UID={username};PWD={password};"
            self.connection = pyodbc.connect(connection_string)
            QMessageBox.information(self, 'Connection Successful', 'Successfully connected to the server.')
            self.backup_button.setEnabled(True)

            # Veritabanlarını listele
            self.listDatabases()
        except pyodbc.Error as ex:
            error_message = str(ex)
            QMessageBox.critical(self, 'Connection Error', f"Error connecting to the server: {error_message}")
            logging.error(f"Connection Error: {error_message}")
            self.connection = None

    def listDatabases(self):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
                self.databases = [row[0] for row in cursor.fetchall()]
                self.backup_combo.clear()
                self.backup_combo.addItems(self.databases)
            except pyodbc.Error as ex:
                error_message = str(ex)
                QMessageBox.critical(self, 'Error', f"Error listing databases: {error_message}")
                logging.error(f"Error listing databases: {error_message}")
        else:
            QMessageBox.critical(self, 'Error', 'Not connected to the server.')
            logging.error('Not connected to the server.')

    def grantBackupDirectoryAccess(self, server, username, password):
        try:
            connection_string = f"Driver={{SQL Server}};Server={server};UID={username};PWD={password};"
            cnxn = pyodbc.connect(connection_string)
            cursor = cnxn.cursor()

            # Check if the backup directory exists
            if not os.path.exists(self.default_backup_dir):
                # Create the backup directory
                os.makedirs(self.default_backup_dir)
                logging.info(f"Created backup directory: {self.default_backup_dir}")

                # Grant privileges on the backup directory to the SQL Server service account
                grant_query = f"USE master; GRANT ALL PRIVILEGES ON DIRECTORY::'{self.default_backup_dir}' TO [KULLANICI_ADI];"
                cursor.execute(grant_query)
                cnxn.commit()
                logging.info("Granted privileges on the backup directory")

            cnxn.close()
        except Exception as ex:
            logging.error(f"Error granting backup directory access: {ex}")

    def log(self, message):
        logging.info(message)


    def backupDatabase(self):
        server = self.server_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        selected_database = self.backup_combo.currentText()  # database_combobox yerine backup_combo olarak değiştirildi
        current_datetime = datetime.now()
        datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        try:
            self.grantBackupDirectoryAccess(server, username, password)

            if not os.path.exists(self.default_backup_dir):  # backup_dir yerine default_backup_dir kullanıldı
                os.makedirs(self.default_backup_dir)
                self.log(f"Created backup directory: {self.default_backup_dir}")  # backup_dir yerine default_backup_dir kullanıldı

            connection_string = f"Driver={{SQL Server}};Server={server};UID={username};PWD={password};"
            cnxn = pyodbc.connect(connection_string)
            self.log(f"Successfully connected to SQL Server! Server: {server}")

            backup_path = os.path.join(self.default_backup_dir, f"{selected_database}_{datetime_str}.bak")  # backup_dir yerine default_backup_dir kullanıldı
            backup_query = f"BACKUP DATABASE [{selected_database}] TO DISK = N'{backup_path}' WITH NOFORMAT, NOINIT, NAME = N'{selected_database}-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, COMPRESSION, STATS = 10"

            backup_cursor = cnxn.cursor()

            try:
                backup_cursor.execute(backup_query)
                self.log(f"Backup of {selected_database} database successful: {backup_path}")
                QMessageBox.information(self, "Success", f"{selected_database} database backup successful: {backup_path}")
                #self.update_progress_bar(100)
            except pyodbc.Error as backup_ex:
                error_message = str(backup_ex)
                self.log(f"Error during backup: {error_message}")
                #self.update_progress_bar(0)
                QMessageBox.critical(self, "Error", f"Error during backup: {error_message}")
            finally:
                backup_cursor.close()
                cnxn.close()

        except pyodbc.Error as ex:
            error_message = str(ex)
            QMessageBox.critical(self, "Error", f"Database connection error: {error_message}")
            self.log(f"Database connection error: {error_message}")

        except Exception as ex:
            error_message = str(ex)
            QMessageBox.critical(self, "Error", f"Unexpected error: {error_message}")
            self.log(f"Unexpected error: {error_message}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BackupDatabaseApp()
    ex.show()
    sys.exit(app.exec_())
