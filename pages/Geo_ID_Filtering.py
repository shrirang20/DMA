import streamlit as st
import pandas as pd

if st.button("← Back to Dashboard"):
    st.switch_page("app.py")

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

    st.title("Geo ID Filtering Tool")
    st.write("""
    This app filters File 1 based on Geo IDs present in File 2.
    Upload both files, specify the Geo ID columns, and download the filtered result.
    """)

    # File upload section
    st.header("1. Upload Files")
    col1, col2 = st.columns(2)
    
    with col1:
        file1 = st.file_uploader("Upload File 1 (Data File)", type=['csv', 'xlsx', 'xls'])
    
    with col2:
        file2 = st.file_uploader("Upload File 2 (Geo ID Reference File)", type=['csv', 'xlsx', 'xls'])

    if file1 is not None and file2 is not None:
        try:
            # Read files based on their types
            def read_file(file):
                if file.name.endswith('.csv'):
                    return pd.read_csv(file)
                else:
                    return pd.read_excel(file)
            
            df1 = read_file(file1)
            df2 = read_file(file2)

            # Display file previews
            st.header("2. File Previews")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("File 1 Preview")
                st.write(df1.head())
            with col2:
                st.subheader("File 2 Preview")
                st.write(df2.head())

            # Column selection
            st.header("3. Select Geo ID Columns")
            
            col1, col2 = st.columns(2)
            with col1:
                file1_geo_col = st.selectbox(
                    "Select Geo ID column in File 1",
                    options=df1.columns
                )
            with col2:
                file2_geo_col = st.selectbox(
                    "Select Geo ID column in File 2",
                    options=df2.columns
                )

            # Filtering process
            st.header("4. Filter and Download")
            
            if st.button("Filter File 1 based on File 2 Geo IDs"):
                # Get unique geo IDs from both files
                file1_geo_ids = set(df1[file1_geo_col].astype(str).str.strip().unique())
                file2_geo_ids = set(df2[file2_geo_col].astype(str).str.strip().unique())
                
                # Find matching geo IDs
                matching_ids = file1_geo_ids.intersection(file2_geo_ids)
                
                if not matching_ids:
                    st.error("No matching Geo IDs found between the two files!")
                    return
                
                # Filter the original dataframe
                filtered_df = df1[
                    df1[file1_geo_col].astype(str).str.strip().isin(matching_ids)
                ]
                
                # Show stats
                st.success(f"""
                Filtering complete!
                - Original records in File 1: {len(df1):,}
                - Valid Geo IDs in File 2: {len(file2_geo_ids):,}
                - Matching Geo IDs found: {len(matching_ids):,}
                - Filtered records in output: {len(filtered_df):,}
                """)
                
                # Show sample of filtered data
                st.subheader("Filtered Data Preview")
                st.write(filtered_df.head())
                
                # Download button
                st.download_button(
                    label="Download Filtered Data as CSV",
                    data=filtered_df.to_csv(index=False).encode('utf-8'),
                    file_name='filtered_output.csv',
                    mime='text/csv'
                )
                
                # Show non-matching geo IDs for reference
                with st.expander("Show non-matching Geo IDs"):
                    non_matching_in_file1 = file1_geo_ids - file2_geo_ids
                    non_matching_in_file2 = file2_geo_ids - file1_geo_ids
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Geo IDs in File 1 not found in File 2 ({len(non_matching_in_file1)}):")
                        st.write(list(non_matching_in_file1)[:10])  # Show first 10 to avoid overload
                    with col2:
                        st.write(f"Geo IDs in File 2 not found in File 1 ({len(non_matching_in_file2)}):")
                        st.write(list(non_matching_in_file2)[:10])

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()