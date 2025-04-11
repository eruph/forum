from app import db
from datetime import datetime
import re
from flask_security import UserMixin, RoleMixin, login_required
from uuid import uuid4

def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'))
)


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), unique=True)
    slug = db.Column(db.String(140), unique=True)
    threads = db.relationship('Thread', backref='topic', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(Topic, self).__init__(*args, **kwargs)
        self.generate_slug()
    
    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
    
    def __repr__(self):
        return f"<Topic {self.title}>"

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    posts = db.relationship('Post', backref='thread', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f"<Thread {self.title} in Topic {self.topic.title}>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    
    tags = db.relationship('Tag', secondary='post_tags', back_populates='posts', overlaps="tags_in_post")

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()
    
    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)
    
    def __repr__(self):
        return f"<Post id: {self.id}, title: {self.title}>"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(140), unique=True)

    posts = db.relationship('Post', secondary='post_tags', back_populates='tags', overlaps="posts_in_tag")

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)
    
    def __repr__(self):
        return f"<Tag id: {self.id}, name: {self.name}>"
    
### FLASK SECURITY

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))