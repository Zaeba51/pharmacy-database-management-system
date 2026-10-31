
import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="pharmacy_user",
    password="PharmacyDB@2026",
    database="pharmacy_db",
    port=3306
)

cur = con.cursor()

while True:
    print("\n--- PHARMACY DATABASE MANAGEMENT SYSTEM ---")
    print("1. View Medicines")
    print("2. Search Medicine")
    print("3. Add Medicine")
    print("4. Update Medicine Price")
    print("5. Delete Medicine")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        cur.execute("SELECT * FROM MEDICINE")
        for row in cur.fetchall():
            print(row)

    elif choice == "2":
        name = input("Enter medicine name: ")
        cur.execute(
            "SELECT * FROM MEDICINE WHERE Medicine_Name = %s",
            (name,)
        )
        print(cur.fetchall())

    elif choice == "3":
        name = input("Medicine name: ")
        category = input("Category: ")
        expiry = input("Expiry date (YYYY-MM-DD): ")
        price = float(input("Price: "))
        supplier = int(input("Supplier ID: "))

        cur.execute(
            """INSERT INTO MEDICINE
            (Medicine_Name, Category, Expiry_Date, Price, Sup_ID)
            VALUES (%s, %s, %s, %s, %s)""",
            (name, category, expiry, price, supplier)
        )
        con.commit()
        print("Medicine added successfully!")

    elif choice == "4":
        mid = int(input("Enter medicine ID: "))
        price = float(input("Enter new price: "))

        cur.execute(
            "UPDATE MEDICINE SET Price = %s WHERE M_ID = %s",
            (price, mid)
        )
        con.commit()
        print("Price updated successfully!")

    elif choice == "5":
        mid = int(input("Enter medicine ID to delete: "))

        cur.execute("DELETE FROM MEDICINE WHERE M_ID = %s", (mid,))
        con.commit()
        print("Medicine deleted successfully!")

    elif choice == "6":
        break

    else:
        print("Invalid choice!")

cur.close()
con.close()
print("Program closed.")