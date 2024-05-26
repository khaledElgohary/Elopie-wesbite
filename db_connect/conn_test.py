#DEMO FOR DATABASE API
from db_connector import *

#create connection returns connection object
conn = create_connection()

#pass conn to search along with input tokens to
#returns a list of tuples
result = search_by_courseID(conn, "comp", "3380")

#pass conn to close
close_connection(conn)

#simple print to show tuples
print(result)
