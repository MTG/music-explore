import json

from flask import Flask, render_template, logging
import plotly

from visualize import get_plotly_fig

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/')
def landing():
    return render_template('index.html', title='Music Exploration')


@app.route('/jamendo/<string:track_id>')
def get_jamendo_stream_url(track_id):
    return {
        'url': f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{app.config["JAMENDO_CLIENT_ID"]}'
    }


@app.route('/plot/<string:plot_type>/<string:embeddings_type>/<int:n_tracks>/<string:projection_type>')
def plot_reduced(plot_type, embeddings_type, n_tracks, projection_type):
    return plot(plot_type, embeddings_type, n_tracks, projection_type)


@app.route('/plot/<string:plot_type>/<string:embeddings_type>/<int:n_tracks>/custom/<int:x>/<int:y>')
def plot_custom(plot_type, embeddings_type, n_tracks, x, y):
    return plot(plot_type, embeddings_type, n_tracks, (x, y))


def plot(plot_type, embeddings_type, n_tracks, projection_type):
    if embeddings_type == 'penultimate':
        path = app.config["EMBEDDINGS_DIR"]
    elif embeddings_type == 'taggrams':
        path = app.config["TAGGRAMS_DIR"]
    else:
        return 400, f"Bad embeddings type: {embeddings_type}"

    try:
        data = get_plotly_fig(path, plot_type, n_tracks, projection_type)
    except ValueError as e:
        return 400, e

    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.run()
