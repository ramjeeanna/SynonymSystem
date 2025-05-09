from app.extensions import db

class Dictionary(db.Model):
    __tablename__ = 'Dictionary'  # Define the SQL Server table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(500), nullable=False)
    synonym = db.Column(db.String(500), unique=True, nullable=False)

    def __repr__(self):
        return f'<Dictionary {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "word": self.word,
            "synonym": self.synonym
        }



