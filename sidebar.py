import streamlit as st

def render_sidebar(df_weekly_scores):
    st.sidebar.title("The Jager Crew ⚽ 2024/25")
    
    # users = sorted(set(df_weekly_scores["player_name"]))
    users = ["Dan", "Rahul", "Samit"]
    
    # if "selected_user" not in st.session_state:
    #     st.session_state.selected_user = users[0]
    # st.sidebar.selectbox(
    #     "Select your name",
    #     users,
    #     key="selected_user",
    # )
    
    # return st.session_state.selected_user
    # st.write(st.session_state.selected_user)  
    
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = users[0]
        # st.session_state.selected_user = "Rahul"
    
    selected_user = st.sidebar.selectbox(
        "Select your name",
        users,
        key="selected_user",
    )
    
    if selected_user != st.session_state.selected_user:
        st.session_state.selected_user = selected_user
        # Debugging output
        # st.write("DEBUG: User changed to:", selected_user)
    
    st.write(st.session_state)
        
    return selected_user