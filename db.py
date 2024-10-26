import pyodbc

def get_db_connection():
    server = 'localhost'  # or your server name
    database = 'YourDatabaseName'  # Replace with your database name
    username = 'root'
    password = 'Poochu@2027'
    
    connection = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    return connection
