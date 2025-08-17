"""
BodySite Model
"""

from models_main import db

class BodySite(db.Model):
    __tablename__ = 'BodySite'
    
    SiteId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SiteName = db.Column(db.String(100), nullable=False)
    BodyPartId = db.Column(db.SmallInteger, db.ForeignKey('BodyPart.BodyPartId'))
    
    def __repr__(self):
        return f'<BodySite {self.SiteName}>'
