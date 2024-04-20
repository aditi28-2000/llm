import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

# Retrieve database credentials from secrets.toml
server = st.secrets["server"]
database = st.secrets["database"]
username = st.secrets["username"]
password = st.secrets["password"]

# Construct the connection string using pymysql dialect
connection_string = f"mysql+pymysql://{username}:{password}@{server}/{database}"

# Function to get database connection
def get_connection():
    return create_engine(connection_string)

# Get database connection
engine = get_connection()

# Function to load data from the database
def load_data():
    query = """
        SELECT CreatedTime, SubmissionID, SubmissionTitle, Text, SubmissionURL, Score, NumberOfComments, TopicName
        FROM reddit_hn ORDER BY CreatedTime Desc;
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

# Load data from the database
df = load_data()

# Print the data using st.dataframe()
st.dataframe(df)
