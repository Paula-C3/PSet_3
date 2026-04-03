# OpsCenter - Sistema de Gestión de Incidentes Operativos

## 📋 Descripción

**OpsCenter** es una plataforma interna para gestionar incidentes operativos, tareas y notificaciones en una fintech. Resuelve el problema de mala trazabilidad, asignación de responsables y visibilidad de estado de incidentes que antes se manejaba con correo, hojas de cálculo y mensajería informal.

### Problema que resuelve
- ❌ Antes: Correo, hojas de cálculo, mensajería informal → baja trazabilidad
- ✅ Ahora: Plataforma integrada → trazabilidad completa, asignación clara, estado visible

---

## 🏗️ Arquitectura Hexagonal

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                           │
│  (Endpoints, Routing, Dependencias, Seguridad)             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (UseCases, DTOs, Coordinación de flujos)                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  (Entidades, Enums, Reglas de negocio, Estados, Patrones)  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  (ORM, Repositorios, BD, Autenticación, EventBus)           │
└──────────────────────────────────────────────────────────────┘
```

### Capas

#### **Domain** (`backend/domain/`)
- **Entidades**: User, Incident, Task, Notification
- **Enums**: Role, Severity, IncidentStatus, TaskStatus, NotificationStatus
- **Patrones**:
  - **State**: Máquina de estados para ciclo de vida de incidentes
  - **Observer**: EventBus y observadores para eventos del sistema
  - **Command**: Abstracción de comandos para envío de notificaciones
  - **Template Method**: Base para construir mensajes según canal
  - **Factory**: IncidentFactory y NotificationFactory para creación consistente
- **Repositorios (interfaces)**: Contrato entre capas

#### **Application** (`backend/application/`)
- **UseCases**: AuthUseCases, IncidentUseCases, TaskUseCases, NotificationUseCases
- **DTOs**: Contrato de entrada/salida (UserDTO, IncidentDTO, TaskDTO, etc.)
- **Lógica de orquestación**: Coordina dominio e infraestructura

#### **Infrastructure** (`backend/infrastructure/`)
- **Repositorios (implementación)**: SQLAlchemy + ORM
- **Modelos ORM**: UserModel, IncidentModel, TaskModel, NotificationModel
- **Base de datos**: Conexión y migraciones con Alembic
- **Autenticación**: hash de passwords con bcrypt, JWT
- **EventBus concreto**: Implementación del patrón Observer
- **Persistencia**: ORM desacoplado del dominio

#### **API** (`backend/api/`)
- **Endpoints**: CRUD para incidentes, tareas, notificaciones
- **Seguridad**: Dependencias y guards (roles/permisos)
- **Rutas**: Organizadas por recurso

#### **Frontend** (`frontend/`)
- **Streamlit**: app.py con vistas dinámicas
- **Login**: Autenticación y sesión
- **Paneles**: Incidentes, tareas, notificaciones
- **Autorización**: Respeta roles desde frontend (validación real en backend)

---

## 📚 Patrones de Diseño Implementados

### Patrones de Comportamiento

#### **1. Observer** (`backend/domain/observer.py`)
**Uso**: Publicar eventos del sistema y reaccionar automáticamente
- **Publisher**: EventBus
- **Observers**:
  - NotificationObserver: genera notificaciones al crear/cambiar incidentes
  - LogObserver: registra eventos en logs
- **Eventos**: INCIDENT_CREATED, INCIDENT_ASSIGNED, TASK_DONE, etc.

**Flujo**:
```python
# En use_cases.py
self.event_bus.publish(EventType.INCIDENT_CREATED, {"id": incident.id})

# El observer reacciona automáticamente creando notificaciones
```

#### **2. Command** (`backend/domain/commands.py`)
**Uso**: Encapsular la ejecución de notificaciones
- **Interfaz**: Command con método execute()
- **Implementaciones**:
  - SendEmailCommand: envío por email
  - SendInAppCommand: notificación en aplicación
- **Factory**: NotificationFactory decide cuál comando usar

**Flujo**:
```python
command = NotificationFactory.create_command(notification)
command.execute()
```

#### **3. State** (`backend/domain/state.py`)
**Uso**: Controlar el ciclo de vida de incidentes
- **Estados**:
  - OpenState: recién creado
  - AssignedState: asignado a usuario
  - InProgressState: en resolución
  - ResolvedState: resuelto
  - ClosedState: cerrado
- **Transiciones**: Validadas por cada estado

**Flujo**:
```python
incident._state.assign(incident, assignee_id)  # Cambia estado automáticamente
incident._state.start_progress(incident)
incident._state.resolve(incident)
```

#### **4. Template Method** (`backend/domain/templates.py`)
**Uso**: Construir mensajes de notificación según canal
- **Clase abstracta**: NotificationTemplate
- **Implementaciones**:
  - EmailNotificationTemplate: formato HTML para email
  - InAppNotificationTemplate: formato JSON compacto
- **Método template**: build_message() define estructura

**Flujo**:
```python
template = NotificationFactory.create_template(NotificationChannel.EMAIL)
message = template.build_message(notification)
```

### Patrones Creacionales

#### **5. Factory** (`backend/domain/factory.py`)
**Uso**: Crear entidades y comandos validando reglas
- **IncidentFactory**: crear incidentes con validaciones
  - Valida: título no vacío, descripción no vacía, severidad válida
  - Retorna: Incident(status=OPEN)
- **NotificationFactory**: crear comandos y templates según canal

#### **6. Abstract Factory** (justificación adicional)
**Implementado en**: NotificationFactory
**Razón**: En sistemas reales, cada canal (Email, SMS, Push) requiere:
- Su propio Command
- Su propio Template
- Su propia lógica de envío

**Beneficio**: Agregar nuevos canales sin modificar código existente
```python
@staticmethod
def create_command(notification: Notification) -> Command:
    if notification.channel == NotificationChannel.EMAIL:
        return SendEmailCommand(notification)
    if notification.channel == NotificationChannel.SMS:  # Futuro
        return SendSMSCommand(notification)
    # ...
