import streamlit as st
from frontend.api_client import APIClient
from typing import Dict, List

def show_incidents_page(api_client: APIClient):
    """Muestra la página de incidentes"""
    st.header("Incidentes")

    tabs = st.tabs(["Lista", "Crear", "Mis Incidentes"])

    with tabs[0]:
        st.subheader("Todos los Incidentes")
        if st.button("Actualizar"):
            st.rerun()

        try:
            incidents = api_client.get_incidents()
            if incidents:
                for inc in incidents:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{inc['title']}**")
                            st.caption(f"{inc['description'][:100]}...")
                        with col2:
                            severity_map = {
                                "LOW": "Bajo",
                                "MEDIUM": "Medio",
                                "HIGH": "Alto",
                                "CRITICAL": "Critico"
                            }
                            st.metric("Severidad", severity_map.get(inc['severity'], inc['severity']))
                        with col3:
                            status_map = {
                                "OPEN": "Abierto",
                                "ASSIGNED": "Asignado",
                                "IN_PROGRESS": "En Progreso",
                                "RESOLVED": "Resuelto",
                                "CLOSED": "Cerrado"
                            }
                            st.metric("Estado", status_map.get(inc['status'], inc['status']))

                        if st.button("Ver Detalles", key=f"detail_{inc['id']}"):
                            st.session_state.selected_incident = inc['id']
                            st.rerun()
            else:
                st.info("No hay incidentes")
        except Exception as e:
            st.error(f"Error al cargar incidentes: {str(e)}")

    with tabs[1]:
        st.subheader("Crear Nuevo Incidente")
        with st.form("create_incident_form"):
            title = st.text_input("Titulo", max_chars=100)
            description = st.text_area("Descripcion", height=120)
            severity = st.selectbox("Severidad", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

            if st.form_submit_button("Crear Incidente", use_container_width=True):
                try:
                    result = api_client.create_incident(title, description, severity)
                    if result:
                        st.success(f"Incidente creado: {result['id']}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al crear incidente: {str(e)}")

    with tabs[2]:
        st.subheader("Mis Incidentes")
        try:
            incidents = api_client.get_incidents()
            user_incidents = [inc for inc in incidents if inc.get('created_by') == st.session_state.user.get('id')]

            if user_incidents:
                for inc in user_incidents:
                    with st.container(border=True):
                        st.markdown(f"**{inc['title']}**")
                        st.caption(f"Estado: {inc['status']} | Severidad: {inc['severity']}")
            else:
                st.info("No tienes incidentes creados")
        except Exception as e:
            st.error(f"Error al cargar tus incidentes: {str(e)}")

def show_incident_detail(api_client: APIClient, incident_id: str):
    """Muestra detalle de un incidente específico"""
    try:
        incident = api_client.get_incident(incident_id)

        st.header(f"Incidente: {incident['title']}")
        st.write(f"**Descripción:** {incident['description']}")
        st.write(f"**Severidad:** {incident['severity']}")
        st.write(f"**Estado:** {incident['status']}")
        st.write(f"**Creado por:** {incident.get('created_by', 'N/A')}")
        st.write(f"**Asignado a:** {incident.get('assigned_to', 'No asignado')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("← Volver a lista"):
                if 'selected_incident' in st.session_state:
                    del st.session_state.selected_incident
                st.rerun()

        with col2:
            new_status = st.selectbox(
                "Cambiar estado",
                ["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"],
                key="change_status"
            )
            if st.button("Actualizar Estado"):
                try:
                    result = api_client.change_incident_status(incident_id, new_status)
                    st.success("Estado actualizado")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al cambiar estado: {str(e)}")

    except Exception as e:
        st.error(f"Error al cargar incidente: {str(e)}")