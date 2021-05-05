from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# course storage

class Course(db.Model):
	__tablename__ = 'course'
	
	id = db.Column(db.Integer, primary_key=True)
	subj = db.Column(db.String, nullable=False)
	code = db.Column(db.Integer, nullable=False)
	name = db.Column(db.String, nullable=False)
	desc = db.Column(db.String, nullable=True)
	credits = db.Column(db.Integer, nullable=False)
	CURover = db.Column(db.Float, nullable=False)
	CURdiff = db.Column(db.Float, nullable=False)
	CURwork = db.Column(db.Float, nullable=False)
	
	def __init__(self, **kwargs):
		self.subj = kwargs.get('subject')
		self.code = kwargs.get('code')
		self.name = kwargs.get('name')
		self.desc = kwargs.get('description')
		self.credits = kwargs.get('credits')
		self.CURover = kwargs.get('overall')
		self.CURdiff = kwargs.get('difficulty')
		self.CURwork = kwargs.get('workload')
	
	def serialize(self):
		return {
			"id": self.id,
			"subject": self.subj,
			"code": self.code,
			"name": self.name,
			"description": self.desc,
			"credit count": self.credits,
			"CU Reviews Overall": self.CURover,
			"CU Reviews Difficulty": self.CURdiff,
			"CU Reviews Workload": self.CURwork
		}
