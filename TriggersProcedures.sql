/*Trigger to update TotalSpaces in ParkingArea after Reservation Insert:*/

DELIMITER //
CREATE TRIGGER update_total_spaces AFTER INSERT ON Reservations
FOR EACH ROW
BEGIN
    DECLARE area_capacity INT;
    SELECT TotalSpaces INTO area_capacity FROM ParkingArea WHERE AreaID = NEW.AreaID;
    UPDATE ParkingArea SET TotalSpaces = area_capacity - 1 WHERE AreaID = NEW.AreaID;
END;
//
DELIMITER ;

/*Trigger to update TotalSpaces in ParkingArea after Reservation Delete:*/
DELIMITER //
CREATE TRIGGER update_total_spaces_after_delete AFTER DELETE ON Reservations
FOR EACH ROW
BEGIN
    DECLARE area_capacity INT;
    SELECT TotalSpaces INTO area_capacity FROM ParkingArea WHERE AreaID = OLD.AreaID;
    UPDATE ParkingArea SET TotalSpaces = area_capacity + 1 WHERE AreaID = OLD.AreaID;
END;
//
DELIMITER ;

/*Trigger to update Availability after Reservation Insert:*/
DELIMITER //
CREATE TRIGGER update_availability_after_insert AFTER INSERT ON Reservations
FOR EACH ROW
BEGIN
    INSERT INTO ParkingAvailability (AreaID, SpaceID, ReservationID, NoneAvailStart, NoneAvailEnd)
    VALUES (NEW.AreaID, NEW.SpaceID, NEW.ReservationID, NEW.ReservationDateTime, DATE_ADD(NEW.ReservationDateTime, INTERVAL NEW.Duration HOUR));
END;
//
DELIMITER ;

/*Trigger to update Availability after Reservation Delete:*/
DELIMITER //
CREATE TRIGGER update_availability_after_delete AFTER DELETE ON Reservations
FOR EACH ROW
BEGIN
    DELETE FROM ParkingAvailability WHERE ReservationID = OLD.ReservationID;
END;
//
DELIMITER ;


/*Trigger to update Payments after Reservation Insert:*/
DELIMITER //
CREATE TRIGGER update_payments_after_insert AFTER INSERT ON Reservations
FOR EACH ROW
BEGIN
    INSERT INTO Payments (UserID, ReservationID, Amount, PaymentDateTime)
    VALUES (NEW.UserID, NEW.ReservationID, calculate_amount_to_be_paid(25.0, 75.0, 1500.0, NEW.Duration, NEW.ReservationDateTime, NOW()), NOW());
END;
//
DELIMITER ;

/*Trigger to update Payments after Reservation Delete:*/
DELIMITER //
CREATE TRIGGER update_payments_after_delete AFTER DELETE ON Reservations
FOR EACH ROW
BEGIN
    DELETE FROM Payments WHERE ReservationID = OLD.ReservationID;
END;
//
DELIMITER ;

/*Trigger to prevent overlapping reservations:*/
DELIMITER //
CREATE TRIGGER prevent_overlapping_reservations BEFORE INSERT ON Reservations
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Reservations
        WHERE SpaceID = NEW.SpaceID
        AND (
            (NEW.ReservationDateTime BETWEEN ReservationDateTime AND DATE_ADD(ReservationDateTime, INTERVAL Duration HOUR))
            OR (DATE_ADD(NEW.ReservationDateTime, INTERVAL NEW.Duration HOUR) BETWEEN ReservationDateTime AND DATE_ADD(ReservationDateTime, INTERVAL Duration HOUR))
            OR (NEW.ReservationDateTime < ReservationDateTime AND DATE_ADD(NEW.ReservationDateTime, INTERVAL NEW.Duration HOUR) > DATE_ADD(ReservationDateTime, INTERVAL Duration HOUR))
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Reservation overlaps with an existing reservation';
    END IF;
END;
//
DELIMITER ;



/*Procedure to calculate the parking fee for a reservation:*/
DELIMITER //
CREATE PROCEDURE CalculateParkingFee(IN reservationID INT)
BEGIN
    DECLARE hourlyRate DECIMAL(10, 2);
    DECLARE dailyRate DECIMAL(10, 2);
    DECLARE monthlyRate DECIMAL(10, 2);
    DECLARE durationHours INT;

    SELECT HourlyRate, DailyRate, MonthlyRate INTO hourlyRate, dailyRate, monthlyRate
    FROM ParkingFee
    WHERE SpaceType = (
        SELECT SpaceType FROM Reservations WHERE ReservationID = reservationID
    );

    SELECT Duration INTO durationHours
    FROM Reservations
    WHERE ReservationID = reservationID;

    IF durationHours < 24 THEN
        SELECT hourlyRate * durationHours AS Fee;
    ELSEIF durationHours < 720 THEN
        SELECT dailyRate * CEIL(durationHours / 24) AS Fee;
    ELSE
        SELECT monthlyRate * CEIL(durationHours / 720) AS Fee;
    END IF;
END;
//
DELIMITER ;


/*Function to get the total number of reservations for a user:*/
DELIMITER //
CREATE FUNCTION GetTotalReservationsForUser(userID INT) RETURNS INT
BEGIN
    DECLARE totalReservations INT;
    SELECT COUNT(*) INTO totalReservations
    FROM Reservations
    WHERE UserID = userID;
    RETURN totalReservations;
END;
//
DELIMITER ;


/*Procedure to update user information:*/
DELIMITER //
CREATE PROCEDURE UpdateUser(
    IN userID INT,
    IN newName VARCHAR(255),
    IN newEmail VARCHAR(255),
    IN newPhoneNumber VARCHAR(20),
    IN newUsername VARCHAR(20),
    IN newPassword VARCHAR(255)
)
BEGIN
    UPDATE Users
    SET Name = newName,
        Email = newEmail,
        PhoneNumber = newPhoneNumber,
        Username = newUsername,
        Password = newPassword
    WHERE UserID = userID;
END;
//
DELIMITER ;


/*Function to get available parking spaces in an area:*/
DELIMITER //
CREATE FUNCTION GetAvailableParkingSpaces(areaID INT) RETURNS INT
BEGIN
    DECLARE totalSpaces INT;
    DECLARE reservedSpaces INT;

    SELECT TotalSpaces INTO totalSpaces
    FROM ParkingArea
    WHERE AreaID = areaID;

    SELECT COUNT(*) INTO reservedSpaces
    FROM Reservations R
    JOIN ParkingSpaces PS ON R.SpaceID = PS.SpaceID
    WHERE R.AreaID = areaID;

    RETURN totalSpaces - reservedSpaces;
END;
//
DELIMITER ;

/*Procedure to delete a user and associated data:*/
DELIMITER //
CREATE PROCEDURE DeleteUserAndData(userID INT)
BEGIN
    DELETE FROM Users WHERE UserID = userID;
    DELETE FROM Vehicles WHERE UserID = userID;
    DELETE FROM Reservations WHERE UserID = userID;
    DELETE FROM Payments WHERE UserID = userID;
END;
//
DELIMITER ;