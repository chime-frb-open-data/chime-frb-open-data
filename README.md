<h1 align="center">
  <br>
  <a href="https://chime-frb-open-data.github.io"><img src="https://github.com/chime-frb-open-data/chime-frb-open-data.github.io/blob/79d7c2d574a6c849125583395f5442333630222d/docs/static/chime-frb-logo.png" alt="" width="25%"></a>
  <br>
  Utililes for CHIME/FRB Open Data Releases.
  <br>
</h1>


## Installation
```
pip install --user cfod

# To install with pandas support,
pip install --user cfod[pandas]
```

## Documentation
Check out the user documentation, [here](https://chime-frb-open-data.github.io/)

### Public VOEvents 

Are you a new or existing subscriber to the **CHIME/FRB VOEvent Service**? All relevant resources are located in `cfod/utilities`, including:
- Answers to frequently asked questions (FAQs).
- A set of introductory and quick-start slides for new subscribers.
- Sample CHIME/FRB VOEvent XML documents.
- A Jupyter notebook tutorial for working with CHIME/FRB VOEvent XML documents.

Or, perhaps you are seeking to [subscribe](https://chime-frb.ca/voevents) to the Service. 

**CHIME/FRB VOEvent Service**? They are located in `cfod/utilities`. 

## Developer
```
# cfod uses poetry for package management and virtualenv management
pip install poetry

git clone git@github.com:chime-frb-open-data/chime-frb-open-data.git
cd chime-frb-open-data

# Install git-commit hook
poetry run pre-commit install

# Make changes to the code and open a PR
```

## Removal
```
pip uninstall cfod
```


<p align="center">
  <a href="Some Love">
    <img src="https://forthebadge.com/images/badges/built-with-love.svg">
  </a>
</p>
