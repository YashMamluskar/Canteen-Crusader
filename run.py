# run.py

from app import create_app, db
from app.models import User, Item # Import models to make them available in the shell context

app = create_app()

# This decorator allows you to run `flask shell` and have app, db, and models pre-imported
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Item': Item}

if __name__ == '__main__':
    app.run(debug=True)