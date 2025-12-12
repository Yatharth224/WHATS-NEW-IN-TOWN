from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from werkzeug.utils import secure_filename

from flask_bcrypt import Bcrypt
import os
import re




app = Flask(__name__)
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="yatharth",
        password="Rachit@224",
        database="Whatsnewdb"
    )


@app.route("/")
def homepage():
    return render_template('homepage.html')


@app.route('/index')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name FROM categories")
    categories = [row["name"] for row in cursor.fetchall()]

    cursor.execute("SELECT name FROM states")
    states = [row["name"] for row in cursor.fetchall()]
    print("debug :", cursor.statement)

    cursor.execute("""
        SELECT cities.name AS city, states.name AS state
        FROM cities
        JOIN states ON cities.state_id = states.id
    """)
    cities = [{"city": row["city"], "state": row["state"]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('index.html', categories=categories, states=states, cities=cities)


CATEGORY_MAP = {
    "Fine Dine": ["Fine Dine", "Casual Dine", "Fine Dining", "Dining"],
    "Restro Bar": ["Restro Bar", "Bar", "Pub", "Restaurant & Bar"],
    "Arcade": ["Arcade", "Gaming Zone"],
    "Bowling": ["Bowling", "Sports Bar"]
}

STATE_MAP = {
    "Madhya Pradesh": ["Madhya Pradesh", "MP"],
    "Maharashtra": ["Maharashtra", "MH"],
    "Karnataka": ["Karnataka", "KA"],
    "Delhi": ["Delhi", "New Delhi", "DL"]
}



PER_PAGE = 15  

@app.route("/filter", methods=["POST"])
def filter_data():
    category = request.form.get("category")
    state = request.form.get("state")
    city = request.form.get("city")

    
    page_raw = request.form.get("page", 1)
    try:
        page = int(page_raw)
    except:
        page = 1
    if page < 1:
        page = 1

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    
    base_query = " FROM business_listings WHERE 1=1"
    params = []

    # CATEGORY FILTER USING MAPPING
    if category:
        mapped_values = CATEGORY_MAP.get(category, [category])
        placeholders = ",".join(["%s"] * len(mapped_values))
        base_query += f" AND LOWER(category) IN ({placeholders})"
        params.extend([v.lower() for v in mapped_values])

    # STATE FILTER USING MAPPING
    if state:
        mapped_states = STATE_MAP.get(state, [state])
        placeholders = ",".join(["%s"] * len(mapped_states))
        base_query += f" AND LOWER(state) IN ({placeholders})"
        params.extend([s.lower() for s in mapped_states])

    # CITY FILTER (Case insensitive)
    if city:
        base_query += " AND LOWER(city) LIKE %s"
        params.append(f"%{city.lower()}%")

    count_sql = "SELECT COUNT(*) AS total" + base_query
    cursor.execute(count_sql, tuple(params))
    total_records = cursor.fetchone()["total"]

    if total_records == 0:
        total_pages = 1
        page = 1
    else:
        total_pages = (total_records + PER_PAGE - 1) // PER_PAGE  
        if page > total_pages:
            page = total_pages

    
    offset = (page - 1) * PER_PAGE

    
    data_sql = (
        "SELECT *" + base_query +
        " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    )
    data_params = params + [PER_PAGE, offset]

    cursor.execute(data_sql, tuple(data_params))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    has_prev = page > 1
    has_next = page < total_pages

    return render_template(
        "whatsnew.html",
        category=category,
        state=state,
        city=city,
        data=data,
        page=page,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
    )

@app.route("/whatsnew")
def whatsnew():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name, photo, cost_for_two, phone, location FROM restaurants")
    restaurants = cursor.fetchall()

    conn.close()

    return render_template("whatsnew.html", restaurants=restaurants)


@app.route('/partner', methods=['GET', 'POST'])
def partner():
    if request.method == 'POST':
        full_name = request.form['full_name']
        state = request.form['state']
        city = request.form['city']
        category = request.form['category']
        cost_for_two = request.form['cost_for_two']
        location = request.form['location']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        photos = []
        for field in ['photo1', 'photo2', 'photo3', 'photo4', 'photo5']:
            file = request.files.get(field)
            if file and file.filename.strip() != "":
                filename = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
            else:
                filename = None
            photos.append(filename)

        # electricity bill (safely handle missing file)
        electricity_filename = None
        electricity_bill = request.files.get('electricity_bill')
        if electricity_bill and electricity_bill.filename.strip() != "":
            electricity_filename = secure_filename(electricity_bill.filename)
            bill_path = os.path.join(app.config['UPLOAD_FOLDER'], electricity_filename)
            electricity_bill.save(bill_path)

        additional_notes = request.form.get('additional_notes')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pending_applications
            (full_name_or_business_name, state, city, category, cost_for_two,
            location, contact_number, email, password_hash,
            photo1, photo2, photo3, photo4, photo5, electricity_bill, additional_notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            full_name, state, city, category, cost_for_two, location, contact_number,
            email, password_hash, photos[0], photos[1], photos[2], photos[3], photos[4],
            electricity_filename, additional_notes
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('homepage'))

    return render_template('partner.html')


@app.route('/admin/pending')
def admin_pending():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pending_applications")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("pending.html", data=data)


USERNAME_PATTERN = r'^[A-Za-z0-9_]{3,20}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$'
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Email is already registered. Please log in or use a different email.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('signup'))

        if not re.fullmatch(USERNAME_PATTERN, username):
            flash("Invalid username! Use 3-20 characters (letters, numbers, underscore).", "error")
            return redirect(url_for('signup'))

        if not re.fullmatch(EMAIL_PATTERN, email):
            flash("Invalid email format!", "error")
            return redirect(url_for('signup'))

        if not re.fullmatch(PASSWORD_PATTERN, raw_password):
            flash("Weak password! Must contain:\n"
                  "- Minimum 8 characters\n"
                  "- At least 1 uppercase letter\n"
                  "- At least 1 lowercase letter\n"
                  "- At least 1 digit\n"
                  "- At least 1 special character (@$!%*?&)", "error")
            return redirect(url_for('signup'))

        password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        cur.execute("INSERT INTO users(name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, "user"))
        conn.commit()

        cur.close()
        conn.close()

        flash("Signup successful! Please login now.", "success")
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            flash("Logged in successfully.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/what_we_offer')
def what_we_offer():
    return render_template('what_we_offer.html')


@app.route('/admin')
def admin_page():
    return redirect(url_for('admin_login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com" and password == "admin1234":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_login.html', error="Invalid Credentials")

    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM pending_applications")
    data = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', data=data)


@app.route('/accept/<int:id>', methods=['POST'])
def accept(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM pending_applications WHERE id=%s", (id,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return "Application not found", 404

    try:
        cursor.execute("""
            INSERT INTO approved_businesses
            (full_name_or_business_name, state, city, category, cost_for_two,
            location, contact_number, email, password_hash,
            photo1, photo2, photo3, photo4, photo5,
            electricity_bill, additional_notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['full_name_or_business_name'],
            row['state'],
            row['city'],
            row['category'],
            row['cost_for_two'],
            row['location'],
            row['contact_number'],
            row['email'],
            row['password_hash'],
            row['photo1'],
            row['photo2'],
            row['photo3'],
            row['photo4'],
            row['photo5'],
            row['electricity_bill'],
            row.get('additional_notes')
        ))

        cursor.execute("""
            INSERT INTO business_listings
            (name, location, city, state, category, cost_for_two,
            photo1, photo2, photo3, photo4, photo5)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['full_name_or_business_name'],
            row['location'],
            row['city'],
            row['state'],
            row['category'],
            row['cost_for_two'],
            row['photo1'],
            row['photo2'],
            row['photo3'],
            row['photo4'],
            row['photo5']
        ))

        cursor.execute("DELETE FROM pending_applications WHERE id=%s", (id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return f"Error while accepting application: {e}", 500

    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/reject/<int:id>', methods=['POST'])
def reject(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pending_applications WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
