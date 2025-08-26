import streamlit as st
import pandas as pd
import joblib
import numpy as np
import base64

# Load model and scaler
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

# -----------------------
# Function to set background
# -----------------------
# def set_bg(image_file):
#     with open(image_file, "rb") as f:
#         data = f.read()
#     encoded = base64.b64encode(data).decode()
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-image: url("data:image/jpg;base64,{encoded}");
#             background-size: cover;
#             background-position: center;
#             background-attachment: fixed;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# # Set background
# set_bg("download.jpg")

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Housing Price Finder", layout="wide")
st.title("🏠 Housing Price Finder")

# -----------------------
# Load dataset & models
# -----------------------
try:
    data = pd.read_csv("Housing_RL (1).csv")
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

try:
    model = joblib.load("model.pkl")
except Exception:
    model = None

try:
    scaler = joblib.load("scaler.pkl")
except Exception:
    scaler = None

# -----------------------
# Lowercase copy for filtering
# -----------------------
data_lower = data.copy()
data_lower.columns = [c.strip().lower().replace(" ", "_") for c in data_lower.columns]

if st.checkbox("Show dataset columns & sample"):
    st.write("Original columns:", list(data.columns))
    st.write("Lowercase columns:", list(data_lower.columns))
    st.dataframe(data_lower.head())

# Detect columns
price_col_l = next((c for c in data_lower.columns if "price" in c), None)
car_col_l = next((c for c in data_lower.columns if "car" in c), None)
rooms_col_l = next((c for c in data_lower.columns if "room" in c), None)
type_col_l = next((c for c in data_lower.columns if any(k in c for k in ("type", "house_type", "property_type"))), None)

# -----------------------
# User Inputs
# -----------------------
st.header("Enter Your Requirements")
budget = st.number_input("Maximum budget (₹)", min_value=0, value=1000000, step=50000)

if car_col_l:
    car_spaces = st.number_input("Minimum car spaces required", min_value=0, value=0, step=1)
else:
    car_spaces = None
    st.info("No 'car' column detected; skipping filter.")

if rooms_col_l:
    rooms = st.number_input("Minimum number of rooms required", min_value=0, value=1, step=1)
else:
    rooms = None
    st.info("No 'rooms' column detected; skipping filter.")

if type_col_l:
    house_types = sorted(data_lower[type_col_l].dropna().unique())
    house_types.insert(0, "Any")
    house_type = st.selectbox("House type", options=house_types)
else:
    house_type = "Any"
    st.info("No 'house type' column detected; skipping filter.")

# -----------------------
# Filtering
# -----------------------
if st.button("Find Houses"):
    filtered_lower = data_lower.copy()

    if price_col_l:
        filtered_lower = filtered_lower[filtered_lower[price_col_l] <= budget]
    if car_col_l and car_spaces is not None:
        filtered_lower = filtered_lower[filtered_lower[car_col_l] >= car_spaces]
    if rooms_col_l and rooms is not None:
        filtered_lower = filtered_lower[filtered_lower[rooms_col_l] >= rooms]
    if type_col_l and house_type != "Any":
        filtered_lower = filtered_lower[filtered_lower[type_col_l] == house_type]

    if filtered_lower.empty:
        st.warning("No houses found matching your criteria.")
    else:
        st.success(f"Found {len(filtered_lower)} houses matching your requirements!")
        filtered_original = data.loc[filtered_lower.index]
        st.markdown("### Filtered Houses")
        st.dataframe(filtered_original.reset_index(drop=True))



