from flask import Flask, render_template, request
from crawler import gather_and_store, search_publications

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        results = gather_and_store()
        return render_template('results.html', results=results)
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_query():
    query = request.args.get('query')
    results = search_publications(query)
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)