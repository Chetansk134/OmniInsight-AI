from backend.app.database.postgres_db import test_connection

try:
    result = test_connection()

    print("PostgreSQL connection successful!")
    print("Database:", result[0])
    print("User:", result[1])
    print("Server:", result[2].splitlines()[0])

except Exception as error:
    print("PostgreSQL connection failed.")
    print("Error:", error)