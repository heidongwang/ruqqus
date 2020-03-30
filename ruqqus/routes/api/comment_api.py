import time
from flask import *
from ruqqus.classes import *
from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from secrets import token_hex
from ruqqus.routes.login import valid_password_regex, valid_username_regex
from ruqqus.__main__ import db, app
import re



@app.route("/api/v1/comments", methods=["GET"])
@app.route("/api/v1/comments/<id>", methods=["GET"])
@app.route("/api/v1/comments/<username>", methods=["GET"])
@admin_level_required(2)
def get_all_comments_api(v, username=None, id=None):
    if username:
        comments = db.query(Comment).filter_by(author_id=db.query(User).filter(User.username.ilike(username).first().id))
    elif id:
        comments = db.query(Comment).filter_by(author_id=base36decode(id))
    else:
        comments = db.query(Comment)
    comment=[]
    for c in comments.all():
        comment.append(c.json())
    return jsonify({"Comments": {comment}})



@app.route("/api/v1/comment/<id>", methods=["GET"])
@admin_level_required(2)
def get_comment_api(v, id):
    return jsonify(db.query(Comment).filter_by(id=base36decode(id)).first().json())

@app.route("/api/v1/comment", methods=["POST"])
@admin_level_required(2)
def create_comment_api(v):
    pass
    # TODO create comment
    #return jsonify(comment)

@app.route("/api/v1/comment/<id>", methods=["PUT"])
@admin_level_required(2)
def update_comment_api(v, id):
    """TODO : update logic"""
    return jsonify(db.query(Comment).filter_by(id=base36decode(id)).first().json())

@app.route("/api/v1/comment/<id>", methods=["DELETE"])
@admin_level_required(2)
def delete_comment_api(v, id):
    pass
    #db.delete(db.query(Comment).filter_by(id=base36decode(id)).first())
    #db.commit()
    #return "", 200

