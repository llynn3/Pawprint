
import boto3
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from peewee import DoesNotExist
from playhouse.shortcuts import model_to_dict
import os
import time

from post import Post
from user import User

post = Blueprint('posts', __name__, url_prefix='/posts')

s3 = boto3.resource('s3')

@post.route('/')
@login_required
def get_all_posts():
    try:
        posts = [model_to_dict(post, exclude=[User.password]) for post in Post.select()]
        return jsonify(posts), 200
    except DoesNotExist:
        return jsonify(message="error getting posts."), 500

@post.route('/<int:id>', methods=['GET'])
@login_required
def get_one_post(id):
    try:
        post = Post.get_by_id(id)
        return jsonify(model_to_dict(post, backrefs=True)), 200
    except DoesNotExist:
        return jsonify(error="error getting the post."), 500

@post.route('/', methods=['POST'])
@login_required
def add_post():
    image = request.files['image']
    image_name = str(time.time_ns())
    response = s3.Bucket(os.environ.get('BUCKET')).put_object(Body=image, Key=image_name)
    caption = request.form['caption']
    image_url = f"https://{os.environ.get('BUCKET')}.s3.amazonaws.com/{image_name}"

    post = Post.create(caption=caption, image_url=image_url, user_id = current_user.id)
    return jsonify(model_to_dict(post, exclude=[User.password])), 201

@post.route('/<int:id>', methods=['PUT'])
@login_required
def update_post(id):
    try:
        body = request.get_json()
        (Post
            .update(**body)
            .where(Post.id == id)
            .execute())
        post = Post.get_by_id(id)
        return jsonify(model_to_dict(post, exclude=[User.password]))
    except DoesNotExist:
        return jsonify(message="error getting post."), 500


@post.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_post(id):
    try:
        (Post
            .delete()
            .where(Post.id == id)
            .execute())
        return jsonify(message="post successfully deleted."), 204
    except DoesNotExist:
        return jsonify(message="error getting post."), 500
