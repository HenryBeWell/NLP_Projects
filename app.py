from flask import Flask
from flask import g
from flask import request
from flask import render_template
from flask import jsonify

from forms.news_extractor import NewsExtractorForm

app = Flask(__name__)


@app.route('/')
def nlp_projects():
    return render_template('index.html')

@app.route('/extract')
def extractor():
    return render_template('news_extractor.html')

if __name__ == '__main__':
    app.run()
