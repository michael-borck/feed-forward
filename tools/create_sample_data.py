#!/usr/bin/env python
"""
Script to populate the FeedForward database with sample data for development and testing
"""

import datetime
import json
import pathlib
import random
import sys
from datetime import timedelta

# Add the project root to the path so we can import app modules
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.assignment import (
    Assignment,
    Rubric,
    RubricCategory,
    assignments,
    rubric_categories,
    rubrics,
)
from app.models.config import (
    AggregationMethod,
    AssignmentSettings,
    FeedbackStyle,
    MarkDisplayOption,
    SystemConfig,
    aggregation_methods,
    assignment_settings,
    feedback_styles,
    mark_display_options,
    system_config,
)
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.feedback import (
    AggregatedFeedback,
    AIModel,
    CategoryScore,
    Draft,
    FeedbackItem,
    ModelRun,
    aggregated_feedback,
    ai_models,
    category_scores,
    drafts,
    feedback_items,
    model_runs,
)
from app.models.user import Role, User, db, users
from app.utils.auth import get_password_hash


# Initialize database connection
def get_current_time():
    """Return current time in ISO format"""
    return datetime.datetime.now().isoformat()


def get_future_date(days=30):
    """Return a future date in ISO format"""
    future_date = datetime.datetime.now() + timedelta(days=days)
    return future_date.isoformat()


def clear_all_tables():
    """Clear all tables in the database"""
    print("Clearing all tables...")
    tables = [
        users,
        courses,
        enrollments,
        assignments,
        rubrics,
        rubric_categories,
        ai_models,
        drafts,
        model_runs,
        category_scores,
        feedback_items,
        aggregated_feedback,
        system_config,
        aggregation_methods,
        feedback_styles,
        mark_display_options,
        assignment_settings,
    ]

    for table in tables:
        try:
            # Get count before deletion
            count = len(list(table()))
            # Clear the table
            db.execute(f"DELETE FROM {table.name}")
            print(f"  Cleared {count} rows from {table.name}")
        except Exception as e:
            print(f"  Error clearing {table.name}: {e!s}")


def create_users():
    """Create sample users"""
    print("Creating sample users...")

    # Admin user
    admin = User(
        email="admin@curtin.edu.au",
        name="System Administrator",
        password=get_password_hash("Admin123!"),  # In production, use a proper password
        role=Role.ADMIN,
        verified=True,
        verification_token="",
        approved=True,
        department="IT Services",
        reset_token="",
        reset_token_expiry="",
        status="active",
        last_active=get_current_time(),
    )
    users.insert(admin)
    print(f"  Created admin user: {admin.email}")

    # Instructors
    instructors = [
        ("michael.borck@curtin.edu.au", "Michael Borck", "Computer Science"),
        ("jane.smith@curtin.edu.au", "Jane Smith", "Data Science"),
        ("david.lee@curtin.edu.au", "David Lee", "Software Engineering"),
    ]

    for email, name, department in instructors:
        instructor = User(
            email=email,
            name=name,
            password=get_password_hash(
                "Instructor123!"
            ),  # In production, use a proper password
            role=Role.INSTRUCTOR,
            verified=True,
            verification_token="",
            approved=True,
            department=department,
            reset_token="",
            reset_token_expiry="",
            status="active",
            last_active=get_current_time(),
        )
        users.insert(instructor)
        print(f"  Created instructor: {instructor.email}")

    # Students
    student_domains = ["student.curtin.edu.au", "postgraduate.curtin.edu.au"]
    student_names = [
        "Alice Johnson",
        "Bob Williams",
        "Charlie Brown",
        "Diana Prince",
        "Edward Stark",
        "Fiona Apple",
        "George Lucas",
        "Hannah Montana",
        "Ian Malcolm",
        "Julia Roberts",
        "Kevin Hart",
        "Laura Croft",
    ]

    for i, name in enumerate(student_names):
        # Create email from name (lowercase first initial + last name)
        first, last = name.split(" ", 1)
        email = f"{first[0].lower()}{last.lower()}@{student_domains[i % len(student_domains)]}"

        student = User(
            email=email,
            name=name,
            password=get_password_hash(
                "Student123!"
            ),  # In production, use a proper password
            role=Role.STUDENT,
            verified=True,
            verification_token="",
            approved=True,
            department="",
            reset_token="",
            reset_token_expiry="",
            status="active",
            last_active=get_current_time(),
        )
        users.insert(student)
        print(f"  Created student: {student.email}")


