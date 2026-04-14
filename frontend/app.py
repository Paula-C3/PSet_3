import os
import streamlit as st
from api_client import APIClient
from views.login import show_login_page
from views.incidents import show_incidents_page, show_incident_detail
from views.tasks import show_tasks_page
from views.notifications import show_notifications_page

st.set_page_config(
    page_title="OpsCenter",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

for key, default in [
    ("token", None),
    ("user", None),
    ("selected_incident", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient(base_url=BASE_URL)

api_client: APIClient = st.session_state.api_client

if st.session_state.token:
    api_client.set_token(st.session_state.token)


def main():
    if not st.session_state.token:
        show_login_page(api_client)
        return

    with st.sidebar:
        st.title("OpsCenter")
        st.divider()

        user = st.session_state.user or {}
        role = user.get("role", "")
        if isinstance(role, dict):
            role = role.get("value", str(role))
        role = str(role).replace("Role.", "")

        st.write(f"**{user.get('email', 'Usuario')}**")
        st.caption(f"Rol: {role}")
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
            st.session_state.selected_incident = None
            api_client.clear_token()
            st.rerun()

    if st.session_state.selected_incident:
        show_incident_detail(api_client, st.session_state.selected_incident)
    elif page == "Incidentes":
        show_incidents_page(api_client)
    elif page == "Tareas":
        show_tasks_page(api_client)
    elif page == "Notificaciones":
        show_notifications_page(api_client)


if __name__ == "__main__":
    main()