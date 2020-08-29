# GSoC Final Documentation

## Adding Search suggestions for osm.org

OSM’s main search engine Nominatim does not support search suggestions. A separate database, which should be derived from the Nominatim database, should be set up for search suggestions. This DB should support regular updates from Nominatim DB. This must handle various languages. It must be small enough to run alongside Nominatim.

This project aims at setting up such a search suggester by comparing various alternative implementations like Elasticsearch, Solr. These suggesters set up indexing to facilitate quick suggestions to the users. The finalized stack will be integrated with the Nominatim search API. Complete installation and setup documentation along with a test suite will be created as a part of this project. 

## All important links

### Code

* [Indexing repository link](https://github.com/krahulreddy/nominatim-indexing/)
* [Nominatim UI PR]()
* [Nominatim UI branch](https://github.com/krahulreddy/nominatim-ui/tree/suggestions)
* [Proof of Concepts](https://github.com/krahulreddy/GSoc_POCs)
* [Elasticsearch and Solr comparison repo (Simple intro before starting the project)](https://github.com/krahulreddy/Search)

### Diary entries

* [Project introduction](https://www.openstreetmap.org/user/krahulreddy/diary/392958)
* [Community bonding](https://www.openstreetmap.org/user/krahulreddy/diary/393314)
* [Elasticsearch vs Solr](https://www.openstreetmap.org/user/krahulreddy/diary/393360)
* [Proof of concepts](https://www.openstreetmap.org/user/krahulreddy/diary/393458)
* [Phase 2 Update](https://www.openstreetmap.org/user/krahulreddy/diary/393800)

### Hosted Server

* [Server with Nominatim-UI (This will be offline after few days of completion of GSoC)](https://gsoc2020.nominatim.org/nominatim/ui/search.html)
* [API with suggestions (This will be offline after few days of completion of GSoC)](https://gsoc2020.nominatim.org/suggest/autocomplete?q=new%20york)


## Recap

This section contains a brief overview of the work done over the last 5 months (Including the proposal writing)

### Proposal
The prerequisite for applying for GSoC for OpenStreetMap was to have mapped with OpenStreetMap. For `Nominatim` projects, there was an extra `Pull Request` requirement. I started working and pushed the following code:

* [First PR](https://github.com/osm-search/Nominatim/pull/1714) for issue [#886](https://github.com/osm-search/Nominatim/issues/886).
    I had to understand how Nominatim processed queries in order to work on this issue and send a PR. This is not merged intentionally. The mentors said that this satisfied the criteria for applying for GSoC.

After this, I went on to selecting the topic for GSoC. I chose `Search suggestions for osm.org`, which was featured in the OpenStreetMap [Ideas Page](https://wiki.openstreetmap.org/wiki/Google_Summer_of_Code/2020/Project_ideas). This project was labeled `Hard`. I was new to Nominatim and Elasticsearch(and other alternatives). I quickly started asking questions on the Mailing list and started gathering requirements and details regarding the project.

Sarah Hoffmann and Marc Tobias helped me out in the process and I was able to come up with a good proposal!

Proposal link: [Final proposal](https://docs.google.com/document/d/1vWBA-2SCWA0mgDrKlynmzn2aVUvovjwlTb_w8wlyitQ/edit)

#### Other contributions

* [Fixed few links while reading the codebase](https://github.com/osm-search/Nominatim/pull/1760)

* [Advanced installations for Nominatim](https://github.com/osm-search/Nominatim/pull/1758) - Enables setup and updates for multiple data extracts for Nominatim.

### Community bonding

During the community bonding period, I took up an issue in Nominatim - [setup-website option](https://github.com/osm-search/Nominatim/pull/1829). This is part of the [modern PHP initiative](https://github.com/osm-search/Nominatim/milestone/2). I hope to take this work forward by taking up more issues of this milestone after GSoC.

I was also provided a server. I set up Nominatim on this server and worked towards understanding the code base better. I was also reading about elasticsearch and Solr during this phase. This helped us in later stage, when we had to decide on which search engine was to be finalized.

### Phase 1

This phase was meant for finalizing the tech stack and implementing Proof of Concepts. After a thorough comparison([diary entry](https://www.openstreetmap.org/user/krahulreddy/diary/393360)) of elasticsearch and Solr, we decided to go ahead with elasticsearch. The PoCs([diary entry](https://www.openstreetmap.org/user/krahulreddy/diary/393458)) covered almost all the technologies to be used in the final code.


### Phase 2

Due to other updates to the Nominatim repository, we decided to upgrade the server to Ubuntu 20.04. This was done by me as part of this phase.

At the end of Phase we had the server up and running with very simple prefix match suggestions. These were just based on the name of the place. Not with proper addresses, but the server was accessible and contained suggestions from elasticsearch.([diary entry](https://www.openstreetmap.org/user/krahulreddy/diary/393800))

### Phase 3

As part of this phase, the following work was done:

* Made sure the address formation is right, and indexed the planet-wide Database in most used languages.
* Made sure the indexing time was < 20 hours (This was regarded well within the limit, and approved.)
* Made sure the DB size was ~15 GB for 10 languages. (This was also well within the expected range and approved.)
* Made sure the final code is clean and well commented.
* Finalized the queries to provide accurate suggestions:
    * Tokenization and completion are used together to provide accurate results.
    * The results are sorted according to the importance score of places. This makes sure the suggestions are of more important places.
* Complete Documentation for setup and API usage (Available [here](https://github.com/krahulreddy/nominatim-indexing/tree/master))
* Updated the API based on suggestions from Sarah and Marc.
* UI of the suggestions was improved.
* Made sure results are returned based on browser default settings as well. (This helps for suggestion with place names only in non-default languages)

## Acknowledgements
My mentors Sarah Hofmann and Marc Tobias helped me throughout the process. Our weekly calls helped a lot in keeping the work flowing in the right direction. 

More than planned amount of work was done by the end of phase 1. I did another internship along with this GSoC project. That affected my work and communication with the mentors during the Phase 2 of the project. This was covered a bit by the extra work done during phase 1. But still, without this other commitment, I could have taken up few other tasks for this project. I still intend to work on this and improve the project beyond the scope of GSoC.

