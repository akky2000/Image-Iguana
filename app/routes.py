from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/usage')
def usage():
    return render_template('usage.html', title='Usage')