```

---

## 🚀 Cómo Correrlo

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

**Servicios**:
- `db`: PostgreSQL en puerto 5432
- `api`: FastAPI en puerto 8000
- `ui`: Streamlit en puerto 8501

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

---

## 📖 Cómo Usarlo

### 1. Login
- Ir a http://localhost:8501
- Ingresar credenciales (usuario de prueba: `admin@test.com` / `password`)

### 2. Crear Incidente (Operator, Supervisor, Admin)
- Ir a "📋 Incidentes" → "Crear"
- Llenar: Título, Descripción, Severidad
- Click "Crear Incidente"
- Evento publicado → Observer crea notificación → Command ejecuta envío

### 3. Asignar Incidente (Supervisor, Admin)
- Ir a "📋 Incidentes" → "Lista"
- Click en incidente
- Ingresar ID de usuario
- Click "Asignar"

### 4. Cambiar Estado (Supervisor, Admin)
- Ir a "📋 Incidentes"
- Selectbox de estado
- State automáticamente valida transición

### 5. Crear / Actualizar Tarea
- Ir a "✅ Tareas"
- Crear: llenar formulario
- Actualizar: selectbox de estado → Click "Actualizar"

### 6. Ver Notificaciones
- Ir a "🔔 Notificaciones"
- Se actualizan en tiempo real cuando hay eventos

---

## 🔐 Roles y Permisos

| Rol | Can Create Incident | Can Assign | Can Change State | Can See All | Can Manage Users |
|-----|-------------------|-----------|-----------------|------------|------------------|
| OPERATOR | ✅ | ❌ | ❌ | ❌ (solo sus) | ❌ |
| SUPERVISOR | ✅ | ✅ | ✅ | ✅ (equipo) | ❌ |
| ADMIN | ✅ | ✅ | ✅ | ✅ (todos) | ✅ |

---

## 📊 Base de Datos

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

---

## 🧪 Tests

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
- ✅ Comandos de notificación
- ✅ Factory de incidentes
- ✅ Observer y EventBus
- ✅ Templates de notificación
- ✅ Repositorios SQLAlchemy
- ✅ Rutas y autenticación
- ✅ UseCases

---

## 📡 Endpoints Disponibles

### Autenticación
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

---

## 🎨 Demo - Escenarios Demostables

1. ✅ **Login exitoso** → Frontend autentica con API
2. ✅ **Crear incidente** → Desde frontend
3. ✅ **Incidente persiste** → En PostgreSQL vía ORM
4. ✅ **Publicar evento** → EventBus.publish()
5. ✅ **Observer reacciona** → NotificationObserver captura
6. ✅ **Template construye mensaje** → EmailNotificationTemplate.build_message()
7. ✅ **Command ejecuta envío** → SendEmailCommand.execute()
8. ✅ **Estado cambia** → State máquina de estados
9. ✅ **Factory crea** → IncidentFactory, NotificationFactory
10. ✅ **Filtrado por rol** → Operator ve solo sus incidentes

---

## 📂 Estructura del Proyecto

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
│   │   ├── database.py       # Conexión SQLAlchemy
│   │   ├── models.py         # ORM models
│   │   ├── repositories.py   # Implementaciones repositorio
│   │   ├── auth.py           # Hash, JWT
│   │   ├── alembic/          # Migraciones
│   │   └── __init__.py
│   └── __init__.py
├── frontend/
│   ├── app.py                # Streamlit principal
│   ├── .streamlit/
│   │   └── config.toml       # Configuración Streamlit
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
├── docker-compose.yml        # Orquestación de contenedores
├── Dockerfile                # Build API
├── requirements.txt          # Dependencias Python
├── pytest.ini                # Configuración pytest
├── alembic.ini               # Configuración migraciones
└── README.md                 # Este archivo
```

---

## 🔧 Tecnologías

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **BD**: PostgreSQL (Docker) / SQLite (Local)
- **Autenticación**: JWT + bcrypt
- **Testing**: pytest
- **Migraciones**: Alembic

### Frontend
- **Framework**: Streamlit
- **HTTP**: requests

### DevOps
- **Contenedores**: Docker
- **Orquestación**: Docker Compose

---

## 🎓 Lecciones de Diseño

### ¿Por qué Arquitectura Hexagonal?

1. **Testabilidad**: Cada capa puede testearse independientemente
2. **Flexible**: Cambiar BD, autenticación sin afectar lógica
3. **Mantenible**: Responsabilidades claras
4. **Escalable**: Fácil agregar nuevas capas

### ¿Por qué Patrones?

| Patrón | Razón |
|--------|-------|
| **State** | Validar transiciones de estado seguras |
| **Observer** | Desacoplar eventos de sus consecuencias |
| **Command** | Encapsular lógica de envío de notificaciones |
| **Template Method** | Reutilizar estructura de mensajes por canal |
| **Factory** | Validar y crear entidades consistentemente |
| **Abstract Factory** | Extensibilidad para nuevos canales sin modificar código |

---

## 🚦 Cómo Contribuir

1. Crear branch: `git checkout -b feature/nombre`
2. Hacer cambios
3. Commit: `git commit -m "feat: descripción"`
4. Push: `git push origin feature/nombre`
5. PR con descripción y cambios

---

## 📝 Licencia

Proyecto educativo PSet_3 - 2026

---

## 📧 Contacto

Preguntas o sugerencias → Email al profesor