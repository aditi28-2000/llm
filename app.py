import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
import plotly.express as px
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

# Load data from CSV before getting SQL data
# df = pd.read_csv("sentiment_reddit_data.csv")

######################################################################
# DESIGN 

# Load and display the image at the top of the page
image = Image.open("LLM2.png")
st.image(image, use_column_width=True)

# Define CSS for the decorative header
header_style = f"""
    <style>
        .header {{
            background-image: url('{image}');
            background-size: cover;
            height: 100px; /* Adjust height as needed */
            width: 100%;
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding-top: 30px; /* Adjust vertical alignment */
        }}
    </style>
"""

# Display the decorative header
st.markdown(header_style, unsafe_allow_html=True)

# Set the configuration option to disable the PyplotGlobalUseWarning
st.set_option("deprecation.showPyplotGlobalUse", False)

# Sidebar layout
with st.sidebar:
    st.title("Navigation Panel")
    tabs = st.radio("Select a tab:", ["Direct Feed", "Filtered Feed"])

    if tabs == "Direct Feed":
        st.markdown("# Total Posts: " + str(len(df)))
        st.subheader("Reddit and Hackernews Data")
        
        # Display each post inside a bordered box
        for index, row in df.head(10).iterrows():
            with st.expander(f"{row['SubmissionTitle']} - {row['SubmissionID']}", expanded=False):
                st.markdown(
                    f"**Score:** {row['Score']} | **Comments:** {row['NumberOfComments']}"
                    f"\n{row['Text'][:200]}{'...' if len(row['Text']) > 200 else ''}"
                    f"\n[Read More]({row['SubmissionURL']})"
                )
                
    elif tabs == "Filtered Feed":
        st.subheader("Filter Options")
        selected_subreddit = st.selectbox(
            "Select Subreddit:", df["TopicName"].unique()
        )
        selected_sentiment = st.selectbox(
            "Select Sentiment Category:", ["Negative", "Neutral", "Positive"]
        )
        
        # Check if the columns exist in the DataFrame
        if {"TopicName", "Sentiment"}.issubset(df.columns):
            filtered_df = df[
                (df["TopicName"] == selected_subreddit)
                & (df["Sentiment"] == selected_sentiment)
            ]
            
            # Display filtered posts inside a bordered box
            for index, row in filtered_df.head(10).iterrows():
                with st.expander(f"{row['SubmissionTitle']} - {row['SubmissionID']}", expanded=False):
                    st.markdown(
                        f"**Score:** {row['Score']} | **Comments:** {row['NumberOfComments']}"
                        f"\n{row['Text'][:200]}{'...' if len(row['Text']) > 200 else ''}"
                        f"\n[Read More]({row['SubmissionURL']})"
                    )
        else:
            st.write("Required columns not found in the DataFrame. Unable to apply filters.")


# Sentiment Analysis
st.subheader("Sentiment Analysis")

# Basic Statistics
st.subheader("Basic Statistics")
st.write(df.drop(columns=["CreatedTime"]).describe())  # Exclude 'CreatedTime' column

# Function to calculate metrics
def calculate_metrics(df):
    total_posts = len(df)
    positive_posts = len(df[df['Sentiment'] == 'POSITIVE'])
    negative_posts = len(df[df['Sentiment'] == 'NEGATIVE'])
    neutral_posts = len(df[df['Sentiment'] == 'NEUTRAL'])
    return total_posts,positive_posts, negative_posts, neutral_posts

# Calculate metrics
total_posts,positive_posts, negative_posts, neutral_posts = calculate_metrics(df)

# Function to plot sentiment counts over time
def plot_sentiment_over_time(df):
    # Group the data by CreatedTime and Sentiment_Category, and calculate the counts
    sentiment_counts = df.groupby([df["CreatedTime"].dt.date, "Sentiment"]).size().reset_index(name='Count')
    
    # Create a line plot using Plotly Express
    fig = px.line(sentiment_counts, x='CreatedTime', y='Count', color='Sentiment',
                  title='Sentiment Analysis Over Time', labels={'Count': 'Count of Posts', 'CreatedTime': 'Date'})
    
    # Update plot layout
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='Count')
    
    # Return the plot
    return fig

# Plot the sentiment counts over time and display it in Streamlit
st.subheader("Sentiment Analysis Over Time")
fig = plot_sentiment_over_time(df)
st.plotly_chart(fig)

# Word Cloud
st.subheader("Word Cloud for All Data")
if "Text" in df.columns:
    df["Text"].fillna("", inplace=True)
    text = " ".join(df["Text"])
    
    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    
    # Plot the word cloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    
    # Hide the axes
    ax.axis("off")
    
    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write("No 'Text' column found in the DataFrame.")


# Close the connection to the database
engine.dispose()
