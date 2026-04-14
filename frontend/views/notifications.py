import streamlit as st          #type:ignore
from api_client import APIClient

def show_notifications_page(api_client: APIClient):
    """Muestra la página de notificaciones"""
    st.header("Notificaciones")

    if st.button("Actualizar"):
        st.rerun()

    try:
        notifications = api_client.get_notifications()
        if notifications:
            for notif in notifications:
                status_map = {
                    "PENDING": "Pendiente",
                    "SENT": "Enviado",
                    "FAILED": "Fallido"
                }
                with st.container(border=True):
                    st.markdown(f"**{notif['event_type']}** {status_map.get(notif['status'], '')}")
                    st.write(notif['message'])
                    st.caption(f"Canal: {notif['channel']} | {notif['created_at']}")
        else:
            st.info("No hay notificaciones")
    except Exception as e:
        st.error(f"Error al cargar notificaciones: {str(e)}")