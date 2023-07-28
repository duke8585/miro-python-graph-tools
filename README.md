# python miro api client for graph tasks

## goal

be able to take a miro graph made of stickies and connectors - e.g. an entity relationship diagram - and convert it to an edge list, such as a [trivial graph format](https://en.wikipedia.org/wiki/Trivial_Graph_Format) file.
the other functionality will be creating a miro graph from such an edge list TGF.
the REST API calls are wrapped into python functions for convenient usage

## install

simply run `make` or `make venv` if you already have pyenv and python 3.9.13 installed

## usage

* test the token via `auth_test()`
* it can be used to create a trivial graph file from a board with connected stickies via `make_tgf()`
* stickies and connectors can be made via `stickies_demo()`


## resources

* testing board: https://miro.com/app/board/uXjVM2vb9AQ=/
* inpired by : https://github.com/EasyLOB/Medium-Miro/blob/master/Python/API-Python/api.py
* article python api: https://medium.com/@easylob/create-miro-api-clients-in-c-and-python-from-openapi-specification-6cf2ae527cee
* tgf example in js: https://github.com/benjaminaaron/OntoEngine/blob/7888737053fd1a9ceaef3a3ce3a08ee0b78848c0/scripts/miro-importer/script.js
* tgf article: https://medium.com/miro-engineering/exploring-structured-data-as-graphs-in-miro-880aa4051b70
* tgf example: https://github.com/benjaminaaron/OntoEngine/tree/7888737053fd1a9ceaef3a3ce3a08ee0b78848c0/scripts/miro-importer
* PAT generation: https://developers.miro.com/reference/get-access-token-context
* dev docs: https://developers.miro.com/?utm_source=app-profile-menu

