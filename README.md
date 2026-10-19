# PulseMarket Flask

Versión Flask del proyecto PulseMarket, con Python + Flask, PostgreSQL, SQLAlchemy, Flask-Login, OAuth Google/GitHub, APIs CRUD, catálogo paginado, actualización masiva, soft delete, Kanban Drag and Drop, seed correlacionado, pruebas y GitHub Actions.

## Lo que incluye

- Autenticación OAuth exclusiva Google/GitHub (Authlib) y protección de dashboard/API.
- Dashboard de ventas, órdenes recientes, clientes, productos y alertas de inventario.
- CRUD de productos: creación, búsqueda, filtro, paginación server-side y soft delete.
- Actualización masiva de precios por categoría.
- Kanban HTML5 Drag and Drop con actualización optimista y rollback si falla la API.
- PostgreSQL mediante SQLAlchemy, relaciones e índices.
- Seed: 1,000 clientes, 1,000 productos, 10,000 ventas, 10,000 partidas y 30 tareas.
- 17 pruebas unitarias y de rutas en pytest.
- Workflow de GitHub Actions para pruebas automáticas.

> Esta es una implementación inicial ejecutable, no una entrega certificada. El documento del concurso exige Next.js 14+ y Zod; Flask cambia esos requisitos de stack y Python usa validadores propios. Si el jurado exige literalmente el stack del documento, Flask podría no ser aceptado. También se deben probar los flujos E2E reales y medir SLA de 400 ms en producción.

## Requisitos
- Python 3.11+
- PostgreSQL 14+
- Git (para CI/CD)
- Credenciales OAuth de Google y GitHub

## Ejecutar localmente (Windows)

Abre PowerShell en la carpeta descomprimida:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con la contraseña de tu PostgreSQL. Crea una base vacía llamada `pulsemarket` desde pgAdmin o SQL Shell. Ejemplo:

`DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/pulsemarket`

Después ejecuta:

```powershell
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
flask --app run.py seed-demo
flask --app run.py run --debug
```

Nota: para un primer arranque simple, la app crea las tablas si no existen. Para entornos mantenidos usa Flask-Migrate. Si `flask db init` dice que `migrations` ya existe, no repitas `init`; sigue con `migrate` y `upgrade`.

Abre `http://127.0.0.1:5000`.

## Configurar OAuth

### Google
1. Abre Google Cloud Console y crea un OAuth Client ID de tipo Web application.
2. En desarrollo, añade `http://127.0.0.1:5000/auth/callback/google` como URI de redirección autorizada.
3. Coloca el Client ID y Client Secret en `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`.

### GitHub
1. En GitHub → Settings → Developer settings → OAuth Apps → New OAuth App.
2. Homepage URL: `http://127.0.0.1:5000`.
3. Callback URL: `http://127.0.0.1:5000/auth/callback/github`.
4. Copia las credenciales en `GITHUB_CLIENT_ID` y `GITHUB_CLIENT_SECRET`.

En producción cambia los callbacks a `https://TU-DOMINIO/auth/callback/google` y `/auth/callback/github`.

## Railway: subir PostgreSQL a la nube

1. Entra a https://railway.com/ y crea un proyecto.
2. Selecciona **New → Database → PostgreSQL**.
3. En Variables del servicio PostgreSQL identifica `DATABASE_URL`.
4. En el servicio web Flask, configura `DATABASE_URL` como referencia a la variable del PostgreSQL de ese proyecto. Usa la URL interna para conexiones entre servicios en Railway. No compartas esa URL porque contiene credenciales.
5. Para transferir datos locales existentes, desde una terminal con `pg_dump`/`psql` disponibles:
   ```bash
   pg_dump "postgresql://postgres:TU_PASSWORD@localhost:5432/pulsemarket" --no-owner --no-acl > pulsemkt.sql
   psql "URL_PUBLICA_DE_RAILWAY" -v ON_ERROR_STOP=1 -f pulsemkt.sql
   ```
   Si no necesitas preservar los datos locales, puedes desplegar la app y ejecutar `flask --app run.py seed-demo` contra Railway.
6. Antes de ejecutar `seed-demo`, haz respaldo: borra ventas, partidas, productos, clientes y tareas actuales para regenerar datos de demo.

## Desplegar Flask en Railway

1. Sube la carpeta del proyecto a GitHub sin incluir `.env`.
2. En Railway crea un servicio web desde el repositorio.
3. Configura variables `DATABASE_URL`, `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` y `BASE_URL`.
4. Configura los callbacks OAuth con el dominio HTTPS asignado.
5. Comando de inicio recomendado:
   ```bash
   gunicorn run:app
   ```
   Para producción agrega `gunicorn>=22,<24` a `requirements.txt` (en este paquete se puede añadir antes de desplegar).
6. Ejecuta `flask --app run.py db upgrade` y luego una sola vez `flask --app run.py seed-demo`.
7. Configura el dominio y comprueba login, productos, Kanban y API.

## Pruebas

```bash
pytest -q
```

El pipeline está en `.github/workflows/ci.yml`. Activa una regla de protección de rama en GitHub para que se requiera el check de CI antes de integrar cambios.

## Decisiones técnicas para defensa oral

- **Paginación server-side:** `/api/products` aplica filtros, ordenamiento, `offset` y `limit` en PostgreSQL; no descarga el catálogo completo al navegador.
- **Índices:** campos de búsqueda/categoría y fechas frecuentes tienen índices. Para búsquedas con comodines en grandes volúmenes, considera `pg_trgm` y un índice GIN.
- **Soft delete:** `deleted_at` archiva sin borrar físicamente, preservando relaciones históricas.
- **Bulk update:** aplica cambios de precio por categoría y confirma transacción.
- **Drag and drop optimista:** cambia la tarjeta en UI y restaura si el servidor devuelve error.
- **Seed correlacionado:** las ventas referencian clientes y las partidas productos y ventas reales.
- **Rendimiento:** se informa `queryMs`, pero el objetivo de 400 ms debe comprobarse en Railway con pruebas de carga.
- **Pruebas:** hay pruebas unitarias de métricas y validación, más una prueba de protección de ruta; faltan los tres flujos E2E completos exigidos por el concurso.

## Importante sobre el stack del documento
Los lineamientos que compartiste exigen explícitamente Next.js 14+ App Router, TypeScript estricto y Zod. Flask no satisface literalmente esos requisitos aunque la aplicación tenga funcionalidades equivalentes. Antes de elegir Flask para el concurso, confirma con el profesor/jurado si aceptan cambiar el framework.
