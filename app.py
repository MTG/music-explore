import json

from flask import Flask, render_template, logging, url_for
import plotly

from visualize import get_plotly_fig

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/')
def landing():
    return render_template('index.html', title='Music Exploration')


def jamendo_template(track_id):
    return f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{app.config["JAMENDO_CLIENT_ID"]}'


def localhost_template(track_id):
    return url_for('static', filename=f'audio/{int(track_id) % 100:02}/{track_id}.mp3')


@app.route('/jamendo/<string:track_id>')
def get_jamendo_stream_url(track_id):
    is_segmented = ':' in track_id
    if is_segmented:
        track_id, start, end = track_id.split(':')

    url = localhost_template(track_id) if app.config['SERVE_AUDIO_LOCALLY'] else jamendo_template(track_id)

    if is_segmented:
        url += f'#t={start},{end}'
    return {
        'url': url
    }


@app.route('/plot/<string:plot_type>/<string:embeddings_type>/<int:n_tracks>/<string:projection_type>')
def plot_reduced(plot_type, embeddings_type, n_tracks, projection_type):
    return plot(plot_type, embeddings_type, n_tracks, projection_type)


@app.route('/plot/<string:plot_type>/<string:embeddings_type>/<int:n_tracks>/custom/<int:x>/<int:y>')
def plot_custom(plot_type, embeddings_type, n_tracks, x, y):
    return plot(plot_type, embeddings_type, n_tracks, (x, y))


def plot(plot_type, embeddings_type, n_tracks, projection_type):
    if embeddings_type == 'penultimate':
        path = app.config['EMBEDDINGS_DIR']
    elif embeddings_type == 'taggrams':
        path = app.config['TAGGRAMS_DIR']
    else:
        return {'error': f'Bad embeddings type: {embeddings_type}'}, 400

    try:
        data = get_plotly_fig(path, plot_type, n_tracks, projection_type)
    except ValueError as e:
        return {'error': str(e)}, 400

    return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.run()
