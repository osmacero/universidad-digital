# Universidad Digital

API académica construida con Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2 y PostgreSQL.

## Dominios implementados

- Autenticación JWT y autorización por roles (`administrator`, `teacher`, `student`).
- Usuarios y relación muchos-a-muchos con roles.
- Materias y asignación de docentes.
- Periodos académicos y ventanas de inscripción.
- Inscripciones únicas por estudiante, materia y periodo.
- Calificaciones con escala de 0 a 5 y ponderación acumulada máxima de 100 %.
- Reporte académico básico con acumulado y porcentaje evaluado por materia.

Cada dominio separa modelos ORM, esquemas Pydantic, servicios de negocio y rutas HTTP. Las rutas no administran transacciones ni acceden directamente a la base de datos.

## Configuración local

1. Crear y activar un entorno virtual con Python 3.11 o superior.
2. Instalar dependencias con `pip install -r Backend/requirements.txt`.
3. Copiar `Backend/.env.example` como `Backend/.env` y reemplazar todas las credenciales.
4. Crear la base de datos y una cuenta PostgreSQL con privilegios limitados al esquema de la aplicación.
5. Ejecutar las migraciones de Alembic antes de iniciar la API.
6. Desde `Backend`, iniciar con `uvicorn app.main:app --reload` para desarrollo.

No se deben versionar `.env`, contraseñas, claves JWT ni credenciales de PostgreSQL.

## API

La API se publica bajo `/api/v1`:

- `/auth/login`, `/auth/me`
- `/users`
- `/roles`
- `/subjects`
- `/academic-periods`
- `/enrollments`
- `/grades`
- `/reports/students/{student_id}`

Todos los recursos, excepto el login y `/health`, requieren un token Bearer. Las operaciones administrativas exigen el rol `administrator`; la escritura de calificaciones acepta administradores y el docente asignado. Estudiantes y docentes solo consultan registros dentro de su alcance.

## Frontend

Frontend construido con React, TypeScript y Vite.

Incluye:

- Autenticación contra FastAPI.
- Persistencia del JWT.
- Rutas protegidas.
- Dashboard académico.
- Cierre de sesión.
- Interfaz responsive.

## Testing

### Frontend

- Vitest + React Testing Library.
- 9 pruebas aprobadas.
- Coverage general: 98.33 %.
- Coverage de funciones: 100 %.
- Cypress E2E: 3 pruebas aprobadas.
- Flujo validado: Login → Dashboard → Logout → protección de rutas.

### Backend

- pytest + pytest-cov.
- 7 pruebas aprobadas.
- Coverage general: 67 %.
- Pruebas de health check, login, autenticación, hashing y JWT.

## Puesta en producción

- Usar una clave JWT aleatoria, extensa y administrada por un almacén de secretos.
- Ejecutar la aplicación detrás de TLS y un proxy confiable.
- Restringir CORS a los orígenes reales.
- Crear los roles iniciales y el primer administrador mediante un proceso operacional controlado.
- Aplicar migraciones en el despliegue; nunca crear tablas automáticamente al arrancar la API.
- Complementar con rate limiting, auditoría, rotación de secretos, backups y monitoreo.
