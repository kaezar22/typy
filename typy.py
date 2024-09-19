import streamlit as st
import time
import pandas as pd


# Function to calculate words per minute




def calculate_wpm(text, elapsed_time):
    words = len(text.split())
    wpm = (words / elapsed_time) * 60  # Words per minute
    return words, wpm


# Function to count mistakes by directly comparing word by word




def count_mistakes(original_text, typed_text):
    original_words = original_text.split()  # Split original text into words
    typed_words = typed_text.split()        # Split typed text into words


    # Initialize mistake counter
    mistakes = 0


    # Compare each word directly
    for i, word in enumerate(typed_words):
        if i >= len(original_words) or word != original_words[i]:
            mistakes += 1


    # If there are missing words in the typed text, count them as mistakes
    missing_words = len(original_words) - len(typed_words)
    if missing_words > 0:
        mistakes += missing_words


    return mistakes




# Initialize session state for start_time and history
if "start_time" not in st.session_state:
    st.session_state.start_time = None


if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["Timestamp", "Words per Minute"])


# App layout
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page", ["Typing Practice", "Typing History"])


if page == "Typing Practice":
    st.title("Typing Practice App")


    # Sidebar for uploading text
    uploaded_file = st.sidebar.file_uploader(
        "Upload a text file for typing practice", type=['txt'])


    if uploaded_file:
        original_text = uploaded_file.read().decode("utf-8")


        # Sidebar for selecting chunk size
        chunk_size = st.sidebar.slider(
            "Select text chunk size (words)", 10, 50, 20)


        # Form to display and write text
        with st.form(key="typing_form"):
            st.write("Read the following text and type it below:")


            # Split the text into chunks of words based on chunk size
            words = original_text.split()
            num_words = len(words)


            # Select the chunk of text to display
            displayed_chunk = " ".join(words[:chunk_size])


            # Show the chunk of text
            st.write(displayed_chunk)


            # Input field for typing the text
            typed_text = st.text_area("Type the text here:", height=200)


            # Start button (starts timer when clicked)
            start_button = st.form_submit_button(label="Start Typing")


            if start_button:
                st.session_state.start_time = time.time()  # Store start time in session state


            # Finish button to submit typing and show results
            finish_button = st.form_submit_button(label="Finish Typing")
            if finish_button:
                if st.session_state.start_time is not None:
                    end_time = time.time()  # End time when the user finishes typing
                    elapsed_time = end_time - st.session_state.start_time  # Total time spent


                    # Convert elapsed time to minutes and seconds
                    minutes = int(elapsed_time // 60)
                    seconds = int(elapsed_time % 60)


                    # Calculate WPM and mistakes
                    num_words_typed, wpm = calculate_wpm(
                        typed_text, elapsed_time)
                    mistakes = count_mistakes(
                        " ".join(words[:chunk_size]), typed_text)


                    # Update history DataFrame
                    new_entry = pd.DataFrame(
                        {"Timestamp": [pd.Timestamp.now()], "Words per Minute": [wpm]})
                    st.session_state.history = pd.concat(
                        [st.session_state.history, new_entry], ignore_index=True)


                    # Show results
                    st.write(f"Words typed: {num_words_typed}")
                    st.write(
                        f"Time spent: {minutes} minutes and {seconds} seconds")
                    st.write(f"Words per minute (WPM): {wpm:.2f}")
                    st.write(f"Number of mistakes: {mistakes}")
                else:
                    st.warning(
                        "Please start typing first by clicking the 'Start Typing' button.")


elif page == "Typing History":
    st.title("Typing History")


    # Display the DataFrame
    if not st.session_state.history.empty:
        st.write(st.session_state.history)
    else:
        st.write("No typing history available.")
