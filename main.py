<<<<<<< HEAD
"""
main.py
───────
End-to-end demo. Exercises every feature in correct dependency order.

Run:
    python main.py

On first run: deploys all 7 contracts, binds sub-contracts, grants roles.
Subsequent runs reuse deployed addresses from config.json.
"""
from python.datasource.university_ds import UniversityDataSource

ds = UniversityDataSource()


def hr(title: str) -> None:
    print(f"\n{'═' * 62}")
    print(f"  {title}")
    print('═' * 62)


def print_transcript(student_id: int) -> None:
    student    = ds.get_student(student_id)
    major      = ds.get_major(student.major_id)
    transcript = ds.get_full_transcript(student_id)
    print(f"\n  ── {student.name}  [{major.code}]  (ID {student_id}) ──")
    if not transcript:
        print("     (no enrollments)")
        return
    for sem in transcript:
        gpa_str = f"{sem.gpa:.2f}/4.00" if sem.gpa is not None else "ungraded"
        print(f"  [{sem.semester}]  courses={sem.total_courses}  graded={sem.graded_count}  GPA={gpa_str}")
        for e in sem.enrollments:
            if e.mark > 0:
                mark_str = f"{e.mark:>3}/100  {e.grade:<3}  {e.gpa_points:.1f}/4.0"
            else:
                mark_str = "  —/100  —    —/4.0"
            flag = "" if e.active else " (dropped)"
            print(f"    {e.course_id:<12}  {mark_str}{flag}")


