from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/experiences')
def experiences():
    return render_template('experiences.html')

@app.route('/stays')
def stays():
    return render_template('stays.html')

@app.route('/estates')
def estates():
    return render_template('estates.html')

if __name__ == '__main__':
    app.run(debug=True)