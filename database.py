from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class Todo(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    notes = db.Column(String(100))
    priority = db.Column(Integer, default=0)
    completed = db.Column(Boolean, default=False)
    recommendations_json = db.Column(db.JSON)
    due_date = db.Column(String(50))

    recommendations = []   

    def __str__(self):
        return self.name
    
    def priority_str(self):
        match self.priority:
            case 1:
                return "High"
            case 2:
                return "Medium"
            case 3: 
                return "Small"
        

    def completed_str(self):
        if self.completed == True:
            return "Yes"
        else: 
            return "No"