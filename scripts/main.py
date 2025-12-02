from createDB import *  
import random
import pickle  

'''
Run to test
'''


def insert_sample_data():
    """Insert at least 20 sample records into major tables"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert CEREMONIES
        ceremonies = [
            ('Fall 2025 College of Engineering Ceremony', '2025-05-15 10:00:00', 'Lane Stadium', '10:00:00', '12:00:00'),
            ('Fall 2025 College of Science Ceremony', '2025-05-15 14:00:00', 'Lane Stadium', '14:00:00', '16:00:00'),
            ('Fall 2025 College of Business Ceremony', '2025-12-18 10:00:00', 'Cassell Coliseum', '10:00:00', '12:00:00'),
            ('Fall 2025 College of Arts Ceremony', '2025-12-18 14:00:00', 'Cassell Coliseum', '14:00:00', '16:00:00'),
        ]
        
        cursor.executemany("""
            INSERT INTO CEREMONY (name, date_time, location, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
        """, ceremonies)
        print(f"✓ Inserted {len(ceremonies)} ceremonies.")

        degrees = [
            # Engineering (1)
            ('Computer Science', 1),
            ('Computer Engineering', 1),
            ('Electrical Engineering', 1),
            ('Mechanical Engineering', 1),
            ('Industrial & Systems Engineering', 1),
            ('Chemical Engineering', 1),
            ('Civil Engineering', 1),
            ('Aerospace Engineering', 1),
            ('Materials Science & Engineering', 1),

            # Science (2)
            ('Biology', 2),
            ('Chemistry', 2),
            ('Physics', 2),
            ('Mathematics', 2),
            ('Statistics', 2),
            ('Biochemistry', 2),
            ('Neuroscience', 2),
            ('Geosciences', 2),

            # Business (3)
            ('Accounting', 3),
            ('Finance', 3),
            ('Marketing', 3),
            ('Management', 3),
            ('Business Information Technology', 3),
            ('Economics', 3),

            # Arts (4)
            ('English', 4),
            ('History', 4),
            ('Philosophy', 4),
            ('Political Science', 4),
            ('Sociology', 4),
            ('Psychology', 4),
            ('Communication', 4),
            ('Studio Art', 4),
            ('Music', 4),
        ]

        cursor.executemany("""
            INSERT INTO DEGREE (degree_name, ceremony_id)
            VALUES (%s, %s)
        """, degrees)
        print(f"✓ Inserted {len(degrees)} degrees.")

        
        # Insert STUDENTS (20+ records)
        students = [
            ('PID001', 'John Smith', 'jsmith@vt.edu', 'Economics', 'BS', True),
            ('PID002', 'Emily Johnson', 'ejohnson@vt.edu', 'Computer Science', 'MS', True),
            ('PID003', 'Michael Brown', 'mbrown@vt.edu', 'Electrical Engineering', 'BS', True),
            ('PID004', 'Sarah Davis', 'sdavis@vt.edu', 'Management', 'PhD', False),
            ('PID005', 'David Wilson', 'dwilson@vt.edu', 'Communication', 'BS', True),
            ('PID006', 'Jessica Martinez', 'jmartinez@vt.edu', 'Computer Science', 'MS', True),
            ('PID007', 'James Anderson', 'janderson@vt.edu', 'Mathematics', 'BS', True),
            ('PID008', 'Ashley Taylor', 'ataylor@vt.edu', 'Finance', 'BS', True),
            ('PID009', 'Christopher Thomas', 'cthomas@vt.edu', 'Civil Engineering', 'MS', False),
            ('PID010', 'Amanda Jackson', 'ajackson@vt.edu', 'Business Information Technology', 'BS', True),
            ('PID011', 'Matthew White', 'mwhite@vt.edu', 'Business Information Technology', 'BS', True),
            ('PID012', 'Jennifer Harris', 'jharris@vt.edu', 'Marketing', 'MS', True),
            ('PID013', 'Daniel Martin', 'dmartin@vt.edu', 'Political Science', 'BS', True),
            ('PID014', 'Lauren Thompson', 'lthompson@vt.edu', 'Business Information Technology', 'BS', False),
            ('PID015', 'Joshua Garcia', 'jgarcia@vt.edu', 'Statistics', 'PhD', True),
            ('PID016', 'Nicole Martinez', 'nmartinez@vt.edu', 'Sociology', 'MS', True),
            ('PID017', 'Andrew Robinson', 'arobinson@vt.edu', 'Geosciences', 'BS', True),
            ('PID018', 'Stephanie Clark', 'sclark@vt.edu', 'Biology', 'BS', True),
            ('PID019', 'Ryan Rodriguez', 'rrodriguez@vt.edu', 'Chemical Engineering', 'BS', True),
            ('PID020', 'Michelle Lewis', 'mlewis@vt.edu', 'Chemical Engineering', 'MS', False),
            ('PID021', 'Kevin Lee', 'klee@vt.edu', 'Studio Art', 'BS', True),
            ('PID022', 'Rachel Walker', 'rwalker@vt.edu', 'Physics', 'MS', True),
        ]
        
        cursor.executemany("""
            INSERT INTO STUDENT (PID, name, email, degree_name, degree_type, opt_in_biometric)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, students)
        print(f"✓ Inserted {len(students)} students.")
        
        
        
        # Insert STAFF
        staff = [
            ('STAFF001', 'Dr. Robert Johnson', 'rjohnson@vt.edu', 'active'),
            ('STAFF002', 'Dr. Maria Garcia', 'mgarcia@vt.edu', 'active'),
            ('STAFF003', 'Prof. William Chen', 'wchen@vt.edu', 'active'),
            ('STAFF004', 'Dr. Linda Martinez', 'lmartinez@vt.edu', 'active'),
            ('STAFF005', 'Prof. James Wilson', 'jwilson@vt.edu', 'active'),
        ]
        
        cursor.executemany("""
            INSERT INTO STAFF (staff_id, name, email, status)
            VALUES (%s, %s, %s, %s)
        """, staff)
        print(f"✓ Inserted {len(staff)} staff members.")
        
        # Insert FACE_IMAGES (for students who opted in)
        face_images_no_emb = [
            ('PID001', '/images/faces/PID001_face.jpg'),
            ('PID002', '/images/faces/PID002_face.jpg'),
            ('PID003', '/images/faces/PID003_face.jpg'),
            ('PID005', '/images/faces/PID005_face.jpg'),
            ('PID006', '/images/faces/PID006_face.jpg'),
            ('PID007', '/images/faces/PID007_face.jpg'),
            ('PID008', '/images/faces/PID008_face.jpg'),
            ('PID010', '/images/faces/PID010_face.jpg'),
            ('PID011', '/images/faces/PID011_face.jpg'),
            ('PID012', '/images/faces/PID012_face.jpg'),
            ('PID013', '/images/faces/PID013_face.jpg'),
            ('PID015', '/images/faces/PID015_face.jpg'),
            ('PID016', '/images/faces/PID016_face.jpg'),
            ('PID017', '/images/faces/PID017_face.jpg'),
            ('PID018', '/images/faces/PID018_face.jpg'),
            ('PID019', '/images/faces/PID019_face.jpg'),
            ('PID021', '/images/faces/PID021_face.jpg'),
            ('PID022', '/images/faces/PID022_face.jpg'),
        ]

        script_dir = os.path.dirname(os.path.abspath(__file__))  # folder containing this script
        embeddings_dir = os.path.join(script_dir, "embeddings.pkl") 

        with open(embeddings_dir, "rb") as f:
            loaded_embeddings = pickle.load(f)


        face_images = [
            (pid, path, emb)
            for (pid, path), emb in zip(face_images_no_emb, loaded_embeddings)
        ]

        cursor.executemany("""
            INSERT INTO FACE_IMAGE (SPID, storage_uri, embedding)
            VALUES (%s, %s, %s)
        """, face_images)
        print(f"✓ Inserted {len(face_images)} face images.")
        
        # Insert MANAGES relationships
        manages = [
            ('STAFF001', 1, 'Coordinator'),
            ('STAFF002', 1, 'Assistant'),
            ('STAFF003', 2, 'Coordinator'),
            ('STAFF004', 2, 'Assistant'),
            ('STAFF005', 3, 'Coordinator'),
            ('STAFF001', 4, 'Assistant'),
        ]
        
        cursor.executemany("""
            INSERT INTO MANAGES (staff_id, ceremony_id, role)
            VALUES (%s, %s, %s)
        """, manages)
        print(f"✓ Inserted {len(manages)} staff-ceremony assignments.")
        
        # Insert QUEUED relationships (students registered for ceremonies)
        queued = [
            ('PID001', 3, '2025-05-15 09:30:00', 'pending'),
            ('PID002', 1, '2025-05-15 13:45:00', 'pending'),
            ('PID003', 1, '2025-05-15 09:25:00', 'pending'),
            ('PID004', 3, '2025-05-15 13:30:00', 'pending'),
            ('PID005', 4, '2025-05-15 09:40:00', 'pending'),
            ('PID006', 1, '2025-05-15 13:50:00', 'pending'),
            ('PID007', 2, '2025-05-15 09:35:00', 'pending'),
            ('PID008', 3, '2025-05-15 09:45:00', 'pending'),
            ('PID009', 1, '2025-05-15 13:40:00', 'pending'),
            ('PID010', 3, '2025-05-15 09:28:00', 'pending'),
            ('PID011', 3, '2025-05-15 09:32:00', 'pending'),
            ('PID012', 3, '2025-05-15 13:42:00', 'pending'),
            ('PID013', 4, '2025-05-15 09:38:00', 'pending'),
            ('PID014', 3, '2025-05-15 09:50:00', 'pending'),
            ('PID015', 2, '2025-05-15 13:35:00', 'pending'),
            ('PID016', 4, '2025-05-15 13:38:00', 'pending'),
            ('PID017', 2, '2025-05-15 09:42:00', 'pending'),
            ('PID018', 2, '2025-05-15 09:48:00', 'pending'),
            ('PID019', 1, '2025-05-15 09:33:00', 'pending'),
            ('PID020', 1, '2025-05-15 13:48:00', 'pending'),
            ('PID021', 4, '2025-05-15 09:36:00', 'pending'),
            ('PID022', 2, '2025-05-15 13:52:00', 'pending'),
        ]
        
        cursor.executemany("""
            INSERT INTO QUEUED (SPID, ceremony_id, time_queued, status)
            VALUES (%s, %s, %s, %s)
        """, queued)
        print(f"✓ Inserted {len(queued)} student queue records.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✓ All sample data inserted successfully!")
        
    except Exception as e:
        print(f"✗ Error inserting sample data: {e}")


