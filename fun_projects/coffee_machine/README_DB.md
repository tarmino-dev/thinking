# Coffee Machine Simulator - Database Mode  

This guide provides instructions on setting up and running the Coffee Machine Simulator in **database mode** using SQL Server.  

## Prerequisites  

Before running the database version, ensure you have:  

- **SQL Server installed and running** (locally or in a Docker container)  
- **ODBC Driver 17 for SQL Server** installed  
- **Configured `config.ini` correctly**  

## Setting Up SQL Server  

### **Option 1: Running SQL Server in Docker**  

If you don't have SQL Server installed, you can run it using Docker:  

docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=pifanalo148D' \
   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2019-latest  

To verify that SQL Server is running:

docker ps

### **Option 2: Installing SQL Server Locally**

If you prefer to install SQL Server directly on your system, download and install it from Microsoft's website.

## Configuring the Database

1. Connect to SQL Server:

If using Docker, connect with:

sqlcmd -S localhost -U sa -P 'pifanalo148D'  

2. Create the Database and Table:

Run the following SQL commands:

CREATE DATABASE CoffeeMachineDB;  
USE CoffeeMachineDB;  

CREATE TABLE Resources (  
    id INT PRIMARY KEY IDENTITY(1,1),  
    water_ml INT NOT NULL,  
    milk_ml INT NOT NULL,  
    coffee_g INT NOT NULL,  
    money DECIMAL(10,2) NOT NULL  
);  

INSERT INTO Resources (water_ml, milk_ml, coffee_g, money)  
VALUES (1000, 500, 200, 0.00);  

3. Configure config.ini

Edit config.ini and set:

USE_DATABASE = True  

## Running the Coffee Machine Simulator

Ensure the database is running, then start the program:

python main.py

or

python3 main.py

## Troubleshooting

If the program cannot connect to SQL Server, ensure that:

- SQL Server is running
- The correct credentials and driver are specified in config.ini
- The ODBC driver is installed properly
