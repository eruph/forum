from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security import current_user

db = SQLAlchemy()
migrate = Migrate()


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect( url_for('security.login', next=request.url ))

class AdminView(AdminMixin, ModelView):
    pass

class HomeAdminView(AdminMixin, AdminIndexView):
    pass

class BaseModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super(BaseModelView, self).on_model_change(form, model, is_created)

class PostAdminView(AdminMixin, BaseModelView):
    pass

class TagAdminView(AdminMixin, BaseModelView):
    pass

def create_app(config_class=Configuration):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from app.view import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    ### ADMIN ###
    admin = Admin(app, 'GlitchNet', url='/', index_view=HomeAdminView(name='home'))
    admin.add_view(PostAdminView(models.Post, db.session))
    admin.add_view(AdminView(models.Thread, db.session))
    admin.add_view(AdminView(models.Topic, db.session))
    admin.add_view(AdminView(models.Tag, db.session))
    admin.add_view(AdminView(models.User, db.session))
    admin.add_view(AdminView(models.Role, db.session))

    ### FLASK SEC ###
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore)

    return app
