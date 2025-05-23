# Proyecto3 BD - Backend de Reportes de Reservas de Canchas Deportivas

Este proyecto es el backend que alimenta los reportes interactivos del sistema de reservas deportivas.
Para visualizarlo puedes ingresar a (https://bd-api.eduvial.space/)

## ¿Qué hace este backend?

Expone una API REST que permite consultar datos sobre reservas deportivas. La API proporciona endpoints para:

1. **Reporte de Reservas**: permite obtener información detallada sobre reservas filtradas por fecha, estado y tipo de cancha.
2. **Reporte de Ingresos**: permite obtener información detallada sobre el total de ingresos generados en un periodo.
3. **Reporte de Usuarios**: consulta usuarios con más reservas, junto con su cancha preferida.
4. **Reporte de Promociones**: muestra las promociones utilizadas.
5. **Reporte de Canchas**: indica qué canchas son más utilizadas y en que horarios.

---

## Instalación y ejecución

1. **Clonar el repositorio**
    ```bash
    git clone https://github.com/Jonialen/Proyecto3_bd_backend.git
    cd Proyecto3_bd_backend


2. **Crear entorno virtual (opcional pero recomendado)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```

4. **Correr el servidor**
    ```bash
    uvicorn main:app --reload
    ```

El servidor quedará corriendo en: http://127.0.0.1:8000
---

## API en producción

La API también está desplegada en:  https://bd-api.eduvial.space/api/usuarios (cambiar rutas para ver los diferentes endpoints)

---
