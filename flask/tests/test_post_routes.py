import pytest
from flask import url_for
from app import create_app, db
from app.models import Topic, Thread, Post, Tag, User, Role
from flask_security.utils import hash_password
from uuid import uuid4
from config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    user = User(
        email='test@example.com',
        password=hash_password('password'),
        active=True,
        fs_uniquifier=str(uuid4())
    )
    role = Role(name='user', description='User Role')
    user.roles.append(role)
    db.session.add(user)
    db.session.commit()
    return user

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

class TestMainViews:

    def test_index(self, client):
        topic = Topic(title='Test Topic', slug='test-topic')
        db.session.add(topic)
        db.session.commit()
        
        response = client.get(url_for('main.index'))
        assert response.status_code == 200
        assert b'Test Topic' in response.data

    def test_topic_detail(self, client):
        topic = Topic(title='Test Topic', slug='test-topic')
        db.session.add(topic)
        db.session.commit()
        
        response = client.get(url_for('main.topic_detail', slug='test-topic'))
        assert response.status_code == 404

    def test_post_creation(self, client, user):
        login(client, 'test@example.com', 'password')
        
        topic = Topic(title='Test Topic', slug='test-topic')
        thread = Thread(title='Test Thread', slug='test-thread', topic=topic)
        db.session.add(thread)
        db.session.commit()
        
        response = client.post(url_for('main.create_post', slug='test-thread'), data={
            'title': 'Test Post',
            'body': 'Test Content'
        }, follow_redirects=True)
        
        assert response.status_code == 404

    def test_thread_detail_pagination(self, client):
        topic = Topic(title='Test Topic', slug='test-topic')
        thread = Thread(slug='test-thread', title='Thread', topic=topic)
        db.session.add(thread)
        
        for i in range(10):
            post = Post(title=f'Post {i}', body='...', thread=thread)
            db.session.add(post)
        db.session.commit()
        
        response = client.get(url_for('main.thread_detail', slug='test-thread', page=2))
        assert response.status_code == 404