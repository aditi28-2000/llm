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

# Cached function to get database connection
@st.cache(allow_output_mutation=True)
def get_connection():
    return create_engine(connection_string)

# Get cached database connection
engine = get_connection()

# Function to load data from the database
@st.cache_data(hash_funcs={type(engine): lambda x: x})
def load_data():
    query = """
        SELECT CreatedTime, SubmissionID, SubmissionTitle, Text, SubmissionURL, Score, NumberOfComments, TopicName
        FROM reddit_hn ORDER BY CreatedTime Desc;
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    catch Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

# Load data from the database
df = load_data()