if __name__ == "__main__":

    from python.blockchain.provider import get as get_w3
    w3       = get_w3()
    accounts = w3.eth.accounts   # Anvil pre-funded accounts

    # ─────────────────────────────────────────────────────────────────────────
    hr("1 · Majors")
    ds.add_major("CS",  "Computer Science",       "Software, systems, algorithms")
    ds.add_major("AI",  "Artificial Intelligence","ML, NLP, computer vision")
    ds.add_major("IT",  "Information Technology", "Networks, sysadmin, security")
    ds.add_major("CYB", "Cybersecurity",           "Offensive and defensive security")
    ds.add_major("EE",  "Electrical Engineering",  "Circuits, signals, embedded systems")

    for m in ds.get_all_majors():
        print(f"  [{m.id}] {m.code:<5} — {m.name}")

    # ─────────────────────────────────────────────────────────────────────────
    hr("2 · Professors  (each needs a distinct address — not the deployer's)")
    # Anvil account[0] is the deployer. Use accounts[1..3] for professors.
    prof_addrs = accounts[1], accounts[2], accounts[3]

    ds.add_professor("Dr. Smith",   "Computer Science", prof_addrs[0])
    ds.add_professor("Dr. Johnson", "Mathematics",      prof_addrs[1])
    ds.add_professor("Dr. Chen",    "Cybersecurity",    prof_addrs[2])

    for p in ds.get_all_professors():
        print(f"  [{p.id}] {p.name:<22} dept={p.department:<22} addr={p.professor_address[:14]}…")

    # ─────────────────────────────────────────────────────────────────────────
    hr("3 · Students")
    ds.add_student("Alice",  major_id=1, year=2024, professor_id=1)
    ds.add_student("Bob",    major_id=2, year=2024, professor_id=2)
    ds.add_student("Carol",  major_id=3, year=2023, professor_id=1)
    ds.add_student("Dave",   major_id=4, year=2025, professor_id=3)
    ds.add_student("Eve",    major_id=1, year=2025, professor_id=2)

    for s in ds.get_all_students():
        major = ds.get_major(s.major_id)
        print(f"  [{s.id}] {s.name:<10} major={major.code:<5} year={s.year}  supervisor={s.academic_supervisor[:14]}…")

    # ─────────────────────────────────────────────────────────────────────────
    hr("4 · Courses")
    ds.create_course("CS101",   "Intro to Programming",   professor_id=1)
    ds.create_course("CS201",   "Data Structures",        professor_id=1)
    ds.create_course("AI301",   "Machine Learning",       professor_id=2)
    ds.create_course("MATH101", "Discrete Mathematics",   professor_id=2)
    ds.create_course("CYB401",  "Network Security",       professor_id=3)

    for c in ds.get_all_courses():
        p = ds.get_professor(c.professor_id)
        print(f"  {c.id:<10}  {c.name:<30}  ({p.name})")

    # ─────────────────────────────────────────────────────────────────────────
    hr("5 · Enrollment — spring2025")
    SEM_A = "spring2025"
    ds.enroll(SEM_A, student_id=1, course_id="CS101")
    ds.enroll(SEM_A, student_id=1, course_id="MATH101")
    ds.enroll(SEM_A, student_id=2, course_id="AI301")
    ds.enroll(SEM_A, student_id=2, course_id="MATH101")
    ds.batch_enroll(SEM_A, student_ids=[3, 4, 5], course_id="CS101")
    print(f"  Enrolled spring2025. Course CS101 roster:")
    for e in ds.get_course_enrollments("CS101"):
        if e.active:
            s = ds.get_student(e.student_id)
            print(f"    student {e.student_id} — {s.name}")

    # ─────────────────────────────────────────────────────────────────────────
    hr("6 · Marks — spring2025")
    ds.update_mark(SEM_A, student_id=1, course_id="CS101",   mark=88)
    ds.update_mark(SEM_A, student_id=1, course_id="MATH101", mark=74)
    ds.update_mark(SEM_A, student_id=2, course_id="AI301",   mark=91)
    ds.update_mark(SEM_A, student_id=2, course_id="MATH101", mark=83)
    ds.update_mark(SEM_A, student_id=3, course_id="CS101",   mark=67)
    ds.update_mark(SEM_A, student_id=4, course_id="CS101",   mark=79)
    ds.update_mark(SEM_A, student_id=5, course_id="CS101",   mark=95)
    print("  Marks recorded for spring2025.")

    # ─────────────────────────────────────────────────────────────────────────
    hr("7 · Enrollment — autumn2025  (second semester)")
    SEM_B = "autumn2025"
    ds.enroll(SEM_B, student_id=1, course_id="CS201")
    ds.enroll(SEM_B, student_id=1, course_id="AI301")
    ds.enroll(SEM_B, student_id=2, course_id="CS201")
    ds.enroll(SEM_B, student_id=3, course_id="CYB401")
    ds.enroll(SEM_B, student_id=5, course_id="CS201")
    ds.enroll(SEM_B, student_id=5, course_id="CYB401")
    ds.update_mark(SEM_B, student_id=1, course_id="CS201",  mark=92)
    ds.update_mark(SEM_B, student_id=1, course_id="AI301",  mark=85)
    ds.update_mark(SEM_B, student_id=2, course_id="CS201",  mark=77)
    ds.update_mark(SEM_B, student_id=3, course_id="CYB401", mark=95)
    ds.update_mark(SEM_B, student_id=5, course_id="CS201",  mark=89)
    ds.update_mark(SEM_B, student_id=5, course_id="CYB401", mark=93)
    print("  autumn2025 enrollments and marks recorded.")

    # ─────────────────────────────────────────────────────────────────────────
    hr("8 · Transcripts")
    for sid in [1, 2, 3, 5]:
        print_transcript(sid)

    # ─────────────────────────────────────────────────────────────────────────
    hr("9 · GPA overview  (4.0 scale)")
    for sid in [1, 2, 3, 4, 5]:
        try:
            s   = ds.get_student(sid)
            gpa = ds.get_gpa(sid)
            gpa_str = f"{gpa:.2f}/4.00" if gpa is not None else "no grades yet"
            print(f"  {s.name:<10}  cumulative GPA = {gpa_str}")
        except Exception as exc:
            print(f"  student {sid}: {exc}")

    # ─────────────────────────────────────────────────────────────────────────
    hr("10 · RBAC — grant registrar to accounts[4]")
    reg_addr = accounts[4]
    ds.grant_role("REGISTRAR_ROLE", reg_addr)
    roles = ds.get_all_roles()
    print(f"  ADMIN_ROLE:      {roles['ADMIN_ROLE']}")
    print(f"  REGISTRAR_ROLE:  {roles['REGISTRAR_ROLE']}")
    print(f"  INSTRUCTOR_ROLE: {[a[:14]+'…' for a in roles['INSTRUCTOR_ROLE']]}")

    # ─────────────────────────────────────────────────────────────────────────
    hr("11 · Unenroll — Alice drops MATH101 from spring2025")
    ds.unenroll(SEM_A, student_id=1, course_id="MATH101")
    print("  Alice's spring2025 after drop:")
    for e in ds.get_semester_enrollments(1, SEM_A):
        status = "active" if e.active else "dropped"
        print(f"    {e.course_id}  mark={e.mark}  ({status})")

    # ─────────────────────────────────────────────────────────────────────────
    hr("12 · Cascade delete — delete Dr. Johnson (removes AI301, MATH101)")
    before = [c.id for c in ds.get_all_courses()]
    print(f"  Courses before: {before}")
    ds.delete_professor(professor_id=2)
    after = [c.id for c in ds.get_all_courses()]
    print(f"  Courses after:  {after}")
    print(f"  INSTRUCTOR_ROLE after: {[a[:14]+'…' for a in ds.get_all_roles()['INSTRUCTOR_ROLE']]}")

    # ─────────────────────────────────────────────────────────────────────────
    hr("13 · Retake — Alice re-enrolls in CS101 spring2026")
    SEM_C = "spring2026"
    ds.enroll(SEM_C, student_id=1, course_id="CS101")
    ds.update_mark(SEM_C, student_id=1, course_id="CS101", mark=97)
    print_transcript(1)

    # ─────────────────────────────────────────────────────────────────────────
    hr("14 · Full system status")
    print(f"\n  Professors: {len(ds.get_all_professors())}")
    print(f"  Students:   {len(ds.get_all_students())}")
    print(f"  Courses:    {len(ds.get_all_courses())}")
    print(f"  Majors:     {len(ds.get_all_majors())}")

    print("\n  ✓ Demo complete.")
 