def create_courses():
    """Create sample courses"""
    print("Creating sample courses...")

    course_data = [
        {
            "code": "COMP1000",
            "title": "Introduction to Programming",
            "term": "Semester 1, 2025",
            "department": "Computer Science",
            "instructor_email": "michael.borck@curtin.edu.au",
        },
        {
            "code": "DATA2000",
            "title": "Data Analysis and Visualization",
            "term": "Semester 1, 2025",
            "department": "Data Science",
            "instructor_email": "jane.smith@curtin.edu.au",
        },
        {
            "code": "SOFT3000",
            "title": "Software Engineering Principles",
            "term": "Semester 1, 2025",
            "department": "Software Engineering",
            "instructor_email": "david.lee@curtin.edu.au",
        },
        {
            "code": "COMP2000",
            "title": "Algorithms and Data Structures",
            "term": "Semester 2, 2025",
            "department": "Computer Science",
            "instructor_email": "michael.borck@curtin.edu.au",
        },
    ]

    for i, data in enumerate(course_data, 1):
        course = Course(
            id=i,
            code=data["code"],
            title=data["title"],
            term=data["term"],
            department=data["department"],
            instructor_email=data["instructor_email"],
            status="active",
            created_at=get_current_time(),
            updated_at=get_current_time(),
        )
        courses.insert(course)
        print(f"  Created course: {course.code} - {course.title}")


def create_enrollments():
    """Create sample enrollments"""
    print("Creating sample enrollments...")

    # Get all students
    all_students = [user for user in users() if user.role == Role.STUDENT]

    # Assign students to courses
    enrollments_data = [
        # COMP1000 - Assign 8 students
        {"course_id": 1, "students": all_students[:8]},
        # DATA2000 - Assign 6 students
        {"course_id": 2, "students": all_students[2:8]},
        # SOFT3000 - Assign 5 students
        {"course_id": 3, "students": all_students[4:9]},
        # COMP2000 - Assign 4 students
        {"course_id": 4, "students": all_students[6:10]},
    ]

    enrollment_id = 1
    for enrollment_data in enrollments_data:
        course_id = enrollment_data["course_id"]
        course = courses[course_id]

        for student in enrollment_data["students"]:
            enrollment = Enrollment(
                id=enrollment_id, course_id=course_id, student_email=student.email
            )
            enrollments.insert(enrollment)
            print(f"  Enrolled {student.email} in {course.code}")
            enrollment_id += 1


def create_assignments():
    """Create sample assignments"""
    print("Creating sample assignments...")

    assignments_data = [
        {
            "course_id": 1,  # COMP1000
            "title": "Basic Programming Concepts",
            "description": "Demonstrate your understanding of variables, data types, and basic control structures by writing a simple program.",
            "due_date": get_future_date(14),
            "max_drafts": 3,
            "created_by": "michael.borck@curtin.edu.au",
        },
        {
            "course_id": 1,  # COMP1000
            "title": "Functions and Methods",
            "description": "Create a program that utilizes functions and methods to solve a simple problem.",
            "due_date": get_future_date(28),
            "max_drafts": 3,
            "created_by": "michael.borck@curtin.edu.au",
        },
        {
            "course_id": 2,  # DATA2000
            "title": "Data Visualization Project",
            "description": "Analyze a provided dataset and create visualizations to communicate key insights.",
            "due_date": get_future_date(21),
            "max_drafts": 2,
            "created_by": "jane.smith@curtin.edu.au",
        },
        {
            "course_id": 3,  # SOFT3000
            "title": "Software Design Patterns",
            "description": "Implement a solution using at least two design patterns and explain your choices.",
            "due_date": get_future_date(35),
            "max_drafts": 4,
            "created_by": "david.lee@curtin.edu.au",
        },
    ]

    for i, data in enumerate(assignments_data, 1):
        assignment = Assignment(
            id=i,
            course_id=data["course_id"],
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            max_drafts=data["max_drafts"],
            created_by=data["created_by"],
            status="active",
            created_at=get_current_time(),
            updated_at=get_current_time(),
        )
        assignments.insert(assignment)
        print(
            f"  Created assignment: {assignment.title} for course ID {assignment.course_id}"
        )


