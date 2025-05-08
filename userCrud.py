import psycopg2
from bd import Database

class UserCrud:
    def __init__(self):
        self.db = Database()

    def get_all_users(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_user, name, last_name, email, id_role
                    FROM users
                    ORDER BY id_user;
                """)
                users = cur.fetchall()
                return {"success": True, "users": users}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_user_by_id(self, id_user):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_user, name, last_name, email, id_role
                    FROM users
                    WHERE id_user = %s;
                """, (id_user,))
                user = cur.fetchone()
                if user:
                    return {"success": True, "user": user}
                else:
                    return {"success": False, "error": "Usuario no encontrado"}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def update_user(self, id_user, name=None, last_name=None, email=None, password=None, id_role=None):
        """
        Actualiza los campos enviados (solo los que no sean None).
        """
        try:
            fields = []
            values = []
            if name is not None:
                fields.append("name = %s")
                values.append(name)
            if last_name is not None:
                fields.append("last_name = %s")
                values.append(last_name)
            if email is not None:
                fields.append("email = %s")
                values.append(email)
            if password is not None:
                fields.append("password = %s")
                values.append(password)
            if id_role is not None:
                fields.append("id_role = %s")
                values.append(id_role)
            if not fields:
                return {"success": False, "error": "No hay campos para actualizar."}
            values.append(id_user)
            query = f"""
                UPDATE users
                SET {', '.join(fields)}
                WHERE id_user = %s
                RETURNING id_user, name, last_name, email, id_role;
            """
            with self.db.get_cursor() as cur:
                cur.execute(query, tuple(values))
                user = cur.fetchone()
                if user:
                    return {"success": True, "user": user}
                else:
                    return {"success": False, "error": "Usuario no encontrado"}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def delete_user(self, id_user):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    DELETE FROM users
                    WHERE id_user = %s
                    RETURNING id_user;
                """, (id_user,))
                result = cur.fetchone()
                if result:
                    return {"success": True, "deleted_id": result["id_user"]}
                else:
                    return {"success": False, "error": "Usuario no encontrado"}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def add_phone(self, id_user, phone_number):
        try:
            with self.db.get_cursor() as cur:
                # Verifica si el usuario existe
                cur.execute("SELECT id_user FROM users WHERE id_user = %s;", (id_user,))
                if not cur.fetchone():
                    return {"success": False, "error": "Usuario no encontrado"}
                # Inserta el teléfono
                cur.execute("""
                    INSERT INTO user_phones (id_user, phone_number)
                    VALUES (%s, %s)
                    RETURNING id_user_phone, phone_number;
                """, (id_user, phone_number))
                phone = cur.fetchone()
                return {"success": True, "phone": phone}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_phones(self, id_user):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_user_phone, phone_number
                    FROM user_phones
                    WHERE id_user = %s
                    ORDER BY id_user_phone;
                """, (id_user,))
                phones = cur.fetchall()
                return {"success": True, "phones": phones}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}
