import json
from pathlib import Path

from flask import Flask, render_template, logging, url_for
import plotly

from visualize.commons import load_embeddings, reduce
from visualize.web import get_plotly_fig

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/')
@app.route('/playground')
def playground():
    return render_template('playground.html')


@app.route('/explore')
def explore():
    return render_template('explore.html')


def jamendo_template(track_id):
    token = app.config["JAMENDO_CLIENT_ID"]
    if not token:
        raise EnvironmentError('Jamendo client ID is not set')
    return f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{app.config["JAMENDO_CLIENT_ID"]}'


def localhost_template(track_id):
    return url_for('static', filename=f'audio/{int(track_id) % 100:02}/{track_id}.mp3')


@app.route('/jamendo/<string:track_id>')
def get_jamendo_stream_url(track_id):
    is_segmented = ':' in track_id
    url_suffix = ''
    if is_segmented:
        track_id, start, end = track_id.split(':')
        url_suffix = f'#t={start},{end}'

    url = localhost_template(track_id) if app.config['SERVE_AUDIO_LOCALLY'] else jamendo_template(track_id)

    return {
        'url': url + url_suffix
    }


@app.route('/tags')
def get_tags():
    return json.dumps(app.config['EMBEDDING_LABELS'])


@app.route('/plot/<string:plot_type>/<string:embeddings_type>/<int:n_tracks>/<string:projection_type>/<int:x>/<int:y>')
def plot(plot_type, embeddings_type, n_tracks, projection_type, x, y):
    try:
        embeddings_dir = Path(app.config['EMBEDDINGS_DIR'])
        if projection_type == 'original':
            embeddings_dir /= embeddings_type
        elif projection_type in ['pca', 'tsne']:
            if app.config['USE_PRECOMPUTED_PCA']:
                embeddings_dir /= f'{embeddings_type}_pca'  # lesser evil so far
            else:
                raise NotImplementedError('Dynamic PCA is not supported yet')
        else:
            raise ValueError(f"Invalid projection_type: {projection_type}, should be 'original', 'pca' or 'tsne'")

        dimensions = [x, y] if projection_type in ['original', 'pca'] else None
        embeddings, names = load_embeddings(embeddings_dir, n_tracks=n_tracks, dimensions=dimensions)

        if projection_type == 'tsne':
            embeddings = reduce(embeddings, projection_type, n_dimensions_out=2)

        figure = get_plotly_fig(embeddings, names, plot_type)

        if projection_type == 'original' and embeddings_type == 'taggrams':
            labels = app.config['EMBEDDING_LABELS']
            figure.update_layout(
                xaxis_title=labels[x],
                yaxis_title=labels[y]
            )
    except ValueError as e:
        return {'error': str(e)}, 400

    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.run()
