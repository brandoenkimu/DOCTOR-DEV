#!C:\Program Files\Python313\python.exe
import bcrypt
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import mysql.connector

print("Content-Type: text/html\n")
print("<html><body><h1>Password Test</h1>")

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Harooh13317265@',
        database='clinic_system'
    )
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if admin:
        print(f"<p>Admin found: {admin['username']}</p>")
        print(f"<p>Stored hash: {admin['password_hash']}</p>")
        
        # Test the password
        if bcrypt.checkpw(b'Admin@123', admin['password_hash'].encode('utf-8')):
            print("<p style='color:green'>Password 'Admin@123' is CORRECT!</p>")
        else:
            print("<p style='color:red'>Password 'Admin@123' is INCORRECT!</p>")
            
        # Generate a new hash for reference
        new_hash = bcrypt.hashpw(b'Admin@123', bcrypt.gensalt()).decode()
        print(f"<p>New sample hash: {new_hash}</p>")
    else:
        print("<p>Admin user not found!</p>")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"<p>Error: {e}</p>")

print("</body></html>")