def create_rubrics():
    """Create sample rubrics and categories"""
    print("Creating sample rubrics and categories...")

    rubric_data = [
        {
            "assignment_id": 1,  # Basic Programming Concepts
            "categories": [
                {
                    "name": "Code Correctness",
                    "description": "Does the code run without errors and produce the expected output?",
                    "weight": 0.4,
                },
                {
                    "name": "Code Style",
                    "description": "Is the code well-organized, properly indented, and well-commented?",
                    "weight": 0.3,
                },
                {
                    "name": "Algorithm Efficiency",
                    "description": "Is the code efficient and does it use appropriate algorithms?",
                    "weight": 0.3,
                },
            ],
        },
        {
            "assignment_id": 2,  # Functions and Methods
            "categories": [
                {
                    "name": "Function Design",
                    "description": "Are functions properly designed with appropriate parameters and return values?",
                    "weight": 0.4,
                },
                {
                    "name": "Code Quality",
                    "description": "Is the code modular, reusable, and maintainable?",
                    "weight": 0.3,
                },
                {
                    "name": "Documentation",
                    "description": "Are functions and methods properly documented?",
                    "weight": 0.3,
                },
            ],
        },
        {
            "assignment_id": 3,  # Data Visualization Project
            "categories": [
                {
                    "name": "Data Analysis",
                    "description": "Is the data analysis thorough and insightful?",
                    "weight": 0.4,
                },
                {
                    "name": "Visualization Quality",
                    "description": "Are visualizations clear, appropriate, and properly labeled?",
                    "weight": 0.4,
                },
                {
                    "name": "Insights and Conclusions",
                    "description": "Are insights from the data clearly articulated?",
                    "weight": 0.2,
                },
            ],
        },
        {
            "assignment_id": 4,  # Software Design Patterns
            "categories": [
                {
                    "name": "Pattern Selection",
                    "description": "Are appropriate design patterns selected for the problem?",
                    "weight": 0.3,
                },
                {
                    "name": "Implementation",
                    "description": "Are the design patterns correctly implemented?",
                    "weight": 0.4,
                },
                {
                    "name": "Explanation",
                    "description": "Is the reasoning behind pattern selection well-explained?",
                    "weight": 0.3,
                },
            ],
        },
    ]

    rubric_id = 1
    category_id = 1

    for data in rubric_data:
        # Create rubric
        rubric = Rubric(id=rubric_id, assignment_id=data["assignment_id"])
        rubrics.insert(rubric)

        # Create categories for this rubric
        for category_data in data["categories"]:
            category = RubricCategory(
                id=category_id,
                rubric_id=rubric_id,
                name=category_data["name"],
                description=category_data["description"],
                weight=category_data["weight"],
            )
            rubric_categories.insert(category)
            category_id += 1

        print(
            f"  Created rubric and {len(data['categories'])} categories for assignment ID {data['assignment_id']}"
        )
        rubric_id += 1


