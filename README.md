markdown# Sistema de Encomiendas — Django REST Framework

Proyecto desarrollado con **Django**, **PostgreSQL**, **Docker** y **Django REST Framework** para la gestión de encomiendas, clientes, rutas, empleados e historial de estados.

El sistema permite registrar encomiendas, consultarlas mediante una API REST, autenticar usuarios con JWT, aplicar filtros, paginación, búsqueda, ordenamiento, permisos personalizados, throttling, versionamiento y documentación automática con Swagger/ReDoc.

---

## 1. Tecnologías utilizadas

| Tecnología | Rol en el proyecto |
|---|---|
| Python 3.11 | Lenguaje base |
| Django | Framework web |
| Django REST Framework | Construcción de la API REST |
| PostgreSQL | Base de datos relacional |
| Docker Compose | Orquestación de contenedores |
| SimpleJWT | Autenticación con tokens JWT |
| django-filter | Filtros avanzados por query params |
| drf-spectacular | Documentación OpenAPI automática |
| django-cors-headers | Control de CORS para el frontend |
| django-redis / Redis | Caché de respuestas costosas |
| Swagger UI / ReDoc | Interfaces de documentación interactiva |

---

## 2. Estructura general del proyecto

```text
encomiendas/
├── api/
│   ├── urls.py             # Rutas v1 de la API
│   ├── urls_v2.py          # Rutas v2 de la API
│   ├── auth_views.py       # JWT personalizado con claims de empleado
│   ├── pagination.py       # Clases de paginación por recurso
│   ├── filters.py          # Filtros avanzados con django-filter
│   ├── permissions.py      # Permisos personalizados
│   ├── throttles.py        # Throttling por scope
│   └── exceptions.py       # Manejador global de errores JSON
├── clientes/               # App de clientes
├── envios/
│   ├── serializers.py      # Serializers principales y anidados
│   ├── api_views.py        # Vistas genéricas de clientes y rutas
│   ├── viewsets.py         # ViewSet principal v1
│   └── viewsets_v2.py      # ViewSet extendido v2
├── rutas/                  # App de rutas
├── config/
│   ├── settings.py         # Configuración del proyecto
│   └── urls.py             # URLs raíz
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 3. Instalación y ejecución

### 3.1. Clonar el repositorio

```bash
git clone https://github.com/Chestoso/encomiendas.git
cd encomiendas
```

### 3.2. Levantar los contenedores

```bash
docker compose up -d --build
```

### 3.3. Ejecutar migraciones

```bash
docker compose exec web python manage.py migrate
```

### 3.4. Crear superusuario

```bash
docker compose exec web python manage.py createsuperuser
```

### 3.5. Verificar la configuración

```bash
docker compose exec web python manage.py check
```

Resultado esperado:

```text
System check identified no issues (0 silenced).
```

---

## 4. Autenticación JWT

La API usa **JSON Web Tokens** gestionados por SimpleJWT. El token de acceso tiene una duración de **60 minutos**; el refresh token dura **7 días** y se invalida automáticamente al rotarse.

El JWT está personalizado e incluye claims adicionales del empleado:

```json
{
  "user_id": 1,
  "username": "admin",
  "email": "admin@empresa.com",
  "is_staff": true,
  "empleado_id": 3,
  "empleado_codigo": "EMP-001",
  "empleado_nombre": "Juan Pérez",
  "cargo": "Operador"
}
```

### 4.1. Obtener token

```http
POST /api/v1/auth/token/
```

Ejemplo con PowerShell:

```powershell
$body = @{
    username = "admin"
    password = "tu_password"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/auth/token/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response
```

Respuesta:

```json
{
  "refresh": "",
  "access": ""
}
```

### 4.2. Usar el token en requests

```powershell
$token = $response.access

$headers = @{
    Authorization = "Bearer $token"
}
```

### 4.3. Renovar el token

```http
POST /api/v1/auth/token/refresh/
Body: { "refresh": "" }
```

### 4.4. Invalidar el token (logout)

```http
POST /api/v1/auth/token/blacklist/
Body: { "refresh": "" }
```

---

## 5. Mapa de endpoints

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/v1/auth/token/` | Obtiene access + refresh token |
| POST | `/api/v1/auth/token/refresh/` | Renueva el access token |
| POST | `/api/v1/auth/token/blacklist/` | Invalida el refresh token |

### Encomiendas v1

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/encomiendas/` | Lista paginada con filtros |
| POST | `/api/v1/encomiendas/` | Registra una encomienda |
| GET | `/api/v1/encomiendas/{id}/` | Detalle completo con historial |
| PUT | `/api/v1/encomiendas/{id}/` | Actualización completa |
| PATCH | `/api/v1/encomiendas/{id}/` | Actualización parcial |
| DELETE | `/api/v1/encomiendas/{id}/` | Elimina una encomienda |
| POST | `/api/v1/encomiendas/{id}/cambiar_estado/` | Cambia el estado |
| GET | `/api/v1/encomiendas/{id}/historial/` | Historial de cambios |
| GET | `/api/v1/encomiendas/pendientes/` | Encomiendas pendientes |
| GET | `/api/v1/encomiendas/con_retraso/` | Encomiendas con retraso |
| GET | `/api/v1/encomiendas/estadisticas/` | Métricas (cacheadas 15 min) |
| POST | `/api/v1/encomiendas/bulk_create/` | Crea varias en una sola petición |
| PATCH | `/api/v1/encomiendas/bulk_estado/` | Cambia estado masivo |

### Recursos de soporte

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/v1/clientes/` | Lista clientes activos |
| GET | `/api/v1/rutas/` | Lista rutas activas |
| GET | `/api/v2/encomiendas/` | Lista encomiendas (versión 2) |

### Documentación

| Herramienta | URL |
|---|---|
| Swagger UI | `http://localhost:8001/api/docs/` |
| ReDoc | `http://localhost:8001/api/redoc/` |
| Schema OpenAPI | `http://localhost:8001/api/schema/` |

---

## 6. Filtros, búsqueda y ordenamiento

Todos los parámetros se pasan como query params en el GET.

### Buscar por texto (`?search=`)

Busca en código, descripción, nombres de remitente/destinatario, origen y destino de ruta:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/?search=ONPE" `
    -Headers $headers
```

### Filtrar por estado (`?estado=`)

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/?estado=PE" `
    -Headers $headers
```

### Filtrar por rango de fechas

```http
GET /api/v1/encomiendas/?desde=2025-01-01&hasta=2025-03-31
```

### Filtrar encomiendas con retraso

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/?con_retraso=true" `
    -Headers $headers
```

### Ordenar resultados (`?ordering=`)

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/?ordering=-fecha_registro" `
    -Headers $headers
```

Campos disponibles para ordenar: `fecha_registro`, `peso_kg`, `costo_envio`, `fecha_entrega_est`.

---

## 7. Paginación

La respuesta de los endpoints de listado siempre incluye:

```json
{
  "count": 8,
  "next": "http://localhost:8001/api/v1/encomiendas/?page=2",
  "previous": null,
  "results": []
}
```

Se puede controlar el tamaño de página:

```http
GET /api/v1/encomiendas/?page=1&page_size=5
```

| Recurso | Clase | Tamaño por defecto | Máximo |
|---|---|---|---|
| Encomiendas | `EncomiendaPagination` | 15 | 100 |
| Clientes | `ClientePagination` | 20 | 50 |
| Historial | `HistorialPagination` | 10 | 50 |

---

## 8. Acciones personalizadas

### Encomiendas pendientes

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/pendientes/" `
    -Headers $headers
```

### Encomiendas con retraso

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/con_retraso/" `
    -Headers $headers
```

### Historial de una encomienda

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/8/historial/" `
    -Headers $headers
```

### Cambiar estado de una encomienda

```powershell
$bodyEstado = @{
    estado      = "TR"
    observacion = "Cambio de estado probado desde la API REST."
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/8/cambiar_estado/" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $bodyEstado
```

### Estadísticas del sistema

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/estadisticas/" `
    -Headers $headers
```

Resultado:

```json
{
  "total_encomiendas": 8,
  "total_activas": 5,
  "pendientes": 2,
  "en_transito": 2,
  "con_retraso": 3,
  "entregadas_hoy": 0,
  "cache": "miss"
}
```

El campo `cache` indica `"miss"` la primera vez (se calculó en BD) y `"hit"` en los siguientes 15 minutos (se sirvió desde Redis).

### Creación masiva (bulk_create)

```powershell
$bulkBody = @(
    @{ remitente = 1; destinatario = 2; ruta = 1; descripcion = "Paquete A"; peso_kg = 2.5 },
    @{ remitente = 3; destinatario = 4; ruta = 2; descripcion = "Paquete B"; peso_kg = 1.0 }
) | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/bulk_create/" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $bulkBody
```

### Cambio masivo de estado (bulk_estado)

```powershell
$bulkEstado = @{
    ids         = @(1, 2, 3)
    estado      = "TR"
    observacion = "Salida de agencia Lima."
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v1/encomiendas/bulk_estado/" `
    -Method PATCH `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $bulkEstado
```

Respuesta:

```json
{
  "mensaje": "Proceso bulk_estado finalizado.",
  "actualizadas": 3,
  "errores": []
}
```

---

## 9. Seguridad

| Mecanismo | Detalle |
|---|---|
| Autenticación JWT | Access token (60 min) + Refresh token (7 días) |
| Blacklist de tokens | El refresh se invalida al rotar o en logout |
| Permisos por rol | `EsEmpleadoActivo` + `EsPropietarioOAdmin` |
| Throttling global | Anónimos: 30/min — Usuarios: 200/min |
| Throttling de login | 5 intentos/min por IP |
| CORS | Configurado para `localhost:3000` y `localhost:8001` |
| Errores uniformes | Toda excepción DRF devuelve el mismo esquema JSON |

---

## 10. Manejo de errores

Todos los errores de la API devuelven la misma estructura:

```json
{
  "success": false,
  "status_code": 401,
  "message": "Error en la solicitud.",
  "errors": {
    "detail": "La combinación de credenciales no tiene una cuenta activa."
  }
}
```

Ejemplo de throttling activo (429):

```json
{
  "success": false,
  "status_code": 429,
  "message": "Error en la solicitud.",
  "errors": {
    "detail": "Solicitud fue regulada (throttled). Se espera que esté disponible en 20 segundos."
  }
}
```

---

## 11. Versionamiento de API

| Versión | Ruta base | Diferencia |
|---|---|---|
| v1 | `/api/v1/` | Versión principal |
| v2 | `/api/v2/` | Serializer extendido con campos adicionales |

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8001/api/v2/encomiendas/" `
    -Headers $headers
```

---

## 12. Documentación automática

Generada con `drf-spectacular`. Para validar el schema:

```bash
docker compose exec web python manage.py spectacular --validate
```

Para exportarlo a archivo:

```bash
docker compose exec web python manage.py spectacular --file schema.yml
```

---

## 13. Comandos útiles

```bash
# Levantar proyecto
docker compose up -d

# Reiniciar solo el servicio web
docker compose restart web

# Ver logs en tiempo real
docker compose logs -f web

# Ejecutar migraciones
docker compose exec web python manage.py migrate

# Crear superusuario
docker compose exec web python manage.py createsuperuser

# Verificar configuración
docker compose exec web python manage.py check

# Apagar contenedores
docker compose down
```

---

## 14. Funcionalidades implementadas

- API REST completa con ViewSets y Router
- Serializers simples y anidados
- Vistas genéricas para clientes y rutas
- Autenticación JWT con claims personalizados de empleado
- Permisos por rol: empleado activo y propietario/admin
- Filtros avanzados con django-filter
- Búsqueda full-text con SearchFilter
- Ordenamiento con OrderingFilter
- Paginación personalizada por recurso
- Acciones personalizadas en ViewSet
- Historial de cambios de estado
- Estadísticas con caché Redis (15 min)
- Throttling global y específico en login
- Manejo uniforme de errores JSON
- Versionamiento `/api/v1/` y `/api/v2/`
- Endpoints bulk para creación y cambio de estado masivo
- Documentación Swagger UI y ReDoc
- Blacklist de tokens JWT