=======
from datasource.university_datasource import UniversityDataSource
from utils.project_components import get_web3, get_config
from web3.exceptions import ContractLogicError

w3 = get_web3()
deployer_address = get_config()["deployer_address"]

university_datasource = UniversityDataSource(
    account_address=deployer_address,
    admin_address=deployer_address,
    web3_provider=w3
)

def print_student(student_id):
    try:
        student = university_datasource.get_student(student_id)
        print(f"\nStudent ID: {student['id']}")
        print(f"Name: {student['name']}")
        print(f"Major: {student['major']}")
        print(f"Year: {student['year']}")
        print(f"Academic Supervisor: {student['academicSupervisor']}")
        print(f"Active: {'Yes' if student['active'] else 'No'}")
    except Exception as e:
        print(f"Error retrieving student: {str(e)}")

def print_professor(professor_id):
    try:
        prof = university_datasource.get_professor(professor_id)
        print(f"\nProfessor ID: {prof['id']}")
        print(f"Name: {prof['name']}")
        print(f"Department: {prof['department']}")
        print(f"Address: {prof['professorAddress']}")
        print(f"Active: {'Yes' if prof['active'] else 'No'}")
    except Exception as e:
        print(f"Error retrieving professor: {str(e)}")

def print_enrollments(student_id):
    try:
        enrollments = university_datasource.get_student_enrollments(student_id)
        if not enrollments:
            print("No enrollments found")
            return

        print(f"\nEnrollments for Student {student_id}:")
        for idx, enrollment in enumerate(enrollments, 1):
            print(f"{idx}. Course: {enrollment['course_id']}")
            print(f"   Mark: {enrollment['mark']}")
            print(f"   Status: {'Active' if enrollment['active'] else 'Inactive'}")
    except Exception as e:
        print(f"Error retrieving enrollments: {str(e)}")

def print_course_enrollments(course_id):
    try:
        enrollments = university_datasource.get_course_enrollments(course_id)
        if not enrollments:
            print("No enrollments found")
            return

        print(f"\nEnrollments for Course {course_id}:")
        for idx, enrollment in enumerate(enrollments, 1):
            print(f"{idx}. Student: {enrollment['student_id']} ({enrollment['student_name']})")
            print(f"   Mark: {enrollment['mark']}")
            print(f"   Status: {'Active' if enrollment['active'] else 'Inactive'}")
    except Exception as e:
        print(f"Error retrieving course enrollments: {str(e)}")

def print_course(course_id):
    try:
        course = university_datasource.get_course(course_id)
        print(f"\nCourse ID: {course['id']}")
        print(f"Name: {course['name']}")
        print(f"Professor ID: {course['professorId']}")
        print(f"Active: {'Yes' if course['active'] else 'No'}")
    except Exception as e:
        print(f"Error retrieving course: {str(e)}")

