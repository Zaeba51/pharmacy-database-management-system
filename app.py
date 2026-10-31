import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, render_template_string, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "pharmacy_user"),
        password=os.getenv("DB_PASSWORD", "PharmacyDB@2026"),
        database=os.getenv("DB_NAME", "pharmacy_db"),
        port=int(os.getenv("DB_PORT", 3306))
    )

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Pharmacy Management System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f1f5f9;
            color: #1e293b;
        }
        header {
            background: #087f8c;
            color: white;
            padding: 24px;
        }
        nav { margin-top: 18px; }
        nav a {
            color: white;
            margin-right: 20px;
            text-decoration: none;
        }
        main { max-width: 1150px; margin: auto; padding: 24px; }
        .cards { display: flex; gap: 15px; flex-wrap: wrap; }
        .card, section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px #0001;
        }
        .card { flex: 1; min-width: 150px; }
        .number { font-size: 28px; color: #087f8c; font-weight: bold; }
        input, select, button {
            padding: 10px;
            margin: 5px 3px;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
        }
        button {
            background: #087f8c;
            color: white;
            cursor: pointer;
            border: none;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 11px 8px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th { background: #e6f4f4; }
        .table-wrap { overflow-x: auto; }
        .message { color: #087f8c; font-weight: bold; }
        .alert { color: #b91c1c; font-weight: bold; }
        .low { color: #b91c1c; }
    </style>
</head>
<body>
<header>
    <h1>Pharmacy Management System</h1>
    <p>Manage medicines, stock, customers and purchases</p>
    <nav>
        <a href="#dashboard">Dashboard</a>
        <a href="#medicines">Medicines</a>
        <a href="#stock">Stock</a>
        <a href="#purchases">Purchases</a>
    </nav>
</header>

<main>
    <section id="dashboard">
        <h2>Dashboard</h2>
        <div class="cards">
            <div class="card">
                Total Medicines
                <div class="number">{{ total }}</div>
            </div>
            <div class="card">
                Total Stock Units
                <div class="number">{{ stock_total }}</div>
            </div>
            <div class="card">
                Total Customers
                <div class="number">{{ customers }}</div>
            </div>
            <div class="card">
                Low Stock Medicines
                <div class="number">{{ low_count }}</div>
            </div>
        </div>
        {% if message %}
        <p class="message">{{ message }}</p>
        {% endif %}
    </section>

    <section id="medicines">
        <h2>Search Medicines</h2>
        <form method="GET" action="/">
            <input name="search" placeholder="Medicine name"
                   value="{{ search }}">
            <button type="submit">Search</button>
            <a href="/">Show All</a>
        </form>

        <h3>Add New Medicine</h3>
        <form method="POST" action="/add">
            <input name="name" placeholder="Medicine name" required>
            <input name="category" placeholder="Category" required>
            <input name="expiry" type="date" required>
            <input name="price" type="number" min="0.01"
                   step="0.01" placeholder="Price" required>
            <select name="supplier" required>
                <option value="">Select supplier</option>
                {% for s in suppliers %}
                <option value="{{ s[0] }}">{{ s[1] }}</option>
                {% endfor %}
            </select>
            <button type="submit">Add Medicine</button>
        </form>

        <h3>Medicine Inventory</h3>
        <div class="table-wrap">
        <table>
            <tr>
    <th>ID</th><th>Name</th><th>Category</th><th>Expiry</th>
    <th>Price (Rs.)</th><th>Update Price</th><th>Delete</th>
</tr>
            {% for m in medicines %}
            <tr>
                <td>{{ m[0] }}</td>
                <td>{{ m[1] }}</td>
                <td>{{ m[2] }}</td>
                <td>{{ m[3] }}</td>
                <td>{{ m[4] }}</td>
                <td>
                    <form method="POST" action="/update/{{ m[0] }}">
                        <input type="number" name="price" min="0.01"
                               step="0.01" placeholder="New price" required>
                        <button type="submit">Update</button>
                    </form>
                </td>
                <td>
    <form method="POST" action="/delete/{{ m[0] }}"
          onsubmit="return confirm('Delete this medicine?');">
        <button type="submit" style="background:#dc2626;">Delete</button>
    </form>
</td>
            </tr>
            {% endfor %}
        </table>
        </div>
    </section>

    <section id="stock">
        <h2>Stock Management</h2>
        {% if low_count > 0 %}
        <p class="alert">Attention: {{ low_count }} medicine(s)
        have stock at or below their reorder level.</p>
        {% else %}
        <p class="message">All medicines are above their reorder levels.</p>
        {% endif %}
        <div class="table-wrap">
        <table>
            <tr>
                <th>Medicine</th><th>Quantity</th><th>Reorder Level</th>
                <th>Status</th><th>Update Stock</th>
            </tr>
            {% for s in stock_items %}
            <tr>
    <td>{{ s[0] }}</td>
    <td>{{ s[1] }}</td>
    <td>{{ s[2] }}</td>
    <td>
        {% if s[1] <= s[2] %}
            <span class="low">Restock Needed</span>
        {% else %}
            In Stock
        {% endif %}
    </td>
    <td>
        <form method="POST" action="/update_stock/{{ s[3] }}">
            <input type="number" name="quantity"
                   min="0" placeholder="New quantity" required>
            <button type="submit">Update</button>
        </form>
    </td>
</tr>
            {% endfor %}
        </table>
        </div>
    </section>

    <section id="customers">
    <h2>Customer Management</h2>

    <h3>Add New Customer</h3>
    <form method="POST" action="/add_customer">
        <input type="text" name="name"
               placeholder="Customer Name" required>

        <input type="tel" name="phone"
               placeholder="Phone Number" required>

        <input type="text" name="address"
               placeholder="Address" required>

        <button type="submit">Add Customer</button>
    </form>
</section>
    <section id="purchases">
        <h2>Purchase Records</h2>
        <h3>New Purchase</h3>
<form method="POST" action="/add_purchase">
    <label>Customer:</label>
    <select name="customer" required>
        <option value="">Select customer</option>
        {% for c in customers_list %}
        <option value="{{ c[0] }}">{{ c[1] }}</option>
        {% endfor %}
    </select>

    <label>Pharmacist:</label>
    <select name="pharmacist" required>
        <option value="">Select pharmacist</option>
        {% for ph in pharmacists_list %}
        <option value="{{ ph[0] }}">{{ ph[1] }}</option>
        {% endfor %}
    </select>

    <label>Medicine:</label>
    <select name="medicine" required>
        <option value="">Select medicine</option>
        {% for m in medicine_options %}
        <option value="{{ m[0] }}">{{ m[1] }} - Rs. {{ m[2] }}</option>
        {% endfor %}
    </select>

    <label>Quantity:</label>
    <input type="number" name="quantity" min="1"
           placeholder="Quantity" required>

    <button type="submit">Save Purchase</button>
</form>
        <div class="table-wrap">
        <table>
            <tr>
                <th>Purchase ID</th><th>Date</th><th>Customer</th>
                <th>Pharmacist</th><th>Bill Amount (Rs.)</th>
            </tr>
            {% for p in purchases %}
            <tr>
                <td>{{ p[0] }}</td>
                <td>{{ p[1] }}</td>
                <td>{{ p[2] }}</td>
                <td>{{ p[3] }}</td>
                <td>{{ p[4] }}</td>
            </tr>
            {% endfor %}
        </table>
        </div>
    </section>
</main>
</body>
</html>
"""


def get_page_data(search=""):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM MEDICINE")
    total = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(Quantity), 0) FROM STOCK")
    stock_total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM CUSTOMER")
    customers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM STOCK WHERE Quantity <= Reorder_Level")
    low_count = cur.fetchone()[0]

    cur.execute("SELECT Sup_ID, Name FROM SUPPLIER")
    suppliers = cur.fetchall()

    cur.execute("SELECT Cust_ID, Name, Phone, Address FROM CUSTOMER")
    customers_list = cur.fetchall()

    cur.execute("SELECT Ph_ID, Name FROM PHARMACIST")
    pharmacists_list = cur.fetchall()

    cur.execute("SELECT M_ID, Medicine_Name, Price FROM MEDICINE")
    medicine_options = cur.fetchall()

    if search:
        cur.execute(
            "SELECT M_ID, Medicine_Name, Category, Expiry_Date, Price "
            "FROM MEDICINE WHERE Medicine_Name LIKE %s",
            ("%" + search + "%",)
        )
    else:
        cur.execute(
            "SELECT M_ID, Medicine_Name, Category, Expiry_Date, Price "
            "FROM MEDICINE"
        )
    medicines = cur.fetchall()

    cur.execute("""
        SELECT M.Medicine_Name, S.Quantity, S.Reorder_Level, S.M_ID
        FROM STOCK S
        JOIN MEDICINE M ON S.M_ID = M.M_ID
        ORDER BY M.Medicine_Name
    """)
    stock_items = cur.fetchall()

    cur.execute("""
        SELECT P.Pur_ID, P.Date, C.Name, PH.Name, P.Bill_Cost
        FROM PURCHASE P
        JOIN CUSTOMER C ON P.Cust_ID = C.Cust_ID
        JOIN PHARMACIST PH ON P.Ph_ID = PH.Ph_ID
        ORDER BY P.Date DESC, P.Pur_ID DESC
    """)
    purchases = cur.fetchall()

    cur.close()
    con.close()

    return {
        "total": total,
        "stock_total": stock_total,
        "customers": customers,
        "low_count": low_count,
        "suppliers": suppliers,
        "medicines": medicines,
        "stock_items": stock_items,
        "purchases": purchases,
        "search": search,
        "customers_list": customers_list,
        "pharmacists_list": pharmacists_list,
        "medicine_options": medicine_options
    }


@app.route("/")
def home():
    data = get_page_data()
    return render_template("dashboard.html", **data)


@app.route("/medicines")
def medicines_page():
    search = request.args.get("search", "").strip()
    data = get_page_data(search)
    return render_template("medicines.html", **data)


@app.route("/stock")
def stock_page():
    data = get_page_data()
    return render_template("stock.html", **data)


@app.route("/customers")
def customers_page():
    data = get_page_data()
    return render_template("customers.html", **data)


@app.route("/suppliers")
def suppliers_page():
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT Sup_ID, Name, Phone, Address FROM SUPPLIER")
    suppliers = cur.fetchall()

    cur.close()
    con.close()

    return render_template("suppliers.html", suppliers=suppliers)



@app.route("/prescriptions")
def prescriptions_page():
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT Cust_ID, Name, Phone, Address FROM CUSTOMER")
    customers_list = cur.fetchall()

    cur.execute("""
        SELECT Pres_ID, Date, Doctor, Cust_ID
        FROM PRESCRIPTION
        ORDER BY Date DESC, Pres_ID DESC
    """)
    prescription_data = cur.fetchall()

    cur.execute("""
        SELECT P.Pres_ID, P.Date, P.Doctor, C.Name
        FROM PRESCRIPTION P
        JOIN CUSTOMER C ON P.Cust_ID = C.Cust_ID
        ORDER BY P.Date DESC, P.Pres_ID DESC
    """)
    prescriptions = cur.fetchall()

    cur.execute("SELECT M_ID, Medicine_Name, Price FROM MEDICINE")
    medicine_options = cur.fetchall()

    cur.execute("""
    SELECT PI.Pres_ID, M.Medicine_Name, PI.Dosage,
           PI.Duration, PI.Quantity
    FROM PRESCRIPTION_ITEM PI
    JOIN MEDICINE M ON PI.Medicine = M.M_ID
    ORDER BY PI.Pres_ID DESC
""")
    prescription_items = cur.fetchall()

    cur.close()
    con.close()

    return render_template(
        "prescriptions.html",
        customers_list=customers_list,
        prescriptions=prescriptions,
        medicine_options=medicine_options,
        prescription_items=prescription_items
    )

@app.route("/purchases")
def purchases_page():
    data = get_page_data()
    return render_template("purchases.html", **data)



@app.route("/add", methods=["POST"])
def add_medicine():
    name = request.form["name"].strip()
    category = request.form["category"].strip()
    expiry = request.form["expiry"]
    price = float(request.form["price"])
    supplier = int(request.form["supplier"])

    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO MEDICINE
            (Medicine_Name, Category, Expiry_Date, Price, Sup_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, category, expiry, price, supplier))

        medicine_id = cur.lastrowid

        cur.execute("""
            INSERT INTO STOCK (Quantity, Reorder_Level, M_ID)
            VALUES (0, 10, %s)
        """, (medicine_id,))

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        cur.close()
        con.close()

    return redirect(url_for(
        "home", message="Medicine and stock record added successfully!"
    ))

@app.route("/update/<int:mid>", methods=["POST"])
def update_price(mid):
    price = float(request.form["price"])

    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "UPDATE MEDICINE SET Price = %s WHERE M_ID = %s",
        (price, mid)
    )
    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("home", message="Medicine price updated!"))


@app.route("/update_stock/<int:mid>", methods=["POST"])
def update_stock(mid):
    quantity = int(request.form["quantity"])

    if quantity < 0:
        return redirect(url_for("home", message="Invalid quantity!"))

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "UPDATE STOCK SET Quantity = %s WHERE M_ID = %s",
        (quantity, mid)
    )

    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("home", message="Stock quantity updated!"))

@app.route("/delete/<int:mid>", methods=["POST"])
def delete_medicine(mid):
    con = get_connection()
    cur = con.cursor()

    try:
        # Check whether the medicine is used in purchases or prescriptions
        cur.execute(
            "SELECT COUNT(*) FROM PURCHASE_ITEM WHERE M_ID = %s",
            (mid,)
        )
        purchase_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM PRESCRIPTION_ITEM WHERE Medicine = %s",
            (mid,)
        )
        prescription_count = cur.fetchone()[0]

        if purchase_count > 0 or prescription_count > 0:
            return redirect(url_for(
                "home",
                message="Cannot delete: medicine is linked to a purchase or prescription."
            ))

        cur.execute("DELETE FROM STOCK WHERE M_ID = %s", (mid,))
        cur.execute("DELETE FROM MEDICINE WHERE M_ID = %s", (mid,))
        con.commit()

    except Exception:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()

    return redirect(url_for("home", message="Medicine deleted successfully!"))

@app.route("/add_purchase", methods=["POST"])
def add_purchase():
    # Validate form inputs
    try:
        customer = int(request.form["customer"])
        pharmacist = int(request.form["pharmacist"])
        medicine = int(request.form["medicine"])
        quantity = int(request.form["quantity"])

        if min(customer, pharmacist, medicine) < 1 or quantity < 1:
            raise ValueError

    except (ValueError, TypeError, KeyError):
        return redirect(url_for(
            "home", message="Invalid input. IDs and quantity must be positive numbers."
        ))

    con = get_connection()
    cur = con.cursor()

    try:
        # Check that customer exists
        cur.execute(
            "SELECT Cust_ID FROM CUSTOMER WHERE Cust_ID = %s",
            (customer,)
        )
        if cur.fetchone() is None:
            return redirect(url_for(
                "home", message="Customer not found."
            ))

        # Check that pharmacist exists
        cur.execute(
            "SELECT Ph_ID FROM PHARMACIST WHERE Ph_ID = %s",
            (pharmacist,)
        )
        if cur.fetchone() is None:
            return redirect(url_for(
                "home", message="Pharmacist not found."
            ))

        # Check medicine price and available stock
        cur.execute("""
            SELECT M.Price, S.Quantity
            FROM MEDICINE M
            JOIN STOCK S ON M.M_ID = S.M_ID
            WHERE M.M_ID = %s
            FOR UPDATE
        """, (medicine,))

        result = cur.fetchone()

        if result is None:
            return redirect(url_for(
                "home", message="Medicine or stock record not found."
            ))

        price, available = result

        if quantity > available:
            return redirect(url_for(
                "home", message=f"Insufficient stock. Available: {available}."
            ))

        bill = price * quantity

        # Create purchase record
        cur.execute("""
            INSERT INTO PURCHASE
                (`Date`, Bill_Cost, Cust_ID, Ph_ID)
            VALUES (CURDATE(), %s, %s, %s)
        """, (bill, customer, pharmacist))

        purchase_id = cur.lastrowid

        # Create purchase item
        cur.execute("""
            INSERT INTO PURCHASE_ITEM
                (Pur_ID, M_ID, Unit_Price, Quantity)
            VALUES (%s, %s, %s, %s)
        """, (purchase_id, medicine, price, quantity))

        # Reduce stock
        cur.execute("""
            UPDATE STOCK
            SET Quantity = Quantity - %s
            WHERE M_ID = %s AND Quantity >= %s
        """, (quantity, medicine, quantity))

        if cur.rowcount != 1:
            raise ValueError("Stock update failed.")

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        cur.close()
        con.close()

    return redirect(url_for(
        "home", message="Purchase saved successfully!"
    ))

@app.route("/add_customer", methods=["POST"])
def add_customer():
    name = request.form["name"].strip()
    phone = request.form["phone"].strip()
    address = request.form["address"].strip()

    if not name or not phone or not address:
        return redirect(url_for(
            "home", message="Please fill in all customer details."
        ))

    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO CUSTOMER (Name, Phone, Address)
            VALUES (%s, %s, %s)
        """, (name, phone, address))

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        cur.close()
        con.close()

    return redirect(url_for(
        "home", message="Customer added successfully!"
    ))

@app.route("/delete_customer/<int:cust_id>", methods=["POST"])
def delete_customer(cust_id):
    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM CUSTOMER WHERE Cust_ID = %s", (cust_id,))
        con.commit()
        message = "Customer deleted successfully!"
    except mysql.connector.Error:
        con.rollback()
        message = "Cannot delete customer. This customer has purchase or prescription records."
    finally:
        cur.close()
        con.close()

    return redirect(url_for("customers_page", message=message))

@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    name = request.form["name"].strip()
    phone = request.form["phone"].strip()
    address = request.form["address"].strip()

    if not name or not address:
        return redirect(url_for("suppliers_page"))

    if len(phone) != 10 or not phone.isdigit() or phone[0] not in "6789":
        return redirect(url_for("suppliers_page"))

    con = get_connection()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO SUPPLIER (Name, Phone, Address) VALUES (%s, %s, %s)",
        (name, phone, address)
    )

    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("suppliers_page"))

@app.route("/delete_supplier/<int:sup_id>", methods=["POST"])
def delete_supplier(sup_id):
    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM SUPPLIER WHERE Sup_ID = %s", (sup_id,))
        con.commit()
        message = "Supplier deleted successfully!"
    except mysql.connector.Error:
        con.rollback()
        message = "Cannot delete supplier. Medicines are linked to this supplier."
    finally:
        cur.close()
        con.close()

    return redirect(url_for("suppliers_page", message=message))

@app.route("/add_prescription", methods=["POST"])
def add_prescription():
    cust_id = request.form["cust_id"]
    date = request.form["date"]
    doctor = request.form["doctor"].strip()

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO PRESCRIPTION (Date, Doctor, Cust_ID)
        VALUES (%s, %s, %s)
    """, (date, doctor, cust_id))

    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("prescriptions_page"))

@app.route("/delete_prescription/<int:pres_id>", methods=["POST"])
def delete_prescription(pres_id):
    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute(
            "DELETE FROM PRESCRIPTION_ITEM WHERE Pres_ID = %s",
            (pres_id,)
        )
        cur.execute(
            "DELETE FROM PRESCRIPTION WHERE Pres_ID = %s",
            (pres_id,)
        )
        con.commit()
        message = "Prescription deleted successfully!"
    except mysql.connector.Error:
        con.rollback()
        message = "Could not delete prescription."
    finally:
        cur.close()
        con.close()

    return redirect(url_for("prescriptions_page", message=message))

@app.route("/add_prescription_item", methods=["POST"])
def add_prescription_item():
    pres_id = request.form["pres_id"]
    medicine = request.form["medicine"].strip()
    dosage = request.form["dosage"].strip()
    duration = request.form["duration"].strip()
    quantity = request.form["quantity"]

    con = get_connection()
    cur = con.cursor()

    try:
        cur.execute("""
            INSERT INTO PRESCRIPTION_ITEM
                (Pres_ID, Medicine, Dosage, Duration, Quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, (pres_id, medicine, dosage, duration, quantity))

        con.commit()
    except mysql.connector.Error as e:
        con.rollback()
        cur.close()
        con.close()
        return f"Could not add medicine: {e}"

    cur.close()
    con.close()

    return redirect(url_for("prescriptions_page"))


if __name__ == "__main__":
    app.run(debug=True)
