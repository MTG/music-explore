from .analyze_spread import plot_dimension_spread_command, synthesize_all_spread_metrics_command
from .hubness import measure_hubness_command, visualize_hubness_command
from .rater_agreement import generate_pairs_command
from .statistics import measure_model_spread_command, measure_spread_command, measure_tag_spread_command


def init_app(app):
    app.cli.add_command(measure_tag_spread_command)
    app.cli.add_command(measure_model_spread_command)
    app.cli.add_command(measure_spread_command)
    app.cli.add_command(plot_dimension_spread_command)
    app.cli.add_command(synthesize_all_spread_metrics_command)
    app.cli.add_command(measure_hubness_command)
    app.cli.add_command(visualize_hubness_command)
    app.cli.add_command(generate_pairs_command)
