import sys
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QListWidget, QMessageBox, QComboBox, QCheckBox, QMenu
)
from PyQt5.QtCore import Qt
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
        
        description_label = QLabel("This tool will help you generate your Self-Reported Academic Record")
        description_label.setStyleSheet("font-size: 16px; margin: 20px;")
        description_label.setAlignment(Qt.AlignCenter)
        
        start_button = QPushButton("Get Started")
        start_button.setStyleSheet("padding: 10px; font-size: 16px;")
        start_button.clicked.connect(self.init_ui)
        
        layout.addWidget(welcome_label)
        layout.addWidget(description_label)
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

        # Add Class Type Dropdown after Subject Dropdown
        class_type_layout = QHBoxLayout()
        self.class_type_label = QLabel("Class Type:")
        self.class_type_dropdown = QComboBox()
        self.class_type_dropdown.addItems([
            "Standard", "Honors", "AP"
        ])
        class_type_layout.addWidget(self.class_type_label)
        class_type_layout.addWidget(self.class_type_dropdown)
        layout.addLayout(class_type_layout)

        # Add event handler for course name changes to detect both class type and subject
        self.course_name_input.textChanged.connect(self.auto_select_class_type)
        self.course_name_input.textChanged.connect(self.auto_select_subject)

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
        self.semester1_input = self.create_grade_dropdown()
        self.semester2_label = QLabel("Semester 2 Grade:")
        self.semester2_input = self.create_grade_dropdown()
        self.full_year_grade_label = QLabel("Full Year Grade:")
        self.full_year_grade_input = self.create_grade_dropdown()

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
        self.course_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.course_list_widget.customContextMenuRequested.connect(self.show_context_menu)
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
        class_type = self.class_type_dropdown.currentText()  # Get class type
        grade_option = "Semester" if self.semester_radio.isChecked() else "Full Year"
        semester1_grade = self.semester1_input.currentText()
        semester2_grade = self.semester2_input.currentText()
        full_year_grade = self.full_year_grade_input.currentText()
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
                course_info_1 = f"{grade_level} | {self.format_course_name(course_name, 'A')} | {subject} | {class_type} | Semester 1 Grade: {semester1_grade} | Credits: {course_credit / 2:.2f}"
                course_info_2 = f"{grade_level} | {self.format_course_name(course_name, 'B')} | {subject} | {class_type} | Semester 2 Grade: {semester2_grade} | Credits: {course_credit / 2:.2f}"
                self.courses.append(course_info_1)
                self.courses.append(course_info_2)
                self.course_list_widget.addItem(course_info_1)
                self.course_list_widget.addItem(course_info_2)
            else:
                course_info = f"{grade_level} | {course_name} | {subject} | {class_type} | Semester 1: {semester1_grade}, Semester 2: {semester2_grade} | Credits: {course_credit}"
                self.courses.append(course_info)
                self.course_list_widget.addItem(course_info)
        else:
            course_info = f"{grade_level} | {course_name} | {subject} | {class_type} | Full Year Grade: {full_year_grade} | Credits: {course_credit}"
            self.courses.append(course_info)
            self.course_list_widget.addItem(course_info)

        # Clear inputs
        self.course_name_input.clear()
        self.course_credit_input.clear()
        self.semester1_input.setCurrentIndex(0)
        self.semester2_input.setCurrentIndex(0)
        self.full_year_grade_input.setCurrentIndex(0)
        self.class_type_dropdown.setCurrentIndex(0)  # Reset class type to Standard

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
            
        # Show form selection screen instead of immediate submission
        self.show_form_selection()

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

    def auto_select_class_type(self, course_name):
        """Automatically select class type based on course name"""
        course_name = course_name.lower().strip()
        if course_name.startswith(("hon", "honors")):
            self.class_type_dropdown.setCurrentText("Honors")
        elif course_name.startswith("ap"):
            self.class_type_dropdown.setCurrentText("AP")
        else:
            self.class_type_dropdown.setCurrentText("Standard")

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
            'robotics', 'electronics', 'design', 'CAD', 'digital'
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SRARApp()
    window.show()
    sys.exit(app.exec_()) 