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
    return create_engine("mssql+pyodbc://username:password@DB_server/database?driver=ODBC+Driver+17+for+SQL+Server", 
                         fast_executemany=True)

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
            SELECT CreatedTime, SubmissionID, SubmissionTitle, Text, SubmissionURL, Score, NumberOfComments, SubredditName, Sentiment, Sentiment_Score
            FROM sentiment_reddit_data ORDER BY CreatedTime Desc;
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

df = load_data()

with st.expander("Data Preview"):
    st.dataframe(df.head(100))

# VISUALIZATION
    
# Function to calculate metrics
def calculate_metrics(df):
    total_posts = len(df)
    positive_posts = len(df[df['Sentiment'] == 'POSITIVE'])
    negative_posts = len(df[df['Sentiment'] == 'NEGATIVE'])
    neutral_posts = len(df[df['Sentiment'] == 'NEUTRAL'])
    return total_posts, positive_posts, negative posts, neutral_posts

# Calculate metrics
total_posts, positive_posts, negative_posts, neutral_posts = calculate_metrics(df)

# Display the total number of posts
st.info('Total Number of Posts in the Database')
st.write(f'Total Posts: {total_posts}')

# Function to plot time series sentiment
def plot_sentiment_over_time(df):
    fig = px.line(df, x='CreatedTime', y='Sentiment_Score', color='Sentiment',
                  title='Sentiment Analysis Over Time', labels={'Sentiment_Score': 'Sentiment Score'})
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Sentiment Score')
    return fig

# Plot average sentiment score per subreddit
def avg_sentiment(df):
    avg_sentiment_per_subreddit = df.groupby('SubredditName')['Sentiment_Score'].mean().reset_index()
    fig = px.bar(avg_sentiment_per_subreddit, x='SubredditName', y='Sentiment_Score',
                 title='Average Sentiment Score per Subreddit')
    fig.update_xaxes(title='Subreddit Name', categoryorder='total descending')
    fig.update_yaxes(title='Average Sentiment Score')
    return fig

# Create a pie chart for sentiment distribution
labels = ['Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment']
values = [positive_posts, negative_posts, neutral_posts]

fig_pie = px.pie(values=values, names=labels, hole=0.5)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(title='Sentiment Distribution')

# Plot total number of positive and negative sentiments for each subreddit
def plot_sentiments_by_subreddit(df):
    sentiments_by_subreddit = df.groupby(['SubredditName', 'Sentiment']).size().reset_index(name='Count')
    fig = px.bar(sentiments_by_subreddit, x='SubredditName', y='Count', color='Sentiment',
                 barmode='group', title='Total Number of Positive and Negative Sentiments for Each Subreddit')
    fig.update_xaxes(title='Subreddit Name')
    fig.update_yaxes(title='Count')
    return fig

# Display the charts in columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader('Sentiment Distribution')
    st.plotly_chart(fig_pie)
    st.subheader('Sentiment Analysis Over Time')
    st.plotly_chart(plot_sentiment_over_time(df))

with col2:
    # Display the plot of sentiments by subreddit
    st.subheader('Total Number of Positive and Negative Sentiments for Each Subreddit')
    st.plotly_chart(plot_sentiments_by_subreddit(df))
    st.subheader('Average Sentiment Score per Subreddit')
    st.plotly_chart(avg_sentiment(df))