def create_ai_models():
    """Create sample AI models"""
    print("Creating sample AI models...")

    # System AI models
    system_models = [
        {
            "name": "GPT-4",
            "provider": "OpenAI",
            "model_id": "gpt-4",
            "api_config": json.dumps({"api_key": "PLACEHOLDER-SYSTEM-KEY-GPT4"}),
            "active": True,
            "owner_type": "system",
            "owner_id": "",
        },
        {
            "name": "Claude 3 Opus",
            "provider": "Anthropic",
            "model_id": "claude-3-opus-20240229",
            "api_config": json.dumps({"api_key": "PLACEHOLDER-SYSTEM-KEY-CLAUDE"}),
            "active": True,
            "owner_type": "system",
            "owner_id": "",
        },
    ]

    # Instructor AI models
    instructor_models = [
        {
            "name": "Personal GPT-4",
            "provider": "OpenAI",
            "model_id": "gpt-4",
            "api_config": json.dumps({"api_key": "PLACEHOLDER-INSTRUCTOR-KEY-1"}),
            "active": True,
            "owner_type": "instructor",
            "owner_id": "michael.borck@curtin.edu.au",
        },
        {
            "name": "Personal Claude",
            "provider": "Anthropic",
            "model_id": "claude-3-sonnet-20240229",
            "api_config": json.dumps({"api_key": "PLACEHOLDER-INSTRUCTOR-KEY-2"}),
            "active": True,
            "owner_type": "instructor",
            "owner_id": "jane.smith@curtin.edu.au",
        },
    ]

    model_id = 1

    # Insert system models
    for model_data in system_models:
        model = AIModel(
            id=model_id,
            name=model_data["name"],
            provider=model_data["provider"],
            model_id=model_data["model_id"],
            api_config=model_data["api_config"],
            active=model_data["active"],
            owner_type=model_data["owner_type"],
            owner_id=model_data["owner_id"],
        )
        ai_models.insert(model)
        print(f"  Created system AI model: {model.name}")
        model_id += 1

    # Insert instructor models
    for model_data in instructor_models:
        model = AIModel(
            id=model_id,
            name=model_data["name"],
            provider=model_data["provider"],
            model_id=model_data["model_id"],
            api_config=model_data["api_config"],
            active=model_data["active"],
            owner_type=model_data["owner_type"],
            owner_id=model_data["owner_id"],
        )
        ai_models.insert(model)
        print(f"  Created instructor AI model: {model.name} (owner: {model.owner_id})")
        model_id += 1


def create_system_config():
    """Create sample system configuration"""
    print("Creating system configuration...")

    # Aggregation methods
    aggregation_methods_data = [
        {
            "id": 1,
            "name": "Average",
            "description": "Simple average of all model scores",
            "is_active": True,
        },
        {
            "id": 2,
            "name": "Weighted Average",
            "description": "Weighted average based on model confidence",
            "is_active": True,
        },
        {
            "id": 3,
            "name": "Maximum",
            "description": "Take the highest score from any model",
            "is_active": False,
        },
    ]

    for data in aggregation_methods_data:
        method = AggregationMethod(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            is_active=data["is_active"],
        )
        aggregation_methods.insert(method)

    # Feedback styles
    feedback_styles_data = [
        {
            "id": 1,
            "name": "Detailed",
            "description": "Provides detailed feedback on all aspects",
            "is_active": True,
        },
        {
            "id": 2,
            "name": "Concise",
            "description": "Provides brief, to-the-point feedback",
            "is_active": True,
        },
        {
            "id": 3,
            "name": "Constructive",
            "description": "Focuses on improvement opportunities",
            "is_active": True,
        },
    ]

    for data in feedback_styles_data:
        style = FeedbackStyle(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            is_active=data["is_active"],
        )
        feedback_styles.insert(style)

    # Mark display options
    mark_display_options_data = [
        {
            "id": 1,
            "display_type": "numeric",
            "name": "Percentage",
            "description": "Display as percentage",
            "icon_type": "",
            "is_active": True,
        },
        {
            "id": 2,
            "display_type": "icon",
            "name": "Stars",
            "description": "Display as star rating",
            "icon_type": "star",
            "is_active": True,
        },
        {
            "id": 3,
            "display_type": "hidden",
            "name": "Hidden",
            "description": "Don't show scores to students",
            "icon_type": "",
            "is_active": True,
        },
    ]

    for data in mark_display_options_data:
        option = MarkDisplayOption(
            id=data["id"],
            display_type=data["display_type"],
            name=data["name"],
            description=data["description"],
            icon_type=data["icon_type"],
            is_active=data["is_active"],
        )
        mark_display_options.insert(option)

    # System configuration
    system_config_data = [
        {
            "key": "institution_name",
            "value": "Curtin University",
            "description": "Name of the institution",
        },
        {
            "key": "feedback_delay_min",
            "value": "30",
            "description": "Minimum delay in seconds before showing feedback",
        },
        {
            "key": "feedback_delay_max",
            "value": "120",
            "description": "Maximum delay in seconds before showing feedback",
        },
        {
            "key": "default_aggregation_method",
            "value": "1",
            "description": "Default aggregation method ID",
        },
        {
            "key": "default_feedback_style",
            "value": "1",
            "description": "Default feedback style ID",
        },
        {
            "key": "default_mark_display",
            "value": "1",
            "description": "Default mark display option ID",
        },
    ]

    for data in system_config_data:
        config = SystemConfig(
            key=data["key"], value=data["value"], description=data["description"]
        )
        system_config.insert(config)

    print(
        "  Created system configuration, aggregation methods, feedback styles, and mark display options"
    )


