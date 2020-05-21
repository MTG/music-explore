import json
from pathlib import Path

from flask import Flask, render_template, url_for, g
import plotly
import yaml

from visualize.commons import load_embeddings, reduce
from visualize.web import get_plotly_fig

MODELS_DESCRIPTION = 'Model: deep learning architecture'

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


@app.route('/metadata')
def get_metadata():
    if 'metadata' not in g:
        with open(Path(__file__).parent / 'metadata.yaml') as fp:  # TODO: find better way
            g.metadata = yaml.safe_load(fp)
    return g.metadata


def get_metadata_dict(entity, attribute='name'):
    metadata = get_metadata()
    return {key: value[attribute] for key, value in metadata[entity].items()}


def get_metadata_triplets(entity, first='name', second='description'):
    metadata = get_metadata()
    return [(key, value[first], value[second]) for key, value in metadata[entity].items()]


def make_triplets(data, description):
    return [(key, value, description) for key, value in data.items()]


@app.route('/tags')
def get_tags():
    return get_metadata_dict('datasets', 'tags')


@app.route('/')
@app.route('/playground')
def playground():
    return render_template('playground.html',
                           datasets=get_metadata_triplets('datasets'),
                           models=get_metadata_triplets('models'),
                           tags=get_tags())


@app.route('/explore')
def explore():
    track_ids = ['1022300:27:30', '1080900:0:3', '1080900:30:33']
    return render_template('explore.html', audio_urls=[get_audio_url(track_id)['url'] for track_id in track_ids])


def jamendo_template(track_id):
    token = app.config["JAMENDO_CLIENT_ID"]
    if not token:
        raise EnvironmentError('Jamendo client ID is not set')
    return f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{app.config["JAMENDO_CLIENT_ID"]}'


def localhost_template(track_id):
    return url_for('static', filename=f'audio/{int(track_id) % 100:02}/{track_id}.mp3')


@app.route('/jamendo/<string:track_id>')
def get_audio_url(track_id):
    is_segmented = ':' in track_id
    url_suffix = ''
    if is_segmented:
        track_id, start, end = track_id.split(':')
        url_suffix = f'#t={start},{end}'

    url = localhost_template(track_id) if app.config['SERVE_AUDIO_LOCALLY'] else jamendo_template(track_id)

    return {
        'url': url + url_suffix
    }


@app.route('/plot/<string:plot_type>/<string:dataset>/<string:model>/<string:layer>/<int:n_tracks>/'
           '<string:projection_type>/<int:x>/<int:y>')
def plot(plot_type, dataset, model, layer, n_tracks, projection_type, x, y):
    try:
        data_dir = Path(app.config['DATA_DIR'])
        # TODO: validate dataset-model-layer
        embeddings_dir = f'{dataset}-{model}-{layer}'

        if projection_type == 'original':
            data_dir /= embeddings_dir
        elif projection_type in ['pca', 'tsne']:
            data_dir /= f'{embeddings_dir}-pca'  # lesser evil so far
        else:
            raise ValueError(f"Invalid projection_type: {projection_type}, should be 'original', 'pca' or 'tsne'")

        dimensions = [x, y] if projection_type in ['original', 'pca'] else None
        embeddings, names = load_embeddings(data_dir, n_tracks=n_tracks, dimensions=dimensions)

        # TODO: try moving tsne to browser
        if projection_type == 'tsne':
            embeddings = reduce(embeddings, projection_type, n_dimensions_out=2)

        figure = get_plotly_fig(embeddings, names, plot_type)

        if projection_type == 'original' and layer == 'taggrams':
            tags = get_tags()[dataset]
            figure.update_layout(
                xaxis_title=tags[x],
                yaxis_title=tags[y]
            )
    except ValueError as e:
        return {'error': str(e)}, 400

    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
