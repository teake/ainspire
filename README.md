ainspire
========

`ainspire` is an [Alfred](http://www.alfredapp.com) workflow to search papers on [INSPIRE](http://inspirehep.net/).
It can do the following:

  * Searching all of INSPIRE from within Alfred.
  * Open the INSPIRE record page of a paper.
  * Search for more publications from a paper author.
  * Open the arXiv PDF of a paper.
  * Open the DOI referral of a paper.
  * Lookup references of a paper.
  * Lookup citations of a paper.
  * Copy the paper's BibTeX to the clipboard.

Installation
------------

Download the [latest release](https://github.com/teake/ainspire/releases)
and open it (from the Finder or from Alfred) to import it in Alfred.

Usage
-----

You can search INSPIRE by typing `insp {query}` in Alfred's main input. `insp` is the default keyword,
which can be changed editing the workflow via Aflred's prefences. For instance,

![incomplete query](https://raw.github.com/teake/ainspire/master/screenshots/incomplete_query.png)

will search for all papers writen by `witten, e`. Note that all queries need to end in a full stop (`.`)
in order to actually search on INSPIRE. So after adding a full stop, Alfred will display the results:

![example search](https://raw.github.com/teake/ainspire/master/screenshots/complete_query.png)

The loading of results may a couple of seconds or more, depending on the current traffic on INSPIRE.
Each paper in the search results is formatted as follows:

    Title of paper
    Year Authors (Journal)

After selecting a paper from the results and pressing enter, a menu for that paper appears:

![paper menu](https://raw.github.com/teake/ainspire/master/screenshots/paper_menu.png)

From this menu, it is possible to do further searches (e.g. for more papers of the authors
or for citations of the paper), to go various websites (e.g. the INSPIRE record page
or the DOI referral page, or to copy the BibTeX of the paper to the clipboard.

If the paper has more than one author, selecting the `Find more papers of authors` item
will display another menu, from which it is possible search for papers from one of the authors:

![paper menu](https://raw.github.com/teake/ainspire/master/screenshots/author_menu.png)


Limitations
-----------

`ainspire` only loads up to 100 results per search. Also, when looking up citations or references
of a paper, `ainspire` only shows those papers that have records in INSPIRE. Thus citations to
websites and such will not be included in the list of citations.
Furthermore, the BibTeX that can be copied to the clipboard is not the exact same BibTeX as
obtained directly from the INSPIRE website, but is equivalent to it.

Dependencies
------------

`ainspire` uses the following non-standard Python libraries:

  * alp (https://github.com/phyllisstein/alp)
  * bibtexparser (https://pypi.python.org/pypi/bibtexparser)
  * bs4 (http://www.crummy.com/software/BeautifulSoup/)
  * pyinspire (https://bitbucket.org/ihuston/pyinspire/)

If you're checking out the source from Git, you need to include these libaries in the `ainspire`
directory root in order obtain a working Alfred workflow. When you download the workflow from
the [releases page](https://github.com/teake/ainspire/releases), this is not necessary.

License
-------

[WTFPL](http://www.wtfpl.net/about/), of course.
