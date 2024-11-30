import sys
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QListWidget, QMessageBox, QComboBox, QCheckBox, QMenu, QGroupBox, QDialog, QInputDialog
)
from PyQt5.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime
from PyQt5.QtGui import QIntValidator

class SRARApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virginia Tech SRAR Form Generator")
        self.setGeometry(100, 100, 800, 600)

        self.courses = []
        self.driver = None
        self.selected_form_type = None
        
        # Start with welcome screen
        self.show_welcome_screen()

    def show_welcome_screen(self):
        # Clear any existing layouts
        if self.layout():
            QWidget().setLayout(self.layout())
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_label = QLabel("Welcome to SRAR Form Generator")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        description_label = QLabel(
            "This tool will help you generate your Self-Reported Academic Record\n\n"
            "Please follow these steps:\n"
            "1. Enter your high school graduation year\n"
            "2. Enter your courses one by one\n"
            "3. Review your entries\n"
            "4. Submit to your chosen school"
        )
        description_label.setStyleSheet("font-size: 16px; margin: 20px;")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        
        # Graduation year input
        grad_year_widget = QWidget()
        grad_year_layout = QHBoxLayout()
        grad_year_label = QLabel("Graduation Year:")
        grad_year_label.setStyleSheet("font-size: 16px;")
        self.grad_year_input = QLineEdit()
        self.grad_year_input.setPlaceholderText("YYYY")
        self.grad_year_input.setMaxLength(4)
        self.grad_year_input.setFixedWidth(100)
        self.grad_year_input.setValidator(QIntValidator(2020, 2030))
        
        grad_year_layout.addWidget(grad_year_label)
        grad_year_layout.addWidget(self.grad_year_input)
        grad_year_layout.addStretch()
        grad_year_widget.setLayout(grad_year_layout)
        
        # Start button
        start_button = QPushButton("Get Started")
        start_button.setStyleSheet("padding: 10px; font-size: 16px;")
        start_button.clicked.connect(self.validate_grad_year)
        
        # Add all widgets to main layout
        layout.addWidget(welcome_label)
        layout.addWidget(description_label)
        layout.addWidget(grad_year_widget)
        layout.addWidget(start_button)
        layout.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)

    def init_ui(self):
        # Clear any existing layouts
        if self.layout():
            QWidget().setLayout(self.layout())
        
        layout = QVBoxLayout()

        # Grade Level Dropdown
        grade_level_layout = QHBoxLayout()
        self.grade_level_label = QLabel("Grade Level:")
        self.grade_level_dropdown = QComboBox()
        self.grade_level_dropdown.addItems([
            "9th Grade", "10th Grade", "11th Grade", "12th Grade"
        ])
        grade_level_layout.addWidget(self.grade_level_label)
        grade_level_layout.addWidget(self.grade_level_dropdown)
        layout.addLayout(grade_level_layout)

        # Course Name with auto-selection
        name_layout = QHBoxLayout()
        self.course_name_label = QLabel("Course Name:")
        self.course_name_input = QLineEdit()
        self.course_name_input.textChanged.connect(self.on_course_name_change)
        name_layout.addWidget(self.course_name_label)
        name_layout.addWidget(self.course_name_input)
        layout.addLayout(name_layout)

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

        # Course Level
        level_layout = QHBoxLayout()
        self.course_level_label = QLabel("Course Level:")
        self.course_level_dropdown = QComboBox()
        self.course_level_dropdown.addItems([
            "Regular", "Honors", "AP", "IB", "Dual Enrollment"
        ])
        level_layout.addWidget(self.course_level_label)
        level_layout.addWidget(self.course_level_dropdown)
        layout.addLayout(level_layout)

        # Course Length
        length_layout = QVBoxLayout()
        self.length_label = QLabel("Course Length:")
        self.length_description = QLabel("How do your courses show up on your report card?")
        self.semester_radio = QRadioButton("by Semester")
        self.full_year_radio = QRadioButton("by Year")
        
        self.length_group = QButtonGroup()
        self.length_group.addButton(self.semester_radio)
        self.length_group.addButton(self.full_year_radio)
        
        length_layout.addWidget(self.length_label)
        length_layout.addWidget(self.length_description)
        length_layout.addWidget(self.semester_radio)
        length_layout.addWidget(self.full_year_radio)
        layout.addLayout(length_layout)

        # First Semester Section
        first_sem_group = QGroupBox("First Semester")
        first_sem_layout = QVBoxLayout()

        self.semester1_label = QLabel("Grade:")
        self.semester1_input = self.create_grade_dropdown()
        first_sem_layout.addWidget(self.semester1_label)
        first_sem_layout.addWidget(self.semester1_input)

        self.semester1_credits = QLineEdit("0.5")
        first_sem_layout.addWidget(QLabel("Credits/Units:"))
        first_sem_layout.addWidget(self.semester1_credits)

        self.semester1_online = QCheckBox("Taken online")
        self.semester1_summer = QCheckBox("Taken during summer")
        self.semester1_retake = QCheckBox("Repeat/retake of prior course")
        first_sem_layout.addWidget(self.semester1_online)
        first_sem_layout.addWidget(self.semester1_summer)
        first_sem_layout.addWidget(self.semester1_retake)

        first_sem_group.setLayout(first_sem_layout)
        layout.addWidget(first_sem_group)

        # Second Semester Section
        second_sem_group = QGroupBox("Second Semester")
        second_sem_layout = QVBoxLayout()

        self.semester2_label = QLabel("Grade:")
        self.semester2_input = self.create_grade_dropdown()
        second_sem_layout.addWidget(self.semester2_label)
        second_sem_layout.addWidget(self.semester2_input)

        self.semester2_credits = QLineEdit("0.5")
        second_sem_layout.addWidget(QLabel("Credits/Units:"))
        second_sem_layout.addWidget(self.semester2_credits)

        self.semester2_online = QCheckBox("Taken online")
        self.semester2_summer = QCheckBox("Taken during summer")
        self.semester2_retake = QCheckBox("Repeat/retake of prior course")
        second_sem_layout.addWidget(self.semester2_online)
        second_sem_layout.addWidget(self.semester2_summer)
        second_sem_layout.addWidget(self.semester2_retake)

        second_sem_group.setLayout(second_sem_layout)
        layout.addWidget(second_sem_group)

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

        # Submit Button (will now open school selection dialog)
        self.submit_button = QPushButton("Submit Courses")
        self.submit_button.clicked.connect(self.show_submission_dialog)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def format_course_name(self, base_name, suffix):
        if base_name[-1].isdigit():
            return f"{base_name}{suffix}"
        return f"{base_name} {suffix}"

    def add_course(self):
        # Create a dictionary of required fields and their values
        required_fields = {
            "Grade Level": self.grade_level_dropdown.currentText(),
            "Course Name": self.course_name_input.text(),
            "Subject": self.subject_dropdown.currentText(),
            "Course Level": self.course_level_dropdown.currentText(),
        }
        
        # Check for empty required fields
        empty_fields = [field for field, value in required_fields.items() 
                       if not value or value.isspace()]
        
        if empty_fields:
            error_message = "Please fill in the following required fields:\n• " + "\n• ".join(empty_fields)
            QMessageBox.warning(self, "Input Error", error_message)
            return

        # If all required fields are filled, continue with adding the course
        grade_level = self.grade_level_dropdown.currentText()
        course_name = self.course_name_input.text()
        subject = self.subject_dropdown.currentText()
        course_level = self.course_level_dropdown.currentText()
        
        semester1_grade = self.semester1_input.currentText()
        semester1_online = self.semester1_online.isChecked()
        semester1_summer = self.semester1_summer.isChecked()
        semester1_retake = self.semester1_retake.isChecked()
        
        semester2_grade = self.semester2_input.currentText()
        semester2_online = self.semester2_online.isChecked()
        semester2_summer = self.semester2_summer.isChecked()
        semester2_retake = self.semester2_retake.isChecked()

        course_info = {
            'grade_level': grade_level,
            'course_name': course_name,
            'subject': subject,
            'course_level': course_level,
            'semester1': {
                'grade': semester1_grade,
                'credits': self.semester1_credits.text(),
                'online': semester1_online,
                'summer': semester1_summer,
                'retake': semester1_retake
            },
            'semester2': {
                'grade': semester2_grade,
                'credits': self.semester2_credits.text(),
                'online': semester2_online,
                'summer': semester2_summer,
                'retake': semester2_retake
            }
        }

        self.courses.append(course_info)  # Store the dictionary

        # Create display text based on semester selection
        if self.semester_radio.isChecked():
            # Display as two separate courses
            # First semester
            sem1_name = self.format_course_name(course_name, "A")
            display_text_1 = (
                f"{grade_level} | {sem1_name} | {subject} | {course_level} | "
                f"Grade: {semester1_grade} (Credits: {self.semester1_credits.text()}) "
                f"{'[Online]' if semester1_online else ''} "
                f"{'[Summer]' if semester1_summer else ''} "
                f"{'[Retake]' if semester1_retake else ''}"
            )
            self.course_list_widget.addItem(display_text_1)

            # Second semester
            sem2_name = self.format_course_name(course_name, "B")
            display_text_2 = (
                f"{grade_level} | {sem2_name} | {subject} | {course_level} | "
                f"Grade: {semester2_grade} (Credits: {self.semester2_credits.text()}) "
                f"{'[Online]' if semester2_online else ''} "
                f"{'[Summer]' if semester2_summer else ''} "
                f"{'[Retake]' if semester2_retake else ''}"
            )
            self.course_list_widget.addItem(display_text_2)
        else:
            # Display as one full-year course
            display_text = (
                f"{grade_level} | {course_name} | {subject} | {course_level} | "
                f"Semester 1: {semester1_grade} (Credits: {self.semester1_credits.text()}) "
                f"{'[Online]' if semester1_online else ''} "
                f"{'[Summer]' if semester1_summer else ''} "
                f"{'[Retake]' if semester1_retake else ''} | "
                f"Semester 2: {semester2_grade} (Credits: {self.semester2_credits.text()}) "
                f"{'[Online]' if semester2_online else ''} "
                f"{'[Summer]' if semester2_summer else ''} "
                f"{'[Retake]' if semester2_retake else ''}"
            )
            self.course_list_widget.addItem(display_text)

        # Clear inputs
        self.course_name_input.clear()
        self.semester1_input.setCurrentIndex(0)
        self.semester2_input.setCurrentIndex(0)
        self.semester1_online.setChecked(False)
        self.semester1_summer.setChecked(False)
        self.semester1_retake.setChecked(False)
        self.semester2_online.setChecked(False)
        self.semester2_summer.setChecked(False)
        self.semester2_retake.setChecked(False)

    def save_courses(self):
        if not self.courses:
            QMessageBox.warning(self, "No Courses", "No courses to save!")
            return

        with open("courses.txt", "w") as file:
            for course in self.courses:
                file.write(course + "\n")

        QMessageBox.information(self, "Success", "Courses saved to courses.txt!")

    def submit_to_srar(self):
        """Confirm before starting the SRAR submission process"""
        reply = QMessageBox.question(self, 'Confirm Submission', 
                                   'Are you ready to submit your courses to Virginia Tech SRAR?\n\n' +
                                   'Please make sure you have:\n' +
                                   '1. Logged into SRAR manually\n' +
                                   '2. Navigated to the course entry page\n' +
                                   '3. All courses entered correctly\n' +
                                   '4. A stable internet connection',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                driver = self.setup_driver()
                self.login_to_srar(driver)
                
                for course in self.courses:
                    try:
                        # Check if the course is split by semester
                        if self.semester_radio.isChecked():
                            # First Semester
                            self.enter_course(driver, course, semester='1')
                            # Second Semester
                            self.enter_course(driver, course, semester='2')
                        else:
                            # Full Year
                            self.enter_course(driver, course)

                    except Exception as e:
                        print(f"Error entering course: {course}")
                        print(f"Error: {str(e)}")
                        print("Continuing with next course...")
                        continue

                QMessageBox.information(self, "Success", "Courses submitted successfully to Virginia Tech SRAR!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error during submission: {str(e)}")
            finally:
                if 'driver' in locals():
                    driver.quit()
        else:
            print("Submission cancelled by user")

    def enter_course(self, driver, course, semester=None):
        """Enter a course into the SRAR system"""
        print(f"Starting to enter course: {course['course_name']}")

        # Wait for the form to be in its initial state
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "add-course-btn"))
        )

        # Fill all fields first
        print("Filling form fields...")

        # Grade Level
        grade_level = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "gradeLevel"))
        )
        Select(grade_level).select_by_visible_text(course['grade_level'])

        # Course Name
        course_name = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "courseName"))
        )
        course_name.clear()
        course_name_suffix = 'A' if semester == '1' else 'B' if semester == '2' else ''
        formatted_course_name = self.format_course_name(course['course_name'], course_name_suffix)
        course_name.send_keys(formatted_course_name)

        # Subject
        subject = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "subject"))
        )
        Select(subject).select_by_visible_text(course['subject'])

        # Course Level
        course_level = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "courseLevel"))
        )
        Select(course_level).select_by_visible_text(course['course_level'])

        # Semester-specific fields
        if semester == '1':
            sem = course['semester1']
        elif semester == '2':
            sem = course['semester2']
        else:
            sem = course['semester1']  # Default to first semester if full year

        if sem['grade']:
            sem_grade = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, f"semester{semester}Grade"))
            )
            Select(sem_grade).select_by_visible_text(sem['grade'])

            if sem['online']:
                driver.find_element(By.ID, f"semester{semester}Online").click()
            if sem['summer']:
                driver.find_element(By.ID, f"semester{semester}Summer").click()
            if sem['retake']:
                driver.find_element(By.ID, f"semester{semester}Retake").click()

        print("All fields filled, clicking Add Course...")

        # Now click Add Course
        add_course_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-course-btn"))
        )
        add_course_button.click()

        # Wait for the course to be added
        time.sleep(1)

        # Click Save
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "save"))
        )
        save_button.click()

        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "success-message"))
        )
        print("Course saved successfully")

        # Wait before next course
        time.sleep(2)

    def handle_form_selection(self):
        if self.form_type_dropdown.currentText() == "Select a school...":
            QMessageBox.warning(self, "Selection Required", "Please select a school!")
            return
            
        self.selected_form_type = self.form_type_dropdown.currentText()
        
        # Show confirmation with selected form type
        confirm = QMessageBox.question(
            self,
            "Confirm Submission",
            f"You are about to submit to {self.selected_form_type} SRAR form.\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return

        # Start the actual submission process
        self.start_submission()

    def start_submission(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Basic ChromeDriver setup
            service = Service()
            driver_path = ChromeDriverManager().install()
            service.path = driver_path
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
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
                    class_type = parts[3]
                    
                    # Parse credits from the last part
                    credits = float(parts[-1].split(": ")[1])
                    
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

                    # Handle different grade formats
                    if "Semester 1 Grade:" in course:
                        # Handle separated semester format
                        semester_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "semester-option"))
                        )
                        semester_radio.click()
                        
                        grade = parts[4].split(": ")[1]
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester1-grade"))
                        ).send_keys(grade)
                    elif "Semester 2 Grade:" in course:
                        semester_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "semester-option"))
                        )
                        semester_radio.click()
                        
                        grade = parts[4].split(": ")[1]
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester2-grade"))
                        ).send_keys(grade)
                    elif "Semester 1:" in course:
                        # Handle combined semester format
                        semester_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "semester-option"))
                        )
                        semester_radio.click()
                        
                        grades = parts[4].split(": ")[1].split(", ")
                        semester1_grade = grades[0]
                        semester2_grade = grades[1]
                        
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester1-grade"))
                        ).send_keys(semester1_grade)
                        
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "semester2-grade"))
                        ).send_keys(semester2_grade)
                    else:
                        # Handle full year format
                        full_year_radio = wait.until(
                            EC.element_to_be_clickable((By.ID, "full-year-option"))
                        )
                        full_year_radio.click()
                        
                        grade = parts[4].split(": ")[1]
                        wait.until(
                            EC.element_to_be_clickable((By.ID, "full-year-grade"))
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
            if self.driver:
                self.driver.quit()

    def create_grade_dropdown(self):
        dropdown = QComboBox()
        grades = ['', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']  # Added empty option
        dropdown.addItems(grades)
        return dropdown

    def show_form_selection(self):
        # Clear any existing layouts
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout()
        
        # Form selection title
        title_label = QLabel("Select Your SRAR Form Type")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Form type dropdown
        self.form_type_dropdown = QComboBox()
        self.form_type_dropdown.addItems([
            "Select a school...",
            "Northeastern",
            "Georgetown",
            "Virginia Tech (SRAR)",
            "UIUC"
        ])
        
        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.handle_form_selection)
        
        layout.addWidget(title_label)
        layout.addWidget(self.form_type_dropdown)
        layout.addWidget(continue_button)
        layout.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)

    def on_course_name_change(self, course_name):
        """Auto-select subject and class type based on course name"""
        self.auto_select_subject(course_name)
        self.auto_select_class_type(course_name)

    def auto_select_class_type(self, course_name):
        """Automatically select class type based on course name"""
        course_name = course_name.lower().strip()
        if course_name.startswith(("hon", "honors")):
            self.course_level_dropdown.setCurrentText("Honors")
        elif course_name.startswith("ap"):
            self.course_level_dropdown.setCurrentText("AP")
        elif "ib" in course_name:
            self.course_level_dropdown.setCurrentText("IB")
        elif any(term in course_name for term in ["dual", "de ", "college"]):
            self.course_level_dropdown.setCurrentText("Dual Enrollment")
        else:
            self.course_level_dropdown.setCurrentText("Regular")

    def auto_select_subject(self, course_name):
        """Automatically select subject based on course name"""
        course_name = course_name.lower().strip()
        
        # Mathematics courses
        math_keywords = [
            'algebra', 'geometry', 'calculus', 'precalculus', 'statistics', 
            'trigonometry', 'math', 'mathematics'
        ]
        
        # English courses
        english_keywords = [
            'english', 'literature', 'composition', 'writing', 'language arts',
            'speech', 'journalism', 'creative writing', 'seminar'
        ]
        
        # Science courses
        science_keywords = [
            'biology', 'chemistry', 'physics', 'anatomy', 'environmental',
            'science', 'astronomy', 'geology', 'earth science'
        ]
        
        # History courses
        history_keywords = [
            'history', 'world history', 'us history', 'european history',
            'geography', 'economics', 'government', 'civics',
            'social studies', 'political science'
        ]
        
        # Foreign Language courses
        language_keywords = [
            'spanish', 'french', 'german', 'latin', 'chinese', 'japanese',
            'italian', 'russian', 'arabic', 'korean', 'portuguese'
        ]
        
        # Physical Education courses
        pe_keywords = [
            'physical education', 'pe', 'health', 'fitness', 'sports',
            'weight training', 'conditioning', 'dance'
        ]
        
        # Technology courses
        tech_keywords = [
            'computer', 'programming', 'coding', 'technology', 'engineering',
            'robotics', 'electronics', 'design', 'cad', 'digital'
        ]
        
        # Arts courses
        arts_keywords = [
            'art', 'music', 'band', 'orchestra', 'choir', 'theater', 'drama',
            'painting', 'drawing', 'sculpture', 'ceramics', 'photography'
        ]

        # Check course name against keywords
        for keyword in math_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Mathematics")
                return
                
        for keyword in english_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("English")
                return
                
        for keyword in science_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Science")
                return
                
        for keyword in history_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("History")
                return
                
        for keyword in language_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Foreign Language")
                return
                
        for keyword in pe_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Physical Education")
                return
                
        for keyword in tech_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Technology")
                return
                
        for keyword in arts_keywords:
            if keyword in course_name:
                self.subject_dropdown.setCurrentText("Arts")
                return

    def show_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit Course")
        delete_action = menu.addAction("Delete Course")
        
        # Get the item at the clicked position
        item = self.course_list_widget.itemAt(position)
        if item is None:
            return
            
        action = menu.exec_(self.course_list_widget.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_course(item)
        elif action == delete_action:
            self.delete_course(item)

    def edit_course(self, item):
        course_info = item.text()
        parts = course_info.split(" | ")
        
        # Parse the course information
        grade_level = parts[0]
        course_name = parts[1]
        subject = parts[2]
        class_type = parts[3]
        
        # Set the values in the input fields
        self.grade_level_dropdown.setCurrentText(grade_level)
        self.course_name_input.setText(course_name)
        self.subject_dropdown.setCurrentText(subject)
        self.class_type_dropdown.setCurrentText(class_type)
        
        # Handle grades based on format
        if "Full Year Grade:" in course_info:
            self.full_year_radio.setChecked(True)
            grade = parts[4].split(": ")[1]
            self.full_year_grade_input.setCurrentText(grade)
        else:
            self.semester_radio.setChecked(True)
            if "Semester 1 Grade:" in course_info:
                # Handle separated semester format
                grade = parts[4].split(": ")[1]
                self.semester1_input.setCurrentText(grade)
                self.separate_semesters_checkbox.setChecked(True)
            else:
                # Handle combined semester format
                grades = parts[4].split(": ")[1].split(", ")
                self.semester1_input.setCurrentText(grades[0])
                self.semester2_input.setCurrentText(grades[1])
                self.separate_semesters_checkbox.setChecked(False)
        
        # Set credits
        credits = float(parts[-1].split(": ")[1])
        self.course_credit_input.setText(str(credits))
        
        # Remove the old course
        row = self.course_list_widget.row(item)
        self.course_list_widget.takeItem(row)
        self.courses.pop(row)
        
        # Update the add course button to show it's in edit mode
        self.add_course_button.setText("Update Course")
        self.add_course_button.clicked.disconnect()
        self.add_course_button.clicked.connect(lambda: self.finish_edit())

    def finish_edit(self):
        # Add the edited course
        self.add_course()
        
        # Reset the add course button
        self.add_course_button.setText("Add Course")
        self.add_course_button.clicked.disconnect()
        self.add_course_button.clicked.connect(self.add_course)
        
        # Clear inputs
        self.course_name_input.clear()
        self.course_credit_input.clear()
        self.semester1_input.setCurrentIndex(0)
        self.semester2_input.setCurrentIndex(0)
        self.full_year_grade_input.setCurrentIndex(0)
        self.class_type_dropdown.setCurrentIndex(0)

    def delete_course(self, item):
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this course?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            row = self.course_list_widget.row(item)
            self.course_list_widget.takeItem(row)
            self.courses.pop(row)

    def on_school_change(self, school):
        """Handle school selection changes"""
        print(f"School changed to: {school}")  # Debug line
        if school == "Virginia Tech (SRAR)":
            self.vt_fields_group.show()
            self.semester_radio.setChecked(True)
            self.full_year_radio.setEnabled(False)
            self.semester1_credits.setText("0.5")
            self.semester2_credits.setText("0.5")
            self.semester1_credits.setEnabled(False)
            self.semester2_credits.setEnabled(False)
        else:
            self.vt_fields_group.hide()
            self.full_year_radio.setEnabled(True)
            self.semester1_credits.setText("1.0")
            self.semester2_credits.setText("1.0")
            self.semester1_credits.setEnabled(True)
            self.semester2_credits.setEnabled(True)

    def show_submission_dialog(self):
        """Show dialog for selecting submission type"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Submit Courses")
        layout = QVBoxLayout()

        # Create radio buttons for different schools
        vt_radio = QRadioButton("Virginia Tech (SRAR)")
        neu_radio = QRadioButton("Northeastern University")
        other_radio = QRadioButton("Other Schools")

        # Add radio buttons to layout
        layout.addWidget(vt_radio)
        layout.addWidget(neu_radio)
        layout.addWidget(other_radio)

        # Create button group
        button_group = QButtonGroup()
        button_group.addButton(vt_radio)
        button_group.addButton(neu_radio)
        button_group.addButton(other_radio)

        # Add submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.submit_to_school(
            "Virginia Tech (SRAR)" if vt_radio.isChecked() 
            else "Northeastern University" if neu_radio.isChecked()
            else "Other", dialog))
        layout.addWidget(submit_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def submit_to_school(self, school, dialog):
        """Handle submission to specific school"""
        if school == "Virginia Tech (SRAR)":
            self.submit_to_srar()
        elif school == "Northeastern University":
            self.submit_to_neu()
        else:
            QMessageBox.information(self, "Info", "Submission to other schools not yet implemented")
        
        dialog.accept()

    def get_generic_title(self, course_name):
        """Generate a generic title based on the course name"""
        # Remove specific identifiers like "Honors", "AP", etc.
        generic = course_name.lower()
        for prefix in ["honors ", "ap ", "ib ", "de "]:
            if generic.startswith(prefix):
                generic = generic[len(prefix):]
        
        # Capitalize first letter of each word
        return generic.title()

    def setup_driver(self):
        """Set up and return a Chrome WebDriver"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options

        # Set up Chrome options
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Uncomment to run in headless mode
        chrome_options.add_argument('--start-maximized')
        
        # Initialize the Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to SRAR
        driver.get("https://srar.org")
        return driver

    def login_to_srar(self, driver):
        """Wait for user to log in to SRAR website"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # Show instructions to user
        QMessageBox.information(
            self, 
            "Manual Login Required",
            "Please:\n"
            "1. Log into SRAR manually\n"
            "2. Navigate to the course entry page\n"
            "3. Click OK when you're ready to begin auto-filling"
        )

        try:
            # Wait for the course entry page to be loaded
            WebDriverWait(driver, 300).until(  # 5 minute timeout
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add Course')]"))
            )
        except Exception as e:
            raise Exception("Could not detect course entry page. Please make sure you're on the correct page.")

    def submit_to_neu(self):
        """Submit courses to Northeastern University"""
        try:
            driver = self.setup_driver()
            self.login_to_srar(driver)
            
            for course in self.courses:
                try:
                    # Check if the course is split by semester
                    if self.semester_radio.isChecked():
                        # First Semester
                        self.enter_neu_course(driver, course, semester='1')
                        # Second Semester
                        self.enter_neu_course(driver, course, semester='2')
                    else:
                        # Full Year
                        self.enter_neu_course(driver, course)

                except Exception as e:
                    print(f"Error entering course: {course}")
                    print(f"Error: {str(e)}")
                    print("Continuing with next course...")
                    continue

            QMessageBox.information(self, "Success", "Courses submitted successfully to Northeastern University!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during submission: {str(e)}")
        finally:
            if 'driver' in locals():
                driver.quit()

    def enter_neu_course(self, driver, course, semester=None):
        """Enter a course into the NEU system"""
        print(f"Starting to enter course: {course['course_name']}")

        # Wait for the form to be in its initial state
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "add-course-btn"))
        )

        # Fill all fields first
        print("Filling form fields...")

        # Calculate start date based on grade level and semester
        start_month, start_year = self.get_start_date(course['grade_level'], semester)
        
        # Set start month
        month_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "startMonth"))
        )
        Select(month_select).select_by_visible_text(start_month)

        # Set start year
        year_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "startYear"))
        )
        Select(year_select).select_by_visible_text(start_year)

        # Subject Area
        subject = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "subjectArea"))
        )
        Select(subject).select_by_visible_text(course['subject'])

        # Course Name
        course_name = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "courseName"))
        )
        course_name.clear()
        course_name_suffix = 'A' if semester == '1' else 'B' if semester == '2' else ''
        formatted_course_name = self.format_course_name(course['course_name'], course_name_suffix)
        course_name.send_keys(formatted_course_name)

        # Course Level
        course_level = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "courseLevel"))
        )
        Select(course_level).select_by_visible_text(course['course_level'])

        # Grade Scale (always "Letter")
        grade_scale = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "gradeScale"))
        )
        Select(grade_scale).select_by_visible_text("Letter")

        # Grade and Credits
        if semester == '1':
            sem = course['semester1']
            credits = "0.5"
        elif semester == '2':
            sem = course['semester2']
            credits = "0.5"
        else:
            sem = course['semester1']  # Use first semester grade for full year
            credits = "1.0"

        if sem['grade']:
            grade_select = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "grade"))
            )
            Select(grade_select).select_by_visible_text(sem['grade'])

        credits_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "credits"))
        )
        credits_input.clear()
        credits_input.send_keys(credits)

        print("All fields filled, clicking Add Course...")

        # Now click Add Course
        add_course_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-course-btn"))
        )
        add_course_button.click()

        # Wait for the course to be added
        time.sleep(1)

        # Click Save
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "save"))
        )
        save_button.click()

        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "success-message"))
        )
        print("Course saved successfully")

        # Wait before next course
        time.sleep(2)

    def get_start_date(self, grade_level, semester):
        """Calculate start date based on grade level and semester"""
        # Extract grade number (9-12) from grade level string
        grade_num = int(grade_level.split('th')[0])
        
        # Calculate years back from graduation year
        # For example: if graduating in 2024:
        # 12th grade starts 2023 (grad_year - 1)
        # 11th grade starts 2022 (grad_year - 2)
        # 10th grade starts 2021 (grad_year - 3)
        # 9th grade starts 2020 (grad_year - 4)
        years_before_graduation = 13 - grade_num  # 13 because we want the start of each grade
        start_year = self.graduation_year - years_before_graduation
        
        if semester == '1':
            return ("August", str(start_year))
        else:
            return ("January", str(start_year + 1))

    def validate_grad_year(self):
        """Validate graduation year and proceed to course entry"""
        grad_year = self.grad_year_input.text()
        
        if not grad_year:
            QMessageBox.warning(self, "Input Error", "Please enter your graduation year.")
            return
        
        try:
            grad_year = int(grad_year)
            current_year = datetime.now().year
            
            if grad_year < current_year:
                QMessageBox.warning(self, "Input Error", "Graduation year cannot be in the past.")
                return
            
            if grad_year > current_year + 6:
                QMessageBox.warning(self, "Input Error", "Graduation year seems too far in the future.")
                return
            
            self.graduation_year = grad_year
            # Initialize the main UI after valid graduation year
            self.init_ui()
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid year.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SRARApp()
    window.show()
    sys.exit(app.exec_()) 