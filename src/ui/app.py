"""Streamlit web UI for the RAG system."""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.pipeline import MultimodalRAGPipeline

load_dotenv()


@st.cache_resource
def get_pipeline():
    """Initialize and cache pipeline."""
    pipeline = MultimodalRAGPipeline(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
        qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
        qdrant_port=int(os.getenv("QDRANT_PORT", "6333")),
        llm_provider="openai",
        llm_model=os.getenv("LLM_MODEL", "gpt-4"),
        llm_api_key=os.getenv("OPENAI_API_KEY"),
    )
    pipeline.initialize()
    return pipeline


def main():
    st.set_page_config(
        page_title="Multimodal RAG System",
        page_icon="📚",
        layout="wide",
    )

    st.title("📚 Multimodal Enterprise RAG System")
    st.markdown("Upload documents and query your knowledge base")

    pipeline = get_pipeline()

    tabs = st.tabs(["💬 Query", "📤 Upload", "📊 Statistics"])

    with tabs[0]:
        st.header("Ask Questions")

        query = st.text_input(
            "Enter your question:",
            placeholder="What is mentioned in the documents about...",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            search_button = st.button("Search", type="primary")

        if search_button and query:
            with st.spinner("Searching..."):
                response = pipeline.query(query)

            st.subheader("Answer")
            st.write(response.answer)

            st.subheader("Metrics")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Confidence", f"{response.confidence:.2%}")
            with cols[1]:
                st.metric(
                    "Response Time",
                    f"{response.metrics.get('total_time_ms', 0):.0f}ms"
                )
            with cols[2]:
                st.metric("Sources", len(response.contexts))

            if response.contexts:
                with st.expander("View Retrieved Context"):
                    for i, context in enumerate(response.contexts, 1):
                        st.markdown(f"**Context {i}:**")
                        st.text(context[:500] + "..." if len(context) > 500 else context)
                        st.divider()

    with tabs[1]:
        st.header("Upload Documents")

        upload_type = st.radio(
            "Upload type:",
            ["Single File", "Multiple Files"],
            horizontal=True,
        )

        if upload_type == "Single File":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "txt", "jpg", "jpeg", "png", "mp3", "wav"],
            )

            if uploaded_file and st.button("Process File"):
                temp_path = Path(f"./temp_{uploaded_file.name}")

                try:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    with st.spinner("Processing..."):
                        success = pipeline.ingest_file(temp_path)

                    if success:
                        st.success(f"Successfully processed {uploaded_file.name}")
                    else:
                        st.error(f"Failed to process {uploaded_file.name}")

                finally:
                    if temp_path.exists():
                        temp_path.unlink()

        else:
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["pdf", "txt", "jpg", "jpeg", "png", "mp3", "wav"],
                accept_multiple_files=True,
            )

            if uploaded_files and st.button("Process All Files"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                successful = 0
                failed = 0

                for i, uploaded_file in enumerate(uploaded_files):
                    temp_path = Path(f"./temp_{uploaded_file.name}")

                    try:
                        status_text.text(f"Processing {uploaded_file.name}...")

                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        success = pipeline.ingest_file(temp_path)

                        if success:
                            successful += 1
                        else:
                            failed += 1

                    finally:
                        if temp_path.exists():
                            temp_path.unlink()

                        progress_bar.progress((i + 1) / len(uploaded_files))

                status_text.text("")
                st.success(f"Processed {successful}/{len(uploaded_files)} files")

                if failed > 0:
                    st.warning(f"Failed to process {failed} files")

    with tabs[2]:
        st.header("System Statistics")

        if st.button("Refresh Stats"):
            stats = pipeline.get_stats()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Knowledge Graph")
                graph_stats = stats.get("graph", {})
                st.metric("Total Entities", graph_stats.get("total_entities", 0))
                st.metric("Total Relationships", graph_stats.get("total_relationships", 0))

                entity_types = graph_stats.get("entity_types", {})
                if entity_types:
                    st.write("**Entity Types:**")
                    for entity_type, count in entity_types.items():
                        st.write(f"- {entity_type}: {count}")

            with col2:
                st.subheader("Vector Database")
                vector_stats = stats.get("vector", {})
                st.metric("Total Vectors", vector_stats.get("total_vectors", 0))
                st.write(f"**Vector Size:** {vector_stats.get('vector_size', 'N/A')}")
                st.write(f"**Distance Metric:** {vector_stats.get('distance_metric', 'N/A')}")


if __name__ == "__main__":
    main()
