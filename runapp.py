


from flask import Flask

app = Flask(__name__)
from app import app
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.run(debug=True)









