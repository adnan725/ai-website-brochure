

CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);



CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    DepartmentID INT,
    Role VARCHAR(50),

    CONSTRAINT FK_Employees_Department
    FOREIGN KEY (DepartmentID)
    REFERENCES Departments(DepartmentID)
);


CREATE TABLE WorkLogs (
    WorkLogID INT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    WorkDate DATE NOT NULL,
    StartTime DATETIME,
    EndTime DATETIME,
    WorkMinutes INT,

    CONSTRAINT FK_WorkLogs_Employee
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees(EmployeeID)
);


CREATE TABLE Vehicles (
    VehicleID INT PRIMARY KEY,
    VehicleName VARCHAR(100) NOT NULL,
    Status VARCHAR(50) CHECK (Status IN ('Active', 'Inactive')),
    DepartmentID INT,

    CONSTRAINT FK_Vehicles_Department
    FOREIGN KEY (DepartmentID)
    REFERENCES Departments(DepartmentID)
);


CREATE TABLE Trips (
    TripID INT PRIMARY KEY,
    VehicleID INT NOT NULL,
    EmployeeID INT NOT NULL,
    StartLocation VARCHAR(100),
    EndLocation VARCHAR(100),
    StartTime DATETIME,
    EndTime DATETIME,
    DistanceKM FLOAT,
    Status VARCHAR(50) CHECK (Status IN ('Completed', 'Delayed')),

    CONSTRAINT FK_Trips_Vehicle
    FOREIGN KEY (VehicleID)
    REFERENCES Vehicles(VehicleID),

    CONSTRAINT FK_Trips_Employee
    FOREIGN KEY (EmployeeID)
    REFERENCES Employees(EmployeeID)
);


CREATE INDEX IDX_WorkLogs_EmployeeID ON WorkLogs(EmployeeID);
CREATE INDEX IDX_WorkLogs_WorkDate ON WorkLogs(WorkDate);

CREATE INDEX IDX_Trips_EmployeeID ON Trips(EmployeeID);
CREATE INDEX IDX_Trips_VehicleID ON Trips(VehicleID);


INSERT INTO Departments (DepartmentID, Name) VALUES
(1, 'Logistics'),
(2, 'Operations'),
(3, 'HR');


INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, Role) VALUES
(1, 'Ali', 'Khan', 1, 'Driver'),
(2, 'Sara', 'Ahmed', 1, 'Driver'),
(3, 'John', 'Miller', 2, 'Supervisor'),
(4, 'Emma', 'Smith', 2, 'Dispatcher'),
(5, 'David', 'Lee', 3, 'HR Manager'),
(6, 'Michael', 'Brown', 1, 'Driver'),
(7, 'Sophia', 'Wilson', 2, 'Supervisor');

INSERT INTO WorkLogs (WorkLogID, EmployeeID, WorkDate, StartTime, EndTime, WorkMinutes) VALUES
(1, 1, '2026-03-27', '2026-03-27 08:00', '2026-03-27 14:00', 360),
(2, 2, '2026-03-27', '2026-03-27 09:00', '2026-03-27 12:00', 180),
(3, 3, '2026-03-27', '2026-03-27 08:00', '2026-03-27 17:00', 540),
(4, 4, '2026-03-27', '2026-03-27 10:00', '2026-03-27 15:00', 300),
(5, 5, '2026-03-27', '2026-03-27 09:00', '2026-03-27 17:00', 480),

(6, 1, '2026-03-28', '2026-03-28 08:00', '2026-03-28 16:00', 480),
(7, 2, '2026-03-28', '2026-03-28 09:00', '2026-03-28 13:00', 240),
(8, 3, '2026-03-28', '2026-03-28 08:00', '2026-03-28 17:00', 540),
(9, 6, '2026-03-28', '2026-03-28 07:00', '2026-03-28 11:00', 240),
(10, 7, '2026-03-28', '2026-03-28 10:00', '2026-03-28 18:00', 480);


INSERT INTO Vehicles (VehicleID, VehicleName, Status, DepartmentID) VALUES
(1, 'Truck A', 'Active', 1),
(2, 'Truck B', 'Inactive', 1),
(3, 'Van C', 'Active', 2),
(4, 'Truck D', 'Active', 1),
(5, 'Van E', 'Inactive', 2);


INSERT INTO Trips (TripID, VehicleID, EmployeeID, StartLocation, EndLocation, StartTime, EndTime, DistanceKM, Status) VALUES
(1, 1, 1, 'Berlin', 'Hamburg', '2026-03-27 08:00', '2026-03-27 12:00', 280, 'Completed'),
(2, 2, 2, 'Munich', 'Stuttgart', '2026-03-27 09:00', '2026-03-27 13:30', 220, 'Delayed'),
(3, 3, 1, 'Cologne', 'Düsseldorf', '2026-03-28 10:00', '2026-03-28 11:30', 45, 'Completed'),
(4, 4, 6, 'Frankfurt', 'Berlin', '2026-03-28 06:00', '2026-03-28 12:00', 550, 'Completed'),
(5, 5, 7, 'Hamburg', 'Bremen', '2026-03-28 11:00', '2026-03-28 13:00', 120, 'Delayed');


PRINT 'Database + Data initialized successfully 🚀';