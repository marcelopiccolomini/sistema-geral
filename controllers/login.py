from config.mysql_connect import create_connection, close_connection
class LoginController():

    def login(username):
        con = create_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        close_connection(con)
        return user
    
    def logout(self):
        # Implement logout functionality here
        return {"status": "success", "message": "Logout successful"}