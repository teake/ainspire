ainspire
========

`ainspire` is an [Alfred 2](http://www.alfredapp.com) workflow for searching papers on [INSPIRE](http://inspirehep.net/).
It can do the following:

  * Searching all of INSPIRE from within Alfred.
  * Open the INSPIRE record page of a paper.
  * Search for more publications of a paper author.
  * Download and open the arXiv PDF of a paper.
  * Open the DOI referral of a paper.
  * Lookup references of a paper.
  * Lookup citations of a paper.
  * Copy the paper's BibTeX to the clipboard.
  * Search locally stored papers


Installation
------------

Download the [latest release](https://github.com/teake/ainspire/releases)
and open it (from the Finder or from Alfred) to import it in Alfred.

Usage
-----

### Searching INSPIRE ###

You can search INSPIRE by typing `insp {query}` in Alfred's main input. `insp` is the default keyword,
which can be changed editing the workflow via Aflred's prefences. For instance,

![incomplete query](https://raw.github.com/teake/ainspire/master/screenshots/incomplete_query.png)

will search for all papers that match `witten`. In order to perform the actual
search, you will need to hit enter after typing a search query. Beforing hitting
enter, `ainspire` will show you list of previous searches that match the
current one.

After pressing enter, Alfred will display the INSPIRE search results:

![example search](https://raw.github.com/teake/ainspire/master/screenshots/complete_query.png)

The loading of results may a couple of seconds or more, depending on the current traffic on INSPIRE.
Each paper in the search results is formatted as follows:

    Title of paper
    (Eprint or Year) Authors (Journal)

After selecting a paper from the results and pressing enter, a menu for that paper appears:

![paper menu](https://raw.github.com/teake/ainspire/master/screenshots/paper_menu.png)

From this menu, it is possible to do further searches (e.g. for more papers of the authors
or for citations of the paper), to go various websites (e.g. the INSPIRE record page
or the DOI referral page), or to copy the BibTeX of the paper to the clipboard.

If the paper has more than one author, selecting the `Find more papers of authors` item
will display another menu, from which it is possible search for papers from one of the authors.

Selecting the arXiv e-print will download it to a local folder (which can be set
in `ainspire`'s settings) and open it.

### Settings ###

By only entering the `ainspire` keyword (which is `insp` by default), it is possible
to go to `ainspire`'s settings:

![no query](https://raw.github.com/teake/ainspire/master/screenshots/no_query.png)

There, the following can be changed:

  * The cache can be cleared, which erased all stored previous searches.
  * The cache timeout (in days) can be adjusted, which affects how long searches are cached.
  * The local directory where PDFs from the arXiv can be set. It defaults to `~/Papers`.

### Local search ###

Not only does the local directory contain the PDFs downloaded from the arXiv, it can
also be searched for PDFs with the `paper` keyword:

![local search](https://raw.github.com/teake/ainspire/master/screenshots/local_search.png)

Besides returning PDFs that match the search query, the local search also offers a fallback
INSPIRE search for the same query, in case the locally stored PDFs are not what you're looking
for.


Limitations
-----------

`ainspire` only loads up to 100 results per search. Also, when looking up citations or references
of a paper, `ainspire` only shows those papers that have records in INSPIRE. Thus citations to
websites and such will not be included in the list of citations.
Furthermore, the BibTeX that can be copied to the clipboard is not the exact same BibTeX as
obtained directly from the INSPIRE website, but is equivalent to it.

Dependencies
------------

`ainspire` needs the following Python libraries:

  * alp (https://github.com/phyllisstein/alp)
    for communicating with Alfred 
  * pyinspire (https://bitbucket.org/ihuston/pyinspire/)
    for performing searches on INSPIRE
  * bs4 (http://www.crummy.com/software/BeautifulSoup/)
    because pyinspire needs it
  * bibtexparser (https://pypi.python.org/pypi/bibtexparser)
    for parsing BibTeX


If you check out the source from Git, you need to include these libaries in the `ainspire`
directory root in order obtain a working Alfred workflow. When you download the workflow from
the [releases page](https://github.com/teake/ainspire/releases), this is not necessary.

License
-------

[WTFPL](http://www.wtfpl.net/about/), of course.
