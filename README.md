# OpsCenter - Sistema de Gestion de Incidentes Operativos

## Descripcion

OpsCenter es una plataforma interna para gestionar incidentes operativos, tareas y notificaciones en una fintech. Resuelve el problema de mala trazabilidad, asignacion de responsables y visibilidad de estado de incidentes que antes se manejaba con correo, hojas de calculo y mensajeria informal.

### Problema que resuelve
- Antes: Correo, hojas de calculo, mensajeria informal → baja trazabilidad
- Ahora: Plataforma integrada → trazabilidad completa, asignacion clara, estado visible

## Arquitectura Hexagonal

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                           │
│  (Endpoints, Routing, Dependencias, Seguridad)             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (UseCases, DTOs, Coordinacion de flujos)                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  (Entidades, Enums, Reglas de negocio, Estados, Patrones)  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (ORM, Repositorios, BD, Autenticacion, EventBus)           │
└──────────────────────────────────────────────────────────────┘
```

### Capas

#### Domain (backend/domain/)
- Entidades: User, Incident, Task, Notification
- Enums: Role, Severity, IncidentStatus, TaskStatus, NotificationStatus
- Patrones:
  - State: Maquina de estados para ciclo de vida de incidentes
  - Observer: EventBus y observadores para eventos del sistema
  - Command: Abstraccion de comandos para envio de notificaciones
  - Template Method: Base para construir mensajes segun canal
  - Factory: IncidentFactory y NotificationFactory para creacion consistente
  - Abstract Factory: NotificationFactory para extensibilidad
- Repositorios (interfaces): Contrato entre capas

#### Application (backend/application/)
- UseCases: AuthUseCases, IncidentUseCases, TaskUseCases, NotificationUseCases
- DTOs: Contrato de entrada/salida (UserDTO, IncidentDTO, TaskDTO, etc.)
- Logica de orquestacion: Coordina dominio e infraestructura

#### Infrastructure (backend/infrastructure/)
- Repositorios (implementacion): SQLAlchemy + ORM
- Modelos ORM: UserModel, IncidentModel, TaskModel, NotificationModel
- Base de datos: Conexion y migraciones con Alembic
- Autenticacion: hash de passwords con bcrypt, JWT
- EventBus concreto: Implementacion del patron Observer
- Persistencia: ORM desacoplado del dominio

#### API (backend/api/)
- Endpoints: CRUD para incidentes, tareas, notificaciones
- Seguridad: Dependencias y guards (roles/permisos)
- Rutas: Organizadas por recurso

#### Frontend (frontend/)
- Streamlit: app.py con vistas dinámicas
- Login: Autenticacion y sesion
- Paneles: Incidentes, tareas, notificaciones
- Autorizacion: Respeta roles desde frontend (validacion real en backend)

## Patrones de Diseño Implementados

### Patrones de Comportamiento

#### 1. Observer (backend/domain/observer.py)
Uso: Publicar eventos del sistema y reaccionar automaticamente
- Publisher: EventBus
- Observers:
  - NotificationObserver: genera notificaciones al crear/cambiar incidentes
  - LogObserver: registra eventos en logs
- Eventos: INCIDENT_CREATED, INCIDENT_ASSIGNED, TASK_DONE, etc.

Flujo:
```python
# En use_cases.py
self.event_bus.publish(EventType.INCIDENT_CREATED, {"id": incident.id})

# El observer reacciona automaticamente creando notificaciones
```

#### 2. Command (backend/domain/commands.py)
Uso: Encapsular la ejecucion de notificaciones
- Interfaz: Command con metodo execute()
- Implementaciones:
  - SendEmailCommand: envio por email
  - SendInAppCommand: notificacion en aplicacion
- Factory: NotificationFactory decide cual comando usar

Flujo:
```python
command = NotificationFactory.create_command(notification)
command.execute()
```

#### 3. State (backend/domain/state.py)
Uso: Controlar el ciclo de vida de incidentes
- Estados:
  - OpenState: recien creado
  - AssignedState: asignado a usuario
  - InProgressState: en resolucion
  - ResolvedState: resuelto
  - ClosedState: cerrado
- Transiciones: Validadas por cada estado

Flujo:
```python
incident._state.assign(incident, assignee_id)  # Cambia estado automaticamente
incident._state.start_progress(incident)
incident._state.resolve(incident)
```

#### 4. Template Method (backend/domain/templates.py)
Uso: Construir mensajes de notificacion segun canal
- Clase abstracta: NotificationTemplate
- Implementaciones:
  - EmailNotificationTemplate: formato HTML para email
  - InAppNotificationTemplate: formato JSON compacto
- Metodo template: build_message() define estructura

Flujo:
```python
template = NotificationFactory.create_template(NotificationChannel.EMAIL)
message = template.build_message(notification)
```

### Patrones Creacionales

#### 5. Factory (backend/domain/factory.py)
Uso: Crear entidades y comandos validando reglas
- IncidentFactory: crear incidentes con validaciones
  - Valida: titulo no vacio, descripcion no vacia, severidad valida
  - Retorna: Incident(status=OPEN)
- NotificationFactory: crear comandos y templates segun canal

#### 6. Abstract Factory (justificacion adicional)
Implementado en: NotificationFactory
Razon: En sistemas reales, cada canal (Email, SMS, Push) requiere:
- Su propio Command
- Su propio Template
- Su propia logica de envio

Beneficio: Agregar nuevos canales sin modificar codigo existente
```python
@staticmethod
def create_command(notification: Notification) -> Command:
    if notification.channel == NotificationChannel.EMAIL:
        return SendEmailCommand(notification)
    if notification.channel == NotificationChannel.SMS:  # Futuro
        return SendSMSCommand(notification)
    # ...
