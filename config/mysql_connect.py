from mysql.connector import Error
import mysql.connector

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='minha_base',
            user='root',
            password='Lca@dallas15',
            port='3306',
            auth_plugin='mysql_native_password'
        )
        if connection.is_connected():
            print("Connection to MySQL database was successful")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("The connection is closed")

# Example usage
if __name__ == "__main__":
    conn = create_connection()
    if conn:
        close_connection(conn)
        # Example usage in another script
        conn = create_connection()
        if conn:
            # Perform database operations
            close_connection(conn)