def create_assignment_settings():
    """Create sample assignment settings"""
    print("Creating assignment settings...")

    settings_data = [
        {
            "id": 1,
            "assignment_id": 1,  # Basic Programming Concepts
            "ai_model_id": 1,  # GPT-4 (system)
            "num_runs": 3,
            "aggregation_method_id": 1,  # Average
            "feedback_style_id": 1,  # Detailed
            "require_review": True,
            "mark_display_option_id": 1,  # Percentage
        },
        {
            "id": 2,
            "assignment_id": 2,  # Functions and Methods
            "ai_model_id": 2,  # Claude 3 Opus (system)
            "num_runs": 2,
            "aggregation_method_id": 2,  # Weighted Average
            "feedback_style_id": 2,  # Concise
            "require_review": False,
            "mark_display_option_id": 2,  # Stars
        },
        {
            "id": 3,
            "assignment_id": 3,  # Data Visualization Project
            "ai_model_id": 3,  # Personal GPT-4 (instructor)
            "num_runs": 3,
            "aggregation_method_id": 1,  # Average
            "feedback_style_id": 3,  # Constructive
            "require_review": True,
            "mark_display_option_id": 1,  # Percentage
        },
        {
            "id": 4,
            "assignment_id": 4,  # Software Design Patterns
            "ai_model_id": 4,  # Personal Claude (instructor)
            "num_runs": 2,
            "aggregation_method_id": 2,  # Weighted Average
            "feedback_style_id": 1,  # Detailed
            "require_review": True,
            "mark_display_option_id": 3,  # Hidden
        },
    ]

    for data in settings_data:
        setting = AssignmentSettings(
            id=data["id"],
            assignment_id=data["assignment_id"],
            ai_model_id=data["ai_model_id"],
            num_runs=data["num_runs"],
            aggregation_method_id=data["aggregation_method_id"],
            feedback_style_id=data["feedback_style_id"],
            require_review=data["require_review"],
            mark_display_option_id=data["mark_display_option_id"],
        )
        assignment_settings.insert(setting)
        print(f"  Created settings for assignment ID {data['assignment_id']}")


