from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    users = [
        {"username":"vmontes","email":"hallen@hotmail.com"},
        {"username":"steven12","email":"hammondjacob@yahoo.com"},
        {"username":"cmartinez","email":"gellis@clark.com"},
        {"username":"raymond89","email":"chase26@castillo.org"},
        {"username":"vmiller","email":"ivanchen@gmail.com"},
        {"username":"cruzdenise","email":"wscott@johnson.com"},
        {"username":"pagetamara","email":"jeffreysmith@hotmail.com"},
        {"username":"connie96","email":"nathanmay@yahoo.com"},
        {"username":"ashley91","email":"jeremybell@mckinney.com"},
        {"username":"hobbsmatthew","email":"lauralove@gmail.com"},
    ]

    for u in users:
        db.session.add(User(
            username=u["username"],
            email=u["email"],
            password_hash=generate_password_hash("password123")
        ))
    db.session.commit()