def wait_for_tx(tx_hash):
    """Wait for transaction to be mined and print result"""
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    status = "Success" if receipt["status"] == 1 else "Failed"
    print(f"Transaction {status}: {tx_hash.hex()}")
    return receipt

# Main execution
if __name__ == "__main__":
    # First ensure we're connected to the network
    if not w3.is_connected():
        print("Failed to connect to Ethereum provider!")
        exit(1)

    print("\n=== Connected to Ethereum network ===")
    print(f"Current block number: {w3.eth.block_number}")

    # Example 1: Initialize System
    print("\n=== Initializing System ===")
    try:
        # Add initial professors
        tx_hash = university_datasource.add_professor("Dr. Smith", "Computer Science")
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.add_professor("Dr. Johnson", "Mathematics")
        wait_for_tx(tx_hash)

        # Add initial students
        tx_hash = university_datasource.add_student("Alice", "Computer Science", 2025, 1)
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.add_student("Bob", "Mathematics", 2026, 2)
        wait_for_tx(tx_hash)

        # Create courses
        tx_hash = university_datasource.create_course("CS101", "Introduction to Programming", 1)
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.create_course("MATH201", "Linear Algebra", 2)
        wait_for_tx(tx_hash)

        print("System initialized with 2 professors, 2 students, and 2 courses")
    except ContractLogicError as e:
        print(f"Initialization error: {e.message}")
    except Exception as e:
        print(f"Error initializing system: {str(e)}")

    # Example 2: Enrollment Operations
    print("\n=== Enrollment Operations ===")
    try:
        # Enroll students
        tx_hash = university_datasource.enroll_student_in_course(1, "CS101")
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.enroll_student_in_course(1, "MATH201")
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.enroll_student_in_course(2, "MATH201")
        wait_for_tx(tx_hash)

        # Print enrollment details
        print_enrollments(1)
        print_course_enrollments("MATH201")

        # Update marks
        tx_hash = university_datasource.update_student_mark(1, "CS101", 85)
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.update_student_mark(1, "MATH201", 78)
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.update_student_mark(2, "MATH201", 92)
        wait_for_tx(tx_hash)

        print("\nAfter updating marks:")
        print_enrollments(1)
        print_course_enrollments("MATH201")

        # Unenroll a student
        tx_hash = university_datasource.remove_course_from_student(1, "MATH201")
        wait_for_tx(tx_hash)

        print("\nAfter unenrolling Alice from MATH201:")
        print_enrollments(1)
        print_course_enrollments("MATH201")
    except ContractLogicError as e:
        print(f"Enrollment error: {e.message}")
    except Exception as e:
        print(f"Error during enrollment operations: {str(e)}")

    # Example 3: Batch Operations
    print("\n=== Batch Operations ===")
    try:
        # Batch enroll students
        tx_hash = university_datasource.batch_enroll_students([1, 2], "CS101")
        wait_for_tx(tx_hash)

        # Batch update marks
        tx_hash = university_datasource.update_student_mark(1, "CS101", 88)
        wait_for_tx(tx_hash)
        tx_hash = university_datasource.update_student_mark(2, "CS101", 95)
        wait_for_tx(tx_hash)

        print("\nAfter batch operations:")
        print_enrollments(1)
        print_enrollments(2)
        print_course_enrollments("CS101")
    except Exception as e:
        print(f"Error during batch operations: {str(e)}")

    # Example 4: Comprehensive System Check
    print("\n=== System Status ===")
    try:
        print("\nProfessors:")
        for prof_id in university_datasource.get_all_professors():
            print_professor(prof_id)

        print("\nStudents:")
        for student_id in university_datasource.get_all_students():
            print_student(student_id)

        print("\nCourses:")
        for course_id in university_datasource.get_all_courses():
            print_course(course_id)

        print("\nAll Enrollments:")
        for student_id in university_datasource.get_all_students():
            print_enrollments(student_id)
    except Exception as e:
        print(f"Error during system check: {str(e)}")

    print("\n=== Demo Complete ===")
>>>>>>> 04f4ed994e9d658d55c20cf71bc416aa1d133cef
