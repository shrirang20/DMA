import streamlit as st
from streamlit_option_menu import option_menu

def main():
    st.set_page_config(
        page_title="Data Processing Toolkit",
        page_icon="🧰",
        layout="wide"
    )
    
    # Custom CSS to hide ALL default Streamlit UI elements
    hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    
    # Your original UI styling
    st.markdown("""
    <style>
    .app-card {
        border: 1px solid #e1e4e8;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        background-color: #f8f9fa;
    }
    .app-card:hover {
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    .app-title {
        color: #1e88e5;
        margin-bottom: 10px;
    }
    .app-description {
        color: #555;
        font-size: 14px;
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="header"><h1>🧰 Data Processing Toolkit</h1></div>', unsafe_allow_html=True)
    
    # App selection
    st.write("Select an application from the options below:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌍 Geo ID Filtering", use_container_width=True, 
                    key="geo_id_button", help="Filter files based on geographic identifiers"):
            st.switch_page("pages/Geo_ID_Filtering.py")
        
        st.markdown("""
        <div class="app-card">
            <h3 class="app-title">Geo ID Filtering</h3>
            <p class="app-description">
                Filter File 1 based on Geo IDs present in File 2. 
                Supports CSV and Excel files with flexible column matching.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📍 DMA Name to Code Converter", use_container_width=True,
                    key="dma_button", help="Convert DMA names to standardized codes"):
            st.switch_page("pages/DMA_Converter.py")
        
        st.markdown("""
        <div class="app-card">
            <h3 class="app-title">DMA Name to Code Converter</h3>
            <p class="app-description">
                Convert DMA names to DMA codes using fuzzy matching. 
                Handles various naming formats and partial matches.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()