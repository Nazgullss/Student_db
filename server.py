from http.server import BaseHTTPRequestHandler , HTTPServer
import json 
import urllib.parse
import mysql.connector


# This is the DB helper 
def get_DB():
    return mysql.connector.connect(
        host = "localhost" ,
        user = "root" ,
        password = "Pranav.init@2004" ,
        database = "Student_db"
    )

def fetch_students():
    db = get_DB()
    cursor = db.cursor(dictionary = True)
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    db.close()
    return rows 

# Insert one student in the database 
def insert_student(data):
    db = get_DB()
    cursor = db.cursor()
    try: 
        cursor.execute(
            "INSERT INTO students(Name , roll_no , mobile_no , address_pincode) VALUES (%s , %s , %s , %s)" ,
            (data["Name"] , data["roll_no"] , data["mobile_no"] , data["address_pincode"])
        )
        db.commit()
    except Exception as e :
        print("Error:" , e)
        db.rollback()
    finally:
        db.close()
    

# building the HTML page 
def build_html(students):
    rows = ""
    for s in students :
        rows += f"""
        <tr> 
            <td>{s['id']}</td>
            <td>{s['Name']}</td>
            <td>{s['roll_no']}</td>
            <td>{s['mobile_no']}</td>
            <td>{s['address_pincode']}</td>
        </tr>"""  

        
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title> Student Records </title>
        <style>
            body {{font-family: Ariel; padding:30px;}} 
            input {{ margin: 5px; padding: 8px; width: 180px; }}
            button {{ padding: 9px 20px; background: #4CAF50; color: white; border: none; cursor: pointer; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 25px; }}
            th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
            th {{ background: #4CAF50; color: white; }}
            #msg {{ color: green; margin-top: 10px; }}
        </style>
    </head>
    <body> 
        <h2> Add student </h2>
        <input id="Name" placeholder="Name" />
        <input id="roll_no" placeholder="Roll No" />
        <input id="mobile_no" placeholder="Mobile No" />
        <input id="pincode" placeholder="Pincode" />
        <button onclick="addStudent()">Add</button>
        <p id="msg"></p>

        <h2>All Students</h2>
        <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Name</th><th>Roll No</th>
                        <th>Mobile</th><th>Pincode</th>
                    </tr>
                </thead>
                <tbody id="tbody">
                    {rows}
                </tbody>
        </table>

        <script>
            async function addStudent() {{
                const payload = {{
                    Name:             document.getElementById("Name").value,
                    roll_no:          document.getElementById("roll_no").value,
                    mobile_no:        document.getElementById("mobile_no").value,
                    address_pincode:  document.getElementById("pincode").value,
                }};
                const res  = await fetch("/add_student", {{
                    method:  "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body:    JSON.stringify(payload)
                }});
                const data = await res.json();
                document.getElementById("msg").textContent = data.message;

                // Refresh the table without reloading page
                const res2 = await fetch("/get_students");
                const students = await res2.json();
                const tbody = document.getElementById("tbody");
                tbody.innerHTML = "";
                students.forEach(s => {{
                    tbody.innerHTML += `<tr>
                        <td>${{s.id}}</td>
                        <td>${{s.Name}}</td>
                        <td>${{s.roll_no}}</td>
                        <td>${{s.mobile_no}}</td>
                        <td>${{s.address_pincode}}</td>
                    </tr>`;
                }});
            }}
        </script>

    </body>
    </html>
    """

# Request Handler.........................
class Handler(BaseHTTPRequestHandler):

    # GET request 
    def do_GET(self):
        if self.path == "/":
            #Serve the HTMl page 
            students = fetch_students()
            html = build_html(students)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/get_students":
            # Return all students as JSON (used by JS fetch)
            students = fetch_students()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(students).encode("utf-8"))
        else :
            self.send_response(404)
            self.end_headers()

    # Post Request 
    def do_POST(self):

        if self.path == "/add_student":
            # Read body
            length = int(self.headers["Content-Length"])
            body   = self.rfile.read(length)
            data   = json.loads(body)

            insert_student(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"message": "Student added successfully!"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    # Silence the default request logs (optional)
    def log_message(self, format, *args):
        print(f"  → {args[0]} {args[1]}")


# ─── Start the server ────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), Handler)
    print("Server running at http://localhost:8080")
    server.serve_forever()

        









    




