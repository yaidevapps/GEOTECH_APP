import streamlit as st
import os
import uuid
import json
from datetime import datetime
from agents import chat_agent, extraction_agent, report_agent
from models import DocumentSummary

# Load the Terra Design System CSS
with open("theme.css", "r") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class='header'>
        <h1 style='margin: 0; font-size: 24px;'>GeoSmart AI</h1>
        <p style='margin: 2px 0 0; font-size: 14px; color: white;'>Geotechnical Analysis & Reporting</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <img src='https://via.placeholder.com/50' style='border-radius: 50%; margin-bottom: 15px;' alt='AI Geotech Assistant Logo'/>
    </div>
    <h2 style='color: #FFFFFF; font-size: 20px; margin-bottom: 10px;'>AI Geotech Assistant</h2>
    <p style='color: var(--text-light); font-size: 13px; font-weight: 300; margin-bottom: 20px;'>A tool for geotechnical analysis and reporting.</p>
    <hr style='border-color: var(--neutral-gray); margin: 25px 0;'>
    <div style='background-color: var(--neutral-light); padding: 15px; border-radius: var(--border-radius-medium);'>
        <h3 style='color: var(--secondary-accent); font-size: 16px; margin-top: 0; margin-bottom: 10px;'>User Instructions</h3>
        <p style='color: var(--text-light); font-size: 13px; line-height: 1.6;'>
            - <b>Expert Chat</b>: Ask geotechnical questions (e.g., "What’s the typical bearing capacity of glacial till in Mercer Island?") to get expert advice.<br>
            - <b>Document Analysis</b>: Upload PDF or DOCX files (up to 200MB) to extract key geotechnical data like soil profiles and hazards.<br>
            - <b>Report Generator</b>: Generate detailed reports by selecting a report type and providing project details. Use analyzed documents for better accuracy.<br>
            <b>Tips</b>:<br>
            - Clear chat or documents as needed using the respective "Clear" buttons.<br>
            - Switch between tabs to analyze documents, generate reports, and chat without losing data.
        </p>
    </div>
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
    if st.button("Clear Chat", key="clear_chat"):
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
                        <div class='chat-bubble-user' role='article' aria-label='User message'>
                            <strong>User:</strong> {message['content']}<br>
                            <small style='color: var(--text-light);'>{timestamp}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class='chat-bubble-ai' role='article' aria-label='AI response'>
                            <strong>AI Geotech Assistant:</strong> {message['content']}<br>
                            <small style='color: var(--neutral-light);'>{timestamp}</small>
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

    st.markdown("<h3>Try these questions:</h3>", unsafe_allow_html=True)
    suggestions = [
        "What is the typical bearing capacity of glacial till in Mercer Island?",
        "How do I assess slope stability in a seismic zone?",
        "What foundation type is best for clay soils?",
        "Can you explain the soil profile for a site in Mercer Island?"
    ]
    for idx, suggestion in enumerate(suggestions):
        if st.button(
            suggestion,
            key=f"suggestion_{idx}",
            help=f"Click to ask: {suggestion}",
            on_click=lambda s=suggestion: st.session_state.update({"chat_input_value": s})
        ):
            st.session_state.chat_input_value = suggestion

    # Chat input using st.form
    with st.form(key=f"chat_form_{len(st.session_state.messages)}", clear_on_submit=True):
        query = st.text_input(
            "Ask a geotechnical question:",
            value=st.session_state.chat_input_value,
            key=f"chat_input_{len(st.session_state.messages)}",
            placeholder="Type your question here..."
        )
        submit_button = st.form_submit_button("Send")

    # Reset the chat input value after submission
    if submit_button and query:
        st.session_state.chat_input_value = ""

        # Add user message to history with timestamp
        timestamp = datetime.now().strftime("%Y-%m-19 22:35:%S")
        st.session_state.messages.append({"role": "user", "content": query, "timestamp": timestamp})

        # Update chat display
        update_chat()

        # Show loading spinner with progress feedback
        with st.spinner("AI is thinking..."):
            try:
                # Construct chat history as a string
                chat_history = "\n".join(
                    [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                )
                # Call the chat agent directly
                result = chat_agent.execute(query, chat_history)
                
                # Add AI response to history with timestamp
                timestamp = datetime.now().strftime("%Y-%m-19 22:35:%S")
                st.session_state.messages.append({"role": "assistant", "content": result, "timestamp": timestamp})

                # Update chat display
                update_chat()

            except Exception as e:
                st.error(f"Error: {e}")
                timestamp = datetime.now().strftime("%Y-%m-19 22:35:%S")
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

    # Add the Clear All button
    if uploaded_files:
        with st.container():
            st.markdown('<div class="clear-all-container">', unsafe_allow_html=True)
            if st.button("Clear All", key="clear_all_button"):
                st.session_state.reset_file_uploader = True
                st.session_state.summaries = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Analyzing documents..."):
            summaries = []
            for uploaded_file in uploaded_files:
                # Save the uploaded file temporarily
                temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                try:
                    with open(temp_filename, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    # Call the extraction agent directly
                    summary = extraction_agent.execute(temp_filename)
                    summaries.append(summary)
                except Exception as e:
                    st.error(f"Error analyzing {uploaded_file.name}: {e}")
                finally:
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
            if summaries:
                st.markdown("<h3>Document Summaries</h3>", unsafe_allow_html=True)
                for idx, summary in enumerate(summaries):
                    badge_color = {
                        "Geotechnical Feasibility Report": "#E7B15D",
                        "Feasibility Report": "#D96A4F",
                        "Site Investigation": "#4F5D75",
                        "Foundation Recommendation": "#2D3142"
                    }.get(summary.doc_type, "#768A9F")
                    st.markdown(
                        f"""
                        <span class='badge' style='background-color: {badge_color};'>
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
    report_type_options = ["Site Investigation", "Foundation Recommendation"]
    report_type = st.selectbox(
        "Report Type",
        report_type_options,
        index=report_type_options.index(st.session_state.report_type),
        key="report_type_selectbox"
    )
    project_info = st.text_input(
        "Project Info (e.g., location, client):",
        value=st.session_state.project_info,
        key="project_info_input",
        placeholder="Enter project details..."
    )
    parameters = st.text_area(
        "Parameters (e.g., soil type, depth):",
        value=st.session_state.parameters,
        key="parameters_input",
        placeholder="Enter geotechnical parameters..."
    )

    # Update session state when inputs change
    st.session_state.report_type = report_type
    st.session_state.project_info = project_info
    st.session_state.parameters = parameters

    if st.button("Generate Report", key="generate_report"):
        with st.spinner("Generating report..."):
            doc_summaries = [s for s in st.session_state.get("summaries", [])]
            try:
                # Call the report agent directly
                report = report_agent.execute(report_type, project_info, parameters, doc_summaries).dict()
                
                st.markdown("<h3>Generated Report</h3>", unsafe_allow_html=True)
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
                    
            except Exception as e:
                st.error(f"Error generating report: {e}")