# Keyword Searching in Patent document using ElasticSearch

This project is to demonstrate usage ElasticSearch along with FastAPI in a dockerised environment. This expose a single '/search' endpoint that accepts a `keyword` url parameter. And returns the list of document that contains that word of similar words. This uses a fuzzy search and also score the document according to the match with the word.

Patent information document are used for test purposes.

**Tech Stack**
Make sure you have git and docker-engine on your system and docker-daemon is running.
Clone this [repo](https://github.com/MaautGaming/patent_search) and move into this directory.

**To start up the system**
Run the following command to run the project:
`docker-compose up`

## Future Scope.

- [x] Semantic Search for keyword to map them to specific keys in json.
- [x] Expermenting with Analysizers for better indexing.
- [x] Query optimisation, experiment with scroll and scan function to reduce time.
- [x] Minimize dependency on external library.
