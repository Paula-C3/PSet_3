# PSet_3
# OpsCenter 🚨

Plataforma interna de gestión de incidentes operativos para una fintech.

# Integrantes
- Vaishali Desai
- Pamela Barbosa
- Ayelén Jaramillo
- Paula Caicedo
- Giuliana Auqui

##  Problema

Actualmente, la gestión de incidentes, tareas y notificaciones se realiza mediante herramientas dispersas como correos electrónicos, hojas de cálculo y mensajería informal. Esto genera:

- Falta de trazabilidad
- Mala asignación de responsabilidades
- Baja visibilidad del estado de incidentes
- Notificaciones inconsistentes

**OpsCenter** resuelve estos problemas centralizando la gestión en una única plataforma. 

---

##  Objetivo

Diseñar e implementar una aplicación completa que incluya:

- Backend con lógica de negocio y persistencia
- Frontend interactivo
- Arquitectura hexagonal
- Uso de ORM
- Autenticación y autorización
- Patrones de diseño
- Docker y despliegue
- Trabajo colaborativo en GitHub 

---

##  Arquitectura
Diseñar e implementar una aplicación completa que incluya:

- El sistema sigue una **arquitectura hexagonal (Ports & Adapters)**:
  Frontend (Streamlit)
  ↓
  API (FastAPI)
  ↓
  Application Layer (Use Cases, DTOs)
  ↓
  Domain Layer (Entidades, reglas, patrones)
  ↓
  Infrastructure Layer (ORM, DB, Auth)
---

### Capas:

- **Domain**
  - Entidades (User, Incident, Task, Notification)
  - Reglas de negocio
  - Patrones de diseño
  - Interfaces de repositorio

- **Application**
  - Casos de uso
  - DTOs
  - Coordinación del flujo

- **Infrastructure**
  - SQLAlchemy (ORM)
  - PostgreSQL
  - JWT Auth
  - Implementaciones de repositorios

- **API**
  - Endpoints REST con FastAPI

- **Frontend**
  - Streamlit (UI)

---

##  Tecnologías

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **ORM:** SQLAlchemy
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT + bcrypt
- **Contenedores:** Docker + Docker Compose

---

##  Patrones de Diseño

###  Observer
- Manejo de eventos del sistema
- Ejemplo: cuando se crea un incidente, se notifica automáticamente

###  Command
- Encapsula acciones como envío de notificaciones
- Ejemplo: `SendEmailCommand`, `SendInAppCommand`

###  State
- Controla el ciclo de vida de los incidentes
- Estados: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`

###  Template Method
- Construcción de mensajes de notificación por canal

###  Factory
- Creación centralizada de entidades y comandos

###  Patrón adicional: Abstract Factory
Se utiliza para generar diferentes tipos de notificaciones según el evento, permitiendo:

- Bajo acoplamiento
- Extensibilidad
- Consistencia en la creación de objetos

---

##  Roles del sistema

- **ADMIN**
  - Acceso total
  - Gestión de incidentes y usuarios

- **SUPERVISOR**
  - Asigna incidentes
  - Supervisa tareas

- **OPERATOR**
  - Crea incidentes
  - Gestiona sus tareas

---

##  Funcionalidades principales

- Login de usuario
- Creación de incidentes
- Asignación de incidentes
- Cambio de estado de incidentes
- Creación y gestión de tareas
- Generación automática de notificaciones
- Visualización por roles

---
## Organización del equipo

El proyecto se desarrolló en 5 roles:

- Arquitectura de dominio
- Patrones de diseño
- Infraestructura
- Aplicación y API
- Frontend y DevOps
---

##  Cómo ejecutar el proyecto

### Requisitos

- Docker
- Docker Compose

### Ejecutar:

```bash
docker compose up --build




