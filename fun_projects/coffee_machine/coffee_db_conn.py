import pyodbc

# Connection settings
server = 'localhost,1433'  # Server is in the Docker container
database = 'CoffeeMachineDB'
username = 'sa'
password = 'pifanalo148D'
driver = '{ODBC Driver 17 for SQL Server}'  # Check driver version

# Connection to the database
try:
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    cursor = conn.cursor()
    print("Connection is successfully established!")
except Exception as e:
    print(f"Connection error: {e}")

def get_resources():
    cursor.execute("SELECT * FROM Resources")
    row = cursor.fetchone()
    if row:
        return {"water_ml": row.water_ml, "milk_ml": row.milk_ml, "coffee_g": row.coffee_g, "money": row.money}
    return None

resources = get_resources()
print("Current resources:", resources)