def verify_data():
    """Verify the data was inserted correctly, including user accounts"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        tables = ['STUDENT', 'DEGREE', 'CEREMONY', 'STAFF', 'FACE_IMAGE', 'MANAGES', 'QUEUED', 'USER_ACCOUNT']
        
        print("\n" + "="*50)
        print("DATABASE VERIFICATION")
        print("="*50)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")

        # Extra: show basic info about user accounts (e.g., how many admins)
        cursor.execute("SELECT COUNT(*) FROM USER_ACCOUNT WHERE is_admin = TRUE;")
        admin_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM USER_ACCOUNT WHERE is_admin = FALSE;")
        user_count = cursor.fetchone()[0]
        print(f"\nUSER_ACCOUNT details -> admins: {admin_count}, non-admins: {user_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error verifying data: {e}")


def main():
    print("Starting PostgreSQL Database Setup...")
    print("="*50)

    create_database()
    create_tables()
    # NEW: create USER_ACCOUNT table and seed the first admin
    create_user_table_and_seed_admin()

    insert_sample_data()
    verify_data()

    print("\n" + "="*50)
    print("Database setup complete!")
    print("="*50)
    print(f"\nDatabase Name: {DB_CONFIG['dbname']}")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Port: {DB_CONFIG['port']}")


if __name__ == "__main__":
    main()
