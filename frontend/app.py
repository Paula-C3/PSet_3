import streamlit as st
import requests
import json
from datetime import datetime

# Configuración
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")
st.set_page_config(page_title="OpsCenter", layout="wide", initial_sidebar_state="expanded")

# Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def api_request(method, endpoint, **kwargs):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        response = requests.request(method, url, headers=headers, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else None
    except requests.exceptions.RequestException as e:
        st.error(f"Error en API: {str(e)}")
        return None

def login_page():
    st.title("OpsCenter - Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sistema de Gestion de Incidentes")
        
        with st.form("login_form"):
            username = st.text_input("Usuario (email)")
            password = st.text_input("Contrasena", type="password")
            submitted = st.form_submit_button("Iniciar Sesion", use_container_width=True)
            
            if submitted:
                result = api_request("POST", "/auth/login", 
                                   json={"username": username, "password": password})
                if result:
                    st.session_state.token = result.get("access_token")
                    st.session_state.user = {"email": username}
                    st.success("Login exitoso")
                    st.rerun()
                else:
                    st.error("Credenciales invalidas")

def incidents_view():
    st.header("Incidentes")
    
    tabs = st.tabs(["Lista", "Crear", "Mis Incidentes"])
    
    with tabs[0]:
        st.subheader("Todos los Incidentes")
        if st.button("Actualizar", key="refresh_incidents"):
            st.rerun()
        
        incidents = api_request("GET", "/incidents")
        if incidents:
            for inc in incidents:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{inc['title']}**")
                        st.caption(f"{inc['description'][:100]}...")
                    with col2:
                        severity_color = {
                            "LOW": "Bajo", "MEDIUM": "Medio", "HIGH": "Alto", "CRITICAL": "Critico"
                        }
                        st.metric("Severidad", severity_color.get(inc['severity'], inc['severity']))
                    with col3:
                        status_color = {
                            "OPEN": "Abierto", "ASSIGNED": "Asignado", 
                            "IN_PROGRESS": "En Progreso", "RESOLVED": "Resuelto", "CLOSED": "Cerrado"
                        }
                        st.metric("Estado", status_color.get(inc['status'], inc['status']))
                    
                    if st.button("Ver Detalles", key=f"detail_{inc['id']}"):
                        st.session_state.selected_incident = inc['id']
                        st.rerun()
        else:
            st.info("No hay incidentes")
    
    with tabs[1]:
        st.subheader("Crear Nuevo Incidente")
        with st.form("create_incident_form"):
            title = st.text_input("Titulo", max_chars=100)
            description = st.text_area("Descripcion", height=120)
            severity = st.selectbox("Severidad", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            
            if st.form_submit_button("Crear Incidente", use_container_width=True):
                result = api_request("POST", "/incidents",
                                   json={
                                       "title": title,
                                       "description": description,
                                       "severity": severity
                                   })
                if result:
                    st.success(f"Incidente creado: {result['id']}")
                    st.rerun()

def tasks_view():
    st.header("Tareas")
    
    tabs = st.tabs(["Mi Panel", "Crear Tarea"])
    
    with tabs[0]:
        st.subheader("Mis Tareas")
        if st.button("Actualizar", key="refresh_tasks"):
            st.rerun()
        
        tasks = api_request("GET", "/tasks")
        if tasks:
            for task in tasks:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{task['title']}**")
                        st.caption(f"Incidente: {task.get('incident_id', 'N/A')}")
                    with col2:
                        status_icon = {"OPEN": "Abierto", "IN_PROGRESS": "En Progreso", "DONE": "Completado"}
                        st.metric("Estado", status_icon.get(task['status'], task['status']))
                    with col3:
                        new_status = st.selectbox(
                            "Cambiar estado",
                            ["OPEN", "IN_PROGRESS", "DONE"],
                            key=f"task_status_{task['id']}"
                        )
                        if st.button("Actualizar", key=f"update_task_{task['id']}"):
                            result = api_request("PATCH", f"/tasks/{task['id']}/status",
                                               json={"new_status": new_status})
                            if result:
                                st.success("Tarea actualizada")
                                st.rerun()
        else:
            st.info("No hay tareas")
    
    with tabs[1]:
        st.subheader("Crear Nueva Tarea")
        with st.form("create_task_form"):
            incident_id = st.text_input("ID del Incidente")
            title = st.text_input("Titulo", max_chars=100)
            description = st.text_area("Descripcion", height=100)
            assigned_to = st.text_input("Asignar a (User ID)")
            
            if st.form_submit_button("Crear Tarea", use_container_width=True):
                result = api_request("POST", "/tasks",
                                   json={
                                       "incident_id": incident_id,
                                       "title": title,
                                       "description": description,
                                       "assigned_to": assigned_to
                                   })
                if result:
                    st.success("Tarea creada")
                    st.rerun()

def notifications_view():
    st.header("Notificaciones")
    
    if st.button("Actualizar", key="refresh_notifications"):
        st.rerun()
    
    notifications = api_request("GET", "/notifications")
    if notifications:
        for notif in notifications:
            status_color = {
                "PENDING": "Pendiente",
                "SENT": "Enviado",
                "FAILED": "Fallido"
            }
            with st.container(border=True):
                st.markdown(f"**{notif['event_type']}** {status_color.get(notif['status'], '')}")
                st.write(notif['message'])
                st.caption(f"Canal: {notif['channel']} | {notif['created_at']}")
    else:
        st.info("No hay notificaciones")

def main():
    if not st.session_state.token:
        login_page()
    else:
        # Sidebar
        with st.sidebar:
            st.title("OpsCenter")
            st.divider()
            
            if st.session_state.user:
                st.write(f"Usuario: {st.session_state.user.get('email', 'Usuario')}")
            
            st.divider()
            page = st.radio(
                "Navegacion",
                ["Incidentes", "Tareas", "Notificaciones"],
                label_visibility="collapsed"
            )
            
            st.divider()
            if st.button("Cerrar Sesion", use_container_width=True):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
        
        # Main content
        if page == "Incidentes":
            incidents_view()
        elif page == "Tareas":
            tasks_view()
        elif page == "Notificaciones":
            notifications_view()

if __name__ == "__main__":
    main()
