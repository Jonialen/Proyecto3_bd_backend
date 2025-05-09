import psycopg2
from bd import Database

class Reports:
    def __init__(self):
        self.db = Database()

    def ingresos_totales_por_mes(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT DATE_TRUNC('month', issue_date) AS mes,
                           SUM(total_amount) AS ingresos_totales
                    FROM INVOICES
                    GROUP BY mes
                    ORDER BY mes DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_usuario(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name,
                           COUNT(b.id_booking) AS total_reservas
                    FROM USERS u
                    LEFT JOIN BOOKINGS b ON u.id_user = b.id_user
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY total_reservas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_estado(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*) AS cantidad
                    FROM BOOKINGS
                    GROUP BY status;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_tipo_cancha(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT ct.type_name, COUNT(bd.id_booking) AS total_reservas
                    FROM COURT_TYPES ct
                    JOIN COURTS c ON ct.id_type = c.id_type
                    JOIN SCHEDULES s ON c.id_court = s.id_court
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    GROUP BY ct.type_name
                    ORDER BY total_reservas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_cancha(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT c.id_court, c.description, COUNT(bd.id_booking) AS total_reservas
                    FROM COURTS c
                    JOIN SCHEDULES s ON c.id_court = s.id_court
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    GROUP BY c.id_court, c.description
                    ORDER BY total_reservas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_dia(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT s.schedule_date, COUNT(bd.id_booking) AS total_reservas
                    FROM SCHEDULES s
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    GROUP BY s.schedule_date
                    ORDER BY s.schedule_date DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_hora(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT s.start_time, COUNT(bd.id_booking) AS total_reservas
                    FROM SCHEDULES s
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    GROUP BY s.start_time
                    ORDER BY s.start_time;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def promociones_mas_usadas(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT p.name, COUNT(bp.id_booking) AS veces_usada
                    FROM PROMOTIONS p
                    LEFT JOIN BOOKING_PROMOTIONS bp ON p.id_promotion = bp.id_promotion
                    GROUP BY p.name
                    ORDER BY veces_usada DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_con_promocion(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT b.id_booking, u.name, u.last_name, p.name AS promocion
                    FROM BOOKINGS b
                    JOIN USERS u ON b.id_user = u.id_user
                    JOIN BOOKING_PROMOTIONS bp ON b.id_booking = bp.id_booking
                    JOIN PROMOTIONS p ON bp.id_promotion = p.id_promotion
                    ORDER BY b.id_booking DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def facturacion_por_usuario(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name, SUM(i.total_amount) AS total_facturado
                    FROM USERS u
                    JOIN BOOKINGS b ON u.id_user = b.id_user
                    JOIN INVOICES i ON b.id_booking = i.id_booking
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY total_facturado DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def facturacion_por_tipo_cancha(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT ct.type_name, SUM(i.total_amount) AS total_facturado
                    FROM COURT_TYPES ct
                    JOIN COURTS c ON ct.id_type = c.id_type
                    JOIN SCHEDULES s ON c.id_court = s.id_court
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    JOIN INVOICES i ON bd.id_booking = i.id_booking
                    GROUP BY ct.type_name
                    ORDER BY total_facturado DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_canceladas_por_usuario(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name, COUNT(b.id_booking) AS canceladas
                    FROM USERS u
                    JOIN BOOKINGS b ON u.id_user = b.id_user
                    WHERE b.status = 'cancelled'
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY canceladas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_pendientes_por_usuario(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name, COUNT(b.id_booking) AS pendientes
                    FROM USERS u
                    JOIN BOOKINGS b ON u.id_user = b.id_user
                    WHERE b.status = 'pending'
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY pendientes DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_confirmadas_por_usuario(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name, COUNT(b.id_booking) AS confirmadas
                    FROM USERS u
                    JOIN BOOKINGS b ON u.id_user = b.id_user
                    WHERE b.status = 'confirmed'
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY confirmadas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def canchas_mas_rentadas(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT c.id_court, c.description, COUNT(bd.id_booking) AS veces_rentada
                    FROM COURTS c
                    JOIN SCHEDULES s ON c.id_court = s.id_court
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    GROUP BY c.id_court, c.description
                    ORDER BY veces_rentada DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def usuarios_con_mas_reservas(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT u.id_user, u.name, u.last_name, COUNT(b.id_booking) AS total_reservas
                    FROM USERS u
                    JOIN BOOKINGS b ON u.id_user = b.id_user
                    GROUP BY u.id_user, u.name, u.last_name
                    ORDER BY total_reservas DESC
                    LIMIT 10;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def promociones_activas_hoy(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_promotion, name, description, discount_percentage
                    FROM PROMOTIONS
                    WHERE CURRENT_DATE BETWEEN start_date AND end_date;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_promocion(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT p.name AS promocion, COUNT(bp.id_booking) AS total_reservas
                    FROM PROMOTIONS p
                    LEFT JOIN BOOKING_PROMOTIONS bp ON p.id_promotion = bp.id_promotion
                    GROUP BY p.name
                    ORDER BY total_reservas DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def ingresos_por_dia(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT issue_date, SUM(total_amount) AS ingresos
                    FROM INVOICES
                    GROUP BY issue_date
                    ORDER BY issue_date DESC;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def reservas_por_rango_fechas(self, fecha_inicio, fecha_fin):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT s.schedule_date, COUNT(bd.id_booking) AS total_reservas
                    FROM SCHEDULES s
                    JOIN BOOKING_DETAILS bd ON s.id_schedule = bd.id_schedule
                    WHERE s.schedule_date BETWEEN %s AND %s
                    GROUP BY s.schedule_date
                    ORDER BY s.schedule_date;
                """, (fecha_inicio, fecha_fin))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

