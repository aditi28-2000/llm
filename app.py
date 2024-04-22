import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from PIL import Image

# DATABASE
######################################################################
# Retrieve database credentials from secrets.toml
server = st.secrets["server"]
database = st.secrets["database"]
username = st.secrets["username"]
password = st.secrets["password"]

# Construct the connection string using pymysql dialect
connection_string = f"mysql+pymysql://{username}:{password}@{server}/{database}"

def get_connection():
    return create_engine(connection_string)

# Get database connection
engine = get_connection()

def load_data():
    query = """
        SELECT * FROM sentiment_analysis;
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading data from the database: {e}")
        return pd.DataFrame()

# Load data from the database
df = load_data()

# Define the Dashboard page
def dashboard():
    st.title("Dashboard")
    
    # Load and display the header image
    image = Image.open("LLM2.png")
    st.image(image, use_column_width=True)
    
    # Display the total number of posts
    total_posts = len(df)
    st.markdown(f"### Total Number of Posts: {total_posts}")

# Define the Direct Feed page
def direct_feed():
    st.title("Direct Feed")
    st.write("Direct Feed content goes here")

# Main function to manage the Streamlit app
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation Panel")
    page = st.sidebar.radio("Select a page:", ["Dashboard", "Direct Feed"])
    
    # Route to the selected page
    if page == "Dashboard":
        dashboard()
    elif page == "Direct Feed":
        direct_feed()

# Run the app
if __name__ == "__main__":
    main()

# Close the connection to the database
engine.dispose()
