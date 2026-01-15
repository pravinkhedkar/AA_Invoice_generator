from shapely import wkt
import pandas as pd
import geopy.distance
from shapely.geometry import Polygon
import os
from convex_hull_map import CONVEX_HULL_MAP
from constants import VILLAGE_CODE_MAPPING_ENGLISH

def create_square_polygon(center_lat, center_lon, side_length_m):
    """
    Creates a square polygon (list of 4 coordinates) centered at a given lat/lon point.

    Args:
        center_lat (float): The latitude of the center point.
        center_lon (float): The longitude of the center point.
        side_length_m (float): The side length of the square in meters.

    Returns:
        list of tuples: The coordinates of the square's corners [(lat1, lon1), ...].
    """
    # Define the starting point
    center_point = geopy.Point(center_lat, center_lon)
    
    # Calculate half of the diagonal distance
    half_diagonal_dist = (side_length_m / 2) * (2**0.5)
    d = geopy.distance.distance(meters=half_diagonal_dist)
    p_nw = d.destination(point=center_point, bearing=315)
    p_ne = d.destination(point=center_point, bearing=45)
    p_se = d.destination(point=center_point, bearing=135)
    p_sw = d.destination(point=center_point, bearing=225)

    corners = [
        (p_sw.latitude, p_sw.longitude),
        (p_se.latitude, p_se.longitude),
        (p_ne.latitude, p_ne.longitude),
        (p_nw.latitude, p_nw.longitude),
        (p_sw.latitude, p_sw.longitude) # Close the polygon
    ]
    
    # Create a shapely polygon object (lon, lat format for shapely)
    polygon = Polygon([(lon, lat) for lat, lon in corners])
    
    return corners, polygon

# Example Usage

def check_convex_hull_intersection(square_poly):
    village_code_intersected = [key for key, value in CONVEX_HULL_MAP.items() if wkt.loads(value).intersects(square_poly)]
    return village_code_intersected

def get_intersected_record(longitude, latitude):
    side_m = 1  # 1 meter side length
    corners, square_poly = create_square_polygon(latitude, longitude, side_m)

    # Get current folder path and construct CSV file path
    current_folder = os.path.dirname(os.path.abspath(__file__))
    village_code_list = check_convex_hull_intersection(square_poly)
    if village_code_list:
        for village_code in village_code_list:
            village_name = VILLAGE_CODE_MAPPING_ENGLISH.get(village_code, "Unknown Village")
            csv_file = os.path.join(current_folder, 'transformed_all_records',f"transformed_gis_data_{village_code}_{village_name}.csv")
            if not os.path.exists(csv_file):
                print(f"Error: CSV file not found at {csv_file}")
                return None, None
            df = pd.read_csv(csv_file)
            for index, row in df.iterrows():
                poly_4326 = wkt.loads(row['geometry_text_transformed'])

                # Check for intersection
                if square_poly.intersects(poly_4326):
                    intersection_result = square_poly.intersection(poly_4326)
                    # Return as DataFrame with geometry columns already dropped
                    data_dict = {
                        'gat_number': row['gat_number'],
                        'info': row['info'],
                        'village_code': row['village_code']
                    }
                    return data_dict, intersection_result

    return None, None

# Example Usage
# if __name__ == '__main__':
#     #425 lon lat
#     lon, lat = 73.66145314738887, 18.540054590592224
#     # lat, lon =  18.545217198626794, 73.6565971064236

#     #363 lon lat
#     # lon, lat =  73.65982448286833, 18.546279760082392
#     data, result = get_intersected_record(lon, lat)
#     if data is not None:
#         # print(data['info'], data['gat_number'], data['geometry_text_transformed'])
#         # print(result)
#         gat_number = data['gat_number']
#         info = data['info']
#         village_code = data['village_code']

#     else:
#         print("No intersecting record found.")