# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2021-09-14

### Added
- Creating playlists from lasso selection in comparison mode

## [0.3.0] - 2021-06-04

### Added
- New mode: comparison interface for proper music exploration
- New mode: similarity interface for gathering user feedback on segment similarity
- Annoy indexes for embeddings storage
- SQLite database for
  - Mapping between Annoy ids and `track_id` with timestamps
  - Track metadata (artist, album, tags)
- Reading metadata from ID3 tags for local collections and consuming Jamendo API for MTG-Jamendo dataset
- New projection: STD-PCA that standardizes individual embedding dimensions before applying PCA
- New projection: UMAP
- Experiments to measure hubness and spread
- Anonymized models for the user experiments
- Aggregation of embeddings into one file instead of having multiple small .npy files per track

### Changed
- Restructured app to have scripts as part of Flask app with `click` instead of `argparse`
- Optimized embeddings extraction script
- Modularized JS code

### Removed
- Old processing code using MusiCNN package directly in favor of newer Essentia extractors
- Support for seaborn plotting

## [0.2.2] - 2020-07-17

### Added
- Show artist name and track name with link to Jamendo website when playing audio

### Changed
- Better alerts
- Merged code for showing segments and trajectories

## [0.2.1] - 2020-05-29

### Added
- Support for different length of segments (for VGGish embeddings)

## [0.2.0] - 2020-05-25

### Added
- UI for selecting different models and datasets
- New dataset (pre-trained): MSD (Million Song Dataset)
- New model: VGG trained on both MSD and MTAT
- Dropdown selector for tags and PCA components with search functionality

### Changed
- UI for audio toggle and log scale moved
- Made the plot section bigger

### Removed
- Support for dynamic PCA
- Selection of layers for t-SNE (now only [0, 1])

## [0.1.0] - 2020-04-16

### Added
- Graph area for visualization
- Input field for number fo tracks
- Embeddings and taggrams from MusiCNN model trained on MTAT
- 3 ways to visualize latent spaces: segments, averages, trajectories
- 2 spaces: taggrams and penultimate
- 3 projections: PCA, t-SNE and original with numerical input fields for X and Y
- Selection of the way audio is played: on-click, on-hover and disabled
- Optional log-scale for visualizations that are too clustered to axes
- Experimental UI for music exploration
