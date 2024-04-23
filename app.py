
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
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
##############################################################################################

# Define the Dashboard page
def dashboard():    
    # Load and display the header image
    image = Image.open("LLM2.png")
    st.image(image, use_column_width=True)
    # Define custom CSS styles
    custom_css = """
        <style>
            /* Increase the font size of the info box and other text */
            .stAlert {
                font-size: 25px; /* Adjust the value as desired */
            }
            /* Increase the font size for text */
            .stText {
                font-size: 25px; /* Adjust the value as desired */
            }
            /* Increase font size */
            body {
                font-size: 22px;
            }
            /* Increase image size */
            .stImage > img {
                width: 100%;  /* Increase image width to 100% */
                height: auto; /* Adjust height to maintain aspect ratio */
            }
             div[data-testid="stMarkdownContainer"][class^="st-emotion-cache-"] p {
            font-size: 18px; /* Increase the font size as desired */
        }
        </style>
    """
    # Apply custom CSS styles using st.markdown
    st.markdown(custom_css, unsafe_allow_html=True)
    
    def calculate_metrics(df):
        total_posts = len(df)
        total_comments = df['NumberOfComments'].sum()  # Calculate total comments
        positive_posts = len(df[df['Sentiment'] == 'POSITIVE'])
        negative_posts = len(df[df['Sentiment'] == 'NEGATIVE'])
        neutral_posts = len(df[df['Sentiment'] == 'NEUTRAL'])
        posts_per_llm = df.groupby('TopicName')['SubmissionID'].nunique().reset_index()
        return total_posts, total_comments, positive_posts, negative_posts, neutral_posts, posts_per_llm


    
    # Calculate metrics
    total_posts, total_comments, positive_posts, negative_posts, neutral_posts, posts_per_llm = calculate_metrics(df)


    # Display total posts
    st.info(f'Total Posts in the Database: {total_posts}')
 
    # Display sentiment distribution
    st.title(" Overall Sentiment Distribution")
    labels = ['Negative Sentiment', 'Positive Sentiment', 'Neutral Sentiment']
    values = [negative_posts, positive_posts, neutral_posts]
    colors = ['grey', 'red', 'skyblue']
    fig_pie = px.pie(values=values, names=labels, hole=0.5, color_discrete_sequence=colors)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, width=800, height=600)

    # Group by TopicName and calculate the total number of comments per Language Model
    total_comments_per_llm = df.groupby('TopicName')['NumberOfComments'].sum().reset_index()

    # Merge total_posts_per_llm and total_comments_per_llm on 'TopicName'
    posts_comments_per_llm = posts_per_llm.merge(total_comments_per_llm, on='TopicName')

    unique_topic_count = df['TopicName'].nunique()
    st.info(f"Distinct Language Models Captured in the Database: {unique_topic_count}")


    # Rename the columns
    posts_comments_per_llm.columns = ["Language Model", "Total Posts", "Total Comments"]
    # Sort the DataFrame by 'Total Posts' in descending order
    posts_comments_per_llm = posts_comments_per_llm.sort_values(by='Total Posts', ascending=False)

    st.dataframe(posts_comments_per_llm)
    st.dataframe(posts_comments_per_llm.style.hide(axis="index"))

    # Sort the DataFrame by 'NumberOfComments' in descending order
    #Make this table actually display the post w number of comments w sentiment
    df_sorted_by_comments = df.sort_values(by='NumberOfComments', ascending=False)

    # Select the top 10 most recent posts with the most comments
    top_10_posts_with_most_comments = df_sorted_by_comments.head(10)

    # Display the table of the top 10 most recent posts with the most comments
    st.write(top_10_posts_with_most_comments)




