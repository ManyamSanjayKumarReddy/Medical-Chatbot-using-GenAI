import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime, timedelta
import csv
import pandas as pd
from PIL import Image

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("dotenv module not found. Please make sure to install it using 'pip install python-dotenv'.")

# Define the path to the CSV file
csv_file_path = 'question_history.csv'

# Function to store questions in CSV file
def store_question(question):
    try:
        current_time = datetime.now()
        expiration_time = current_time + timedelta(days=7)  # Auto delete after a week

        # Format the data (question, expiration time)
        data = [question, expiration_time.strftime('%Y-%m-%d')]

        # Append the data to the CSV file
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        st.error(f"An error occurred while storing the question: {e}")


# Function to read question history from CSV file
def read_question_history():
    try:
        with open(csv_file_path, mode='r') as file:
            reader = csv.reader(file)
            history_data = list(reader)
        return history_data
    except FileNotFoundError:
        return []
    

        
# Function to configure API key
def configure_api_key():
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    except Exception as e:
        st.warning(f"An error occurred while configuring the API key: {e}")


# Function for educational chat using Google Gemini Pro API
def gemini_pro(input_text, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt, input_text])
        return response.text
    except Exception as e:
        st.error(f"An error occurred during Healthcare Application: {e}")
# Function for MultiModal chat using Google Gemini Pro Vision API
def geminiprovision(image, custom_prompt):
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([image[0], custom_prompt])
        return response.text
    except Exception as e:
        st.error(f"An error occurred during Healthcare Application: {e}")

# Function to prepare image data for Gemini Pro Vision API
def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")



# Updated and more powerful prompt
prompt = """

You are an Expert in Health Care industry & You Need to help Users for their better Health Conditions.

If the user asks to Give Image as output Please tell him to use our MultiModal Application for more Details..
"""

# Initialize Streamlit app
st.set_page_config(page_title="An Advanced AI Powered Healthcare Bot")

# Sidebar Features
st.sidebar.title("Chat Bot Features")

# Help Section
st.sidebar.subheader("Help")
st.sidebar.markdown(
    "Welcome to the Chat Bot app! You can ask questions or use MultiModal to analyze images."
)

# About Section
st.sidebar.subheader("About")
st.sidebar.markdown(
    "- This app uses Google's Generative AI models to provide responses to your queries. "
    "\n- It combines MultiModal capabilities for image analysis and Multi-Domain expertise for answering questions. "
    "\n- Feel free to explore and interact with the chat bot."
)

# Project Details Section
st.sidebar.subheader("Project Details")
st.sidebar.markdown(
    "- This project integrates natural language processing and computer vision using Google's Generative AI models."
    "\n- The MultiModal Chat Bot analyzes images, extracting information based on user-provided details."
    "\n- The Multi-Domain Chat Bot answers questions across various sectors with a tailored prompt."
    "\n- Explore the power of AI in this interactive chat bot application."
)

# Option to choose between MultiModal and Multi-Domain Chat Bot
use_multimodal = st.checkbox("Use MultiModal (For Images)")

# Display MultiModal functionality if checkbox is selected
if use_multimodal:
    st.header("MultiModal Healthcare Bot")

    # Instructions for MultiModal
    st.markdown(
        "### Instructions for MultiModal Healthcare Bot\n"
        "1. Upload an image using the 'Choose an image...' button.\n"
        "2. Optionally, enter details about the image in the text area.\n"
        "3. Click the 'Get Information' button to analyze the image and receive a response."
    )

    # File uploader for image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Process the image and get user input for custom prompt
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

        custom_prompt = st.text_area("Enter details you want to know about the image (optional):")

        if not custom_prompt:
           # Updated default custom prompt for image analysis
            custom_prompt = """
                    Analyze the uploaded image and provide detailed information, including objects present, contextual details, and any notable aspects.
                    See actually you are an expert in Healthcare Domain so please results based on that.

                    Also give the Complete Details about the Image & also specify if that images has any history.
            """


        submit = st.button("Get Information")

        if submit:
            configure_api_key()  # Configure API key
            image_data = input_image_setup(uploaded_file)
            response = geminiprovision(image_data, custom_prompt)
            st.subheader("The Response is")
            st.write(response)

# Display Multi-Domain Chat Bot functionality if checkbox is not selected
else:
    st.header("Healthcare Application using AI")

    # Instructions for Multi-Domain
    st.markdown(
        "### Instructions for Healthcare Application using AI\n"
        "1. Enter a question or topic in the 'Input' text box.\n"
        "2. Click the 'Send Message' button to receive a response."
    )

    # Set a default value for the text input
    input_text_value = "Ask a question or provide a topic"
    input_text = st.text_input("Input:", placeholder=input_text_value, key="text_input")

    # Check if the "Send Message" button is clicked
    if st.button("Send Message"):
        if not input_text:
            st.warning("Please enter a question or topic.")
        else:
            configure_api_key()  # Configure API key
            # Store question in CSV file
            store_question(input_text)

            # Generate response
            response = gemini_pro(input_text, prompt)

            # Display response
            st.subheader("Answer:")
            st.write(response)

    # Display last 5 rows of question history with column names
    history_data = read_question_history()
    if history_data:
        st.subheader("Recent Search History")

        # Convert the list of lists to a DataFrame
        df = pd.DataFrame(history_data, columns=["Question", "Expire On"])

        # Display the last 5 rows in reverse order
        st.write(df.tail(50).iloc[::-1])
    else:
        st.info("No question history available.")

