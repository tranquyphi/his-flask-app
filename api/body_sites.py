from flask import Blueprint, request, jsonify, render_template
from models import db, BodySite, BodyPart

body_sites_bp = Blueprint('body_sites', __name__)

# ---- API ROUTES ----
@body_sites_bp.route('/api/body_parts', methods=['GET'])
def list_body_parts():
    parts = BodyPart.query.order_by(BodyPart.BodyPartName).all()
    return jsonify([
        {"BodyPartId": p.BodyPartId, "BodyPartName": p.BodyPartName} for p in parts
    ])

@body_sites_bp.route('/api/body_sites', methods=['GET'])
def list_body_sites():
    body_part_id = request.args.get('BodyPartId')
    query = BodySite.query.join(BodyPart, BodySite.BodyPartId == BodyPart.BodyPartId, isouter=True)
    if body_part_id:
        query = query.filter(BodySite.BodyPartId == body_part_id)
    sites = query.with_entities(
        BodySite.SiteId, 
        BodySite.SiteName, 
        BodySite.BodyPartId,
        BodyPart.BodyPartName
    ).order_by(BodySite.SiteName.asc()).all()
    return jsonify([{
        "SiteId": s.SiteId, 
        "SiteName": s.SiteName, 
        "BodyPartId": s.BodyPartId,
        "BodyPartName": s.BodyPartName
    } for s in sites])

@body_sites_bp.route('/api/body_sites/<int:site_id>', methods=['GET'])
def get_body_site(site_id):
    site = BodySite.query.join(BodyPart, BodySite.BodyPartId == BodyPart.BodyPartId, isouter=True) \
        .filter(BodySite.SiteId == site_id) \
        .with_entities(
            BodySite.SiteId, 
            BodySite.SiteName, 
            BodySite.BodyPartId,
            BodyPart.BodyPartName
        ).first_or_404()
    return jsonify({
        "SiteId": site.SiteId, 
        "SiteName": site.SiteName, 
        "BodyPartId": site.BodyPartId,
        "BodyPartName": site.BodyPartName
    })

@body_sites_bp.route('/api/body_sites', methods=['POST'])
def create_body_site():
    data = request.json or {}
    site = BodySite(SiteName=data.get('SiteName'), BodyPartId=data.get('BodyPartId'))
    db.session.add(site)
    db.session.commit()
    # Return SiteId so frontend can show it in the success message
    return jsonify({"message": "Created", "SiteId": site.SiteId}), 201

@body_sites_bp.route('/api/body_sites/<int:site_id>', methods=['PUT'])
def update_body_site(site_id):
    data = request.json or {}
    site = BodySite.query.get_or_404(site_id)
    if 'SiteName' in data:
        site.SiteName = data['SiteName']
    if 'BodyPartId' in data:
        site.BodyPartId = data['BodyPartId']
    db.session.commit()
    return jsonify({"message": "Updated"})

@body_sites_bp.route('/api/body_sites/<int:site_id>', methods=['DELETE'])
def delete_body_site(site_id):
    site = BodySite.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ---- UI ROUTE ----
@body_sites_bp.route('/body_sites')
def body_sites_page():
    return render_template('body_sites.html')