```

## Como Correrlo

### Con Docker Compose (Recomendado)

```bash
# Clonar proyecto
git clone <repo>
cd PSet_3

# Levantar servicios
docker compose up --build

# Esperar a que inicie PostgreSQL, luego acceder:
# Frontend: http://localhost:8501
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

Servicios:
- db: PostgreSQL en puerto 5432
- api: FastAPI en puerto 8000
- ui: Streamlit en puerto 8501

### Sin Docker (Local)

```bash
# 1. Crear venv
python -m venv venv
.\venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar BD
python backend/infrastructure/database.py

# 4. Ejecutar API
uvicorn backend.api.main:app --reload

# 5. En otra terminal, ejecutar frontend
cd frontend
streamlit run app.py
```

## Como Usarlo

### 1. Login
- Ir a http://localhost:8501
- Ingresar credenciales (usuario de prueba: admin@test.com / password)

### 2. Crear Incidente (Operator, Supervisor, Admin)
- Ir a "Incidentes" → "Crear"
- Llenar: Titulo, Descripcion, Severidad
- Click "Crear Incidente"
- Evento publicado → Observer crea notificacion → Command ejecuta envio

### 3. Asignar Incidente (Supervisor, Admin)
- Ir a "Incidentes" → "Lista"
- Click en incidente
- Ingresar ID de usuario
- Click "Asignar"

### 4. Cambiar Estado (Supervisor, Admin)
- Ir a "Incidentes"
- Selectbox de estado
- State automaticamente valida transicion

### 5. Crear / Actualizar Tarea
- Ir a "Tareas"
- Crear: llenar formulario
- Actualizar: selectbox de estado → Click "Actualizar"

### 6. Ver Notificaciones
- Ir a "Notificaciones"
- Se actualizan en tiempo real cuando hay eventos

## Roles y Permisos

| Rol | Can Create Incident | Can Assign | Can Change State | Can See All | Can Manage Users |
|-----|-------------------|-----------|-----------------|------------|------------------|
| OPERATOR | Si | No | No | No (solo sus) | No |
| SUPERVISOR | Si | Si | Si | Si (equipo) | No |
| ADMIN | Si | Si | Si | Si (todos) | Si |

## Base de Datos

### Tablas
```sql
users
  - id (PK)
  - name
  - email (UNIQUE)
  - hashed_password
  - role (ENUM: ADMIN, SUPERVISOR, OPERATOR)

incidents
  - id (PK)
  - title
  - description
  - severity (ENUM: LOW, MEDIUM, HIGH, CRITICAL)
  - status (ENUM: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED)
  - created_by (FK users.id)
  - assigned_to (FK users.id, nullable)
  - created_at

tasks
  - id (PK)
  - incident_id (FK incidents.id)
  - title
  - description
  - status (ENUM: OPEN, IN_PROGRESS, DONE)
  - assigned_to (FK users.id)
  - created_at

notifications
  - id (PK)
  - recipient (FK users.id)
  - channel (ENUM: EMAIL, IN_APP)
  - message
  - event_type (ENUM: INCIDENT_CREATED, etc.)
  - status (ENUM: PENDING, SENT, FAILED)
  - created_at
```

## Tests

Todos pasando (31/31):

```bash
# Ejecutar todos
pytest -v

# Solo unit tests
pytest test/unit/ -v

# Solo integration tests
pytest tests/integration/ -v

# Con cobertura
pytest --cov=backend --cov-report=html
```

### Cobertura
- Comandos de notificacion
- Factory de incidentes
- Observer y EventBus
- Templates de notificacion
- Repositorios SQLAlchemy
- Rutas y autenticacion
- UseCases

## Endpoints Disponibles

### Autenticacion
```
POST   /auth/register     → Register new user
POST   /auth/login        → Login & get token
GET    /me                → Get current user info
```

