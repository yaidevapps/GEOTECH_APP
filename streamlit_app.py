import streamlit as st
import requests
from models import DocumentSummary
from datetime import datetime
import json
import os
import uuid

# Custom CSS for modern styling
st.markdown("""
    <style>
    /* General app styling */
    .stApp {
        background-color: #f5f6fa;
    }
    .stTabs {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
    }
    .stTabs button:hover {
        background-color: #ecf0f1;
        transition: background-color 0.3s;
    }
    body {
        font-family: 'Inter', sans-serif;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50, #34495e);
    }
    /* Report Generator styling */
    .st-expander[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    .st-expander summary {
        font-weight: bold;
        color: #2c3e50;
        background-color: #ecf0f1;
        padding: 10px;
        border-radius: 8px 8px 0 0;
    }
    .st-expander p {
        color: #34495e;
        line-height: 1.6;
        margin: 5px 0;
    }
    h3 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }
    /* Document Analysis styling */
    .st-expander[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: #ffffff;
    }
    /* Chat styling */
    .stChat {
        background-color: #f5f6fa;
        padding: 20px;
        border-radius: 10px;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }
    div[style*="background-color: #d1e7dd"] {
        background-color: #d1e7dd !important;
        border: 1px solid #b7d8c9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        max-width: 70%;
        align-self: flex-start;
        margin: 10px 0;
        padding: 15px;
        border-radius: 15px;
    }
    div[style*="background-color: #e0f7fa"] {
        background-color: #e0f7fa !important;
        border: 1px solid #b3e5fc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        max-width: 70%;
        align-self: flex-end;
        margin: 10px 0;
        padding: 15px;
        border-radius: 15px;
    }
    .stChatInput {
        margin-top: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 25px;
        padding: 5px;
    }
    /* Inputs styling */
    .stTextInput > div > input, .stTextArea > div > textarea {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        background-color: #ffffff;
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    /* Chat suggestion buttons */
    .suggestion-button {
        background: linear-gradient(90deg, #95a5a6, #7f8c8d);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 5px 10px;
        font-size: 12px;
        margin: 5px;
    }
    .suggestion-button:hover {
        background: linear-gradient(90deg, #7f8c8d, #95a5a6);
    }
    </style>
""", unsafe_allow_html=True)

