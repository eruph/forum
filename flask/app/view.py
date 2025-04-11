from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Topic, Thread, Post, Tag
from app.forms import PostForm
from app import db
from flask_security import login_required

main = Blueprint('main', __name__)

@main.route('/post/<slug>/create', methods=['POST', 'GET'])
@login_required
def create_post(slug):

    thread_obj = Thread.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        try:
            post = Post(title=title, body=body, thread=thread_obj)
            db.session.add(post)
            db.session.commit()
        except:
            print("Error while add post")
        
        return redirect(url_for('main.thread_detail', slug=slug))
    
    form = PostForm()
    return render_template('create_post.html', form=form, thread=thread_obj)

@main.route('/post/<slug>/edit', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    thread_obj = post.thread
    form = PostForm(formdata=request.form, obj=post)

    if request.method == 'POST':
        form.populate_obj(post)
        db.session.commit()
        return redirect(url_for('main.thread_detail', slug=thread_obj.slug))
    
    return render_template('edit_post.html', post=post, form=form, thread=thread_obj)


@main.route('/')
def index():
    q = request.args.get('q')
    if q:
        topics = Topic.query.filter(Topic.title.ilike(f"%{q}%")).all()
    else:
        topics = Topic.query.all()

    return render_template('index.html', topics=topics)

@main.route('/<slug>')
def topic_detail(slug):
   
    topic = Topic.query.filter(Topic.slug==slug).first_or_404() 
    
    return render_template('topic_detail.html', topic=topic)

@main.route('/post')
def post():
    p = request.args.get('q')
    if p:
        posts = Post.query.filter(Post.title.ilike(f"%{p}%")).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template('post.html', posts=posts)


@main.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    return render_template('post_detail.html', post=post, tags=tags)


@main.route('/thread/<slug>')
def thread_detail(slug):
    thread_obj = Thread.query.filter_by(slug=slug).first_or_404()
    p = request.args.get('p')

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    if p:
        posts = thread_obj.posts.filter(Post.title.ilike(f"%{p}%"))
    else:
        posts = thread_obj.posts

    pages = posts.paginate(page=page, per_page=3)

    return render_template('thread_detail.html', thread=thread_obj, posts=posts, pages=pages)

@main.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug==slug).first()
    posts = tag.posts
    return render_template('tag_detail.html', tag=tag, posts=posts)
