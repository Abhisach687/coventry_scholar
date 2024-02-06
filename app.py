from flask import Flask, render_template, request
from crawler import crawl_and_index, search

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        results = crawl_and_index()
        return render_template('results.html', results=results)
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_query():
    query = request.args.get('query')
    results = search(query)
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)