### Incidentes
```
POST   /incidents         → Create incident
GET    /incidents         → List (filtered by role)
GET    /incidents/{id}    → Get detail
PATCH  /incidents/{id}/assign/{user_id}  → Assign
PATCH  /incidents/{id}/status → Change status
DELETE /incidents/{id}    → Delete (admin only)
```

### Tareas
```
POST   /tasks             → Create task
GET    /tasks             → List (filtered by role)
PATCH  /tasks/{id}/status → Change status
```

### Notificaciones
```
GET    /notifications     → List (filtered by user)
```

## Demo - Escenarios Demostrables

1. Login exitoso → Frontend autentica con API
2. Crear incidente → Desde frontend
3. Incidente persiste → En PostgreSQL via ORM
4. Publicar evento → EventBus.publish()
5. Observer reacciona → NotificationObserver captura
6. Template construye mensaje → EmailNotificationTemplate.build_message()
7. Command ejecuta envio → SendEmailCommand.execute()
8. Estado cambia → State maquina de estados
9. Factory crea → IncidentFactory, NotificationFactory
10. Filtrado por rol → Operator ve solo sus incidentes

## Estructura del Proyecto

```
PSet_3/
├── backend/
│   ├── api/
│   │   ├── main.py          # FastAPI app
│   │   ├── routes.py        # Endpoints
│   │   ├── dependencies.py   # Guards y seguridad
│   │   └── __init__.py
│   ├── application/
│   │   ├── use_cases.py      # AuthUseCases, IncidentUseCases, etc.
│   │   ├── dtos.py           # DTOs
│   │   └── __init__.py
│   ├── domain/
│   │   ├── entities.py       # User, Incident, Task, Notification
│   │   ├── enums.py          # Role, Severity, etc.
│   │   ├── repositories.py   # Interfaces repositorio
│   │   ├── observer.py       # EventBus, Observer
│   │   ├── commands.py       # SendEmailCommand, etc.
│   │   ├── templates.py      # EmailTemplate, InAppTemplate
│   │   ├── state.py          # Estados de incidente
│   │   ├── factory.py        # IncidentFactory, NotificationFactory
│   │   └── __init__.py
│   ├── infrastructure/
│   │   ├── database.py       # Conexion SQLAlchemy
│   │   ├── models.py         # ORM models
│   │   ├── repositories.py   # Implementaciones repositorio
│   │   ├── auth.py           # Hash, JWT
│   │   ├── alembic/          # Migraciones
│   │   └── __init__.py
│   └── __init__.py
├── frontend/
│   ├── app.py                # Streamlit principal
│   ├── .streamlit/
│   │   └── config.toml       # Configuracion Streamlit
│   └── requirements.txt
├── test/
│   └── unit/                 # Unit tests
├── tests/
│   ├── integration/          # Integration tests
│   └── unit/
├── docs/
│   ├── use_cases.puml        # Diagrama UML
│   ├── class_diagram.puml    # Diagrama UML
│   └── sequence_diagram.puml # Diagrama UML
├── docker-compose.yml        # Orquestacion de contenedores
├── Dockerfile                # Build API
├── requirements.txt          # Dependencias Python
├── pytest.ini                # Configuracion pytest
├── alembic.ini               # Configuracion migraciones
└── README.md                 # Este archivo
```

## Tecnologias

### Backend
- Framework: FastAPI
- ORM: SQLAlchemy
- BD: PostgreSQL (Docker) / SQLite (Local)
- Autenticacion: JWT + bcrypt
- Testing: pytest
- Migraciones: Alembic

### Frontend
- Framework: Streamlit
- HTTP: requests

### DevOps
- Contenedores: Docker
- Orquestacion: Docker Compose

## Lecciones de Diseño

### Por que Arquitectura Hexagonal?

1. Testabilidad: Cada capa puede testearse independientemente
2. Flexible: Cambiar BD, autenticacion sin afectar logica
3. Mantenible: Responsabilidades claras
4. Escalable: Facil agregar nuevas capas

### Por que Patrones?

| Patron | Razon |
|--------|-------|
| State | Validar transiciones de estado seguras |
| Observer | Desacoplar eventos de sus consecuencias |
| Command | Encapsular logica de envio de notificaciones |
| Template Method | Reutilizar estructura de mensajes por canal |
| Factory | Validar y crear entidades consistentemente |
| Abstract Factory | Extensibilidad para nuevos canales sin modificar codigo |

## Como Contribuir

1. Crear branch: git checkout -b feature/nombre
2. Hacer cambios
3. Commit: git commit -m "feat: descripcion"
4. Push: git push origin feature/nombre
5. PR con descripcion y cambios

## Licencia

Proyecto educativo PSet_3 - 2026

## Contacto

Preguntas o sugerencias → Email al profesor