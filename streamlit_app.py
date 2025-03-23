import streamlit as st
import os
import uuid
import json
from datetime import datetime
from agents import chat_agent, extraction_agent, report_agent
from models import DocumentSummary

# Load the Next Edit Design System CSS
with open("theme.css", "r") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("GeoSmart AI")

MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB

# Initialize session state at the top level
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Load chat history from file if it exists
    chat_file = "chat_history.json"
    if os.path.exists(chat_file):
        with open(chat_file, "r") as f:
            st.session_state.messages = json.load(f)
if "reset_file_uploader" not in st.session_state:
    st.session_state.reset_file_uploader = False
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "report_type" not in st.session_state:
    st.session_state.report_type = "Site Investigation"
if "project_info" not in st.session_state:
    st.session_state.project_info = ""
if "parameters" not in st.session_state:
    st.session_state.parameters = ""
if "chat_input_value" not in st.session_state:
    st.session_state.chat_input_value = ""

# Header
st.markdown("""
    <div class='report-header'>
        <h1 style='margin: 0; font-size: var(--font-size-heading3);'>GeoSmart AI</h1>
        <p style='margin: var(--spacing-1) 0 0; font-size: var(--font-size-small);'>Geotechnical Analysis & Reporting</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("AI Geotech Assistant")
    st.markdown("""
        <p style='font-size: var(--font-size-body); line-height: 1.5;'>
            A tool for geotechnical analysis and reporting. Use the tabs to:
            <ul>
                <li><b>Expert Chat</b>: Ask geotechnical questions (e.g., "What’s the typical bearing capacity of glacial till in Mercer Island?").</li>
                <li><b>Document Analysis</b>: Upload PDF or DOCX files (up to 200MB) to extract key data like soil profiles and hazards.</li>
                <li><b>Report Generator</b>: Generate detailed reports by selecting a type and providing project details.</li>
            </ul>
            <b>Tips</b>: Clear chat or documents using the "Clear" buttons. Switch tabs without losing data.
        </p>
    """, unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Expert Chat", "Document Analysis", "Report Generator"])

# Expert Chat
with tab1:
    st.header("Expert Chat")
    if st.button("Clear Chat", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        with open("chat_history.json", "w") as f:
            json.dump(st.session_state.messages, f)

    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            cls = "chat-bubble-user" if message["role"] == "user" else "chat-bubble-ai"
            st.markdown(
                f'<div class="{cls}"><strong>{message["role"].capitalize()}:</strong> {message["content"]}<br><small>{message["timestamp"]}</small></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

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
            on_click=lambda s=suggestion: st.session_state.update({"chat_input_value": s}),
            use_container_width=True
        ):
            st.session_state.chat_input_value = suggestion

    with st.form(key="chat_form", clear_on_submit=True):
        query = st.text_input(
            "Ask a geotechnical question:",
            value=st.session_state.chat_input_value,
            key="chat_input",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button("Send", use_container_width=True)

    if submit_button and query:
        st.session_state.chat_input_value = ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": query, "timestamp": timestamp})
        with st.spinner("AI is thinking..."):
            try:
                chat_history = "\n".join(
                    [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages[:-1]]
                )
                result = chat_agent.execute(query, chat_history)
                st.session_state.messages.append({"role": "assistant", "content": result, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                with open("chat_history.json", "w") as f:
                    json.dump(st.session_state.messages, f)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

# Document Analysis
with tab2:
    st.header("Document Analysis")
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

    if uploaded_files:
        st.markdown('<div class="clear-all-container">', unsafe_allow_html=True)
        if st.button("Clear All", key="clear_all_button", use_container_width=True):
            st.session_state.reset_file_uploader = True
            st.session_state.summaries = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Analyzing documents..."):
            summaries = []
            for uploaded_file in uploaded_files:
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.error(f"File {uploaded_file.name} exceeds 200MB limit.")
                    continue
                temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
                try:
                    with open(temp_filename, "wb") as f:
                        f.write(uploaded_file.getvalue())
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
                        "Geotechnical Feasibility Report": "#4a6b8a",  # Primary Blue
                        "Feasibility Report": "#4a6b8a",
                        "Site Investigation": "#4a6b8a",
                        "Foundation Recommendation": "#4a6b8a"
                    }.get(summary.doc_type, "#4a6b8a")
                    st.markdown(
                        f'<span class="badge" style="background-color: {badge_color};">{summary.doc_type}</span>',
                        unsafe_allow_html=True
                    )
                    with st.expander(f"Summary for {uploaded_files[idx].name}", expanded=True):
                        content_lines = [
                            f"- **Document Type:** {summary.doc_type}",
                            f"- **Project Info:** Location: {summary.project_info.location}, Client: {summary.project_info.client or 'Unknown'}, Date: {summary.project_info.date or 'Unknown'}",
                            "- **Soil Profile:**"
                        ]
                        if summary.soil_profile:
                            for layer in summary.soil_profile:
                                content_lines.append(f"  - Depth {layer.depth_start}-{layer.depth_end}m: {layer.soil_type}, Strength: {layer.strength if layer.strength is not None else 'Not Provided'} kPa")
                        else:
                            content_lines.append("  - (No data available)")
                        content_lines.extend([
                            f"- **Groundwater Depth:** {summary.groundwater_depth if summary.groundwater_depth is not None else 'Not Provided'} m",
                            "- **Test Results:**"
                        ])
                        if summary.test_results:
                            for key, value in summary.test_results.items():
                                content_lines.append(f"  - {key}: {value}")
                        else:
                            content_lines.append("  - (No data available)")
                        if summary.hazards:
                            content_lines.extend([
                                "- **Hazards:**",
                                f"  - Erosion: {summary.hazards.erosion or 'Not Provided'}",
                                f"  - Slide: {summary.hazards.slide or 'Not Provided'}",
                                f"  - Seismic: {summary.hazards.seismic or 'Not Provided'}",
                                f"  - Steep Slope: {summary.hazards.steep_slope or 'Not Provided'}",
                                f"  - Watercourse Buffer: {summary.hazards.watercourse_buffer or 'Not Provided'}"
                            ])
                        content_lines.extend([
                            f"- **Slope Angle:** {summary.slope_angle if summary.slope_angle is not None else 'Not Provided'}°",
                            f"- **Lake Proximity:** {summary.lake_proximity if summary.lake_proximity is not None else 'Not Provided'} m",
                            f"- **Confidence:** {summary.confidence}"
                        ])
                        if summary.recommendations:
                            content_lines.append("- **Recommendations:**")
                            for rec in summary.recommendations:
                                content_lines.append(f"  - {rec}")
                        st.markdown(
                            f'<div class="expander-content">{"<br>".join(content_lines)}</div>',
                            unsafe_allow_html=True
                        )
                st.session_state.summaries = summaries

# Report Generator
with tab3:
    st.header("Report Generator")
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

    st.session_state.report_type = report_type
    st.session_state.project_info = project_info
    st.session_state.parameters = parameters

    if st.button("Generate Report", key="generate_report", use_container_width=True):
        with st.spinner("Generating report..."):
            doc_summaries = [s for s in st.session_state.get("summaries", [])]
            try:
                report = report_agent.execute(report_type, project_info, parameters, doc_summaries).dict()
                st.markdown("<h3>Generated Report</h3>", unsafe_allow_html=True)
                for section, content in report.items():
                    if section != "report_type":
                        with st.expander(section.replace("_", " ").title(), expanded=True):
                            content_lines = content.split(". ")
                            content_html = "<br>".join([f"- {line.strip()}" if not line.startswith("-") else line.strip() for line in content_lines if line.strip()])
                            st.markdown(
                                f'<div class="expander-content">{content_html}</div>',
                                unsafe_allow_html=True
                            )
            except Exception as e:
                st.error(f"Error generating report: {e}")