def create_sample_drafts():
    """Create sample drafts for assignments"""
    print("Creating sample drafts...")

    # Get all enrollments
    all_enrollments = list(enrollments())

    # Sample draft content for basic programming
    basic_programming_content = """
# Basic Calculator Program

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

# Main program
print("Welcome to Basic Calculator")
print("Select operation:")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")

choice = input("Enter choice (1/2/3/4): ")
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

if choice == '1':
    print(f"{num1} + {num2} = {add(num1, num2)}")
elif choice == '2':
    print(f"{num1} - {num2} = {subtract(num1, num2)}")
elif choice == '3':
    print(f"{num1} * {num2} = {multiply(num1, num2)}")
elif choice == '4':
    print(f"{num1} / {num2} = {divide(num1, num2)}")
else:
    print("Invalid input")
"""

    # Sample draft content for functions and methods
    functions_content = """
# Library Management System

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available = True
    
    def check_out(self):
        if self.available:
            self.available = False
            return True
        return False
    
    def check_in(self):
        self.available = True

class Library:
    def __init__(self):
        self.books = []
    
    def add_book(self, book):
        self.books.append(book)
    
    def find_book_by_title(self, title):
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None
    
    def find_book_by_isbn(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def check_out_book(self, isbn):
        book = self.find_book_by_isbn(isbn)
        if book:
            return book.check_out()
        return False
    
    def check_in_book(self, isbn):
        book = self.find_book_by_isbn(isbn)
        if book:
            book.check_in()
            return True
        return False

# Test the library system
library = Library()
library.add_book(Book("Python Programming", "John Smith", "12345"))
library.add_book(Book("Data Science Basics", "Jane Doe", "67890"))

print("Books in the library:")
for book in library.books:
    print(f"{book.title} by {book.author} (ISBN: {book.isbn})")

library.check_out_book("12345")
print("After checking out a book:")
for book in library.books:
    status = "Available" if book.available else "Checked Out"
    print(f"{book.title}: {status}")
"""

    # Sample data visualization content
    data_viz_content = """
# Data Visualization Project

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
data = pd.read_csv('sales_data.csv')

# Data cleaning
data.dropna(inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data['Month'] = data['Date'].dt.month
data['Year'] = data['Date'].dt.year

# Summary statistics
print("Summary Statistics:")
print(data.describe())

# Monthly sales analysis
monthly_sales = data.groupby('Month')['Revenue'].sum().reset_index()

# Visualization 1: Monthly Sales Trend
plt.figure(figsize=(12, 6))
sns.barplot(x='Month', y='Revenue', data=monthly_sales)
plt.title('Monthly Sales Revenue')
plt.xlabel('Month')
plt.ylabel('Revenue (USD)')
plt.savefig('monthly_sales.png')

# Visualization 2: Product Category Distribution
plt.figure(figsize=(10, 10))
category_sales = data.groupby('Category')['Revenue'].sum()
plt.pie(category_sales, labels=category_sales.index, autopct='%1.1f%%')
plt.title('Sales by Product Category')
plt.savefig('category_distribution.png')

# Visualization 3: Regional Comparison
plt.figure(figsize=(12, 6))
sns.boxplot(x='Region', y='Revenue', data=data)
plt.title('Revenue Distribution by Region')
plt.xlabel('Region')
plt.ylabel('Revenue (USD)')
plt.savefig('regional_comparison.png')

# Key Insights
print("Key Insights:")
print("1. Highest revenue month:", monthly_sales.loc[monthly_sales['Revenue'].idxmax()]['Month'])
print("2. Top-performing category:", category_sales.idxmax())
print("3. Region with highest average revenue:", data.groupby('Region')['Revenue'].mean().idxmax())
print("4. Region with most consistent revenue (lowest std dev):", data.groupby('Region')['Revenue'].std().idxmin())
"""

    # Sample design patterns content
    design_patterns_content = """
# Design Patterns Implementation

from abc import ABC, abstractmethod

# Observer Pattern
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(self, *args, **kwargs)

class Observer(ABC):
    @abstractmethod
    def update(self, subject, *args, **kwargs):
        pass

class WeatherStation(Subject):
    def __init__(self):
        super().__init__()
        self._temperature = 0
        self._humidity = 0
    
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        self.notify()
    
    @property
    def humidity(self):
        return self._humidity
    
    @humidity.setter
    def humidity(self, value):
        self._humidity = value
        self.notify()

class TemperatureDisplay(Observer):
    def update(self, subject, *args, **kwargs):
        print(f"Temperature Display: {subject.temperature}°C")

class HumidityDisplay(Observer):
    def update(self, subject, *args, **kwargs):
        print(f"Humidity Display: {subject.humidity}%")

# Factory Method Pattern
class LoggerFactory(ABC):
    @abstractmethod
    def create_logger(self):
        pass

class FileLoggerFactory(LoggerFactory):
    def create_logger(self):
        return FileLogger()

class ConsoleLoggerFactory(LoggerFactory):
    def create_logger(self):
        return ConsoleLogger()

class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

class FileLogger(Logger):
    def log(self, message):
        print(f"Writing to file: {message}")

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"Logging to console: {message}")

# Test the Observer Pattern
print("Testing Observer Pattern:")
weather_station = WeatherStation()
temp_display = TemperatureDisplay()
humidity_display = HumidityDisplay()

weather_station.attach(temp_display)
weather_station.attach(humidity_display)

weather_station.temperature = 25
weather_station.humidity = 60

# Test the Factory Method Pattern
print("\\nTesting Factory Method Pattern:")
file_factory = FileLoggerFactory()
console_factory = ConsoleLoggerFactory()

file_logger = file_factory.create_logger()
console_logger = console_factory.create_logger()

file_logger.log("This is an important message")
console_logger.log("This is a debug message")

# Explanation of Pattern Selection
print("\\nDesign Pattern Selection Rationale:")
print("1. Observer Pattern: Used for the weather station to allow multiple displays")
print("   to be notified of changes in weather data without tight coupling.")
print("2. Factory Method Pattern: Used for creating logger objects, allowing the")
print("   application to create different types of loggers without knowing their")
print("   concrete classes, supporting the Open/Closed Principle.")
"""

    # Map assignments to draft content
    draft_contents = {
        1: basic_programming_content,
        2: functions_content,
        3: data_viz_content,
        4: design_patterns_content,
    }

    draft_id = 1

    # Create drafts for each assignment-student pair (not all students submit to all assignments)
    for assignment_id, content in draft_contents.items():
        # Get the course for this assignment
        assignment = assignments[assignment_id]
        course_id = assignment.course_id

        # Get enrollments for this course
        course_enrollments = [e for e in all_enrollments if e.course_id == course_id]

        # For each enrolled student, create 1-2 drafts
        for enrollment in course_enrollments[:4]:  # Limit to first 4 students
            student_email = enrollment.student_email

            # First draft - all students
            draft = Draft(
                id=draft_id,
                assignment_id=assignment_id,
                student_email=student_email,
                version=1,
                content=content,
                submission_date=get_current_time(),
                status="feedback_ready",  # Already processed
            )
            drafts.insert(draft)
            print(
                f"  Created draft for assignment ID {assignment_id}, student {student_email}"
            )
            draft_id += 1

            # Second draft - some students
            if random.random() > 0.5:
                # Add some improvements to the content
                improved_content = (
                    content
                    + "\n\n# Improvements based on feedback\n# Added error handling and comments"
                )
                draft = Draft(
                    id=draft_id,
                    assignment_id=assignment_id,
                    student_email=student_email,
                    version=2,
                    content=improved_content,
                    submission_date=get_current_time(),
                    status="submitted",  # Pending processing
                )
                drafts.insert(draft)
                print(
                    f"  Created second draft for assignment ID {assignment_id}, student {student_email}"
                )
                draft_id += 1


