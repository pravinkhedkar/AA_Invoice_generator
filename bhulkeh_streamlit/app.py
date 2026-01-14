import streamlit as st
from get_gat_number_data import get_intersected_record

# Page configuration
st.set_page_config(page_title="Gat Number Finder", layout="centered")

# Title
st.title("🗺️ Gat Number Finder")
st.markdown("Enter latitude and longitude to find intersecting plot information")

# Input method selection
input_method = st.radio(
    "Choose input method:",
    ["Separate Fields", "Comma Separated"],
    horizontal=True
)

latitude = None
longitude = None

if input_method == "Separate Fields":
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input(
            "Latitude",
            value=None,
            format="%.15f",
            help="Enter the latitude coordinate"
        )
    
    with col2:
        longitude = st.number_input(
            "Longitude",
            value=None,
            format="%.15f",
            help="Enter the longitude coordinate"
        )

else:  # Comma Separated
    coords_input = st.text_input(
        "Enter coordinates (format: latitude, longitude)",
        placeholder="18.545217198626794, 73.6565971064236",
        help="Enter latitude and longitude separated by comma"
    )
    
    if coords_input:
        try:
            parts = [x.strip() for x in coords_input.split(',')]
            
            if len(parts) != 2:
                st.error("❌ Please enter exactly 2 values separated by comma (latitude, longitude)")
            else:
                try:
                    latitude = float(parts[0])
                    longitude = float(parts[1])
                    
                    # Validate ranges
                    if not (-90 <= latitude <= 90):
                        st.error("❌ Latitude must be between -90 and 90")
                        latitude = None
                    elif not (-180 <= longitude <= 180):
                        st.error("❌ Longitude must be between -180 and 180")
                        longitude = None
                    else:
                        st.success(f"✅ Valid coordinates: Latitude={latitude}, Longitude={longitude}")
                
                except ValueError:
                    st.error("❌ Invalid input. Please enter numeric values only")
                    latitude = None
                    longitude = None
        
        except Exception as e:
            st.error(f"❌ Error parsing input: {str(e)}")
            latitude = None
            longitude = None

# Search button
if st.button("🔍 Search", use_container_width=True):
    if latitude is None or longitude is None:
        st.error("❌ Please enter both Latitude and Longitude values")
    else:
        with st.spinner("Searching for intersecting records..."):
            data, result = get_intersected_record(longitude, latitude)
            
            if data is not None and not data.empty:
                st.success("✅ Intersecting record found!")
                
                # Display results in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(label="Gat Number", value=data['gat_number'])
                
                # with col2:
                #     st.metric(label="Village/Info", value=data['info'])
                
                # Display additional details
                st.divider()
                st.subheader("Details")
                
                details_col1, details_col2 = st.columns(2)
                with details_col1:
                    st.write(f"**Latitude:** {latitude}")
                    st.write(f"**Longitude:** {longitude}")
                
                # with details_col2:
                #     st.write(f"**Intersection Area:** {result.area}")
                #     st.write(f"**Geometry Type:** {result.geom_type}")
                
                # Display full row data
                st.subheader("Full Record Data")
                st.dataframe(data, use_container_width=True, hide_index=True)

            else:
                st.warning("⚠️ No intersecting record found for the given coordinates.")
                st.info("Try using different latitude/longitude values.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>Mahabhulekh Gat Number Finder | Powered by Streamlit</small>
</div>
""", unsafe_allow_html=True)