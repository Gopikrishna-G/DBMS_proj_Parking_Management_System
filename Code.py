import streamlit as st
import pymysql
import pandas as pd
import re
from datetime import datetime, timedelta, time
import base64
import smtplib
import random

st.set_page_config(
    page_title="Parking Management System",
    page_icon="🚗",
)

# Establish a connection to the MySQL database
connection = pymysql.connect(host="localhost", user="root", password="Gopi-09092003", database="parking")

# Create a cursor object to interact with the database
cursor = connection.cursor()

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = None

if "selected_area_id" not in st.session_state:
    st.session_state.selected_area_id = None

if "res_id" not in st.session_state:
    st.session_state.res_id = None

if "otp" not in st.session_state:
    st.session_state.otp = None

def is_valid_email(email):
    # Regular expression to validate email address
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

def is_valid_phone(phone):
    # Regular expression to validate phone number
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone)

def is_valid_password(password):
    # Regular expression to validate password
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[-@$!%*?&])[A-Za-z\d@$!%*?&-]{8,}$'
    return re.match(pattern, password)


def create_user():
    st.subheader("Sign Up to Create an Account now!")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    phone_number = st.text_input("Enter your phone number")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea")
    parking_areas = cursor.fetchall()
    parking_areas_df = pd.DataFrame(parking_areas, columns=["AreaID", "AreaName", "Location"])
    parking_areas_df["Area Type"] = ["Two Wheeler","Four Wheeler","Two Wheeler, Four Wheeler, Large Vehicles"]
    st.markdown("## Parking Area IDs:")
    st.dataframe(parking_areas_df)
    area_id = st.radio("Select your Area ID", options=[area[0] for area in parking_areas])
    
    if st.button("Sign Up"):
        if not is_valid_email(email):
            st.error("Invalid email address. Please enter a valid email.")
        elif not is_valid_phone(phone_number):
            st.error("Invalid phone number. Please enter a 10-digit phone number.")
        elif cursor.execute("SELECT * FROM Users WHERE Username=%s", (username,)):
            st.error("Username already exists. Please choose a different one.")
        elif not is_valid_password(password):
            st.error("Invalid password. Password must be at least 8 characters long and include at least 1 special character(-@$!%*?&), 1 capital letter, and 1 number.")
        else:
            # Insert the new user into the Users table
            cursor.execute("INSERT INTO Users (Adn, Name, Email, PhoneNumber, Username, Password, AreaID) VALUES (0, %s, %s, %s, %s, %s, %s)",
                           (name, email, phone_number, username, password, area_id))  # You may modify the AreaID as per your requirement
            connection.commit()
            st.success("Account created! You can now sign in.")



