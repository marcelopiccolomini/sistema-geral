from config.mysql_connect import create_connection, close_connection
class ChangePassController():

    def change_pass(user_id, new_pass):
        con = create_connection()
        cur = con.cursor(dictionary=True)
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_pass, user_id))
        con.commit()
        close_connection(con)
        return {"status": "success", "message": "Password changed successfully"}