import streamlit as st          #type:ignore
from api_client import APIClient

def show_login_page(api_client: APIClient):
    """Muestra la página de login"""
    st.title("OpsCenter - Login")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Sistema de Gestion de Incidentes")

        with st.form("login_form"):
            username = st.text_input("Usuario (email)")
            password = st.text_input("Contrasena", type="password")
            submitted = st.form_submit_button("Iniciar Sesion", use_container_width=True)

            if submitted:
                try:
                    result = api_client.login(username, password)
                    if result and "access_token" in result:
                        st.session_state.token = result["access_token"]
                        st.session_state.user = {"email": username}
                        st.success("Login exitoso")
                        st.rerun()
                    else:
                        st.error("Credenciales invalidas")
                except Exception as e:
                    st.error(f"Error: {str(e)}")