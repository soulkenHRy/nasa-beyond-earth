"""Galaxy pictures: which kind of galaxy a picture shows, from the Galaxy-CLIP model, zero-shot.

    clip.py      loads the model from models/galaxy-clip-finetuned/ and ranks labels for a picture
    classify.py  the same from the terminal:  .venv/bin/python -m galaxy.classify picture.jpg
    check.py     tries it on ten well-known galaxies and saves what it says in numbers/GC_*.csv

The model is only used here, never trained. Its files are downloaded once and are not in git (see README).
"""