def sign_in():
    st.subheader("Sign In / Login to your Account")
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    if st.button("Sign In"):
        # Check if the provided credentials match any user in the Users table (case-sensitive)
        cursor.execute("SELECT * FROM Users WHERE BINARY Username=%s AND BINARY Password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
            return None

def user_profile(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID=%s", (user_id,))
    user_details = cursor.fetchone()

    if user_details:
        st.markdown(f"# {user_details[2]}'s Profile Page")
        st.markdown("# 👇")
        st.markdown("### Your ID is {}".format(user_details[0]))
        st.markdown("### Your Name is {}".format(user_details[2]))
        st.markdown("### Your Email is {}".format(user_details[3]))
        st.markdown("### Your Phone Number is {}".format(user_details[4]))
        st.markdown("### Your Username is {}".format(user_details[5]))
        st.markdown("### Your Password is {}".format(user_details[6]))
        st.markdown("### Your Area ID is {}".format(user_details[7]))
        return True
    else:
        st.header("Profile")
        st.markdown("# OOPS!!!")
        st.markdown("## User not found.")
        return False


def edit_profile(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID=%s", (user_id,))
    user_details = cursor.fetchone()

    st.markdown(f"# {user_details[2]}'s Profile Editing Page")
    st.markdown("# 👇")
    
    name = st.text_input("Edit Your Name", value=user_details[2])
    email = st.text_input("Edit Your Email", value=user_details[3])
    phone_number = st.text_input("Edit Your Phone Number", value=user_details[4])
    password = st.text_input("Edit Your Password", type="password", value=user_details[6])

    if st.button("Submit"):
        if not is_valid_email(email):
            st.error("Invalid email address. Please enter a valid email.")
        elif not is_valid_phone(phone_number):
            st.error("Invalid phone number. Please enter a 10-digit phone number.")
        elif not is_valid_password(password):
            st.error("Invalid password. Password must be at least 8 characters long and include at least 1 special character(-@$!%*?&), 1 capital letter, and 1 number.")
        else:
            cursor.execute("UPDATE Users SET Name=%s, Email=%s, PhoneNumber=%s, Password=%s WHERE UserID=%s",
                           (name, email, phone_number, password, user_id))
            connection.commit()
            st.success("Profile updated successfully!, Go to the profile page to see the changes.")
            # Update session state with the new user details
            st.session_state.update = (user_details[0], name, email, phone_number, user_details[5], password, user_details[7])

def get_vehicle_details_by_user_id(user_id):
    query = "SELECT * FROM Vehicles WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

def display_vehicle_details(user_id):
    st.subheader("Vehicle Details")
    vehicle_details = get_vehicle_details_by_user_id(user_id)

    if vehicle_details:
        vehicle_details_df = pd.DataFrame(vehicle_details, columns=["VehicleID", "UserID", "RegistrationNumber", "VehicleType", "Color"])
        st.dataframe(vehicle_details_df)
    else:
        st.info("No vehicle details found.")
        st.markdown("## Vehicles not found, add a new vehicle first!!.")

def edit_vehicle_details(user_id, vehicle_id, registration_number, vehicle_type, color):
    cursor.execute("UPDATE Vehicles SET RegistrationNumber=%s, VehicleType=%s, Color=%s WHERE UserID=%s AND VehicleID=%s",
                   (registration_number, vehicle_type, color, user_id, vehicle_id))
    connection.commit()
    st.success("Vehicle details updated successfully!")

def add_new_vehicle(user_id, registration_number, vehicle_type, color):
    cursor.execute("INSERT INTO Vehicles (UserID, RegistrationNumber, VehicleType, Color) VALUES (%s, %s, %s, %s)",
                   (user_id, registration_number, vehicle_type, color))
    connection.commit()
    st.success("New vehicle added successfully!")

def edit_vehicle(user_id, vehicle_id):
    cursor.execute("SELECT * FROM Vehicles WHERE UserID=%s AND VehicleID=%s", (user_id, vehicle_id))
    vehicle_details = cursor.fetchone()

    if vehicle_details:
        registration_number = st.text_input("Edit Registration Number", value=vehicle_details[2], max_chars=10)
        vehicle_type = st.selectbox("Edit Vehicle Type", ["Two-Wheeler", "Four-Wheeler", "Large Vehicle"], index=["Two-Wheeler", "Four-Wheeler", "Large Vehicle"].index(vehicle_details[3]))
        color = st.text_input("Edit Vehicle Color", value=vehicle_details[4])

        if st.button("Save Changes"):
            edit_vehicle_details(user_id, vehicle_id, registration_number, vehicle_type, color)

def add_vehicle(user_id):
    st.subheader("Add Vehicle")
    registration_number = st.text_input("Enter Registration Number", max_chars=10)
    vehicle_type = st.selectbox("Select Vehicle Type", ["Two-Wheeler", "Four-Wheeler", "Large Vehicle"])
    color = st.text_input("Enter Vehicle Color")

    if st.button("Add Vehicle"):
        add_new_vehicle(user_id, registration_number, vehicle_type, color)

from datetime import datetime

def calculate_amount_to_be_paid(hourly_rate, daily_rate, monthly_rate, duration, reservation_datetime, payment_datetime):
    extra_charge = 0
    
    # Check if payment_datetime is not None
    if payment_datetime is not None:
        # Convert payment_datetime to a datetime object if it's not already
        if not isinstance(payment_datetime, datetime):
            payment_datetime = datetime.strptime(payment_datetime, "%Y-%m-%d %H:%M:%S")

        # Calculate the difference in hours between ReservationDateTime and PaymentDateTime
        time_difference = (reservation_datetime - payment_datetime).total_seconds() / 3600
        
        # Add extra charges based on the time difference
        if time_difference >= 720:  # 1 month
            extra_charge = 15
        elif time_difference >= 168:  # 1 week
            extra_charge = 10
        elif time_difference >= 24:  # 1 day
            extra_charge = 5
    else:
        # Handle the case when payment_datetime is None
        time_difference = 0

    # Calculate the amount to be paid
    amount_to_be_paid = (
        hourly_rate * duration
        if duration < 24
        else daily_rate * (duration // 24)
        if duration < 720
        else monthly_rate * (duration // (24 * 30))
    ) + extra_charge
    
    return amount_to_be_paid


def get_active_reservations(user_id):
    query = """
    SELECT
        R.ReservationID,
        PS.SpaceType,
        R.ReservationDateTime,
        R.Duration,
        V.RegistrationNumber,
        V.VehicleType,
        PA.AreaName,
        PA.Location,
        PF.HourlyRate,
        PF.DailyRate,
        PF.MonthlyRate,
        PY.Amount AS AmountPaid,
        PY.PaymentDateTime
    FROM
        Reservations R
        JOIN ParkingSpaces PS ON R.SpaceID = PS.SpaceID
        JOIN Vehicles V ON R.UserID = V.UserID AND R.VehicleID = V.VehicleID
        JOIN ParkingArea PA ON PS.AreaID = PA.AreaID
        JOIN ParkingFee PF ON PS.SpaceType = PF.SpaceType
        LEFT JOIN Payments PY ON R.ReservationID = PY.ReservationID
    WHERE
        R.UserID = %s
        AND R.ReservationDateTime <= NOW()
        AND (R.ReservationDateTime + INTERVAL R.Duration HOUR) >= NOW()
        AND V.VehicleID IN (SELECT VehicleID FROM Vehicles WHERE UserID = %s)
    """
    cursor.execute(query, (user_id, user_id))
    reservations = cursor.fetchall()

    if cursor.rowcount > 0:
        st.success("Active reservations found:")
        reservation_data = []
        for reservation in reservations:
            (
                reservation_id,
                space_type,
                reservation_datetime,
                duration,
                registration_number,
                vehicle_type,
                area_name,
                location,
                hourly_rate,
                daily_rate,
                monthly_rate,
                amount_paid,
                payment_datetime,
            ) = reservation

            amount_to_be_paid = calculate_amount_to_be_paid(
                hourly_rate, daily_rate, monthly_rate, duration, reservation_datetime, payment_datetime
            )

            reservation_data.append(
                [
                    reservation_id,
                    space_type,
                    reservation_datetime,
                    duration,
                    registration_number,
                    vehicle_type,
                    area_name,
                    location,
                    hourly_rate,
                    daily_rate,
                    monthly_rate,
                    amount_paid,
                    amount_to_be_paid,
                ]
            )

        reservations_df = pd.DataFrame(
            reservation_data,
            columns=[
                "ReservationID",
                "SpaceType",
                "ReservationDateTime",
                "Duration",
                "RegistrationNumber",
                "VehicleType",
                "AreaName",
                "Location",
                "HourlyRate",
                "DailyRate",
                "MonthlyRate",
                "AmountPaid",
                "AmountToBePaid",
            ],
        )
        st.dataframe(reservations_df)
    else:
        st.info("No active reservations found.")

def get_future_reservations(user_id):
    query = """
    SELECT
        R.ReservationID,
        PS.SpaceType,
        R.ReservationDateTime,
        R.Duration,
        V.RegistrationNumber,
        V.VehicleType,
        PA.AreaName,
        PA.Location,
        PF.HourlyRate,
        PF.DailyRate,
        PF.MonthlyRate,
        PY.Amount AS AmountPaid,
        PY.PaymentDateTime
    FROM
        Reservations R
        JOIN ParkingSpaces PS ON R.SpaceID = PS.SpaceID
        JOIN Vehicles V ON R.UserID = V.UserID AND R.VehicleID = V.VehicleID
        JOIN ParkingArea PA ON PS.AreaID = PA.AreaID
        JOIN ParkingFee PF ON PS.SpaceType = PF.SpaceType
        LEFT JOIN Payments PY ON R.ReservationID = PY.ReservationID
    WHERE
        R.UserID = %s
        AND R.ReservationDateTime > NOW()
    """
    cursor.execute(query, (user_id,))
    reservations = cursor.fetchall()

    if cursor.rowcount > 0:
        st.success("Future reservations found:")
        reservation_data = []
        for reservation in reservations:
            (
                reservation_id,
                space_type,
                reservation_datetime,
                duration,
                registration_number,
                vehicle_type,
                area_name,
                location,
                hourly_rate,
                daily_rate,
                monthly_rate,
                amount_paid,
                payment_datetime,
            ) = reservation

            amount_to_be_paid = calculate_amount_to_be_paid(
                hourly_rate, daily_rate, monthly_rate, duration, reservation_datetime, payment_datetime
            )

            reservation_data.append(
                [
                    reservation_id,
                    space_type,
                    reservation_datetime,
                    duration,
                    registration_number,
                    vehicle_type,
                    area_name,
                    location,
                    hourly_rate,
                    daily_rate,
                    monthly_rate,
                    amount_paid,
                    amount_to_be_paid,
                ]
            )

        reservations_df = pd.DataFrame(
            reservation_data,
            columns=[
                "ReservationID",
                "SpaceType",
                "ReservationDateTime",
                "Duration",
                "RegistrationNumber",
                "VehicleType",
                "AreaName",
                "Location",
                "HourlyRate",
                "DailyRate",
                "MonthlyRate",
                "AmountPaid",
                "AmountToBePaid",
            ],
        )
        st.dataframe(reservations_df)
    else:
        st.info("No future reservations found.")

def get_past_reservations(user_id):
    query = """
    SELECT
        R.ReservationID,
        PS.SpaceType,
        R.ReservationDateTime,
        R.Duration,
        V.RegistrationNumber,
        V.VehicleType,
        PA.AreaName,
        PA.Location,
        PF.HourlyRate,
        PF.DailyRate,
        PF.MonthlyRate,
        PY.Amount AS AmountPaid,
        PY.PaymentDateTime
    FROM
        Reservations R
        JOIN ParkingSpaces PS ON R.SpaceID = PS.SpaceID
        JOIN Vehicles V ON R.UserID = V.UserID AND R.VehicleID = V.VehicleID
        JOIN ParkingArea PA ON PS.AreaID = PA.AreaID
        JOIN ParkingFee PF ON PS.SpaceType = PF.SpaceType
        LEFT JOIN Payments PY ON R.ReservationID = PY.ReservationID
    WHERE
        R.UserID = %s
        AND R.ReservationDateTime < NOW()
    """
    cursor.execute(query, (user_id,))
    reservations = cursor.fetchall()

    if cursor.rowcount > 0:
        st.success("Past reservations found:")
        reservation_data = []
        for reservation in reservations:
            (
                reservation_id,
                space_type,
                reservation_datetime,
                duration,
                registration_number,
                vehicle_type,
                area_name,
                location,
                hourly_rate,
                daily_rate,
                monthly_rate,
                amount_paid,
                payment_datetime,
            ) = reservation

            amount_to_be_paid = calculate_amount_to_be_paid(
                hourly_rate, daily_rate, monthly_rate, duration, reservation_datetime, payment_datetime
            )

            reservation_data.append(
                [
                    reservation_id,
                    space_type,
                    reservation_datetime,
                    duration,
                    registration_number,
                    vehicle_type,
                    area_name,
                    location,
                    hourly_rate,
                    daily_rate,
                    monthly_rate,
                    amount_paid,
                    amount_to_be_paid,
                ]
            )

        reservations_df = pd.DataFrame(
            reservation_data,
            columns=[
                "ReservationID",
                "SpaceType",
                "ReservationDateTime",
                "Duration",
                "RegistrationNumber",
                "VehicleType",
                "AreaName",
                "Location",
                "HourlyRate",
                "DailyRate",
                "MonthlyRate",
                "AmountPaid",
                "AmountToBePaid",
            ],
        )
        st.dataframe(reservations_df)
    else:
        st.info("No past reservations found.")

def display_parking_areas():
    cursor.execute("SELECT * FROM ParkingArea")
    parking_areas = cursor.fetchall()
    parking_areas_df = pd.DataFrame(parking_areas, columns=["AreaID", "AreaName", "Location", "TotalSpaces"])
    parking_areas_df["Area Type"] = ["Two-Wheeler", "Four-Wheeler", "Two-Wheeler, Four-Wheeler, Large Vehicles"]
    st.dataframe(parking_areas_df)

def check_space_availability_for_duration(area_id, reservation_start_time, end_time, duration):
    # Check if the space is available in the specified area, date, and time for the entire duration
    query = """
    SELECT COUNT(*) 
    FROM ParkingAvailability
    WHERE SpaceID IN (
        SELECT SpaceID
        FROM ParkingSpaces
        WHERE AreaID = %s
    )
    AND (
        (NoneAvailStart >= %s AND NoneAvailStart < %s) OR
        (NoneAvailEnd > %s AND NoneAvailEnd <= %s) OR
        (NoneAvailStart <= %s AND NoneAvailEnd >= %s)
    )
    """
    cursor.execute(query, (area_id, end_time, reservation_start_time, end_time, reservation_start_time, reservation_start_time, end_time))
    availability_count = cursor.fetchone()[0]

    return availability_count == 0

def hourly_reservation(user_id, vehicle_details, area_id):
    st.info("Hourly reservation logic goes here!")

    # Get the number of hours for reservation
    hours = st.number_input("Enter the number of hours for reservation:", min_value=1, value=1, step=1)

    # Get the date for reservation
    reservation_date = st.date_input("Select the date for reservation:", min_value=datetime.now().date())

    # Get the start time for reservation
    start_time = st.time_input("Select the start time for reservation:")

    # Combine date and time to get the full reservation start time
    reservation_start_time = datetime(reservation_date.year, reservation_date.month, reservation_date.day, start_time.hour, start_time.minute, start_time.second)

    # Calculate the end time based on the selected hours
    end_time = reservation_start_time + timedelta(hours=hours)

    # Check if the space is available
    if check_space_availability_for_duration(area_id, reservation_date, reservation_start_time, end_time):
        st.success("Space is available! You can proceed with the reservation.")
        return hours, reservation_start_time, end_time

    else:
        st.error("Space is already reserved for the selected date and time. Please choose a different date or time.")
        return None, None, None



def daily_reservation(user_id, vehicle_details, area_id):
    st.info("Daily reservation logic goes here!")

    # Ask for the number of days for reservation
    num_days = st.number_input("Enter the number of days for reservation:", min_value=1, value=1, step=1)

    # Get the date for reservation
    reservation_date = st.date_input("Select the date for reservation:", min_value=datetime.now().date())


    # Get the start time for reservation
    start_time = st.time_input("Select the start time for reservation:")

    # Combine date and time to get the full reservation start time
    reservation_start_time = datetime(reservation_date.year, reservation_date.month, reservation_date.day, start_time.hour, start_time.minute, start_time.second)

    # Calculate the end time based on the selected duration
    end_time = reservation_start_time + timedelta(days=num_days) - timedelta(seconds=1)

    # Check if the space is available
    if check_space_availability_for_duration(area_id, reservation_start_time, end_time, num_days*24):
        st.success("Space is available! You can proceed with the reservation.")
        return num_days*24, reservation_start_time, end_time
        
    else:
        st.error("Space is already reserved for the selected date and time. Please choose a different date or time.")
        return None, None, None

def monthly_reservation(user_id, vehicle_details, area_id):
    st.info("Monthly reservation logic goes here!")

    # Ask for the number of months for reservation
    num_months = st.number_input("Enter the number of months for reservation:", min_value=1, value=1, step=1)

    # Get the date for reservation
    reservation_date = st.date_input("Select the date for reservation:", min_value=datetime.now().date())

    # Get the start time for reservation
    start_time = st.time_input("Select the start time for reservation:")

    # Combine date and time to get the full reservation start time
    reservation_start_time = datetime(reservation_date.year, reservation_date.month, reservation_date.day, start_time.hour, start_time.minute, start_time.second)

    # Calculate the end time based on the selected duration
    end_time = reservation_start_time + timedelta(days=num_months*30) - timedelta(seconds=1)

    # Check if the space is available
    if check_space_availability_for_duration(area_id, reservation_start_time, end_time, num_months*30*24):
        st.success("Space is available! You can proceed with the reservation.")
        return num_months*30*24, reservation_start_time, end_time
    else:
        st.error("Space is already reserved for the selected date and time. Please choose a different date or time.")
        return None, None, None

def get_next_reservation_time(area_id, vehicle_type, current_time):
    # Query the database to get the next reservation time
    cursor.execute("""
        SELECT MIN(ReservationDateTime + INTERVAL Duration HOUR) 
        FROM Reservations 
        WHERE AreaID = %s 
            AND VehicleID IN (
                SELECT VehicleID FROM Vehicles WHERE VehicleType = %s
            )
            AND ReservationDateTime > %s
            AND ReservationDateTime <= %s
    """, (area_id, vehicle_type, current_time, current_time))

    next_reservation_time = cursor.fetchone()[0]

    return next_reservation_time

def get_vehicle_type_id(vehicle_type):
    cursor.execute("SELECT VehicleID FROM Vehicles WHERE VehicleType = %s", (vehicle_type,))
    vehicle_type_id = cursor.fetchall()[0]
    return vehicle_type_id

def calculate_waiting_time(area_id, vehicle_type, current_time):
    # Check the availability of parking spaces for the given area and vehicle type
    if not check_space_availability_for_duration(area_id, current_time, current_time, vehicle_type):
        # Calculate the waiting time based on existing reservations
        vehicle_type_id = get_vehicle_type_id(vehicle_type)
        next_reservation_time = get_next_reservation_time(area_id, vehicle_type_id, current_time)

        if next_reservation_time:
            waiting_time = (next_reservation_time - current_time).total_seconds() / 60  # Convert to minutes
            return int(waiting_time)
    return None

def get_waiting_times_for_other_areas(vehicle_type, current_time, selected_area_id):
    # Initialize a dictionary to store waiting times for other areas
    waiting_times = {}

    # Iterate over other parking areas (excluding the selected one)
    for area_id in range(1, 4):
        if area_id != selected_area_id:
            # Check the availability and waiting time for each area
            waiting_time = calculate_waiting_time(area_id, vehicle_type, current_time)
            waiting_times[area_id] = waiting_time

    return waiting_times

def display_parking_fees():
    cursor.execute("""
        SELECT *
        FROM ParkingFee
    """)
    fees = cursor.fetchall()

    # Convert the result to a DataFrame
    fee_df = pd.DataFrame(fees, columns=["FeeID","SpaceType","HourlyRate","DailyRate","MonthlyRate"])

    st.markdown("## Parking Fees Table:")
    st.dataframe(fee_df)

if 'otp' not in st.session_state:
    st.session_state.otp = None
SENDER_EMAIL = 'parkingdbms@gmail.com'  # Replace with your email
SENDER_PASSWORD = 'cshe egbh yycx cocu'  # Replace with your password

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(receiver_email, otp):
    subject = 'Your OTP for verification'
    body = f'Your OTP is: {otp}'
    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, message)
        st.success("An OTP has been sent to the your email!!.")
    st.session_state.otp = otp

def get_available_space(area_id, reservation_start_time, reservation_end_time):
    try:
        # Convert reservation times to strings to match the TIMESTAMPDIFF format
        start_time_str = reservation_start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = reservation_end_time.strftime('%Y-%m-%d %H:%M:%S')

        query = """
            SELECT SpaceID
            FROM ParkingSpaces
            WHERE AreaID = %s
            AND SpaceID NOT IN (
                SELECT DISTINCT p.SpaceID
                FROM ParkingAvailability p
                WHERE p.AreaID = %s
                AND (
                    (p.NoneAvailEnd <= %s AND p.NoneAvailEnd > %s) OR
                    (p.NoneAvailStart < %s AND p.NoneAvailEnd >= %s) OR
                    (p.NoneAvailStart >= %s AND p.NoneAvailEnd <= %s)
                )
            )
            LIMIT 1
        """

        cursor.execute(query, (area_id, area_id, end_time_str, start_time_str, end_time_str, start_time_str, start_time_str, end_time_str))
        result = cursor.fetchone()

        if result:
            available_space_id = result[0]
            return available_space_id
        else:
            st.warning("No available parking spaces found for the selected time period.")
            return None
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

def reserve_parking_space(user_id):
    park_choice = st.sidebar.radio("Would you like to park?", ("Yes", "No"))

    if park_choice == "Yes":
        # Get user's vehicles for reservation
        user_vehicles = get_vehicle_details_by_user_id(user_id)

        if not user_vehicles:
            st.warning("No vehicles available for reservation. Please add a vehicle first.")
            return

        st.markdown("## Your Vehicles for Reservation:")

        # Display user's vehicles for selection
        selected_vehicle = st.selectbox("Select a vehicle for reservation:", [f"{vehicle[3]} ({vehicle[4]}) ({vehicle[2]}) ({vehicle[0]})" for vehicle in user_vehicles])
        
        # Extract vehicle details from the selected option
        selected_vehicle_details = re.match(r"(.+) \((.+)\ \((.+)\) \((.+)\)", selected_vehicle)
        if selected_vehicle_details:
            selected_vehicle_type = selected_vehicle_details.group(1)
            selected_vehicle_color = selected_vehicle_details.group(2)
            selected_vehicle_registration_number = selected_vehicle_details.group(3)
            vid = selected_vehicle_details.group(4)

            st.success(f"Vehicle selected for reservation: {selected_vehicle_type} ({selected_vehicle_color}) ({selected_vehicle_registration_number})")

        # Get default area ID for the user
        cursor.execute("SELECT AreaID FROM Users WHERE UserID = %s", (user_id,))
        default_area_id = cursor.fetchone()[0]

        if selected_vehicle_type == "Two-Wheeler":
            st.sidebar.markdown("### Parking Area Descriptions:")
            cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea WHERE AreaID = 1 OR AreaID = 3")
            area = cursor.fetchall()
            df = pd.DataFrame(area, columns=["AreaID", "AreaName", "Location"])
            st.sidebar.dataframe(df)
            st.sidebar.markdown("## Parking Area IDs 👇 for two-wheelers")
            if default_area_id == 1:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 1 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                area_ids.remove(default_area_id)
                default_area_id = f"{default_area_id} (default)"
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= [default_area_id ] + area_ids)
            elif default_area_id == 3:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 1 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                area_ids.remove(default_area_id)
                default_area_id = f"{default_area_id} (default)"
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= [default_area_id ] + area_ids)
            else:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 1 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= area_ids)

            if st.session_state.selected_area_id:            
                # Display buttons for reservation types
                st.markdown("## Select Reservation Type:")
                hourly_button = st.button("Hourly Reservation")
                daily_button = st.button("Daily Reservation")
                monthly_button = st.button("Monthly Reservation")

                if hourly_button:
                    st.session_state.page = "hourly"
                elif daily_button:
                    st.session_state.page = "daily"
                elif monthly_button:
                    st.session_state.page = "monthly"

                if st.session_state.page == "hourly":
                    hours, reservation_date, end_time = hourly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")#hourly_rate, daily_rate, monthly_rate, duration, reservation_datetime, payment_datetime
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                proceed_payment = st.checkbox("I want to proceed with the payment, send the otp!")
                                if proceed_payment:
                                    
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email,st.session_state.otp)
                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)
                                    
                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    if p:
                                        if entered_otp == st.session_state.otp:
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, %s, %s, NOW())
                                            """, (user_id, st.session_state.res_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                        elif entered_otp != st.session_state.otp:
                                            st.error("Invalid OTP. Please try again.")

                    
                elif st.session_state.page == "daily":
                    hours, reservation_date, end_time = daily_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())}")

                                otp = generate_otp()
                                proceed_payment = st.checkbox("I want to proceed with the payment, send the otp!")
                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    while p: 
                                        if entered_otp == f"{otp}":
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                            """, (user_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                        elif entered_otp != f"{otp}":
                                            st.error("Invalid OTP. Please try again.")
                                            break


                elif st.session_state.page == "monthly":
                    hours, reservation_date, end_time = monthly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())}")

                                otp = generate_otp()
                                proceed_payment = st.checkbox("I want to proceed with the payment, send the otp!")
                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    # Verify OTP
                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    while p: 
                                        if entered_otp == f"{otp}":
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                            """, (user_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                        elif entered_otp != f"{otp}":
                                            st.error("Invalid OTP. Please try again.")
                                            break

        
        elif selected_vehicle_type == "Four-Wheeler":
            st.sidebar.markdown("### Parking Area Descriptions:")
            cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea WHERE AreaID = 2 OR AreaID = 3")
            area = cursor.fetchall()
            df = pd.DataFrame(area, columns=["AreaID", "AreaName", "Location"])
            st.sidebar.dataframe(df)
            st.sidebar.markdown("## Parking Area IDs 👇 for four-wheelers")
            if default_area_id == 2:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 2 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                area_ids.remove(default_area_id)
                default_area_id = f"{default_area_id} (default)"
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= [default_area_id ] + area_ids)
            elif default_area_id == 3:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 2 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                area_ids.remove(default_area_id)
                default_area_id = f"{default_area_id} (default)"
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= [default_area_id ] + area_ids)
            else:
                cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 2 OR AreaID = 3")
                area_ids = cursor.fetchall()
                area_ids = [area[0] for area in area_ids]
                st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= area_ids)

            if st.session_state.selected_area_id:            
                # Display buttons for reservation types
                st.markdown("## Select Reservation Type:")
                hourly_button = st.button("Hourly Reservation")
                daily_button = st.button("Daily Reservation")
                monthly_button = st.button("Monthly Reservation")

                if hourly_button:
                    st.session_state.page = "hourly"
                elif daily_button:
                    st.session_state.page = "daily"
                elif monthly_button:
                    st.session_state.page = "monthly"

                if st.session_state.page == "hourly":
                    hours, reservation_date, end_time = hourly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(30.0, 85.0, 1700.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    # Verify OTP
                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    while p: 
                                        if entered_otp == f"{otp}":
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                            """, (user_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                            break
                                        elif entered_otp != f"{otp}":
                                            st.error("Invalid OTP. Please try again.")
                                            break

                    
                elif st.session_state.page == "daily":
                    hours, reservation_date, end_time = daily_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(30.0, 85.0, 1700.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    while p: 
                                        if entered_otp == f"{otp}":
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                            """, (user_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                        elif entered_otp != f"{otp}":
                                            st.error("Invalid OTP. Please try again.")
                                            break


                elif st.session_state.page == "monthly":
                    hours, reservation_date, end_time = monthly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(30.0, 85.0, 1700.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    p = st.checkbox("Proceed!!!")
                                    # Verify OTP
                                    while p: 
                                        if entered_otp == f"{otp}":
                                            cursor.execute("""
                                                INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                                VALUES (%s, %s, %s, %s)
                                            """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                            # Insert into Payments table
                                            cursor.execute("""
                                                INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                                VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                            """, (user_id, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, hours, reservation_date, datetime.now())))
                                            st.success("Payment successful!")
                                            st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")
                                        elif entered_otp != f"{otp}":
                                            st.error("Invalid OTP. Please try again.")
                                            break

        
        elif selected_vehicle_type == "Large-Vehicle":
            st.sidebar.markdown("### Parking Area Descriptions:")
            cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea WHERE AreaID = 3")
            area = cursor.fetchall()
            df = pd.DataFrame(area, columns=["AreaID", "AreaName", "Location"])
            st.sidebar.dataframe(df)
            st.sidebar.markdown("## Parking Area IDs 👇 for Large vehicles")
            cursor.execute("SELECT AreaID FROM ParkingArea WHERE AreaID = 3")
            area_ids = cursor.fetchall()
            area_ids = [area[0] for area in area_ids]
            st.session_state.selected_area_id = st.sidebar.selectbox("Select Parking Area ID:", options= area_ids)

            if st.session_state.selected_area_id:            
                # Display buttons for reservation types
                st.markdown("## Select Reservation Type:")
                hourly_button = st.button("Hourly Reservation")
                daily_button = st.button("Daily Reservation")
                monthly_button = st.button("Monthly Reservation")

                if hourly_button:
                    st.session_state.page = "hourly"
                elif daily_button:
                    st.session_state.page = "daily"
                elif monthly_button:
                    st.session_state.page = "monthly"

                if st.session_state.page == "hourly":
                    hours, reservation_date, end_time = hourly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    # Verify OTP
                                    while entered_otp == f"{otp}":
                                        cursor.execute("""
                                            INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                            VALUES (%s, %s, %s, %s)
                                        """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                        # Insert into Payments table
                                        cursor.execute("""
                                            INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                            VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                        """, (user_id, calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())))
                                        st.success("Payment successful!")
                                        st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")


                elif st.session_state.page == "daily":
                    hours, reservation_date, end_time = daily_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    # Verify OTP
                                    while entered_otp == f"{otp}":
                                        cursor.execute("""
                                            INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                            VALUES (%s, %s, %s, %s)
                                        """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                        # Insert into Payments table
                                        cursor.execute("""
                                            INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                            VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                        """, (user_id, calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())))
                                        connection.commit()
                                        st.success("Payment successful!")
                                        st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")


                elif st.session_state.page == "monthly":
                    hours, reservation_date, end_time = monthly_reservation(user_id, selected_vehicle_details, st.session_state.selected_area_id)
                    if hours is not None and reservation_date is not None and end_time is not None:
                        proceed_reservation = st.checkbox("I want to proceed with the reservation")
                        if proceed_reservation:
                            spaceid = get_available_space(st.session_state.selected_area_id, reservation_date, end_time)
                            cursor.execute("""
                                INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (user_id, st.session_state.selected_area_id[0], spaceid, vid, reservation_date, hours))

                            # Get the last inserted ReservationID
                            st.session_state.res_id = cursor.lastrowid

                            # Commit the changes to the database
                            connection.commit()

                            st.success("Reservation successful! You can proceed with the payment.")

                            st.markdown("### Please pay now.")
                            email = st.text_input("Enter your email:")
                            if is_valid_email(email):
                                st.markdown(f"### Amount to pay: ${calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())}")

                                # Display pay now button
                                if st.button("Pay Now"):
                                    # Send OTP to email
                                    otp = generate_otp()
                                    send_otp(email, otp)

                                    # Ask for OTP
                                    entered_otp = st.text_input("Enter the OTP sent to your email:", type="password", max_chars=6)

                                    # Verify OTP
                                    while entered_otp == f"{otp}":
                                        cursor.execute("""
                                            INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
                                            VALUES (%s, %s, %s, %s)
                                        """, (spaceid, st.session_state.res_id, reservation_date, end_time))
                                        # Insert into Payments table
                                        cursor.execute("""
                                            INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
                                            VALUES (%s, LAST_INSERT_ID(), %s, NOW())
                                        """, (user_id, calculate_amount_to_be_paid(35.0, 95.0, 1900.0, hours, reservation_date, datetime.now())))
                                        connection.commit()
                                        st.success("Payment successful!")
                                        st.markdown("### Go to the present reservations OR future reservations page to see your reservation details.")


    else:
        st.markdown("# Thanks for using our app!")

def get_user_reservations(user_id):
    try:
        # Fetch user's reservations with details
        cursor.execute("""
            SELECT r.ReservationID, r.ReservationDateTime, r.Duration, v.RegistrationNumber,
                   p.SpaceType, a.AreaName
            FROM Reservations r
            LEFT JOIN Vehicles v ON r.VehicleID = v.VehicleID
            LEFT JOIN ParkingSpaces p ON r.SpaceID = p.SpaceID
            LEFT JOIN ParkingArea a ON r.AreaID = a.AreaID
            WHERE r.UserID = %s
        """, (user_id,))

        user_reservations = cursor.fetchall()

        # Convert the result into a list of strings for display in Streamlit selectbox
        reservations_details = [
            f"Reservation ID: {reservation[0]}, Area: {reservation[5]}, Vehicle: {reservation[4]}, "
            f"Reservation Date: {reservation[1]}, Duration: {reservation[2]} hours"
            for reservation in user_reservations
        ]

        return reservations_details

    except Exception as e:
        st.error(f"Error fetching user reservations: {e}")
    
def cancel_reservation(user_id):
    st.markdown("## Your Reservations:")
    
    # Fetch user's reservations
    user_reservations = get_user_reservations(user_id)

    if not user_reservations:
        st.warning("You have no reservations to cancel.")
        return

    # Display user's reservations for selection
    selected_reservation = st.selectbox("Select a reservation to cancel:", user_reservations)

    # Print out the selected_reservation string for debugging
    st.write("Selected Reservation String:", selected_reservation)

    # Extract reservation details from the selected option
    selected_reservation_details = re.match(r"Reservation ID: (\d+), Area: (.+), Vehicle: (.+), Reservation Date: (.+), Duration: (.+)", selected_reservation)

    if selected_reservation_details:
        reservation_id = int(selected_reservation_details.group(1))

        st.info(f"Reservation selected for cancellation: {selected_reservation}")

        # Ask the user to confirm the cancellation
        confirm_cancel = st.checkbox("I want to cancel this reservation")
        if confirm_cancel:
            try:
                # Fetch reservation details
                cursor.execute("""
                    SELECT r.ReservationID, p.SpaceID, r.ReservationDateTime, r.Duration
                    FROM Reservations r
                    LEFT JOIN ParkingAvailability p ON r.ReservationID = p.ReservationID
                    WHERE r.ReservationID = %s
                """, (reservation_id,))

                reservation_data = cursor.fetchone()

                if reservation_data:
                    reservation_id, space_id, reservation_datetime, duration = reservation_data

                    # Delete from ParkingAvailability
                    cursor.execute("DELETE FROM ParkingAvailability WHERE ReservationID = %s", (reservation_id,))

                    # Delete from Payments
                    cursor.execute("DELETE FROM Payments WHERE ReservationID = %s", (reservation_id,))

                    # Delete from Reservations
                    cursor.execute("DELETE FROM Reservations WHERE ReservationID = %s", (reservation_id,))

                    # Commit the changes to the database
                    connection.commit()

                    st.success("Reservation canceled successfully!")
                else:
                    st.error("Error fetching reservation details.")
            except Exception as e:
                st.error(f"Error cancelling reservation: {e}")
        else:
            st.info("Reservation cancellation canceled.")
    else:
        st.error("Invalid reservation selection. Please try again.")

def delete_vehicle(user_id, vehicle_id):
    # Check if the vehicle exists for the given user
    cursor.execute("SELECT * FROM Vehicles WHERE UserID=%s AND VehicleID=%s", (user_id, vehicle_id))
    vehicle = cursor.fetchone()

    if vehicle:
        b = st.button("Delete Vehicle")
        if b:    
            # Delete associated records in Reservations table
            cursor.execute("DELETE FROM Reservations WHERE UserID=%s AND VehicleID=%s", (user_id, vehicle_id))

            # Delete the vehicle from the Vehicles table
            cursor.execute("DELETE FROM Vehicles WHERE UserID=%s AND VehicleID=%s", (user_id, vehicle_id))


            connection.commit()
            st.success("Vehicle and associated records deleted successfully!")
    else:
        st.warning("Vehicle not found, add vehicle first.")

def set_bg_hack(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()}) center center no-repeat;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_sidebar_bg_hack(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
        <style>
        .stSidebar {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()}) center center no-repeat;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def disable_radio_on_condition(condition):
        if condition:
            st.sidebar.radio("Select the required option to proceed!", options=["Signin / login", "Signup"], disabled=True)
        else:
            return st.sidebar.radio("Select the required option to proceed!", options=["Signin / login", "Signup"])

