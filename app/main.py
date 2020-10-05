import json
from pathlib import Path

from flask import Flask, render_template, url_for, g
import plotly

from visualize.commons import load_embeddings, reduce
from visualize.web import get_plotly_fig



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
           '<projection>/<int:x>/<int:y>')
def plot(plot_type, dataset, model, layer, n_tracks, projection, x, y):
    try:
        data_dir = Path(app.config['DATA_DIR'])
        # TODO: validate dataset-model-layer
        embeddings_dir = f'{dataset}-{model}-{layer}'

        if projection == 'original':
            data_dir /= embeddings_dir
        elif projection in ['pca', 'tsne']:
            data_dir /= f'{embeddings_dir}-pca'  # lesser evil so far
        else:
            raise ValueError(f"Invalid projection: {projection}, should be 'original', 'pca' or 'tsne'")

        dimensions = [x, y] if projection in ['original', 'pca'] else None
        embeddings, names = load_embeddings(data_dir, n_tracks=n_tracks, dimensions=dimensions)

        # TODO: try moving tsne to browser
        if projection == 'tsne':
            embeddings = reduce(embeddings, projection, n_dimensions_out=2)

        segment_length = get_metadata()['models'][model]['segment-length']
        figure = get_plotly_fig(embeddings, names, plot_type, segment_length)

        if projection == 'original' and layer == 'taggrams':
            tags = get_tags()[dataset]
            figure.update_layout(
                xaxis_title=tags[x],
                yaxis_title=tags[y]
            )
    except ValueError as e:
        return {'error': str(e)}, 400
    except FileNotFoundError as e:
        return {'error': str(e)}, 404

    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
