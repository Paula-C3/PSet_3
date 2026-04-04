import streamlit as st          #type:ignore
from api_client import APIClient
from views.login import show_login_page
from views.incidents import show_incidents_page, show_incident_detail
from views.tasks import show_tasks_page
from views.notifications import show_notifications_page

# Configuración
st.set_page_config(page_title="OpsCenter", layout="wide", initial_sidebar_state="expanded")

# Estado de sesión
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# Cliente API
api_client = APIClient()

def main():
    # Configurar token en cliente API
    if st.session_state.token:
        api_client.set_token(st.session_state.token)

    if not st.session_state.token:
        show_login_page(api_client)
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
                api_client.clear_token()
                st.rerun()

        # Main content
        if 'selected_incident' in st.session_state:
            show_incident_detail(api_client, st.session_state.selected_incident)
        elif page == "Incidentes":
            show_incidents_page(api_client)
        elif page == "Tareas":
            show_tasks_page(api_client)
        elif page == "Notificaciones":
            show_notifications_page(api_client)

if __name__ == "__main__":
    main()
