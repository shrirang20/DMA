import streamlit as st
import pandas as pd
import re
from fuzzywuzzy import process, fuzz

if st.button("← Back to Dashboard"):
    st.switch_page("app.py")

def load_reference_file(ref_file):
    """Load reference file and let the user select DMA Name and DMA Code columns."""
    if ref_file.name.endswith('.csv'):
        ref_df = pd.read_csv(ref_file)
    elif ref_file.name.endswith('.xlsx'):
        ref_df = pd.read_excel(ref_file)
    else:
        st.error("Unsupported file format. Please upload a CSV or XLSX file.")
        return None
    
    return ref_df

def clean_dma_name(value):
    """Cleans DMA name by removing extra spaces and standardizing formatting."""
    return re.sub(r'[^a-zA-Z0-9\s,()-]', '', value).strip().lower()

def map_dma(value, dma_mapping):
    """Convert DMA name to DMA ID with fuzzy matching and multi-region handling."""
    if pd.isna(value):  # If NaN, return as-is
        return value

    try:
        # If already an integer (DMA ID), return as is
        if isinstance(value, (int, float)) and not pd.isna(value):
            return int(value)

        cleaned_value = clean_dma_name(str(value))  # Ensure value is string before cleaning
        
        # 1️⃣ **Exact Match First**
        if cleaned_value in dma_mapping:
            return dma_mapping[cleaned_value]

        # 2️⃣ **Fuzzy Matching (Threshold 75)**
        match_result = process.extractOne(cleaned_value, dma_mapping.keys(), scorer=fuzz.ratio, score_cutoff=75)
        if match_result:
            best_match, score = match_result[0], match_result[1]
            return dma_mapping.get(best_match, value)

        # 3️⃣ **Handle Multi-Region Names (Hyphen, Comma, Space)**
        split_names = re.split(r'[-,]', cleaned_value)
        for split_name in split_names:
            split_name = split_name.strip()
            match_result = process.extractOne(split_name, dma_mapping.keys(), scorer=fuzz.ratio, score_cutoff=65)
            if match_result:
                best_match, score = match_result[0], match_result[1]
                return dma_mapping.get(best_match, value)

        # 4️⃣ **Try Each Word for Partial Matches (Lower Threshold)**
        words = cleaned_value.split()
        for word in words:
            match_result = process.extractOne(word, dma_mapping.keys(), scorer=fuzz.ratio, score_cutoff=60)
            if match_result:
                best_match, score = match_result[0], match_result[1]
                return dma_mapping.get(best_match, value)

        # 5️⃣ **Handle City-State Cases like "Florence-Myrtle Beach SC"**
        state_pattern = re.compile(r'([a-zA-Z\s]+)\s([A-Z]{2})$')  # Match "City StateCode" format
        match = state_pattern.match(cleaned_value)
        if match:
            city_part = match.group(1).strip()
            match_result = process.extractOne(city_part, dma_mapping.keys(), scorer=fuzz.ratio, score_cutoff=55)
            if match_result:
                best_match, score = match_result[0], match_result[1]
                return dma_mapping.get(best_match, value)

        return value  # Return original value if no match found
    except Exception as e:
        st.warning(f"Error processing value {value}: {e}")
        return value  # Return the original value in case of error

def process_data_file(df, dma_mapping, geo_column):
    """Replace DMA Names with DMA Codes while keeping existing DMA Codes intact."""
    df[geo_column] = df[geo_column].apply(lambda x: map_dma(x, dma_mapping))

    # Check if "unknown" exists and ask user if they want to remove those rows
    if "unknown" in df[geo_column].values:
        remove_unknown = st.radio("Some rows contain 'unknown'. Do you want to remove them?", ["Yes", "No"])
        if remove_unknown == "Yes":
            df = df[df[geo_column] != "unknown"]
    
    return df

def main():

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

    # st.set_page_config(page_title="DMA Name to Number Converter", layout="wide")
    st.title("📍 DMA Name to Number Converter")

    # Step 1: Upload Reference File
    st.subheader("🗂 Upload Reference File (Contains DMA Name and DMA Code columns)")
    ref_file = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"], key="ref")

    dma_mapping = None
    if ref_file:
        ref_df = load_reference_file(ref_file)
        if ref_df is not None:
            st.subheader("🔹 Select Columns from Reference File")
            name_column = st.selectbox("Select DMA Name Column", ref_df.columns, key="name_column")
            dma_column = st.selectbox("Select DMA Code Column", ref_df.columns, key="dma_column")
            
            # Create a mapping dictionary
            dma_mapping = {clean_dma_name(name): code for name, code in zip(ref_df[name_column], ref_df[dma_column])}

    # Step 2: Upload Data File
    st.subheader("📂 Upload Data File (Contains column to modify)")
    data_file = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"], key="data")

    if ref_file and data_file and dma_mapping:
        data_df = pd.read_csv(data_file) if data_file.name.endswith('.csv') else pd.read_excel(data_file)
        st.subheader("🔹 Select Column to Modify in Data File")
        geo_column = st.selectbox("Select Column Containing DMA Names/Numbers", data_df.columns, key="geo_column")

        # Step 3: Process Data File
        processed_df = process_data_file(data_df, dma_mapping, geo_column)

        # Step 4: Display Processed Data and Provide Download Option
        if processed_df is not None:
            st.subheader("✅ Processed Data Preview")
            st.dataframe(processed_df.head(20))  # Show only first 20 rows
            
            # Save for download
            csv = processed_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Processed File", csv, "processed_data.csv", "text/csv")

if __name__ == "__main__":
    main()