def create_sample_feedback():
    """Create sample feedback for drafts"""
    print("Creating sample feedback...")

    # Get all drafts with feedback_ready status
    ready_drafts = [draft for draft in drafts() if draft.status == "feedback_ready"]

    model_run_id = 1
    category_score_id = 1
    feedback_item_id = 1
    aggregated_feedback_id = 1

    for draft in ready_drafts:
        assignment_id = draft.assignment_id

        # Get assignment settings
        setting = next(
            (s for s in assignment_settings() if s.assignment_id == assignment_id), None
        )
        if not setting:
            continue

        # Get the rubric for this assignment
        rubric = next((r for r in rubrics() if r.assignment_id == assignment_id), None)
        if not rubric:
            continue

        # Get rubric categories
        categories = [cat for cat in rubric_categories() if cat.rubric_id == rubric.id]

        # Create model runs for this draft
        for run_number in range(1, setting.num_runs + 1):
            # Create model run
            model_run = ModelRun(
                id=model_run_id,
                draft_id=draft.id,
                model_id=setting.ai_model_id,
                run_number=run_number,
                timestamp=get_current_time(),
                prompt=f"Analyze the following code for assignment {assignment_id}...",
                raw_response="The detailed response from the LLM goes here...",
                status="complete",
            )
            model_runs.insert(model_run)

            # Create category scores for each category
            for category in categories:
                # Generate a random score between 0.7 and 1.0
                score = 0.7 + (random.random() * 0.3)
                confidence = 0.8 + (random.random() * 0.2)  # High confidence

                category_score = CategoryScore(
                    id=category_score_id,
                    model_run_id=model_run_id,
                    category_id=category.id,
                    score=score,
                    confidence=confidence,
                )
                category_scores.insert(category_score)
                category_score_id += 1

                # Create feedback items (1 strength, 1 improvement)
                # Strength feedback
                feedback_item = FeedbackItem(
                    id=feedback_item_id,
                    model_run_id=model_run_id,
                    category_id=category.id,
                    type="strength",
                    content=f"Strong point in {category.name}: The code demonstrates excellent {category.name.lower()}.",
                    is_strength=True,
                    is_aggregated=False,
                )
                feedback_items.insert(feedback_item)
                feedback_item_id += 1

                # Improvement feedback
                feedback_item = FeedbackItem(
                    id=feedback_item_id,
                    model_run_id=model_run_id,
                    category_id=category.id,
                    type="improvement",
                    content=f"Area for improvement in {category.name}: Consider enhancing {category.name.lower()} by applying best practices.",
                    is_strength=False,
                    is_aggregated=False,
                )
                feedback_items.insert(feedback_item)
                feedback_item_id += 1

            print(f"  Created model run {run_number} for draft ID {draft.id}")
            model_run_id += 1

        # Create aggregated feedback for each category
        for category in categories:
            # Get all category scores for this draft and category
            draft_runs = [run.id for run in model_runs() if run.draft_id == draft.id]
            category_scores_list = [
                score
                for score in category_scores()
                if score.model_run_id in draft_runs and score.category_id == category.id
            ]

            # Calculate aggregated score (simple average)
            if category_scores_list:
                aggregated_score = sum(
                    score.score for score in category_scores_list
                ) / len(category_scores_list)
            else:
                aggregated_score = 0.0

            # Create aggregated feedback
            agg_feedback = AggregatedFeedback(
                id=aggregated_feedback_id,
                draft_id=draft.id,
                category_id=category.id,
                aggregated_score=aggregated_score,
                feedback_text=f"Aggregated feedback for {category.name}: Overall good work with some areas for improvement.",
                edited_by_instructor=False,
                instructor_email="",
                release_date="",
                status="pending_review",  # Needs instructor review
            )
            aggregated_feedback.insert(agg_feedback)
            aggregated_feedback_id += 1

        print(f"  Created aggregated feedback for draft ID {draft.id}")


def main():
    """Main function to create all sample data"""
    # First clear all existing data
    clear_all_tables()

    # Create data in the correct order to maintain relationships
    create_users()
    create_courses()
    create_enrollments()
    create_assignments()
    create_rubrics()
    create_ai_models()
    create_system_config()
    create_assignment_settings()
    create_sample_drafts()
    create_sample_feedback()

    print("\nSample data creation complete!")


if __name__ == "__main__":
    main()
