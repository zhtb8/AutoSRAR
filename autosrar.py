import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QListWidget, QMessageBox, QComboBox, QCheckBox
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SRARApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Self-Reported Academic Record")
        self.setGeometry(100, 100, 600, 500)

        self.courses = []
        self.driver = None  # To store the Selenium driver

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Grade Level Dropdown
        grade_level_layout = QHBoxLayout()
        self.grade_level_label = QLabel("Grade Level:")
        self.grade_level_dropdown = QComboBox()
        self.grade_level_dropdown.addItems([
            "Middle School", "9th Grade", "10th Grade", "11th Grade", "12th Grade"
        ])
        grade_level_layout.addWidget(self.grade_level_label)
        grade_level_layout.addWidget(self.grade_level_dropdown)
        layout.addLayout(grade_level_layout)

        # Course Name
        name_layout = QHBoxLayout()
        self.course_name_label = QLabel("Course Name:")
        self.course_name_input = QLineEdit()
        name_layout.addWidget(self.course_name_label)
        name_layout.addWidget(self.course_name_input)
        layout.addLayout(name_layout)

        # Course Credit
        credit_layout = QHBoxLayout()
        self.course_credit_label = QLabel("Course Credit (0-1):")
        self.course_credit_input = QLineEdit()
        credit_layout.addWidget(self.course_credit_label)
        credit_layout.addWidget(self.course_credit_input)
        layout.addLayout(credit_layout)

        # Subject Dropdown
        subject_layout = QHBoxLayout()
        self.subject_label = QLabel("Subject:")
        self.subject_dropdown = QComboBox()
        self.subject_dropdown.addItems([
            "Mathematics", "English", "Science", "History", "Foreign Language",
            "Physical Education", "Technology", "Arts", "Other"
        ])
        subject_layout.addWidget(self.subject_label)
        subject_layout.addWidget(self.subject_dropdown)
        layout.addLayout(subject_layout)

        # Grade Option (Semester/Full Year)
        grade_option_layout = QHBoxLayout()
        self.grade_option_label = QLabel("Grade Option:")
        self.semester_radio = QRadioButton("Semester")
        self.full_year_radio = QRadioButton("Full Year")
        self.semester_radio.setChecked(True)

        self.grade_button_group = QButtonGroup()
        self.grade_button_group.addButton(self.semester_radio)
        self.grade_button_group.addButton(self.full_year_radio)
        self.semester_radio.toggled.connect(self.toggle_grade_fields)

        grade_option_layout.addWidget(self.grade_option_label)
        grade_option_layout.addWidget(self.semester_radio)
        grade_option_layout.addWidget(self.full_year_radio)
        layout.addLayout(grade_option_layout)

        # Option to Separate Semester Grades
        self.separate_semesters_checkbox = QCheckBox("Separate Semester Grades")
        layout.addWidget(self.separate_semesters_checkbox)

        # Grade Entry
        self.grade_layout = QHBoxLayout()
        self.semester1_label = QLabel("Semester 1 Grade:")
        self.semester1_input = QLineEdit()
        self.semester2_label = QLabel("Semester 2 Grade:")
        self.semester2_input = QLineEdit()
        self.full_year_grade_label = QLabel("Full Year Grade:")
        self.full_year_grade_input = QLineEdit()

        self.grade_layout.addWidget(self.semester1_label)
        self.grade_layout.addWidget(self.semester1_input)
        self.grade_layout.addWidget(self.semester2_label)
        self.grade_layout.addWidget(self.semester2_input)
        self.grade_layout.addWidget(self.full_year_grade_label)
        self.grade_layout.addWidget(self.full_year_grade_input)
        layout.addLayout(self.grade_layout)

        # Add Course Button
        self.add_course_button = QPushButton("Add Course")
        self.add_course_button.clicked.connect(self.add_course)
        layout.addWidget(self.add_course_button)

        # List of Added Courses
        self.course_list_widget = QListWidget()
        layout.addWidget(self.course_list_widget)

        # Save Courses Button
        self.save_button = QPushButton("Save Courses")
        self.save_button.clicked.connect(self.save_courses)
        layout.addWidget(self.save_button)

        # Submit to SRAR Button
        self.submit_button = QPushButton("Submit to SRAR")
        self.submit_button.clicked.connect(self.submit_to_srar)
        layout.addWidget(self.submit_button)

        # Initially hide the full-year grade field
        self.toggle_grade_fields()

        self.setLayout(layout)

    def toggle_grade_fields(self):
        if self.semester_radio.isChecked():
            self.semester1_label.show()
            self.semester1_input.show()
            self.semester2_label.show()
            self.semester2_input.show()
            self.full_year_grade_label.hide()
            self.full_year_grade_input.hide()
        else:
            self.semester1_label.hide()
            self.semester1_input.hide()
            self.semester2_label.hide()
            self.semester2_input.hide()
            self.full_year_grade_label.show()
            self.full_year_grade_input.show()

    def format_course_name(self, base_name, suffix):
        if base_name[-1].isdigit():
            return f"{base_name}{suffix}"
        return f"{base_name} {suffix}"

    def add_course(self):
        grade_level = self.grade_level_dropdown.currentText()
        course_name = self.course_name_input.text()
        course_credit = self.course_credit_input.text()
        subject = self.subject_dropdown.currentText()
        grade_option = "Semester" if self.semester_radio.isChecked() else "Full Year"
        semester1_grade = self.semester1_input.text()
        semester2_grade = self.semester2_input.text()
        full_year_grade = self.full_year_grade_input.text()
        separate_semesters = self.separate_semesters_checkbox.isChecked()

        if not course_name or not course_credit or not subject:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields!")
            return

        try:
            course_credit = float(course_credit)
            if not (0 <= course_credit <= 1):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Course credit must be a number between 0 and 1!")
            return

        if grade_option == "Semester" and (not semester1_grade or not semester2_grade):
            QMessageBox.warning(self, "Input Error", "Please provide grades for both semesters!")
            return

        if grade_option == "Full Year" and not full_year_grade:
            QMessageBox.warning(self, "Input Error", "Please provide a full-year grade!")
            return

        if grade_option == "Semester":
            if separate_semesters:
                course_info_1 = f"{grade_level} | {self.format_course_name(course_name, 'A')} | {subject} | Semester 1 Grade: {semester1_grade} | Credits: {course_credit / 2:.2f}"
                course_info_2 = f"{grade_level} | {self.format_course_name(course_name, 'B')} | {subject} | Semester 2 Grade: {semester2_grade} | Credits: {course_credit / 2:.2f}"
                self.courses.append(course_info_1)
                self.courses.append(course_info_2)
                self.course_list_widget.addItem(course_info_1)
                self.course_list_widget.addItem(course_info_2)
            else:
                course_info = f"{grade_level} | {course_name} | {subject} | Semester 1: {semester1_grade}, Semester 2: {semester2_grade} | Credits: {course_credit}"
                self.courses.append(course_info)
                self.course_list_widget.addItem(course_info)
        else:
            course_info = f"{grade_level} | {course_name} | {subject} | Full Year Grade: {full_year_grade} | Credits: {course_credit}"
            self.courses.append(course_info)
            self.course_list_widget.addItem(course_info)

        self.course_name_input.clear()
        self.course_credit_input.clear()
        self.semester1_input.clear()
        self.semester2_input.clear()
        self.full_year_grade_input.clear()

    def save_courses(self):
        if not self.courses:
            QMessageBox.warning(self, "No Courses", "No courses to save!")
            return

        with open("courses.txt", "w") as file:
            for course in self.courses:
                file.write(course + "\n")

        QMessageBox.information(self, "Success", "Courses saved to courses.txt!")

    def submit_to_srar(self):
        if not self.courses:
            QMessageBox.warning(self, "No Courses", "No courses to submit!")
            return

        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--remote-debugging-port=9222")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            wait = WebDriverWait(self.driver, 10)

            QMessageBox.information(
                self, 
                "Instructions",
                "1. Please log into the SRAR website manually\n"
                "2. Navigate to the course entry page\n"
                "3. Click OK when you're ready to begin auto-filling"
            )

            time.sleep(5)  # Initial wait for page load

            for course in self.courses:
                try:
                    parts = course.split(" | ")
                    grade_level = parts[0]
                    course_name = parts[1]
                    subject = parts[2]
                    
                    # Fill in form fields first
                    wait.until(
                        EC.presence_of_element_located((By.ID, "grade-level"))
                    ).send_keys(grade_level)
                    
                    wait.until(
                        EC.presence_of_element_located((By.ID, "course-name"))
                    ).send_keys(course_name)
                    
                    wait.until(
                        EC.presence_of_element_located((By.ID, "subject"))
                    ).send_keys(subject)

                    if "Semester 1 Grade:" in parts[3]:
                        semester_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "semester-option"))
                        )
                        semester_radio.click()
                        
                        grade = parts[3].split(": ")[1]
                        credits = float(parts[4].split(": ")[1])
                        
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester1-grade"))
                        ).send_keys(grade)
                        
                    elif "Semester 2 Grade:" in parts[3]:
                        semester_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "semester-option"))
                        )
                        semester_radio.click()
                        
                        grade = parts[3].split(": ")[1]
                        credits = float(parts[4].split(": ")[1])
                        
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester2-grade"))
                        ).send_keys(grade)

                    wait.until(
                        EC.presence_of_element_located((By.ID, "credits"))
                    ).send_keys(str(credits))

                    # Now click Add Course after all fields are filled
                    add_course_button = wait.until(
                        EC.element_to_be_clickable((By.ID, "add-course-btn"))
                    )
                    add_course_button.click()

                    # Submit the course entry
                    submit_button = wait.until(
                        EC.element_to_be_clickable((By.ID, "submit-course-btn"))
                    )
                    submit_button.click()
                    
                    time.sleep(2)  # Wait for submission to complete

                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Entry Error",
                        f"Error entering course: {course}\nError: {str(e)}\nContinuing with next course..."
                    )
                    continue

            QMessageBox.information(self, "Success", "All courses have been submitted to SRAR!")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during submission:\n{str(e)}"
            )
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SRARApp()
    window.show()
    sys.exit(app.exec_()) 