import os
import pandas as pd
import plotly.express as px
import streamlit as st
import mysql.connector
import hashlib
from sqlalchemy import create_engine

#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Sentiment Analysis Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Sentiment Analysis Dashboard")

# Cached function to get database connection
@st.cache(allow_output_mutation=True)
def get_connection():
    return create_engine("mssql+pyodbc://username:password@DB_server/database")

# Get cached database connection
engine = get_connection()

# DATA LOADING

# Custom hashing function for MySQL connection
def hash_custom_conn(obj):
    return hashlib.md5(str(obj).encode()).hexdigest()

# Function to load data from MySQL database
@st.cache_data(hash_funcs={type(engine): hash_custom_conn})
def load_data():
    try:
        query = """
            SELECT CreatedTime, SubmissionID, SubmissionTitle, Text, SubmissionURL, Score, NumberOfComments, TopicName
            FROM reddit_hn ORDER BY CreatedTime Desc;
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

df = load_data()

with st.expander("Data Preview"):
    st.dataframe(df.head(100))

