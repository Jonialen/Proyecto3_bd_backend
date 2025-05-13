import psycopg2
from bd import Database

def get_time_range(horario_dia):
    if not horario_dia:
        return None, None
    horario_dia = horario_dia.lower()
    if horario_dia == "manana":
        return "00:00:00", "12:00:00"
    elif horario_dia == "tarde":
        return "12:00:00", "18:00:00"
    elif horario_dia == "noche":
        return "18:00:00", "24:00:00"
    return None, None

class CustomReports:
    def __init__(self):
        self.db = Database()

    def get_courts_type(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_type, type_name FROM court_types ORDER BY id_type;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_promociones(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT id_promotion, name, description, discount_percentage, start_date, end_date
                    FROM promotions
                    ORDER BY name;
                """)
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_horarios(self):
        return {
            "success": True,
            "data": [
                {"nombre": "Manana", "inicio": "06:00", "fin": "12:00"},
                {"nombre": "Tarde", "inicio": "12:00", "fin": "18:00"},
                {"nombre": "Noche", "inicio": "18:00", "fin": "24:00"},
            ]
        }

    def reservas(self, fecha_inicio=None, fecha_fin=None, canchas_tipo=None, estado=None):
        try:
            with self.db.get_cursor() as cur:
                query = """
                    SELECT u.name AS nombre_usuario, b.id_booking AS id_reserva, b.status AS estado, ct.type_name AS tipo_cancha
                    FROM bookings b
                    JOIN users u ON b.id_user = u.id_user
                    JOIN booking_details bd ON b.id_booking = bd.id_booking
                    JOIN schedules s ON bd.id_schedule = s.id_schedule
                    JOIN courts c ON s.id_court = c.id_court
                    JOIN court_types ct ON c.id_type = ct.id_type
                    WHERE 1=1
                """
                params = []
                if fecha_inicio:
                    query += " AND s.schedule_date >= %s"
                    params.append(fecha_inicio)
                if fecha_fin:
                    query += " AND s.schedule_date <= %s"
                    params.append(fecha_fin)
                if canchas_tipo:
                    query += " AND ct.id_type = %s"
                    params.append(canchas_tipo)
                if estado:
                    query += " AND b.status = %s"
                    params.append(estado)
                query += " ORDER BY s.schedule_date DESC"
                cur.execute(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def ingresos(self, fecha_inicio=None, fecha_fin=None, agrupar="dia", cancha_tipo=None):
        try:
            with self.db.get_cursor() as cur:
                if agrupar == "mes":
                    group_by = "DATE_TRUNC('month', s.schedule_date)"
                    select_group = "DATE_TRUNC('month', s.schedule_date) AS periodo"
                elif agrupar == "anio":
                    group_by = "DATE_TRUNC('year', s.schedule_date)"
                    select_group = "DATE_TRUNC('year', s.schedule_date) AS periodo"
                else:
                    group_by = "s.schedule_date"
                    select_group = "s.schedule_date AS periodo"
                query = f"""
                    SELECT {select_group}, ct.type_name AS cancha_tipo, COUNT(b.id_booking) AS cant_reservas, COALESCE(SUM(i.total_amount),0) AS total_income
                    FROM bookings b
                    JOIN booking_details bd ON b.id_booking = bd.id_booking
                    JOIN schedules s ON bd.id_schedule = s.id_schedule
                    JOIN courts c ON s.id_court = c.id_court
                    JOIN court_types ct ON c.id_type = ct.id_type
                    LEFT JOIN invoices i ON b.id_booking = i.id_booking
                    WHERE 1=1
                """
                params = []
                if fecha_inicio:
                    query += " AND s.schedule_date >= %s"
                    params.append(fecha_inicio)
                if fecha_fin:
                    query += " AND s.schedule_date <= %s"
                    params.append(fecha_fin)
                if cancha_tipo:
                    query += " AND ct.id_type = %s"
                    params.append(cancha_tipo)
                # Usa la expresión, no el alias, en el GROUP BY
                query += f" GROUP BY {group_by}, ct.type_name ORDER BY {group_by} DESC"
                cur.execute(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def usuarios(self, fecha_inicio=None, fecha_fin=None, horario_dia=None, min_reservas=1):
        try:
            with self.db.get_cursor() as cur:
                query = """
                    SELECT u.name, COUNT(b.id_booking) AS cantidad_reservas,
                        (SELECT ct.type_name
                         FROM bookings b2
                         JOIN booking_details bd2 ON b2.id_booking = bd2.id_booking
                         JOIN schedules s2 ON bd2.id_schedule = s2.id_schedule
                         JOIN courts c2 ON s2.id_court = c2.id_court
                         JOIN court_types ct ON c2.id_type = ct.id_type
                         WHERE b2.id_user = u.id_user
                         GROUP BY ct.type_name
                         ORDER BY COUNT(*) DESC
                         LIMIT 1
                        ) AS cancha_preferida
                    FROM users u
                    JOIN bookings b ON u.id_user = b.id_user
                    JOIN booking_details bd ON b.id_booking = bd.id_booking
                    JOIN schedules s ON bd.id_schedule = s.id_schedule
                    WHERE 1=1
                """
                params = []
                if fecha_inicio:
                    query += " AND s.schedule_date >= %s"
                    params.append(fecha_inicio)
                if fecha_fin:
                    query += " AND s.schedule_date <= %s"
                    params.append(fecha_fin)
                if horario_dia:
                    start, end = get_time_range(horario_dia)
                    if start and end:
                        query += " AND s.start_time >= %s AND s.end_time < %s"
                        params.extend([start, end])
                query += " GROUP BY u.id_user, u.name"
                if min_reservas:
                    query += " HAVING COUNT(b.id_booking) >= %s"
                    params.append(min_reservas)
                query += " ORDER BY cantidad_reservas DESC"
                cur.execute(query, tuple(params))
                print(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def promociones_aplicadas(self, fecha_inicio=None, fecha_fin=None, nombre_promocion=None):
        try:
            with self.db.get_cursor() as cur:
                query = """
                    SELECT u.name AS nombre_usuario, b.id_booking AS id_reserva, p.discount_percentage AS porcentaje_desc
                    FROM bookings b
                    JOIN users u ON b.id_user = u.id_user
                    JOIN booking_promotions bp ON b.id_booking = bp.id_booking
                    JOIN promotions p ON bp.id_promotion = p.id_promotion
                    WHERE 1=1
                """
                params = []
                if fecha_inicio:
                    query += " AND b.booking_date >= %s"
                    params.append(fecha_inicio)
                if fecha_fin:
                    query += " AND b.booking_date <= %s"
                    params.append(fecha_fin)
                if nombre_promocion:
                    query += " AND p.name ILIKE %s"
                    params.append(f"%{nombre_promocion}%")
                query += " ORDER BY b.id_booking DESC"
                cur.execute(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def cuantas_veces(self, nombre_promocion=None):
        try:
            with self.db.get_cursor() as cur:
                query = """
                    SELECT u.id_user, p.name AS promocion, COUNT(bp.id_booking) AS cant_usada
                    FROM users u
                    JOIN bookings b ON u.id_user = b.id_user
                    JOIN booking_promotions bp ON b.id_booking = bp.id_booking
                    JOIN promotions p ON bp.id_promotion = p.id_promotion
                    WHERE 1=1
                """
                params = []
                if nombre_promocion:
                    query += " AND p.name ILIKE %s"
                    params.append(f"%{nombre_promocion}%")
                query += " GROUP BY u.id_user, p.name ORDER BY cant_usada DESC"
                cur.execute(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def disponibilidad_canchas(self, fecha_inicio=None, fecha_fin=None, tipo_cancha=None, horario_dia=None):
        try:
            with self.db.get_cursor() as cur:
                query = """
                    SELECT c.id_court, ct.type_name AS tipo_cancha, COUNT(bd.id_booking) AS veces_reservada
                    FROM courts c
                    JOIN court_types ct ON c.id_type = ct.id_type
                    JOIN schedules s ON c.id_court = s.id_court
                    JOIN booking_details bd ON s.id_schedule = bd.id_schedule
                    WHERE 1=1
                """
                params = []
                if fecha_inicio:
                    query += " AND s.schedule_date >= %s"
                    params.append(fecha_inicio)
                if fecha_fin:
                    query += " AND s.schedule_date <= %s"
                    params.append(fecha_fin)
                if tipo_cancha:
                    query += " AND ct.id_type = %s"
                    params.append(tipo_cancha)
                if horario_dia:
                    start, end = get_time_range(horario_dia)
                    if start and end:
                        query += " AND s.start_time >= %s AND s.end_time < %s"
                        params.extend([start, end])
                query += " GROUP BY c.id_court, ct.type_name ORDER BY veces_reservada DESC"
                cur.execute(query, tuple(params))
                return {"success": True, "data": cur.fetchall()}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

