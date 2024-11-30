from app import db
from datetime import datetime

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade_level = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_type = db.Column(db.String(20), nullable=False)
    credit = db.Column(db.Float, nullable=False)
    grade_option = db.Column(db.String(20), nullable=False)
    semester1_grade = db.Column(db.String(2))
    semester2_grade = db.Column(db.String(2))
    full_year_grade = db.Column(db.String(2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
