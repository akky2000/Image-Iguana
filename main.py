from app import create_app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        from app.models import db
        db.create_all()
        import os
        os.makedirs('static', exist_ok=True)
        os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)