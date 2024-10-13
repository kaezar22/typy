import streamlit as st
import time
import pandas as pd
from io import StringIO
import docx
from streamlit.components.v1 import html

# Initialize session state for WPM history
if "wpm_history" not in st.session_state:
    st.session_state["wpm_history"] = pd.DataFrame(columns=["Words Typed", "Total Time (s)", "WPM"])

# Set wide page layout
st.set_page_config(layout="wide")

# Function to compare two texts word by word and list mistakes
def compare_texts(uploaded_text, typed_text):
    uploaded_words = uploaded_text.split()
    typed_words = typed_text.split()
    
    # Find the length of the shorter text
    min_len = min(len(uploaded_words), len(typed_words))
    
    mistakes = []
    for i in range(min_len):
        if uploaded_words[i] != typed_words[i]:
            mistakes.append({"Your Word": typed_words[i], "Correct Word": uploaded_words[i]})
    
    # If there are extra words in either text, they are considered mistakes
    if len(uploaded_words) > min_len:
        for word in uploaded_words[min_len:]:
            mistakes.append({"Your Word": "", "Correct Word": word})
    elif len(typed_words) > min_len:
        for word in typed_words[min_len:]:
            mistakes.append({"Your Word": word, "Correct Word": ""})

    # Return the number of mistakes and the mistake details
    return len(mistakes), pd.DataFrame(mistakes)

# Custom CSS to adjust width
st.markdown("""
    <style>
    .stTextArea {
        width: 100% !important;
    }
    .scrollable-textbox {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Page Navigation
page = st.sidebar.radio("Select Page", ["Typing Practice", "WPM History"])
st.sidebar.markdown("""
### Instructions:
1. Load a `.txt` or `.docx` document.
2. Click on "Start Typing".
3. Type the text as shown.
4. Click on "Finish Typing".

### On the "WPM History"
Check your improvements!

Copy the WPM per minute column and keep track in an Excel file.
""")

# Page 1: Typing Practice
if page == "Typing Practice":
    st.markdown("<h1 style='text-align: center;'>TYPY</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])  # Increase ratio to make col1 wider

    uploaded_text = ""
    with col1:
        uploaded_file = st.file_uploader("Upload Text (.docx or .txt)", type=["docx", "txt"])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                uploaded_text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            else:
                doc = docx.Document(uploaded_file)
                uploaded_text = "\n".join([para.text for para in doc.paragraphs])
            # Display the uploaded text in a scrollable HTML component
            html(f"<div style='height: 400px; overflow-y: scroll;'>{uploaded_text}</div>", height=400, scrolling=True)

    with col2:
        if "start_time" not in st.session_state:
            st.session_state["start_time"] = 0

        if st.button("Start Typing"):
            st.session_state["start_time"] = time.time()

        typed_text = st.text_area("Type here:", height=300)  # Adjust height, width is handled by CSS

        if st.button("Finish Typing"):
            end_time = time.time()
            total_time = end_time - st.session_state["start_time"]
            words_typed = len(typed_text.split())
            wpm = words_typed / (total_time / 60)
            
            # Compare uploaded text and typed text for mistakes
            mistakes_count, mistakes_df = compare_texts(uploaded_text, typed_text)

            st.write(f"Total Words: {words_typed}")
            st.write(f"Total Time: {total_time:.2f} seconds")
            st.write(f"Words Per Minute (WPM): {wpm:.2f}")
            st.write(f"Mistakes: {mistakes_count}")

            if mistakes_count > 0:
                st.write("Here are your mistakes:")
                st.dataframe(mistakes_df)

            # Save WPM data in session state dataframe using pd.concat
            new_data = pd.DataFrame({"Words Typed": [words_typed], "Total Time (s)": [total_time], "WPM": [wpm]})
            st.session_state["wpm_history"] = pd.concat([st.session_state["wpm_history"], new_data], ignore_index=True)

# Page 2: WPM History
elif page == "WPM History":
    st.markdown("<h1 style='text-align: center;'>WPM History</h1>", unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([1, 1])  # You can adjust the proportions if needed

    # Column 1: DataFrame
    with col1:
        st.write("WPM History Data:")
        st.dataframe(st.session_state["wpm_history"])

        # Extract the "WPM" column
        wpm_column = st.session_state["wpm_history"]["WPM"].round(2)
        
        # Convert to string format
        wpm_column_string = wpm_column.to_csv(index=False, header=False)

        # Button to copy WPM column to clipboard
        if st.button("Copy WPM Column"):
            # Create a simple HTML and JavaScript snippet
            js_code = f"""
            <script>
            navigator.clipboard.writeText(`{wpm_column_string}`);
            alert('WPM Column copied to clipboard!');
            </script>
            """
            # Use Streamlit's HTML component to execute the JS
            html(js_code)

    # Column 2: Line Chart
    with col2:
        st.write("Words Per Minute Over Time:")
        if not st.session_state["wpm_history"].empty:
            st.line_chart(st.session_state["wpm_history"]["WPM"])
        else:
            st.write("No data available to display.")
