import streamlit as st
from Beatrice_Advisors import display_beatrice
from Christina_Lewis import display_christina

st.set_page_config(
    page_title="Data Metrics Visualization",
    page_icon="📊",
    layout="wide"
)
def app():
    with st.sidebar:
        # st.logo(
        #     "C:\\Users\\mRemfort\\PycharmProjects\\data_workspace - Database\\Beatrice_Logo_2 Color_RGB@3840.png", size="large", icon_image= "C:\\Users\\mRemfort\\PycharmProjects\\data_workspace - Database\\Beatrice_Shield_2 Color_RGB@3840.png"
        #
        # )
        workspace = st.selectbox("Workspace", options=["Beatrice Advisors", "Christina Lewis"])
        st.divider()

    if workspace == "Beatrice Advisors":
        display_beatrice()
    else:
        display_christina()

if __name__ == "__main__":
    app()