# Header bar
st.markdown("""
    <div style='background-color: #2c3e50; padding: 15px; border-radius: 8px 8px 0 0; color: white;'>
        <h1 style='margin: 0; font-size: 24px;'>AI-Assisted Geotechnical Engineering</h1>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
    <div style='text-align: center;'>
        <img src='https://via.placeholder.com/50' style='border-radius: 50%; margin-bottom: 10px;'/>
    </div>
    <h2 style='color: white; font-size: 20px;'>AI Geotech Assistant</h2>
    <p style='color: #bdc3c7;'>A tool for geotechnical analysis and reporting.</p>
    <h3 style='color: white; font-size: 16px; margin-top: 20px;'>User Instructions</h3>
    <p style='color: #bdc3c7; line-height: 1.5;'>
        - <b>Expert Chat</b>: Ask geotechnical questions (e.g., "What’s the typical bearing capacity of glacial till in Mercer Island?") to get expert advice.<br>
        - <b>Document Analysis</b>: Upload PDF or DOCX files (up to 200MB) to extract key geotechnical data like soil profiles and hazards.<br>
        - <b>Report Generator</b>: Generate detailed reports by selecting a report type and providing project details. Use analyzed documents for better accuracy.<br>
        <b>Tips</b>:<br>
        - Clear chat or documents as needed using the respective "Clear" buttons.<br>
        - Switch between tabs to analyze documents, generate reports, and chat without losing data.
    </p>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Expert Chat", "Document Analysis", "Report Generator"])

# Expert Chat
with tab1:
    # Load chat history from file if it exists
    chat_file = "chat_history.json"
    if os.path.exists(chat_file):
        with open(chat_file, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

    # Add a clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        with open(chat_file, "w") as f:
            json.dump(st.session_state.messages, f)

    # Create a placeholder for the chat messages
    chat_placeholder = st.empty()

    # Function to update chat display
    def update_chat():
        with chat_placeholder.container():
            for message in st.session_state.messages:
                timestamp = message.get("timestamp", "Unknown time")
                if message["role"] == "user":
                    st.markdown(
                        f"""
                        <div style='background-color: #d1e7dd; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>User:</strong> {message['content']}<br>
                            <small style='color: #7f8c8d;'>{timestamp}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style='background-color: #e0f7fa; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>AI:</strong> {message['content']}<br>
                            <small style='color: #7f8c8d;'>{timestamp}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # Initial chat display
    update_chat()

    # Auto-scroll to the bottom
    st.markdown(
        """
        <script>
        const chatContainer = window.parent.document.querySelector('.stChat');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # Chat suggestions
    if "chat_input_value" not in st.session_state:
        st.session_state.chat_input_value = ""

    st.markdown("**Try these questions:**")
    cols = st.columns(4)
    suggestions = [
        "What is the typical bearing capacity of glacial till in Mercer Island?",
        "How do I assess slope stability in a seismic zone?",
        "What foundation type is best for clay soils?",
        "Can you explain the soil profile for a site in Mercer Island?"
    ]
    for idx, suggestion in enumerate(suggestions):
        with cols[idx]:
            if st.button(suggestion, key=f"suggestion_{idx}", help="Click to use this question", on_click=lambda s=suggestion: st.session_state.update({"chat_input_value": s})):
                st.session_state.chat_input_value = suggestion

    # Chat input using st.form
    with st.form(key=f"chat_form_{len(st.session_state.messages)}", clear_on_submit=True):
        query = st.text_input(
            "Ask a geotechnical question:",
            value=st.session_state.chat_input_value,
            key=f"chat_input_{len(st.session_state.messages)}"
        )
        submit_button = st.form_submit_button("Send")

    # Reset the chat input value after submission
    if submit_button and query:
        st.session_state.chat_input_value = ""

        # Add user message to history with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": query, "timestamp": timestamp})

        # Update chat display
        update_chat()

        # Show loading spinner
        with st.spinner("AI is thinking..."):
            try:
                # Construct chat history as a string
                chat_history = "\n".join(
                    [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                )
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"query": query, "chat_history": chat_history}
                )
                response.raise_for_status()
                result = response.json().get("response", "Error: No response from backend.")
                
                # Add AI response to history with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "assistant", "content": result, "timestamp": timestamp})

                # Update chat display
                update_chat()

            except requests.exceptions.RequestException as e:
                st.error(f"Error: Could not connect to the backend. Please ensure the FastAPI server is running at http://localhost:8000. You can start it by running 'uvicorn fastapi_app:app --port 8000' in your terminal.")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: Could not connect to the backend. Please try again later.", "timestamp": timestamp})
                update_chat()
            except (KeyError, ValueError) as e:
                st.error(f"Unexpected response from backend: {e}. Please check the FastAPI server logs for more details.")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}", "timestamp": timestamp})
                update_chat()

        # Save chat history to file
        with open(chat_file, "w") as f:
            json.dump(st.session_state.messages, f)

# Document Analysis
with tab2:
    # Use a session state variable to control reset
    if "reset_file_uploader" not in st.session_state:
        st.session_state.reset_file_uploader = False

    # Conditionally render the file uploader based on the reset state
    if st.session_state.reset_file_uploader:
        # Reset the flag and rerun to clear the file uploader
        st.session_state.reset_file_uploader = False
        uploaded_files = st.file_uploader(
            "Upload Geotechnical Documents",
            accept_multiple_files=True,
            type=["pdf", "docx"],
            key=f"file_uploader_{uuid.uuid4()}"
        )
    else:
        uploaded_files = st.file_uploader(
            "Upload Geotechnical Documents",
            accept_multiple_files=True,
            type=["pdf", "docx"],
            key="file_uploader"
        )

    # Add the Clear All button directly below the file uploader with custom styling
    if uploaded_files:
        # Add a container for the button to control its alignment and spacing
        st.markdown(
            """
            <style>
            .clear-all-container {
                display: flex;
                justify-content: flex-end;
                margin-top: 10px;
                margin-bottom: 20px;
            }
            .clear-all-button {
                background: linear-gradient(90deg, #e74c3c, #c0392b);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            .clear-all-button:hover {
                background: linear-gradient(90deg, #c0392b, #e74c3c);
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Place the button in a container for alignment
        with st.container():
            st.markdown('<div class="clear-all-container">', unsafe_allow_html=True)
            if st.button("Clear All", key="clear_all_button"):
                # Set the reset flag and clear summaries
                st.session_state.reset_file_uploader = True
                st.session_state.summaries = []  # Clear summaries
                st.rerun()  # Rerun the app to reset the file uploader
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Analyzing documents..."):
            summaries = []
            for uploaded_file in uploaded_files:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post("http://localhost:8000/analyze_document", files=files)
                    response.raise_for_status()
                    summary_data = response.json()
                    summaries.append(DocumentSummary(**summary_data))
                except requests.exceptions.RequestException as e:
                    st.error(f"Error analyzing {uploaded_file.name}: {e}. Please ensure the FastAPI server is running at http://localhost:8000.")
                except ValueError as e:
                    st.error(f"Invalid summary format for {uploaded_file.name}: {e}")
            if summaries:
                st.markdown("### Document Summaries")
                for idx, summary in enumerate(summaries):
                    badge_color = {
                        "Geotechnical Feasibility Report": "#3498db",
                        "Feasibility Report": "#f1c40f",
                        "Site Investigation": "#2ecc71",
                        "Foundation Recommendation": "#e74c3c"
                    }.get(summary.doc_type, "#95a5a6")
                    st.markdown(
                        f"""
                        <span style='background-color: {badge_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; margin-right: 10px;'>
                            {summary.doc_type}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )
                    with st.expander(f"Summary for {uploaded_files[idx].name}", expanded=True):
                        st.markdown(f"**Document Type:** {summary.doc_type}")
                        st.markdown(f"**Project Info:** Location: {summary.project_info.location}, Client: {summary.project_info.client or 'Unknown'}, Date: {summary.project_info.date or 'Unknown'}")
                        st.markdown("**Soil Profile:**")
                        if summary.soil_profile:
                            for layer in summary.soil_profile:
                                st.markdown(f"- Depth {layer.depth_start}-{layer.depth_end}m: {layer.soil_type}, Strength: {layer.strength if layer.strength is not None else 'Not Provided'} kPa")
                        else:
                            st.markdown("(No data available)")
                        st.markdown(f"**Groundwater Depth:** {summary.groundwater_depth if summary.groundwater_depth is not None else 'Not Provided'} m")
                        st.markdown("**Test Results:**")
                        if summary.test_results:
                            for key, value in summary.test_results.items():
                                st.markdown(f"- {key}: {value}")
                        else:
                            st.markdown("(No data available)")
                        if summary.hazards:
                            st.markdown("**Hazards:**")
                            st.markdown(f"- Erosion: {summary.hazards.erosion or 'Not Provided'}")
                            st.markdown(f"- Slide: {summary.hazards.slide or 'Not Provided'}")
                            st.markdown(f"- Seismic: {summary.hazards.seismic or 'Not Provided'}")
                            st.markdown(f"- Steep Slope: {summary.hazards.steep_slope or 'Not Provided'}")
                            st.markdown(f"- Watercourse Buffer: {summary.hazards.watercourse_buffer or 'Not Provided'}")
                        st.markdown(f"**Slope Angle:** {summary.slope_angle if summary.slope_angle is not None else 'Not Provided'}°")
                        st.markdown(f"**Lake Proximity:** {summary.lake_proximity if summary.lake_proximity is not None else 'Not Provided'} m")
                        st.markdown(f"**Confidence:** {summary.confidence}")
                        if summary.recommendations:
                            st.markdown("**Recommendations:**")
                            for rec in summary.recommendations:
                                st.markdown(f"- {rec}")
                st.session_state.summaries = summaries

# Report Generator
with tab3:
    # Initialize session state for inputs if not already set
    if "report_type" not in st.session_state:
        st.session_state.report_type = "Site Investigation"
    if "project_info" not in st.session_state:
        st.session_state.project_info = ""
    if "parameters" not in st.session_state:
        st.session_state.parameters = ""

    # Use session state to persist input values
    report_type = st.selectbox(
        "Report Type",
        ["Site Investigation", "Foundation Recommendation"],
        index=["Site Investigation", "Foundation Recommendation"].index(st.session_state.report_type),
        key="report_type_selectbox"
    )
    project_info = st.text_input(
        "Project Info (e.g., location, client):",
        value=st.session_state.project_info,
        key="project_info_input"
    )
    parameters = st.text_area(
        "Parameters (e.g., soil type, depth):",
        value=st.session_state.parameters,
        key="parameters_input"
    )

    # Update session state when inputs change
    st.session_state.report_type = report_type
    st.session_state.project_info = project_info
    st.session_state.parameters = parameters

    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            doc_summaries = [s.model_dump() for s in st.session_state.get("summaries", [])]
            try:
                response = requests.post(
                    "http://localhost:8000/generate_report",
                    json={
                        "report_type": report_type,
                        "project_info": project_info,
                        "parameters": parameters,
                        "doc_summaries": doc_summaries
                    }
                )
                response.raise_for_status()
                report = response.json()
                
                st.markdown("### Generated Report")
                with st.expander("Executive Summary", expanded=True):
                    st.markdown(f"**{report['executive_summary']}**")
                with st.expander("Site Description"):
                    st.markdown(report['site_description'])
                with st.expander("Methodology"):
                    st.markdown(report['methodology'])
                with st.expander("Findings"):
                    st.markdown(report['findings'])
                with st.expander("Recommendations"):
                    st.markdown(report['recommendations'])
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Error generating report: {e}. Please ensure the FastAPI server is running at http://localhost:8000.")
            except ValueError as e:
                st.error(f"Invalid report format: {e}")