# Keyword Searching in Patent using simply with FastAPI

This project uses FastAPI to expose a endpoint that accepts a keyword(as query parameter) and retreive document based on that contain that keyword.

Patent information document are used for test purposes.

### Required Setup

Make sure you have **_git_** and **_docker-engine_** on your system and is running.

### To start up the system

- Clone this [repo](https://github.com/MaautGaming/patent_search).

- Switch to branch **simplest_search_app** using
  `git checkout simplest_search_app`

- Run the following command to run the project:<br>
  `docker-compose up`

## Future Scope.

- [ ] Rate documents according to matching
- [ ] Entire string is matched as one can match up by breaking words.
