from flask import Flask, render_template, url_for, request
from db_connect import db_connector
from db_connect.db_connector import search_by_courseID

app = Flask(__name__, static_url_path='/static', static_folder='static')


@app.route('/')
def home():
    # Just render the template if it's a GET request to the home page
    return render_template('index.html')


@app.route('/generate_course_code', methods=['POST'])
def generate_course_code():
    # Extract form data
    faculty_code = request.form.get('uname')
    course_num = request.form.get('cnumber')

    # Establish connection to the database
    db_conn = db_connector.create_connection()

    # Perform the search
    courses = search_by_courseID(db_conn, faculty_code, course_num)

    # Close the database connection
    db_connector.close_connection(db_conn)

    # Render the template with courses data
    return render_template('index.html', courses=courses)


if __name__ == "__main__":
    app.run(debug=True)