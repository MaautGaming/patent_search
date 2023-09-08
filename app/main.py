import os, json
from datetime import datetime
from fastapi import FastAPI
from elasticsearch import Elasticsearch


# Path of patent jsons
DOCS_DIR_NAME = "patent_jsons"
# Index name
INDEX_NAME = "patent_docs"

# get url for elasticsearch to connect:
ELASTIC_URL = os.environ.get("ELASTICSEARCH_HOSTS", "http://localhost:9200")

TYPE_FIELD_NAME_DICT = {"long": [], "date": [], "text": [], "boolean": []}


INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "abstracts": {
                "properties": {
                    "lang": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "paragraph_markup": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
            "application_date": {"type": "date"},
            "assignees": {
                "properties": {
                    "first_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "last_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
            "claims": {
                "properties": {
                    "claims": {
                        "properties": {
                            "num": {"type": "long"},
                            "paragraph_markup": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "parent": {"type": "long"},
                            "type": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                        }
                    },
                    "lang": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
            "cpc_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    }
                }
            },
            "descriptions": {
                "properties": {
                    "lang": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "paragraph_markup": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "ignore_malformed": "true",
                        },
                    },
                }
            },
            "ecla_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    }
                }
            },
            "f_term_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    }
                }
            },
            "family_id": {"type": "long"},
            "family_members": {
                "properties": {
                    "titles": {
                        "properties": {
                            "lang": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                            "text": {
                                "type": "text",
                                "fields": {"keyword": {"type": "keyword"}},
                            },
                        }
                    },
                    "ucid": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
            "inventors": {
                "properties": {
                    "first_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "last_name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "name": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
            "ipc_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "primary": {"type": "boolean"},
                }
            },
            "ipcr_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    }
                }
            },
            "legal_status": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "national_classes": {
                "properties": {
                    "label": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "primary": {"type": "boolean"},
                }
            },
            "patent_number": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "priority_date": {"type": "date"},
            "publication_date": {"type": "date"},
            "publication_id": {"type": "long"},
            "titles": {
                "properties": {
                    "lang": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "text": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                }
            },
        }
    }
}

# Try to connect to the elasticsearch service:
client = Elasticsearch(ELASTIC_URL)
while not client.ping():
    import time

    time.sleep(5)
    client = Elasticsearch(ELASTIC_URL)

# Initiate FastAPI app
app = FastAPI()


def extract_field_name(attr_dict: dict, field: str):
    if attr_dict.get("properties"):
        for k, v in attr_dict.get("properties").items():
            new_field = "%s.%s" % (field, k)
            extract_field_name(v, new_field)
    else:
        TYPE_FIELD_NAME_DICT[attr_dict["type"]].append(field)


# Checking if index exist and if not creating index on startup:
@app.on_event("startup")
def create_index():
    for field, type_dict in INDEX_MAPPING["mappings"]["properties"].items():
        extract_field_name(type_dict, field)
    # Check if index exist.
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=INDEX_MAPPING, ignore=[400])
        # Get all the json files from the folder:and open file to read from:
        for file_name in os.listdir(DOCS_DIR_NAME):
            full_path = "%s/%s" % (DOCS_DIR_NAME, file_name)
            with open(full_path) as file:
                # Get data in json format:
                doc_content = json.load(file)
                # Get all the data in a single text:
                client.index(
                    index=INDEX_NAME, id=doc_content["patent_number"], body=doc_content
                )


# Close connection when closing app.
@app.on_event("shutdown")
def close_conn():
    client.close()


@app.get("/search")
async def search(keyword: str):
    if keyword.isdecimal():
        keyword = int(keyword)
        match_into = [
            {"match": {"%s" % (field): keyword}}
            for field in TYPE_FIELD_NAME_DICT["long"]
        ]
    else:
        try:
            keyword = datetime.strptime(keyword, "%Y-%m-%d").date()
        except:
            match_into = match_into = [
                {"match": {"%s" % (field): keyword}}
                for field in TYPE_FIELD_NAME_DICT["text"]
            ]
        else:
            match_into = [
                {"match": {"%s" % (field): keyword}}
                for field in TYPE_FIELD_NAME_DICT["date"]
            ]
    script_query = {"query": {"bool": {"should": match_into}}}
    # Execute the search query
    search_results = client.search(index=INDEX_NAME, body=script_query)
    results = [i["_id"] for i in search_results["hits"]["hits"]]
    # Process and return the search results
    return {"results": results}
