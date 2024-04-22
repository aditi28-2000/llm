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
        </style>
    """
    # Apply custom CSS styles using st.markdown
    st.markdown(custom_css, unsafe_allow_html=True)
    
    def calculate_metrics(df):
        total_posts = len(df)
        positive_posts = len(df[df['Sentiment'] == 'POSITIVE'])
        negative_posts = len(df[df['Sentiment'] == 'NEGATIVE'])
        neutral_posts = len(df[df['Sentiment'] == 'NEUTRAL'])
        return total_posts,positive_posts, negative_posts, neutral_posts

    
    # Calculate metrics
    total_posts, positive_posts, negative_posts, neutral_posts = calculate_metrics(df)
    
    st.info('Total Posts in the Database')
    st.write(f'Total Posts: {total_posts}') 

    st.title("Sentiment Distribution")
    
    # Create a pie chart for sentiment distribution
    labels = ['Negative Sentiment', 'Positive Sentiment', 'Neutral Sentiment']
    values = [negative_posts, positive_posts, neutral_posts]
    
    # Define the color scheme for the pie chart
    colors = ['grey', 'red', 'skyblue'] 

    # Create the pie chart using Plotly Express
    fig_pie = px.pie(values=values, names=labels, hole=0.5, color_discrete_sequence=colors)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    # fig_pie.update_layout(title='Sentiment Distribution')
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig_pie, width=800, height=600)

# Define the Direct Feed page
def direct_feed():
    st.title("Direct Feed")

    # Create filters for TopicName and Sentiment
    topic_options = df['TopicName'].unique()
    selected_topic = st.selectbox("Select Topic Name:", topic_options)
    
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
    
    # Display the filtered posts in rectangular boxes
    for index, row in recent_posts.iterrows():
        # Define a custom style for the rectangular box
        custom_style = """
            <style>
                .rectangular-box {
                    border: 1px solid #ccc;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                }
                .rectangular-box p {
                    margin: 0;
                }
            </style>
        """
        # Apply the custom style using st.markdown
        st.markdown(custom_style, unsafe_allow_html=True)
        
        # Display the rectangular box
        st.markdown(
            f"""
            <div class="rectangular-box">
                <p><strong>Created Time:</strong> {row['CreatedTime']}</p>
                <p><strong>Submission Title:</strong> {row['SubmissionTitle']}</p>
                <p><strong>Text:</strong> {row['Text'][:200]}{'...' if len(row['Text']) > 200 else ''}</p>
                <p><strong>Sentiment:</strong> {row['Sentiment']}</p>
                <p><strong>Topic Name:</strong> {row['TopicName']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    


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
