from flask import Flask, render_template, logging

from process import process

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


@app.route('/')
def landing():
    audio_url = get_jamendo_stream_url('1100')
    return render_template('index.html', title='Music Exploration', url=audio_url)


def get_jamendo_stream_url(track_id):
    return f'https://mp3l.jamendo.com/?trackid={track_id}&format=mp31&from=app-{app.config["JAMENDO_CLIENT_ID"]}'


@app.route('/recompute_embeddings')
def recompute_embeddings():
    process()


if __name__ == '__main__':
    app.run()
