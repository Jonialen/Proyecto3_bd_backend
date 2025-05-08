import psycopg2
from bd import Database

class CourtCrud:
    def __init__(self):
        self.db = Database()

    def get_all_courts(self):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT c.id_court, c.description, c.price_per_hour, ct.type_name
                    FROM courts c
                    JOIN court_types ct ON c.id_type = ct.id_type
                    ORDER BY c.id_court;
                """)
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_courts_by_type(self, id_type):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT c.id_court, c.description, c.price_per_hour, ct.type_name
                    FROM courts c
                    JOIN court_types ct ON c.id_type = ct.id_type
                    WHERE c.id_type = %s
                    ORDER BY c.id_court;
                """, (id_type,))
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_court_details(self, id_court):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT c.id_court, c.description, c.price_per_hour, ct.type_name
                    FROM courts c
                    JOIN court_types ct ON c.id_type = ct.id_type
                    WHERE c.id_court = %s;
                """, (id_court,))
                data = cur.fetchone()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_unavailable_schedules(self, id_court):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT s.id_schedule, s.schedule_date, s.start_time, s.end_time
                    FROM schedules s
                    JOIN booking_details bd ON s.id_schedule = bd.id_schedule
                    JOIN bookings b ON bd.id_booking = b.id_booking
                    WHERE s.id_court = %s AND b.status <> 'cancelled'
                    ORDER BY s.schedule_date, s.start_time;
                """, (id_court,))
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def make_booking_with_schedule(self, id_user, id_court, schedule_date, start_time, end_time):
        """
        Crea un horario y luego una reserva asociada a ese horario.
        """
        try:
            with self.db.get_cursor() as cur:
                # 1. Crear el horario
                cur.execute("""
                    INSERT INTO schedules (id_court, schedule_date, start_time, end_time)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_schedule;
                """, (id_court, schedule_date, start_time, end_time))
                id_schedule = cur.fetchone()['id_schedule']

                # 2. Crear la reserva
                cur.execute("""
                    INSERT INTO bookings (id_user, booking_date, status)
                    VALUES (%s, CURRENT_DATE, 'pending')
                    RETURNING id_booking;
                """, (id_user,))
                id_booking = cur.fetchone()['id_booking']

                # 3. Asociar reserva y horario
                cur.execute("""
                    INSERT INTO booking_details (id_booking, id_schedule)
                    VALUES (%s, %s);
                """, (id_booking, id_schedule))

                return {
                    "success": True,
                    "id_booking": id_booking,
                    "id_schedule": id_schedule
                }
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def update_booking_status(self, id_booking, new_status):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    UPDATE bookings
                    SET status = %s
                    WHERE id_booking = %s
                    RETURNING id_booking, status;
                """, (new_status, id_booking))
                result = cur.fetchone()
                if result:
                    return {"success": True, "booking": result}
                else:
                    return {"success": False, "error": "Reserva no encontrada"}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_user_pending_bookings(self, id_user):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT
                        b.id_booking,
                        s.schedule_date,
                        s.start_time,
                        s.end_time,
                        c.description AS court_description,
                        ct.type_name AS court_type
                    FROM bookings b
                    JOIN booking_details bd ON b.id_booking = bd.id_booking
                    JOIN schedules s ON bd.id_schedule = s.id_schedule
                    JOIN courts c ON s.id_court = c.id_court
                    JOIN court_types ct ON c.id_type = ct.id_type
                    WHERE b.id_user = %s AND b.status = 'pending'
                    ORDER BY s.schedule_date, s.start_time;
                """, (id_user,))
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_user_confirmed_bookings(self, id_user):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT
                        b.id_booking,
                        s.schedule_date,
                        s.start_time,
                        s.end_time,
                        c.description AS court_description,
                        ct.type_name AS court_type
                    FROM bookings b
                    JOIN booking_details bd ON b.id_booking = bd.id_booking
                    JOIN schedules s ON bd.id_schedule = s.id_schedule
                    JOIN courts c ON s.id_court = c.id_court
                    JOIN court_types ct ON c.id_type = ct.id_type
                    WHERE b.id_user = %s AND b.status = 'confirmed'
                    ORDER BY s.schedule_date, s.start_time;
                """, (id_user,))
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}

    def get_available_schedules(self, id_court):
        try:
            with self.db.get_cursor() as cur:
                cur.execute("""
                    SELECT s.id_schedule, s.schedule_date, s.start_time, s.end_time
                    FROM schedules s
                    WHERE s.id_court = %s
                    AND s.id_schedule NOT IN (
                        SELECT bd.id_schedule
                        FROM booking_details bd
                        JOIN bookings b ON bd.id_booking = b.id_booking
                        WHERE b.status <> 'cancelled'
                    )
                    ORDER BY s.schedule_date, s.start_time;
                """, (id_court,))
                data = cur.fetchall()
                return {"success": True, "data": data}
        except psycopg2.Error as e:
            return {"success": False, "error": str(e).split('\n')[0]}
