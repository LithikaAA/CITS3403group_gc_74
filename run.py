from app import create_app, db

# Create the app using the factory
app = create_app()

# Create tables inside app context
with app.app_context():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