# Define the Direct Feed page
def direct_feed():
    st.title("Direct Feed")

    # Create filters for TopicName and Sentiment
    topic_options = df['TopicName'].unique()
    selected_topic = st.selectbox("Select Language Model:", topic_options)
    
    sentiment_options = ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
    selected_sentiment = st.selectbox("Select Sentiment:", sentiment_options)

    # Filter the data based on selected filters
    filtered_df = df[
        (df['TopicName'] == selected_topic) &
        (df['Sentiment'] == selected_sentiment)
    ]

    # Sort the filtered data frame by CreatedTime in descending order
    filtered_df_sorted = filtered_df.sort_values(by='CreatedTime', ascending=False)

    # Select the 10 most recent posts from the filtered data
    recent_posts = filtered_df_sorted.head(10)
    
    # Define custom CSS for the expander header
    custom_style = """
        <style>
            .expander-header {
                font-size: 18px; /* Adjust the font size as desired */
                font-weight: bold; /* Make the text bold */
                color: blue; /* Set the text color to blue */
            }
            /* Target the specific div element using data-testid and class attributes */

            div[data-testid="stMarkdownContainer"][class^="st-emotion-cache-"] p {
            font-size: 18px; /* Increase the font size as desired */
        }
     }
        }
        </style>
    """
    # Apply the custom CSS using st.markdown
    st.markdown(custom_style, unsafe_allow_html=True)

    # Display the filtered posts in rectangular boxes
    for index, row in recent_posts.iterrows():
        # Define inline CSS for the expander header
        expander_header_text = f"{row['SubmissionTitle']} - {row['CreatedTime']}"
        
        # Display the rectangular box with a "Read More" expander
        with st.expander(expander_header_text, expanded=False):
            st.markdown(
                f"""
                <div class="rectangular-box">
                    <p><strong>Submission Title:</strong> {row['SubmissionTitle']}</p>
                    <p><strong>Sentiment:</strong> {row['Sentiment']}</p>
                    <p><strong>Topic Name:</strong> {row['TopicName']}</p>
                    <p><strong>Text:</strong> {row['Text']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Define the Analytics page
def analytics():
    # Load and display the analytics image
    image_path = "analytics.JPG"
    image = Image.open(image_path)
    st.image(image, use_column_width=True)

    # Define custom CSS styles
    custom_css = """
        <style>
            /* Increase the font size of the info box and other text */
            .stAlert {
                font-size: 25px; /* Adjust the value as desired */
            }
            /* Increase the font size for text */
            .stText {
                font-size: 25px; /* Adjust the value as desired */
            }
            /* Increase font size */
            body {
                font-size: 22px;
            }
            /* Increase image size */
            .stImage > img {
                width: 100%;  /* Increase image width to 100% */
                height: auto; /* Adjust height to maintain aspect ratio */
            }
             div[data-testid="stMarkdownContainer"][class^="st-emotion-cache-"] p {
            font-size: 18px; /* Increase the font size as desired */
        }
        </style>
    """
    # Apply custom CSS styles using st.markdown
    st.markdown(custom_css, unsafe_allow_html=True)

    # You can add other analytics content here
    # Basic Statistics
    st.subheader("Basic Statistics")
    st.write(df.drop(columns=["CreatedTime"]).describe())  # Exclude 'CreatedTime' column

    # Calculate sentiment polarity and categorize into negative, neutral, and positive
    if "Text" in df.columns:
        # Replace missing values with empty strings
        df["Text"].fillna("", inplace=True)

        # Calculate sentiment polarity and handle None values
        sentiments = [
            TextBlob(answer).sentiment.polarity if answer else None for answer in df["Text"]
        ]
        df["Sentiment"] = sentiments

        # Categorize sentiment into negative, neutral, and positive
        df["Sentiment_Category"] = pd.cut(
            df["Sentiment"],
            bins=[-1, -0.01, 0.01, 1],
            labels=["Negative", "Neutral", "Positive"],
        )
    else:
        st.write("No 'Text' column found in the DataFrame.")

    # Line graph of Reddit Sentiment Trend by topic
    st.subheader("Sentiment Trend by Topic Over Time")
    if "SubmissionTitle" in df.columns:
        grouped_df = (
            df.groupby([df["CreatedTime"].dt.date, "Sentiment_Category"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        fig, ax = plt.subplots()
        ax.plot(
            grouped_df["CreatedTime"], grouped_df["Negative"], label="Negative", color="red"
        )
        ax.plot(
            grouped_df["CreatedTime"],
            grouped_df["Positive"],
            label="Positive",
            color="green",
        )
        plt.xlabel("Date")
        plt.ylabel("Number of Posts")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(fig)
    else:
        st.write("No 'SubmissionTitle' column found in the DataFrame.")

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


    # Group by topic name and calculate average sentiment polarity
    topic_sentiments = df.groupby("TopicName")["Sentiment"].mean().reset_index()

    # Bar graph of average sentiment by topic
    st.subheader("Average Sentiment by Topic")
    if not topic_sentiments.empty:
        fig, ax = plt.subplots()
        ax.bar(
            topic_sentiments["TopicName"],
            topic_sentiments["Sentiment"],
            color="blue",
        )
        plt.xlabel("Topic")
        plt.ylabel("Average Sentiment")
        plt.title("Average Sentiment by Topic")
        plt.xticks(rotation=45, fontsize=6)
        st.pyplot(fig)
    else:
        st.write("No data available for average sentiment by topic.")


    # Group by TopicName and Sentiment and calculate sentiment counts
grouped_sentiments = df.groupby(['TopicName', 'Sentiment']).size().unstack(fill_value=0).reset_index()

# Print statement to check if data is available
print("Grouped Sentiments DataFrame:")
print(grouped_sentiments)

# Main function to manage the Streamlit app
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation Panel")
    page = st.sidebar.radio("Select a page:", ["Dashboard", "Direct Feed", "Analytics"])
    
    # Route to the selected page
    if page == "Dashboard":
        dashboard()
    elif page == "Direct Feed":
        direct_feed()
    elif page == "Analytics":
        analytics()

# Run the app
if __name__ == "__main__":
    main()

# Close the connection to the database
engine.dispose()
