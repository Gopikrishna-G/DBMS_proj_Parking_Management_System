create database p;
use p;
-- Create ParkingArea table
CREATE TABLE ParkingArea (
    AreaID INT AUTO_INCREMENT PRIMARY KEY,
    AreaName VARCHAR(255) UNIQUE,
    Location VARCHAR(255),
    TotalSpaces INT
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Adn BIT,
    Name VARCHAR(255),
    Email VARCHAR(255) UNIQUE,
    PhoneNumber VARCHAR(20),
    Username VARCHAR(20) UNIQUE,
    Password VARCHAR(255),
    AreaID INT,
    FOREIGN KEY (AreaID) REFERENCES ParkingArea(AreaID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create Vehicles table
CREATE TABLE Vehicles (
    VehicleID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    RegistrationNumber VARCHAR(20) UNIQUE,
    VehicleType VARCHAR(20),
    Color VARCHAR(20),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create ParkingSpaces table
CREATE TABLE ParkingSpaces (
    SpaceID INT AUTO_INCREMENT PRIMARY KEY,
    SpaceType VARCHAR(20),
    AreaID INT,
    FOREIGN KEY (AreaID) REFERENCES ParkingArea(AreaID)
);

-- Create ParkingFee table
CREATE TABLE ParkingFee (
    FeeID INT AUTO_INCREMENT PRIMARY KEY,
    SpaceType VARCHAR(20),
    HourlyRate DECIMAL(10, 2),
    DailyRate DECIMAL(10, 2),
    MonthlyRate DECIMAL(10, 2)
);

-- Create Reservations table
CREATE TABLE Reservations (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    AreaID INT,
    SpaceID INT,
    VehicleID INT,
    ReservationDateTime DATETIME,
    Duration INT, -- in hours
	FOREIGN KEY (UserID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (SpaceID) REFERENCES ParkingSpaces(SpaceID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (VehicleID) REFERENCES Vehicles(VehicleID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (AreaID) REFERENCES ParkingArea(AreaID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create Payments table
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    ReservationID INT,
    Amount DECIMAL(10, 2),
    PaymentDateTime DATETIME,
	FOREIGN KEY (UserID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (ReservationID) REFERENCES Reservations(ReservationID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create ParkingAvailability table
CREATE TABLE ParkingAvailability (
    AvailabilityID INT AUTO_INCREMENT PRIMARY KEY,
    AreaID INT,
    SpaceID INT,
    ReservationID INT,
    NoneAvailStart DATETIME,
    NoneAvailEnd DATETIME,
    FOREIGN KEY (AreaID) REFERENCES ParkingArea(AreaID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
	FOREIGN KEY (SpaceID) REFERENCES ParkingSpaces(SpaceID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (ReservationID) REFERENCES Reservations(ReservationID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Insert data into the ParkingArea table
INSERT INTO ParkingArea (AreaID, AreaName, Location, TotalSpaces)
VALUES
    (1, 'Frontgate', 'Campus Entrance', 15),
    (2, 'GJBC Parking Lot', 'Main Building', 20),
    (3, 'Backgate', 'Rear Entrance', 15);

-- Insert data into the Users table
INSERT INTO Users (UserID, Adn, Name, Email, PhoneNumber, Username, Password, AreaID)
VALUES
    (1, 1, 'Virat Kohli', 'VK@example.com', '9318471828', 'virat', 'Vir', NULL),
    (2, 0, 'Leela Krishna', 'leela@example.com', '1234567890', 'leela', 'Lee', 1),
    (3, 0, 'Pranav', 'pranav@example.com', '9876543210', 'pranav', 'Pra', 2),
    (4, 0, 'Hrishi', 'hrishi@example.com', '1112223333', 'hrishi', 'Hri', 3),
    (5, 0, 'Gopi Krishna', 'gopik@example.com', '4445556666', 'gopik', 'Gop', 1),
    (6, 0, 'Saketh', 'saketh@example.com', '7778889999', 'saketh', 'Sak', 2),
    (7, 0, 'Prajwal', 'prajwal@example.com', '1231231234', 'prajwal', 'Pra', 3),
    (8, 0, 'Ganesh', 'ganesh@example.com', '5556667777', 'ganesh', 'Gan', 1),
    (9, 0, 'Gajendra', 'gajendra@example.com', '9990001111', 'gajendra', 'Gaj', 2),
    (10, 0, 'Girish', 'girish@example.com', '8887776666', 'girish', 'Gir', 3),
    (11, 0, 'Hari Krishna', 'hari@example.com', '2223334444', 'hari', 'Har', 1),
    (12, 0, 'Amit Patel', 'amit@example.com', '3334445555', 'amit', 'Ami', 2),
    (13, 0, 'Neha Sharma', 'neha@example.com', '7778889999', 'neha', 'Neh', 3),
    (14, 0, 'Arun Kumar', 'arun@example.com', '5556667777', 'arun', 'Aru', 1),
    (15, 0, 'Anjali Gupta', 'anjali@example.com', '9990001111', 'anjali', 'Anj', 2),
    (16, 0, 'Rajesh Singh', 'rajesh@example.com', '8887776666', 'rajesh', 'Raj', 3),
    (17, 0, 'Priya Verma', 'priya@example.com', '2223334444', 'priya', 'Pri', 1),
    (18, 0, 'Rahul Mishra', 'rahul@example.com', '1112223333', 'rahul', 'Rah', 2),
    (19, 0, 'Divya Reddy', 'divya@example.com', '3334445555', 'divya', 'Div', 3),
    (20, 0, 'Sanjay Agarwal', 'sanjay@example.com', '4445556666', 'sanjay', 'San', 1),
    (21, 0, 'Aparna Das', 'aparna@example.com', '7778889999', 'aparna', 'Apa', 2);

-- Insert data into the Vehicles table
INSERT INTO Vehicles (VehicleID, UserID, RegistrationNumber, VehicleType, Color)
VALUES
    (1, 2, 'KA01AB1234', 'Two-Wheeler', 'Red'),
    (2, 3, 'MH02CD5678', 'Four-Wheeler', 'Blue'),
    (3, 4, 'TS03EF9876', 'Four-Wheeler', 'Green'),
    (4, 5, 'AP04GH5432', 'Two-Wheeler', 'Black'),
    (5, 6, 'KL05IJ6789', 'Four-Wheeler', 'Silver'),
    (6, 7, 'UP06KL4321', 'Two-Wheeler', 'White'),
    (7, 8, 'TN07MN9876', 'Two-Wheeler', 'Yellow'),
    (8, 9, 'HR08OP2345', 'Four-Wheeler', 'Red'),
    (9, 10, 'DL09QR7654', 'Four-Wheeler', 'Blue'),
    (10, 11, 'RJ10ST8765', 'Two-Wheeler', 'Green'),
    (11, 12, 'KA01AB3412', 'Four-Wheeler', 'Red'),
    (12, 13, 'MH02CD7856', 'Four-Wheeler', 'Blue'),
    (13, 14, 'TS03EF7698', 'Two-Wheeler', 'Green'),
    (14, 15, 'AP04GH3254', 'Four-Wheeler', 'Black'),
    (15, 16, 'KL05IJ9867', 'Four-Wheeler', 'Silver'),
    (16, 17, 'UP06KL4213', 'Two-Wheeler', 'White'),
    (17, 18, 'TN07MN8769', 'Four-Wheeler', 'Yellow'),
    (18, 19, 'HR08OP4532', 'Four-Wheeler', 'Red'),
    (19, 20, 'DL09QR5746', 'Two-Wheeler', 'Blue'),
    (20, 21, 'RJ10ST7568', 'Four-Wheeler', 'Green');

-- Insert data into the ParkingSpaces table
INSERT INTO ParkingSpaces (SpaceID, SpaceType, AreaID)
VALUES
    (1, 'Two-Wheeler', 1),
    (2, 'Two-Wheeler', 1),
    (3, 'Two-Wheeler', 1),
    (4, 'Two-Wheeler', 1),
    (5, 'Two-Wheeler', 1),
    (6, 'Two-Wheeler', 1),
    (7, 'Two-Wheeler', 1),
    (8, 'Two-Wheeler', 1),
    (9, 'Two-Wheeler', 1),
    (10, 'Two-Wheeler', 1),
    (11, 'Two-Wheeler', 1),
    (12, 'Two-Wheeler', 1),
    (13, 'Two-Wheeler', 1),
    (14, 'Two-Wheeler', 1),
    (15, 'Two-Wheeler', 1),
    (16, 'Four-Wheeler', 2),
    (17, 'Four-Wheeler', 2),
    (18, 'Four-Wheeler', 2),
    (19, 'Four-Wheeler', 2),
    (20, 'Four-Wheeler', 2),
    (21, 'Four-Wheeler', 2),
    (22, 'Four-Wheeler', 2),
    (23, 'Four-Wheeler', 2),
    (24, 'Four-Wheeler', 2),
    (25, 'Four-Wheeler', 2),
    (26, 'Four-Wheeler', 2),
    (27, 'Four-Wheeler', 2),
    (28, 'Four-Wheeler', 2),
    (29, 'Four-Wheeler', 2),
    (30, 'Four-Wheeler', 2),
    (31, 'Four-Wheeler', 2),
    (32, 'Four-Wheeler', 2),
    (33, 'Four-Wheeler', 2),
    (34, 'Four-Wheeler', 2),
    (35, 'Four-Wheeler', 2),
    (36, 'Four-Wheeler', 3),
    (37, 'Four-Wheeler', 3),
    (38, 'Four-Wheeler', 3),
    (39, 'Four-Wheeler', 3),
    (40, 'Four-Wheeler', 3),
    (41, 'Four-Wheeler', 3),
    (42, 'Two-Wheeler', 3),
    (43, 'Two-Wheeler', 3),
    (44, 'Two-Wheeler', 3),
    (45, 'Two-Wheeler', 3),
    (46, 'Two-Wheeler', 3),
    (47, 'Two-Wheeler', 3),
    (48, 'Two-Wheeler', 3),
    (49, 'Large-Vehicle', 3),
    (50, 'Large-Vehicle', 3);

-- Insert data into the ParkingFee table
INSERT INTO ParkingFee (FeeID, SpaceType, HourlyRate, DailyRate, MonthlyRate)
VALUES
    (1, 'Two-Wheeler', 25.00, 75.00, 1500.00),
    (2, 'Four-Wheeler', 30.00, 85.00, 1700.00),
    (3, 'Large Vehicle', 35.00, 95.00, 1900.00);

-- Insert data into the Reservations table
INSERT INTO Reservations (ReservationID, UserID, AreaID, SpaceID, VehicleID, ReservationDateTime, Duration)
VALUES
    (1, 2, 1, 1, 1, '2023-11-10 10:00:00', 2),
    (2, 3, 2, 16, 2, '2023-11-12 14:30:00', 3),
    (3, 4, 3, 36, 3, '2023-11-15 08:45:00', 1),
    (4, 5, 1, 2, 4, '2023-11-16 11:30:00', 2),
    (5, 6, 2, 17, 5, '2023-11-17 13:15:00', 4),
    (6, 7, 3, 42, 6, '2023-11-18 17:30:00', 3),
    (7, 8, 1, 3, 7, '2023-11-20 09:00:00', 2),
    (8, 9, 2, 18, 8, '2023-11-22 12:45:00', 1),
    (9, 10, 3, 37, 9, '2023-11-23 14:30:00', 3),
    (10, 11, 1, 4, 10, '2023-11-25 15:30:00', 2),
    (11, 12, 2, 19, 11, '2023-11-26 10:15:00', 2),
    (12, 13, 3, 38, 12, '2023-11-28 16:00:00', 3),
    (13, 14, 1, 5, 13, '2023-11-30 09:45:00', 1),
    (14, 15, 2, 20, 14, '2023-12-01 14:15:00', 2),
    (15, 16, 3, 39, 15, '2023-12-03 12:30:00', 4),
    (16, 17, 1, 6, 16, '2023-12-04 15:30:00', 2),
    (17, 18, 2, 21, 17, '2023-12-05 10:15:00', 24),
    (18, 19, 3, 40, 18, '2023-12-08 16:00:00', 720),
    (19, 20, 1, 7, 19, '2023-12-09 09:45:00', 24),
    (20, 21, 2, 22, 20, '2023-12-10 14:15:00', 48);

-- Insert data into the Payments table
INSERT INTO Payments (PaymentID, UserID, ReservationID, Amount, PaymentDateTime)
VALUES
    (1, 2, 1, 50.00, '2023-11-10 09:45:00'),
    (2, 3, 2, 90.00, '2023-11-12 14:25:00'),
    (3, 4, 3, 30.00, '2023-11-15 07:35:00'),
    (4, 5, 4, 50.00, '2023-11-15 12:45:00'),
    (5, 6, 5, 120.00, '2023-11-17 12:30:00'),
    (6, 7, 6, 75.00, '2023-11-18 15:15:00'),
    (7, 8, 7, 50.00, '2023-11-20 08:00:00'),
    (8, 9, 8, 30.00, '2023-11-22 12:00:00'),
    (9, 10, 9, 95.00, '2023-11-22 12:30:00'),
    (10, 11, 10, 50.00, '2023-11-24 16:00:00'),
    (11, 12, 11, 70.00, '2023-11-10 10:30:00'),
    (12, 13, 12, 100.00, '2023-11-12 15:00:00'),
    (13, 14, 13, 35.00, '2023-11-23 09:30:00'),
    (14, 15, 14, 70.00, '2023-11-24 12:45:00'),
    (15, 16, 15, 130.00, '2023-11-17 14:30:00'),
    (16, 17, 16, 65.00, '2023-11-03 18:15:00'),
    (17, 18, 17, 95.00, '2023-11-20 10:45:00'),
    (18, 19, 18, 1705.00, '2023-12-06 13:00:00'),
    (19, 20, 19, 85.00, '2023-11-23 16:30:00'),
    (20, 21, 20, 175.00, '2023-12-04 16:00:00');

-- Insert data into the ParkingAvailability table
INSERT INTO ParkingAvailability (AvailabilityID, AreaID, SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
VALUES
    (1, 1, 1, 1, '2023-11-10 10:00:00', '2023-11-10 12:00:00'),
    (2, 2, 16, 2, '2023-11-12 14:30:00', '2023-11-12 17:30:00'),
    (3, 3, 36, 3, '2023-11-15 08:45:00', '2023-11-15 09:45:00'),
    (4, 1, 2, 4, '2023-11-16 11:30:00', '2023-11-16 13:30:00'),
    (5, 2, 17, 5, '2023-11-17 13:15:00', '2023-11-17 17:15:00'),
    (6, 3, 42, 6, '2023-11-18 17:30:00', '2023-11-18 20:30:00'),
    (7, 1, 3, 7, '2023-11-20 09:00:00', '2023-11-20 11:00:00'),
    (8, 2, 1, 8, '2023-11-22 12:45:00', '2023-11-22 13:45:00'),
    (9, 3, 37, 9, '2023-11-23 14:30:00', '2023-11-23 17:30:00'),
    (10, 1, 4, 10, '2023-11-25 15:30:00', '2023-11-25 17:30:00'),
    (11, 2, 19, 11, '2023-11-26 10:15:00', '2023-11-26 12:15:00'),
    (12, 3, 38, 12, '2023-11-28 16:00:00', '2023-11-28 19:00:00'),
    (13, 1, 5, 13, '2023-11-30 09:45:00', '2023-11-30 10:45:00'),
    (14, 2, 20, 14, '2023-12-01 14:15:00', '2023-12-01 16:15:00'),
    (15, 3, 39, 15, '2023-12-03 12:30:00', '2023-12-03 16:30:00'),
    (16, 1, 6, 16, '2023-12-04 15:30:00', '2023-12-04 17:30:00'),
    (17, 2, 21, 17, '2023-12-05 10:15:00', '2023-12-06 10:15:00'),
    (18, 3, 40, 18, '2023-12-08 16:00:00', '2024-01-08 16:00:00'),
    (19, 1, 7, 19, '2023-12-09 09:45:00', '2023-12-10 09:45:00'),
    (20, 2, 22, 20, '2023-12-10 14:15:00', '2023-12-12 14:15:00');

create role 'users'@'localhost';
create role 'admins'@'localhost';

grant select, insert, update on parking.users to 'users'@'localhost';
grant select on parking.parkingarea to 'users'@'localhost';
grant select, insert, update, delete on parking.vehicles to 'users'@'localhost';
grant select on parking.parkingspaces to 'users'@'localhost';
grant select on parking.parkingfee to 'users'@'localhost';
grant select, insert, update, delete on parking.reservations to 'users'@'localhost';
grant select, insert, update, delete on parking.payments to 'users'@'localhost';
grant select, insert, update, delete on parking.parkingavailability to 'users'@'localhost';
grant all privileges on parking.* to 'admins'@'localhost';

grant 'users'@'localhost' to 'root'@'localhost';
grant 'admins'@'localhost' to 'root'@'localhost';
set role 'users'@'localhost';
set role 'admins'@'localhost';

