from .statictics import measure_tag_spread_command, measure_model_spread_command, measure_spread_command
from .analyze_spread import plot_dimension_spread_command


def init_app(app):
    app.cli.add_command(measure_tag_spread_command)
    app.cli.add_command(measure_model_spread_command)
    app.cli.add_command(measure_spread_command)
    app.cli.add_command(plot_dimension_spread_command)
