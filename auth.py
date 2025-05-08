import psycopg2
from bd import Database

class Auth:
    def __init__(self):
        self.db = Database()

    def register(self, name, last_name, email, password, id_role=2):
        """
        Registra un nuevo usuario. Por defecto, el rol es 'client' (id_role=2).
        """
        try:
            with self.db.get_cursor() as cur:
                # Verifica si el email ya existe
                cur.execute("SELECT id_user FROM users WHERE email = %s;", (email,))
                if cur.fetchone():
                    return {"success": False, "error": "El email ya está registrado."}
                # Inserta el usuario
                cur.execute("""
                    INSERT INTO users (name, last_name, email, password, id_role)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_user, name, last_name, email, id_role;
                """, (name, last_name, email, password, id_role))
                user = cur.fetchone()
                return {"success": True, "user": user}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def login(self, email, password):
        """
        Verifica usuario y contraseña. Retorna datos básicos si es correcto.
        """
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_user, name, last_name, email, id_role
                    FROM users
                    WHERE email = %s AND password = %s;
                """, (email, password))
                user = cur.fetchone()
                if user:
                    return {"success": True, "user": user}
                else:
                    return {"success": False, "error": "Credenciales incorrectas."}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}