def admin_dashboard():
    st.subheader("Administrator Dashboard")

    # Define the tables
    tables = ['Users', 'Vehicles', 'Reservations', 'Payments', 'ParkingSpaces', 'ParkingArea', 'ParkingFee', 'ParkingAvailability']

    # Create a radio button to select the table
    selected_table = st.sidebar.radio("Select a table:", tables)

    # Display the selected table
    st.markdown(f"### {selected_table} Table")
    
    # Fetch data from the selected table
    cursor.execute(f"SELECT * FROM {selected_table}")
    data = cursor.fetchall()

    if data:
        # Display the data in a DataFrame
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info(f"No data in the {selected_table} table.")

def get_all_users():
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return users

def get_user_by_id(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID=%s", (user_id,))
    user = cursor.fetchone()
    return user

def users_table():
    st.markdown("## Users Table")
    cursor.execute("SELECT * FROM Users")
    data = cursor.fetchall()
    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Users table.")

    option = st.sidebar.radio("Select an action:", ["Add User", "Update User", "Delete User"])
    
    if option == "Add User":
        st.markdown("### Add User")
        name = st.text_input("Enter name")
        adn = st.checkbox("IS THE USER A ADMINISTRATOR?")
        if adn:
            adn = b'\x01'
        else:
            adn = b'\x00'
        email = st.text_input("Enter email")
        phone_number = st.text_input("Enter phone number")
        username = st.text_input("Enter username")
        password = st.text_input("Enter password", type="password")

        cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea")
        parking_areas = cursor.fetchall()
        parking_areas_df = pd.DataFrame(parking_areas, columns=["AreaID", "AreaName", "Location"])
        st.markdown("## Parking Area IDs:")
        st.dataframe(parking_areas_df)
        area_id = st.radio("Select your Area ID", options=[area[0] for area in parking_areas])
        
        if st.button("Add User"):
            if not is_valid_email(email):
                st.error("Invalid email address. Please enter a valid email.")
            elif not is_valid_phone(phone_number):
                st.error("Invalid phone number. Please enter a 10-digit phone number.")
            elif cursor.execute("SELECT * FROM Users WHERE Username=%s", (username,)):
                st.error("Username already exists. Please choose a different one.")
            elif not is_valid_password(password):
                st.error("Invalid password. Password must be at least 8 characters long and include at least 1 special character(-@$!%*?&), 1 capital letter, and 1 number.")
            else:
                # Insert the new user into the Users table
                cursor.execute("INSERT INTO Users (Name, Email, PhoneNumber, Username, Password, AreaID) VALUES (%s, %s, %s, %s, %s, %s)",
                            (name, email, phone_number, username, password, area_id))  # You may modify the AreaID as per your requirement
                connection.commit()
                st.success("User added successfully!")
                if st.button("Refresh"):
                    st.rerun()

    elif option == "Update User":
        st.markdown("### Edit User")
        users = get_all_users()

        if not users:
            st.warning("No users available for editing. Add a new user first.")
            return

        selected_user_id = st.selectbox("Select a user to edit:", [user[0] for user in users])
        selected_user = get_user_by_id(selected_user_id)

        if selected_user:
            st.markdown("## Update User Information:")
            new_adn = st.checkbox("IS THIS USER AN ADMINISTRATOR?", value=selected_user[1])
            if new_adn:
                new_adn = b'\x01'
            else:
                new_adn = b'\x00'
            new_name = st.text_input("Enter new name:", value=selected_user[2])
            new_email = st.text_input("Enter new email:", value=selected_user[3])
            new_phone_number = st.text_input("Enter new phone number:", value=selected_user[4])
            new_username = st.text_input("Enter new username:", value=selected_user[5])
            new_password = st.text_input("Enter new password:", value=selected_user[6])

            cursor.execute("SELECT AreaID, AreaName, Location FROM ParkingArea")
            parking_areas = cursor.fetchall()
            parking_areas_df = pd.DataFrame(parking_areas, columns=["AreaID", "AreaName", "Location"])
            st.markdown("## Parking Area IDs:")
            st.dataframe(parking_areas_df)
            new_area_id = st.radio("Select your Area ID", options=[area[0] for area in parking_areas])

            if st.button("Update User"):
                if not is_valid_email(new_email):
                    st.error("Invalid email address. Please enter a valid email.")
                elif not is_valid_phone(new_phone_number):
                    st.error("Invalid phone number. Please enter a 10-digit phone number.")
                elif not is_valid_password(new_password):
                    st.error("Invalid password. Password must be at least 8 characters long and include at least 1 special character(-@$!%*?&), 1 capital letter, and 1 number.")
                elif cursor.execute("SELECT * FROM Users WHERE Username=%s AND UserID != %s", (new_username, selected_user_id)):
                    st.error("Username already exists. Please choose a different one.")
                else:
                    # Update the user information in the Users table
                    cursor.execute("UPDATE Users SET Adn=%s, Name=%s, Email=%s, PhoneNumber=%s, Username=%s, Password=%s, AreaID=%s WHERE UserID=%s",
                                (new_adn, new_name, new_email, new_phone_number, new_username, new_password, new_area_id, selected_user_id))
                    connection.commit()
                    st.success("User information updated successfully!")
                    if st.button("Refresh"):
                        st.rerun()

        else:
            st.warning("No user selected for editing. Add a new user first.")

    elif option == "Delete User":
        st.subheader("Delete User")
        users = get_all_users()

        if not users:
            st.warning("No users available for deletion. Add a new user first.")
            return

        selected_user_id = st.selectbox("Select a user to Delete:", [user[0] for user in users])
        selected_user = get_user_by_id(selected_user_id)

        if selected_user:
            st.markdown("## User Details:")
            st.markdown(f"### **User ID:** {selected_user[0]}")
            if selected_user[1] == b'\x01':
                st.markdown(f"### **Admin:** Yes")
            st.markdown(f"### **Name:** {selected_user[2]}")
            st.markdown(f"### **Email:** {selected_user[3]}")
            st.markdown(f"### **Phone Number:** {selected_user[4]}")
            st.markdown(f"### **Username:** {selected_user[5]}")
            st.markdown(f"### **Password:** {selected_user[6]}")
            st.markdown(f"### **Area ID:** {selected_user[7]}")

            confirmation = st.checkbox("I confirm that I want to delete this user.")
            if confirmation and st.button("Delete User"):
                # Delete the user from the Users table
                cursor.execute("DELETE FROM Users WHERE UserID=%s", (selected_user_id,))
                connection.commit()
                st.success("User deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No user selected for deletion. Add a new user first.")

def vehicles_table():
    st.markdown("## Vehicles Table")
    cursor.execute("SELECT Vehicles.*, Users.Name FROM Vehicles JOIN Users ON Vehicles.UserID = Users.UserID")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Vehicles table.")

    option = st.sidebar.radio("Select an action:", ["Add Vehicle", "Update Vehicle", "Delete Vehicle"])
    
    if option == "Add Vehicle":
        st.markdown("### Add Vehicle")
        user_id = st.selectbox("Select user:", [user[0] for user in get_all_users()])
        vehicle_type = st.selectbox("Edit Vehicle Type", ["Two-Wheeler", "Four-Wheeler", "Large Vehicle"])
        registration_number = st.text_input("Enter registration number:", max_chars=10)
        color = st.text_input("Enter vehicle color:")

        if st.button("Add Vehicle"):
            # Check if the user exists
            if not get_user_by_id(user_id):
                st.error("User does not exist. Please enter a valid user ID.")
            else:
                # Insert the new vehicle into the Vehicles table
                cursor.execute("INSERT INTO Vehicles (UserID, VehicleType, RegistrationNumber, Color) VALUES (%s, %s, %s, %s)",
                            (user_id, vehicle_type, registration_number, color))
                connection.commit()
                st.success("Vehicle added successfully!")
                if st.button("Refresh"):
                    st.rerun()

    elif option == "Update Vehicle":
        st.markdown("### Edit Vehicle")
        cursor.execute("SELECT * FROM Vehicles")
        vehicles = cursor.fetchall()

        if not vehicles:
            st.warning("No vehicles available for editing. Add a new vehicle first.")
            return

        selected_vehicle_id = st.selectbox("Select a vehicle to edit:", [vehicle[0] for vehicle in vehicles])
        cursor.execute("SELECT * FROM Vehicles WHERE VehicleID=%s", (selected_vehicle_id,))
        selected_vehicle = cursor.fetchone()

        if selected_vehicle:
            st.markdown("## Update Vehicle Information:")
            new_user_id = st.text_input("Enter the user ID:", value=selected_vehicle[1])
            new_vehicle_type = st.text_input("Enter new vehicle type:", value=selected_vehicle[2])
            new_registration_number = st.text_input("Enter new registration number:", value=selected_vehicle[3], max_chars=10)
            new_color = st.text_input("Enter new vehicle color:", value=selected_vehicle[4])

            if st.button("Update Vehicle"):
                # Check if the user exists
                if not get_user_by_id(new_user_id):
                    st.error("User does not exist. Please enter a valid user ID.")
                else:
                    # Update the vehicle information in the Vehicles table
                    cursor.execute("UPDATE Vehicles SET UserID=%s, VehicleType=%s, RegistrationNumber=%s, Color=%s WHERE VehicleID=%s",
                                (new_user_id, new_vehicle_type, new_registration_number, new_color, selected_vehicle_id))
                    connection.commit()
                    st.success("Vehicle information updated successfully!")
                    if st.button("Refresh"):
                        st.rerun()

        else:
            st.warning("No vehicle selected for editing. Add a new vehicle first.")

    elif option == "Delete Vehicle":
        st.subheader("Delete Vehicle")
        cursor.execute("SELECT * FROM Vehicles")
        vehicles = cursor.fetchall()

        if not vehicles:
            st.warning("No vehicles available for deletion. Add a new vehicle first.")
            return

        selected_vehicle_id = st.selectbox("Select a vehicle to edit:", [vehicle[0] for vehicle in vehicles])
        cursor.execute("SELECT Vehicles.*, Users.Name FROM Vehicles JOIN Users ON Vehicles.UserID = Users.UserID WHERE VehicleID=%s", (selected_vehicle_id,))
        selected_vehicle = cursor.fetchone()

        if selected_vehicle:
            st.markdown("## Vehicle Details:")
            st.markdown(f"### **Vehicle ID:** {selected_vehicle[0]}")
            st.markdown(f"### **User ID:** {selected_vehicle[1]}")
            st.markdown(f"### **Vehicle Type:** {selected_vehicle[2]}")
            st.markdown(f"### **Registration Number:** {selected_vehicle[3]}")
            st.markdown(f"### **Color:** {selected_vehicle[4]}")
            st.markdown(f"### **User's Name:** {selected_vehicle[5]}")

            confirmation = st.checkbox("I confirm that I want to delete this vehicle.")
            if confirmation and st.button("Delete Vehicle"):
                # Delete the vehicle from the Vehicles table
                cursor.execute("DELETE FROM Vehicles WHERE VehicleID=%s", (selected_vehicle_id,))
                connection.commit()
                st.success("Vehicle deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No vehicle selected for deletion. Add a new vehicle first.")

def get_all_areas():
    cursor.execute("SELECT * FROM ParkingArea")
    return cursor.fetchall()

def get_all_spaces_by_area(area_id):
    cursor.execute("SELECT * FROM ParkingSpaces WHERE AreaID=%s", (area_id,))
    return cursor.fetchall()

def get_all_vehicles_by_user(user_id):
    cursor.execute("SELECT * FROM Vehicles WHERE UserID=%s", (user_id,))
    return cursor.fetchall()

def get_area_by_id(area_id):
    cursor.execute("SELECT * FROM ParkingArea WHERE AreaID=%s", (area_id,))
    return cursor.fetchone()

def is_space_available(space_id, reservation_datetime, duration):
    cursor.execute("SELECT * FROM Reservations WHERE SpaceID=%s AND ReservationDateTime=%s AND ReservationDuration=%s",
                   (space_id, reservation_datetime, duration))
    return cursor.fetchone() is None

def mark_space_unavailable(space_id, reservation_datetime, duration):
    cursor.execute("INSERT INTO Reservations (SpaceID, ReservationDateTime, ReservationDuration) VALUES (%s, %s, %s)",
                   (space_id, reservation_datetime, duration))
    connection.commit()

def get_index_of_user(user_id):
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    for i, user in enumerate(users):
        if user[0] == user_id:
            return i
def get_index_of_space(space_id):
    cursor.execute("SELECT * FROM ParkingSpaces")
    spaces = cursor.fetchall()
    for i, space in enumerate(spaces):
        if space[0] == space_id:
            return i
def get_index_of_vehicle(vehicle_id):
    cursor.execute("SELECT * FROM Vehicles")
    vehicles = cursor.fetchall()
    for i, vehicle in enumerate(vehicles):
        if vehicle[0] == vehicle_id:
            return i

def get_index_of_area(area_id):
    cursor.execute("SELECT * FROM ParkingArea")
    areas = cursor.fetchall()
    for i, area in enumerate(areas):
        if area[0] == area_id:
            return i

def mark_space_available(space_id, reservation_datetime, duration):
    # Calculate the end datetime of the reservation
    end_datetime = reservation_datetime + timedelta(hours=duration)

    # Update the availability status of the parking space
    cursor.execute("UPDATE ParkingSpaces SET IsAvailable = TRUE WHERE SpaceID = %s AND IsAvailable = FALSE "
                   "AND ReservationEndDateTime = %s", (space_id, end_datetime))
    connection.commit()

def reservations_table():
    st.markdown("## Reservations Table")
    cursor.execute("SELECT Reservations.*, Users.Name, Vehicles.RegistrationNumber, ParkingSpaces.SpaceType, ParkingArea.AreaName FROM Reservations "
                   "JOIN Users ON Reservations.UserID = Users.UserID "
                   "JOIN Vehicles ON Reservations.VehicleID = Vehicles.VehicleID "
                   "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                   "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Reservations table.")

    option = st.sidebar.radio("Select an action:", ["Add Reservation", "Update Reservation", "Delete Reservation"])

    if option == "Add Reservation":
        st.markdown("### Add Reservation")
        user_id = st.selectbox("Select user:", [user[0] for user in get_all_users()])
        area_id = st.selectbox("Select parking area:", [area[0] for area in get_all_areas()])
        space_id = st.selectbox("Select parking space:", [space[0] for space in get_all_spaces_by_area(area_id)])
        vehicle_id = st.selectbox("Select vehicle:", [vehicle[0] for vehicle in get_all_vehicles_by_user(user_id)])
        reservation_date = st.date_input("Select reservation date:")
        reservation_time = st.time_input("Select reservation time:")
        duration = st.number_input("Enter reservation duration (in hours):", min_value=1)

        # Convert reservation date and time to datetime
        reservation_datetime = datetime.combine(reservation_date, reservation_time)

        if st.button("Add Reservation"):
            # Check if the user exists
            if not get_user_by_id(user_id):
                st.error("User does not exist. Please enter a valid user ID.")
            # Check if the parking area exists
            elif not get_area_by_id(area_id):
                st.error("Parking area does not exist. Please enter a valid area ID.")
            # Check if the parking space is available
            elif not is_space_available(space_id, reservation_datetime, duration):
                st.error("Selected space is not available for the specified duration. Choose another space or time.")
            else:
                # Insert the new reservation into the Reservations table
                cursor.execute("INSERT INTO Reservations (UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration) "
                               "VALUES (%s, %s, %s, %s, %s, %s)",
                               (user_id, area_id, space_id, vehicle_id, reservation_datetime, duration))
                connection.commit()
                # Mark the reserved space as unavailable during the reservation period
                mark_space_unavailable(space_id, reservation_datetime, duration)
                st.success("Reservation added successfully!")
                if st.button("Refresh"):
                    st.rerun()

    elif option == "Update Reservation":
        st.markdown("### Update Reservation")
        cursor.execute("SELECT * FROM Reservations")
        reservations = cursor.fetchall()

        if not reservations:
            st.warning("No reservations available for editing. Add a new reservation first.")
            return

        selected_reservation_id = st.selectbox("Select a reservation to edit:", [reservation[0] for reservation in reservations])
        cursor.execute("SELECT * FROM Reservations WHERE ReservationID=%s", (selected_reservation_id,))
        selected_reservation = cursor.fetchone()

        if selected_reservation:
            st.markdown("## Update Reservation Information:")
            new_user_id = st.selectbox("Select user:", [user[0] for user in get_all_users()], index=get_index_of_user(selected_reservation[1]))
            new_area_id = st.selectbox("Select parking area:", [area[0] for area in get_all_areas()], index=get_index_of_area(selected_reservation[2]))
            new_space_id = st.selectbox("Select parking space:", [space[0] for space in get_all_spaces_by_area(new_area_id)],
                                        index=get_index_of_space(selected_reservation[3]))
            new_vehicle_id = st.selectbox("Select vehicle:", [vehicle[0] for vehicle in get_all_vehicles_by_user(new_user_id)],
                                          index=get_index_of_vehicle(selected_reservation[4]))
            new_reservation_date = st.date_input("Select reservation date:")
            new_reservation_time = st.time_input("Select reservation time:")
            new_duration = st.number_input("Enter new reservation duration (in hours):", value=selected_reservation[6], min_value=1)

            new_reservation_datetime = datetime.combine(new_reservation_date, new_reservation_time)

            if st.button("Update Reservation"):
                # Check if the user exists
                if not get_user_by_id(new_user_id):
                    st.error("User does not exist. Please enter a valid user ID.")
                # Check if the parking area exists
                elif not get_area_by_id(new_area_id):
                    st.error("Parking area does not exist. Please enter a valid area ID.")
                # Check if the parking space is available
                elif not is_space_available(new_space_id, new_reservation_datetime, new_duration):
                    st.error("Selected space is not available for the specified duration. Choose another space or time.")
                else:
                    # Mark the previously reserved space as available
                    mark_space_available(selected_reservation[3], selected_reservation[5], selected_reservation[6])
                    # Update the reservation information in the Reservations table
                    cursor.execute("UPDATE Reservations SET UserID=%s, AreaID=%s, SpaceID=%s, VehicleID=%s, ReservationDateTime=%s, Duration=%s "
                                   "WHERE ReservationID=%s",
                                   (new_user_id, new_area_id, new_space_id, new_vehicle_id, new_reservation_datetime, new_duration, selected_reservation_id))
                    connection.commit()
                    # Mark the updated space as unavailable during the updated reservation period
                    mark_space_unavailable(new_space_id, new_reservation_datetime, new_duration)
                    st.success("Reservation information updated successfully!")
                    if st.button("Refresh"):
                        st.rerun()

        else:
            st.warning("No reservation selected for editing. Add a new reservation first.")

    elif option == "Delete Reservation":
        st.subheader("Delete Reservation")
        cursor.execute("SELECT Reservations.*, Users.Name, Vehicles.RegistrationNumber, ParkingSpaces.SpaceType, ParkingArea.AreaName "
                       "FROM Reservations "
                       "JOIN Users ON Reservations.UserID = Users.UserID "
                       "JOIN Vehicles ON Reservations.VehicleID = Vehicles.VehicleID "
                       "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                       "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID")
        reservations = cursor.fetchall()

        if not reservations:
            st.warning("No reservations available for deletion. Add a new reservation first.")
            return

        selected_reservation_id = st.selectbox("Select a reservation to delete:", [reservation[0] for reservation in reservations])
        cursor.execute("SELECT Reservations.*, Users.Name, Vehicles.RegistrationNumber, ParkingSpaces.SpaceType, ParkingArea.AreaName "
                       "FROM Reservations "
                       "JOIN Users ON Reservations.UserID = Users.UserID "
                       "JOIN Vehicles ON Reservations.VehicleID = Vehicles.VehicleID "
                       "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                       "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID "
                       "WHERE ReservationID=%s", (selected_reservation_id,))
        selected_reservation = cursor.fetchone()

        if selected_reservation:
            st.markdown("## Reservation Details:")
            st.markdown(f"### **Reservation ID:** {selected_reservation[0]}")
            st.markdown(f"### **User ID:** {selected_reservation[1]}")
            st.markdown(f"### **User's Name:** {selected_reservation[7]}")
            st.markdown(f"### **Vehicle ID:** {selected_reservation[4]}")
            st.markdown(f"### **Vehicle Registration Number:** {selected_reservation[8]}")
            st.markdown(f"### **Parking Area ID:** {selected_reservation[2]}")
            st.markdown(f"### **Parking Area Name:** {selected_reservation[10]}")
            st.markdown(f"### **Parking Space ID:** {selected_reservation[3]}")
            st.markdown(f"### **Parking Space Type:** {selected_reservation[9]}")
            st.markdown(f"### **Reservation Date and Time:** {selected_reservation[5]}")
            st.markdown(f"### **Duration:** {selected_reservation[6]} hours")

            confirmation = st.checkbox("I confirm that I want to delete this reservation.")
            if confirmation and st.button("Delete Reservation"):
                # Mark the reserved space as available
                mark_space_available(selected_reservation[3], selected_reservation[5], selected_reservation[6])
                # Delete the reservation from the Reservations table
                cursor.execute("DELETE FROM Reservations WHERE ReservationID=%s", (selected_reservation_id,))
                connection.commit()
                st.success("Reservation deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No reservation selected for deletion. Add a new reservation first.")

def get_all_reservations():
    cursor.execute("SELECT ReservationID FROM Reservations")
    return cursor.fetchall()

def get_reservation_by_id(reservation_id):
    cursor.execute("SELECT * FROM Reservations WHERE ReservationID=%s", (reservation_id,))
    return cursor.fetchone()

def get_index_of_reservation(reservation_id):
    for i, reservation in enumerate(get_all_reservations()):
        if reservation[0] == reservation_id:
            return i
    return None

def payments_table():
    st.markdown("## Payments Table")
    cursor.execute("SELECT Payments.*, Users.Name, Reservations.ReservationDateTime, Reservations.Duration, ParkingSpaces.SpaceType, ParkingArea.AreaName "
                   "FROM Payments "
                   "JOIN Reservations ON Payments.ReservationID = Reservations.ReservationID "
                   "JOIN Users ON Reservations.UserID = Users.UserID "
                   "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                   "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Payments table.")

    option = st.sidebar.radio("Select an action:", ["Add Payment", "Update Payment", "Delete Payment"])

    if option == "Add Payment":
        st.markdown("### Add Payment")
        reservation_id = st.selectbox("Select reservation:", [reservation[0] for reservation in get_all_reservations()])
        payment_datetime = st.datetime_input("Select payment date and time:")
        amount = st.number_input("Enter payment amount:")
        payment_method = st.selectbox("Select payment method:", ["Credit Card", "Debit Card", "Cash"])

        if st.button("Add Payment"):
            # Check if the reservation exists
            if not get_reservation_by_id(reservation_id):
                st.error("Reservation does not exist. Please enter a valid reservation ID.")
            else:
                # Insert the new payment into the Payments table
                cursor.execute("INSERT INTO Payments (ReservationID, PaymentDateTime, Amount, PaymentMethod) "
                               "VALUES (%s, %s, %s, %s)",
                               (reservation_id, payment_datetime, amount, payment_method))
                connection.commit()
                st.success("Payment added successfully!")
                if st.button("Refresh"):
                    st.rerun()

    elif option == "Update Payment":
        st.markdown("### Update Payment")
        cursor.execute("SELECT * FROM Payments")
        payments = cursor.fetchall()

        if not payments:
            st.warning("No payments available for editing. Add a new payment first.")
            return

        selected_payment_id = st.selectbox("Select a payment to edit:", [payment[0] for payment in payments])
        cursor.execute("SELECT * FROM Payments WHERE PaymentID=%s", (selected_payment_id,))
        selected_payment = cursor.fetchone()

        if selected_payment:
            st.markdown("## Update Payment Information:")
            new_reservation_id = st.selectbox("Select reservation:", [reservation[0] for reservation in get_all_reservations()],
                                              index=get_index_of_reservation(selected_payment[1]))
            new_payment_datetime = st.datetime_input("Select new payment date and time:", value=selected_payment[2])
            new_amount = st.number_input("Enter new payment amount:", value=selected_payment[3])
            new_payment_method = st.selectbox("Select new payment method:", ["Credit Card", "Debit Card", "Cash"],
                                              index=["Credit Card", "Debit Card", "Cash"].index(selected_payment[4]))

            if st.button("Update Payment"):
                # Check if the reservation exists
                if not get_reservation_by_id(new_reservation_id):
                    st.error("Reservation does not exist. Please enter a valid reservation ID.")
                else:
                    # Update the payment information in the Payments table
                    cursor.execute("UPDATE Payments SET ReservationID=%s, PaymentDateTime=%s, Amount=%s, PaymentMethod=%s WHERE PaymentID=%s",
                                   (new_reservation_id, new_payment_datetime, new_amount, new_payment_method, selected_payment_id))
                    connection.commit()
                    st.success("Payment information updated successfully!")
                    if st.button("Refresh"):
                        st.rerun()

        else:
            st.warning("No payment selected for editing. Add a new payment first.")

    elif option == "Delete Payment":
        st.subheader("Delete Payment")
        cursor.execute("SELECT Payments.*, Users.Name, Reservations.ReservationDateTime, Reservations.Duration, ParkingSpaces.SpaceType, ParkingArea.AreaName "
                       "FROM Payments "
                       "JOIN Reservations ON Payments.ReservationID = Reservations.ReservationID "
                       "JOIN Users ON Reservations.UserID = Users.UserID "
                       "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                       "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID")
        payments = cursor.fetchall()

        if not payments:
            st.warning("No payments available for deletion. Add a new payment first.")
            return

        selected_payment_id = st.selectbox("Select a payment to delete:", [payment[0] for payment in payments])
        cursor.execute("SELECT Payments.*, Users.Name, Reservations.ReservationDateTime, Reservations.Duration, ParkingSpaces.SpaceType, ParkingArea.AreaName "
                       "FROM Payments "
                       "JOIN Reservations ON Payments.ReservationID = Reservations.ReservationID "
                       "JOIN Users ON Reservations.UserID = Users.UserID "
                       "JOIN ParkingSpaces ON Reservations.SpaceID = ParkingSpaces.SpaceID "
                       "JOIN ParkingArea ON Reservations.AreaID = ParkingArea.AreaID "
                       "WHERE PaymentID=%s", (selected_payment_id,))
        selected_payment = cursor.fetchone()

        if selected_payment:
            st.markdown("## Payment Details:")
            st.markdown(f"### **Payment ID:** {selected_payment[0]}")
            st.markdown(f"### **Reservation ID:** {selected_payment[1]}")
            st.markdown(f"### **User ID:** {selected_payment[7]}")
            st.markdown(f"### **User's Name:** {selected_payment[8]}")
            st.markdown(f"### **Reservation Date and Time:** {selected_payment[11]}")
            st.markdown(f"### **Duration:** {selected_payment[12]} hours")
            st.markdown(f"### **Parking Space Type:** {selected_payment[14]}")
            st.markdown(f"### **Parking Area Name:** {selected_payment[15]}")
            st.markdown(f"### **Payment Date and Time:** {selected_payment[2]}")
            st.markdown(f"### **Amount:** {selected_payment[3]}")
            st.markdown(f"### **Payment Method:** {selected_payment[4]}")

            confirmation = st.checkbox("I confirm that I want to delete this payment.")
            if confirmation and st.button("Delete Payment"):
                # Delete the payment from the Payments table
                cursor.execute("DELETE FROM Payments WHERE PaymentID=%s", (selected_payment_id,))
                connection.commit()
                st.success("Payment deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No payment selected for deletion. Add a new payment first.")

def parking_spaces_table():
    st.markdown("## Parking Spaces Table")
    cursor.execute("SELECT ParkingSpaces.*, ParkingArea.AreaName FROM ParkingSpaces "
                   "JOIN ParkingArea ON ParkingSpaces.AreaID = ParkingArea.AreaID")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Parking Spaces table.")

    option = st.sidebar.radio("Select an action:", ["Add Parking Space", "Update Parking Space", "Delete Parking Space"])

    if option == "Add Parking Space":
        st.markdown("### Add Parking Space")
        area_id = st.selectbox("Select parking area:", [area[0] for area in get_all_areas()])
        space_type = st.selectbox("Select parking space type:", ["Two-Wheeler", "Four-Wheeler", "Large Vehicle"])

        if st.button("Add Parking Space"):
            # Check if the parking area exists
            if not get_index_of_area(area_id):
                st.error("Parking area does not exist. Please enter a valid area ID.")
            else:
                # Insert the new parking space into the ParkingSpaces table
                cursor.execute("INSERT INTO ParkingSpaces (AreaID, SpaceType) VALUES (%s, %s)",
                               (area_id, space_type))
                connection.commit()
                st.success("Parking space added successfully!")
                if st.button("Refresh"):
                    st.rerun()

    elif option == "Update Parking Space":
        st.markdown("### Update Parking Space")
        cursor.execute("SELECT * FROM ParkingSpaces")
        parking_spaces = cursor.fetchall()

        if not parking_spaces:
            st.warning("No parking spaces available for editing. Add a new parking space first.")
            return

        selected_space_id = st.selectbox("Select a parking space to edit:", [space[0] for space in parking_spaces])
        cursor.execute("SELECT * FROM ParkingSpaces WHERE SpaceID=%s", (selected_space_id,))
        selected_space = cursor.fetchone()

        if selected_space:
            st.markdown("## Update Parking Space Information:")
            new_area_id = st.selectbox("Select new parking area:", [area[0] for area in get_all_areas()],
                                       index=[area[0] for area in get_all_areas()].index(selected_space[0]))
            new_space_type = st.selectbox("Select new parking space type:", ["Two-Wheeler", "Four-Wheeler", "Large Vehicle"],
                                          index=["Two-Wheeler", "Four-Wheeler", "Large Vehicle"].index(selected_space[1]))

            if st.button("Update Parking Space"):
                # Check if the parking area exists
                if not get_index_of_area(new_area_id):
                    st.error("Parking area does not exist. Please enter a valid area ID.")
                else:
                    # Update the parking space information in the ParkingSpaces table
                    cursor.execute("UPDATE ParkingSpaces SET AreaID=%s, SpaceType=%s WHERE SpaceID=%s",
                                   (new_area_id, new_space_type, selected_space_id))
                    connection.commit()
                    st.success("Parking space information updated successfully!")
                    if st.button("Refresh"):
                        st.rerun()

        else:
            st.warning("No parking space selected for editing. Add a new parking space first.")

    elif option == "Delete Parking Space":
        st.subheader("Delete Parking Space")
        cursor.execute("SELECT ParkingSpaces.*, ParkingArea.AreaName FROM ParkingSpaces "
                       "JOIN ParkingArea ON ParkingSpaces.AreaID = ParkingArea.AreaID")
        parking_spaces = cursor.fetchall()

        if not parking_spaces:
            st.warning("No parking spaces available for deletion. Add a new parking space first.")
            return

        selected_space_id = st.selectbox("Select a parking space to delete:", [space[0] for space in parking_spaces])
        cursor.execute("SELECT ParkingSpaces.*, ParkingArea.AreaName FROM ParkingSpaces "
                       "JOIN ParkingArea ON ParkingSpaces.AreaID = ParkingArea.AreaID "
                       "WHERE SpaceID=%s", (selected_space_id,))
        selected_space = cursor.fetchone()

        if selected_space:
            st.markdown("## Parking Space Details:")
            st.markdown(f"### **Space ID:** {selected_space[0]}")
            st.markdown(f"### **Area ID:** {selected_space[1]}")
            st.markdown(f"### **Area Name:** {selected_space[3]}")
            st.markdown(f"### **Space Type:** {selected_space[2]}")

            confirmation = st.checkbox("I confirm that I want to delete this parking space.")
            if confirmation and st.button("Delete Parking Space"):
                # Delete the parking space from the ParkingSpaces table
                cursor.execute("DELETE FROM ParkingSpaces WHERE SpaceID=%s", (selected_space_id,))
                connection.commit()
                st.success("Parking space deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking space selected for deletion. Add a new parking space first.")

def parking_area_table():
    st.markdown("## Parking Area Table")
    cursor.execute("SELECT * FROM ParkingArea")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Parking Area table.")

    option = st.sidebar.radio("Select an action:", ["Add Parking Area", "Update Parking Area", "Delete Parking Area"])

    if option == "Add Parking Area":
        st.markdown("### Add Parking Area")
        area_name = st.text_input("Enter parking area name:")
        location = st.text_input("Enter parking area location:")
        total_spaces = st.number_input("Enter total parking spaces:", min_value=1, step=1)

        if st.button("Add Parking Area"):
            # Insert the new parking area into the ParkingArea table
            cursor.execute("INSERT INTO ParkingArea (AreaName, Location, TotalSpaces) VALUES (%s, %s, %s)",
                           (area_name, location, total_spaces))
            connection.commit()
            st.success("Parking area added successfully!")
            if st.button("Refresh"):
                st.rerun()

    elif option == "Update Parking Area":
        st.markdown("### Update Parking Area")
        cursor.execute("SELECT * FROM ParkingArea")
        parking_areas = cursor.fetchall()

        if not parking_areas:
            st.warning("No parking areas available for editing. Add a new parking area first.")
            return

        selected_area_id = st.selectbox("Select a parking area to edit:", [area[0] for area in parking_areas])
        cursor.execute("SELECT * FROM ParkingArea WHERE AreaID=%s", (selected_area_id,))
        selected_area = cursor.fetchone()

        if selected_area:
            st.markdown("## Update Parking Area Information:")
            new_area_name = st.text_input("Enter new parking area name:", value=selected_area[1])
            new_location = st.text_input("Enter new parking area location:", value=selected_area[2])
            new_total_spaces = st.number_input("Enter new total parking spaces:", value=selected_area[3], min_value=1, step=1)

            if st.button("Update Parking Area"):
                # Update the parking area information in the ParkingArea table
                cursor.execute("UPDATE ParkingArea SET AreaName=%s, Location=%s, TotalSpaces=%s WHERE AreaID=%s",
                               (new_area_name, new_location, new_total_spaces, selected_area_id))
                connection.commit()
                st.success("Parking area information updated successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking area selected for editing. Add a new parking area first.")

    elif option == "Delete Parking Area":
        st.subheader("Delete Parking Area")
        cursor.execute("SELECT * FROM ParkingArea")
        parking_areas = cursor.fetchall()

        if not parking_areas:
            st.warning("No parking areas available for deletion. Add a new parking area first.")
            return

        selected_area_id = st.selectbox("Select a parking area to delete:", [area[0] for area in parking_areas])
        cursor.execute("SELECT * FROM ParkingArea WHERE AreaID=%s", (selected_area_id,))
        selected_area = cursor.fetchone()

        if selected_area:
            st.markdown("## Parking Area Details:")
            st.markdown(f"### **Area ID:** {selected_area[0]}")
            st.markdown(f"### **Area Name:** {selected_area[1]}")
            st.markdown(f"### **Location:** {selected_area[2]}")
            st.markdown(f"### **Total Spaces:** {selected_area[3]}")

            confirmation = st.checkbox("I confirm that I want to delete this parking area.")
            if confirmation and st.button("Delete Parking Area"):
                # Delete the parking area from the ParkingArea table
                cursor.execute("DELETE FROM ParkingArea WHERE AreaID=%s", (selected_area_id,))
                connection.commit()
                st.success("Parking area deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking area selected for deletion. Add a new parking area first.")

def parking_fee_table():
    st.markdown("## Parking Fee Table")
    cursor.execute("SELECT * FROM ParkingFee")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Parking Fee table.")

    option = st.sidebar.radio("Select an action:", ["Add Parking Fee", "Update Parking Fee", "Delete Parking Fee"])

    if option == "Add Parking Fee":
        st.markdown("### Add Parking Fee")
        space_type = st.text_input("Select space type:")
        hourly_rate = st.number_input("Enter hourly rate:", min_value=0.0, step=1.0)
        daily_rate = st.number_input("Enter daily rate:", min_value=0.0, step=1.0)
        monthly_rate = st.number_input("Enter monthly rate:", min_value=0.0, step=1.0)

        if st.button("Add Parking Fee"):
            # Insert the new parking fee into the ParkingFee table
            cursor.execute("INSERT INTO ParkingFee (SpaceType, HourlyRate, DailyRate, MonthlyRate) VALUES (%s, %s, %s, %s)",
                           (space_type, hourly_rate, daily_rate, monthly_rate))
            connection.commit()
            st.success("Parking fee added successfully!")
            if st.button("Refresh"):
                st.rerun()

    elif option == "Update Parking Fee":
        st.markdown("### Update Parking Fee")
        cursor.execute("SELECT * FROM ParkingFee")
        parking_fees = cursor.fetchall()

        if not parking_fees:
            st.warning("No parking fees available for editing. Add a new parking fee first.")
            return

        selected_fee_id = st.selectbox("Select a parking fee to edit:", [fee[0] for fee in parking_fees])
        cursor.execute("SELECT * FROM ParkingFee WHERE FeeID=%s", (selected_fee_id,))
        selected_fee = cursor.fetchone()

        if selected_fee:
            st.markdown("## Update Parking Fee Information:")
            new_space_type = st.text_input("Enter new space type:", value=selected_fee[1])
            new_hourly_rate = st.number_input("Enter new hourly rate:", value=float(selected_fee[2]), min_value=0.0, step=1.0)
            new_daily_rate = st.number_input("Enter new daily rate:", value=float(selected_fee[3]), min_value=0.0, step=1.0)
            new_monthly_rate = st.number_input("Enter new monthly rate:", value=float(selected_fee[4]), min_value=0.0, step=1.0)

            if st.button("Update Parking Fee"):
                # Update the parking fee information in the ParkingFee table
                cursor.execute("UPDATE ParkingFee SET SpaceType=%s, HourlyRate=%s, DailyRate=%s, MonthlyRate=%s WHERE FeeID=%s",
                               (new_space_type, new_hourly_rate, new_daily_rate, new_monthly_rate, selected_fee_id))
                connection.commit()
                st.success("Parking fee information updated successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking fee selected for editing. Add a new parking fee first.")

    elif option == "Delete Parking Fee":
        st.subheader("Delete Parking Fee")
        cursor.execute("SELECT * FROM ParkingFee")
        parking_fees = cursor.fetchall()

        if not parking_fees:
            st.warning("No parking fees available for deletion. Add a new parking fee first.")
            return

        selected_fee_id = st.selectbox("Select a parking fee to delete:", [fee[0] for fee in parking_fees])
        cursor.execute("SELECT * FROM ParkingFee WHERE FeeID=%s", (selected_fee_id,))
        selected_fee = cursor.fetchone()

        if selected_fee:
            st.markdown("## Parking Fee Details:")
            st.markdown(f"### **Fee ID:** {selected_fee[0]}")
            st.markdown(f"### **Space Type:** {selected_fee[1]}")
            st.markdown(f"### **Hourly Rate:** {selected_fee[2]}")
            st.markdown(f"### **Daily Rate:** {selected_fee[3]}")
            st.markdown(f"### **Monthly Rate:** {selected_fee[4]}")

            confirmation = st.checkbox("I confirm that I want to delete this parking fee.")
            if confirmation and st.button("Delete Parking Fee"):
                # Delete the parking fee from the ParkingFee table
                cursor.execute("DELETE FROM ParkingFee WHERE FeeID=%s", (selected_fee_id,))
                connection.commit()
                st.success("Parking fee deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking fee selected for deletion. Add a new parking fee first.")

def get_all_parking_spaces():
    cursor.execute("SELECT * FROM ParkingSpaces")
    return cursor.fetchall()

def get_index_by_value(list, value):
    for i, item in enumerate(list):
        if item[0] == value:
            return i
    return None

def parking_availability_table():
    st.markdown("## Parking Availability Table")
    cursor.execute("SELECT * FROM ParkingAvailability")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.dataframe(df)
    else:
        st.info("No data in the Parking Availability table.")

    option = st.sidebar.radio("Select an action:", ["Add Parking Availability", "Update Parking Availability", "Delete Parking Availability"])

    if option == "Add Parking Availability":
        st.markdown("### Add Parking Availability")
        space_id = st.selectbox("Select space ID:", [space[0] for space in get_all_parking_spaces()])
        reservation_id = st.selectbox("Select reservation ID:", [reservation[0] for reservation in get_all_reservations()])
        none_avail_start = st.text_input("Enter start date-time for non-availability (YYYY-MM-DD HH:MM:'SS'):")
        none_avail_end = st.text_input("Enter end date-time for non-availability (YYYY-MM-DD HH:MM:'SS'):")

        if st.button("Add Parking Availability"):
            # Insert the new parking availability into the ParkingAvailability table
            cursor.execute("INSERT INTO ParkingAvailability (SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd) VALUES (%s, %s, %s, %s)",
                           (space_id, reservation_id, none_avail_start, none_avail_end))
            connection.commit()
            st.success("Parking availability added successfully!")
            if st.button("Refresh"):
                st.rerun()

    elif option == "Update Parking Availability":
        st.markdown("### Update Parking Availability")
        cursor.execute("SELECT * FROM ParkingAvailability")
        parking_availabilities = cursor.fetchall()

        if not parking_availabilities:
            st.warning("No parking availabilities available for editing. Add a new parking availability first.")
            return

        selected_avail_id = st.selectbox("Select a parking availability to edit:", [avail[0] for avail in parking_availabilities])
        cursor.execute("SELECT * FROM ParkingAvailability WHERE AvailabilityID=%s", (selected_avail_id,))
        selected_availability = cursor.fetchone()

        if selected_availability:
            st.markdown("## Update Parking Availability Information:")
            new_space_id = st.selectbox("Select new space ID:", [space[0] for space in get_all_parking_spaces()], index=get_index_by_value(get_all_parking_spaces(), selected_availability[1]))
            new_reservation_id = st.selectbox("Select new reservation ID:", [reservation[0] for reservation in get_all_reservations()], index=get_index_by_value(get_all_reservations(), selected_availability[2]))
            new_none_avail_start = st.text_input("Enter new start time for non-availability (YYYY-MM-DD HH:MM:'SS'):", value=selected_availability[3])
            new_none_avail_end = st.text_input("Enter new end time for non-availability (YYYY-MM-DD HH:MM:'SS'):", value=selected_availability[4])

            if st.button("Update Parking Availability"):
                # Update the parking availability information in the ParkingAvailability table
                cursor.execute("UPDATE ParkingAvailability SET SpaceID=%s, ReservationID=%s, NoneAvailStart=%s, NoneAvailEnd=%s WHERE AvailabilityID=%s",
                               (new_space_id, new_reservation_id, new_none_avail_start, new_none_avail_end, selected_avail_id))
                connection.commit()
                st.success("Parking availability information updated successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking availability selected for editing. Add a new parking availability first.")

    elif option == "Delete Parking Availability":
        st.subheader("Delete Parking Availability")
        cursor.execute("SELECT * FROM ParkingAvailability")
        parking_availabilities = cursor.fetchall()

        if not parking_availabilities:
            st.warning("No parking availabilities available for deletion. Add a new parking availability first.")
            return

        selected_avail_id = st.selectbox("Select a parking availability to delete:", [avail[0] for avail in parking_availabilities])
        cursor.execute("SELECT * FROM ParkingAvailability WHERE AvailabilityID=%s", (selected_avail_id,))
        selected_availability = cursor.fetchone()

        if selected_availability:
            st.markdown("## Parking Availability Details:")
            st.markdown(f"### **Availability ID:** {selected_availability[0]}")
            st.markdown(f"### **Space ID:** {selected_availability[1]}")
            st.markdown(f"### **Reservation ID:** {selected_availability[2]}")
            st.markdown(f"### **None Availability Start:** {selected_availability[3]}")
            st.markdown(f"### **None Availability End:** {selected_availability[4]}")

            confirmation = st.checkbox("I confirm that I want to delete this parking availability.")
            if confirmation and st.button("Delete Parking Availability"):
                # Delete the parking availability from the ParkingAvailability table
                cursor.execute("DELETE FROM ParkingAvailability WHERE AvailabilityID=%s", (selected_avail_id,))
                connection.commit()
                st.success("Parking availability deleted successfully!")
                if st.button("Refresh"):
                    st.rerun()

        else:
            st.warning("No parking availability selected for deletion. Add a new parking availability first.")


def main():
    user = st.session_state.get("user")
    st.markdown("# Parking Management System 🚗")
    set_bg_hack("image.png")
    #set_sidebar_bg_hack("C:/Users/Harshith/Downloads/dbms1.jpeg")
    hide_streamlit_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    .stDeployButton {
                        visibility: hidden;
                    }
                    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 2rem;}
                    #root > div:nth-child(1) > div > div > div > div > section > div > div {padding-top: 2rem;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    if user:
        if user[1] == b'\x00':
            st.sidebar.markdown(f"# Welcome, {user[2]}!")
            st.sidebar.markdown("# Navigation Bar")
            selected_option = st.sidebar.radio("Select the required option to proceed!", options=["User Profile", "Edit Profile", "Vehicle Details", "Add/Edit Vehicle Details", "Remove Vehicle", "Active Reservations", "Future Reservations", "Past Reservations", "Reserve a Parking Space", "Cancel Reservation"])

            if selected_option == "User Profile":
                user_profile(user[0])
            
            elif selected_option == "Edit Profile":
                edit_profile(user[0])
            
            elif selected_option == "Vehicle Details":
                display_vehicle_details(user[0])

            elif selected_option == "Add/Edit Vehicle Details":
                st.sidebar.subheader("Manage Vehicles")
                vehicle_action = st.sidebar.radio("Select an action:", ["Add Vehicle", "Edit Vehicle Details"])

                if vehicle_action == "Edit Vehicle Details":
                    available_vehicles = get_vehicle_details_by_user_id(user[0])
                    if available_vehicles:
                        selected_vehicle_id = st.selectbox("Select a vehicle to edit:", [vehicle[0] for vehicle in available_vehicles])
                        edit_vehicle(user[0], selected_vehicle_id)
                    else:
                        st.warning("No vehicles available for editing. Add a new vehicle first.")

                elif vehicle_action == "Add Vehicle":
                    add_vehicle(user[0])

            elif selected_option == "Remove Vehicle":
                available_vehicles = get_vehicle_details_by_user_id(user[0])

                if available_vehicles:
                    # Create a list of labels for each vehicle
                    vehicle_labels = [f"{vehicle[2]} ({vehicle[3]}) ({vehicle[4]})" for vehicle in available_vehicles]
                    
                    # Display the dropdown box with vehicle details
                    selected_vehicle_label = st.selectbox("Select a vehicle to remove:", vehicle_labels)

                    # Extract the vehicle ID based on the selected label
                    selected_vehicle_id = available_vehicles[vehicle_labels.index(selected_vehicle_label)][0]

                    # Call the delete_vehicle function
                    delete_vehicle(user[0], selected_vehicle_id)
                else:
                    st.warning("No vehicles available for removal. Add a new vehicle first.")
            
            elif selected_option == "Active Reservations":
                get_active_reservations(user[0])

            elif selected_option == "Future Reservations":
                get_future_reservations(user[0])
            
            elif selected_option == "Past Reservations":
                get_past_reservations(user[0])

            elif selected_option == "Reserve a Parking Space":
                st.markdown("# Parking Reservation")
                reserve_parking_space(user[0])
            
            elif selected_option == "Cancel Reservation":
                cancel_reservation(user[0])

        elif user[1] == b'\x01':
            st.sidebar.markdown(f"# Welcome Admin, {user[2]}!")
            st.sidebar.markdown("# Navigation Bar")
            
            # Administrator options
            selected_option_admin = st.sidebar.radio("Select the required option for administration operations:", options=["Administrator Dashboard", "Manage Users Table", "Manage Vehicles Table", "Manage Reservations Table", "Manage Payments Table", "Manage Parking Spaces Table", "Manage Parking Area Table", "Manage Parking Fee Table", "Manage Parking Availability Table"])

            if selected_option_admin == "Administrator Dashboard":
                admin_dashboard()
            
            elif selected_option_admin == "Manage Users Table":
                users_table()

            elif selected_option_admin == "Manage Vehicles Table":
                vehicles_table()

            elif selected_option_admin == "Manage Reservations Table":
                reservations_table()

            elif selected_option_admin == "Manage Payments Table":
                payments_table()

            elif selected_option_admin == "Manage Parking Spaces Table":
                parking_spaces_table()

            elif selected_option_admin == "Manage Parking Area Table":
                parking_area_table()

            elif selected_option_admin == "Manage Parking Fee Table":
                parking_fee_table()

            elif selected_option_admin == "Manage Parking Availability Table":
                parking_availability_table()

        with st.sidebar:
                if st.button("Logout", use_container_width=True):
                    st.session_state.user = None
                    st.rerun()

    else:
        st.sidebar.markdown("# Signin / Signup")
        op = disable_radio_on_condition(user is not None)
        if op == "Signin / login":
            sign_in()
        elif op == "Signup":
            create_user()

if __name__ == "__main__":
    main()
