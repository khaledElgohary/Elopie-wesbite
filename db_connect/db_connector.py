import sqlite3 

sql_file_name = "entries.sql"
db_name = "entries.db"

def create_connection():
    db_conn = sqlite3.connect(db_name)

    db_cursor = db_conn.cursor()

    with open(sql_file_name, "r") as file:
        sql_content = file.read()
    
    db_cursor.executescript(sql_content)

    db_conn.commit()

    return db_conn


def validate_input(input_str):
    valid = True
    if(input_str is None):
        valid = False
    else:
        injection_str = ['INSERT', 'DELETE', 'DROP', '=', 'OR', 'CREATE', 'JOIN', '--', 'WHERE', '*', '>', '<', 'ADD']
        for entry in injection_str:
            if(entry in input_str.upper()):
                valid = False
    return valid

def search_by_courseID(db_conn, faculty_code, course_num):
    query_result = None

    if(db_conn is not None and validate_input(faculty_code) and validate_input(course_num)):
        db_cursor = db_conn.cursor()
        faculty_code = faculty_code.upper()
        course_num = course_num.upper()
        query = "SELECT * FROM Entry WHERE uofm_course_details LIKE '%" + faculty_code + "%' AND  uofm_course_details LIKE '%" + course_num + "%';"
        db_cursor.execute(query)
        query_result = db_cursor.fetchall()
    
    return query_result

def close_connection(db_conn):
    if(db_conn is not None):
        db_conn.close()

def dummy(db_conn):
    db_cursor = db_conn.cursor()
    db_cursor.execute("SELECT * FROM Entry WHERE province LIKE '%Manitoba%';")
    return db_cursor.fetchall()





    










