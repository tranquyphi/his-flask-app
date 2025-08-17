"""
VisitSign Model
"""

from models_main import db

class VisitSign(db.Model):
    __tablename__ = 'VisitSign'
    
    VisitId = db.Column(db.BigInteger, db.ForeignKey('Visit.VisitId'), primary_key=True)
    SignId = db.Column(db.SmallInteger, db.ForeignKey('Sign.SignId'), primary_key=True)
    BodySiteId = db.Column(db.Integer, db.ForeignKey('BodySite.SiteId'))
    LeftRight = db.Column(db.Enum('trái', 'phải', 'cả hai bên', name='left_right'))
    Section = db.Column(db.Enum('toàn bộ', '1/3', '1/4', '1/5', name='section'))
    UpperLower = db.Column(db.Enum('trên', 'dưới', 'giữa', name='upper_lower'))
    FrontBack = db.Column(db.Enum('mặt trước', 'mặt sau', 'mặt trong', 'mặt ngoài', name='front_back'))
    SignValue = db.Column(db.Enum('', 'BT', 'Có DHBL', 'Có', 'Không', 'Ít', 'Vừa', 'Nhiều', 'Nhẹ', 'Tăng', 'Giảm', 'Như cũ', name='sign_value'))
    FollowUp = db.Column(db.Boolean, default=False)
    ForEmr = db.Column(db.Boolean, default=False)
    IsCustom = db.Column(db.Boolean, default=False)
