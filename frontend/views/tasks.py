import streamlit as st        #type:ignore
from api_client import APIClient

def show_tasks_page(api_client: APIClient):
    """Muestra la página de tareas"""
    st.header("Tareas")

    tabs = st.tabs(["Mi Panel", "Crear Tarea"])

    with tabs[0]:
        st.subheader("Mis Tareas")
        if st.button("Actualizar"):
            st.rerun()

        try:
            tasks = api_client.get_tasks()
            if tasks:
                for task in tasks:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{task['title']}**")
                            st.caption(f"Incidente: {task.get('incident_id', 'N/A')}")
                        with col2:
                            status_map = {"OPEN": "Abierto", "IN_PROGRESS": "En Progreso", "DONE": "Completado"}
                            st.metric("Estado", status_map.get(task['status'], task['status']))
                        with col3:
                            new_status = st.selectbox(
                                "Cambiar estado",
                                ["OPEN", "IN_PROGRESS", "DONE"],
                                key=f"task_status_{task['id']}"
                            )
                            if st.button("Actualizar", key=f"update_task_{task['id']}"):
                                try:
                                    result = api_client.change_task_status(task['id'], new_status)
                                    st.success("Tarea actualizada")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al actualizar tarea: {str(e)}")
            else:
                st.info("No hay tareas")
        except Exception as e:
            st.error(f"Error al cargar tareas: {str(e)}")

    with tabs[1]:
        st.subheader("Crear Nueva Tarea")
        with st.form("create_task_form"):
            incident_id = st.text_input("ID del Incidente")
            title = st.text_input("Titulo", max_chars=100)
            description = st.text_area("Descripcion", height=100)
            assigned_to = st.text_input("Asignar a (User ID)")

            if st.form_submit_button("Crear Tarea", use_container_width=True):
                try:
                    result = api_client.create_task(incident_id, title, description, assigned_to)
                    if result:
                        st.success("Tarea creada")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al crear tarea: {str(e)}")