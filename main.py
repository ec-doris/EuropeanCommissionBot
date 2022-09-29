import datetime

import pywikibot

from SPARQLWrapper import SPARQLWrapper, JSON


def sparql_query(sparql: SPARQLWrapper, query: str, print_query: bool = False) -> dict:
    """
    Query the SPARQL endpoint.
    :param print_query:
    :param sparql:
    :param query:
    :return:
    """

    if print_query:
        print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def import_to_wikidata(wikibase_repo):
    query = '''SELECT ?s ?id WHERE {
          ?s wdt:P1 ?id;
            wikibase:statements ?n.
          FILTER(?n > 4)
        }
        '''
    sparql = SPARQLWrapper('https://query.linkedopendata.eu/proxy/wdqs/bigdata/namespace/wdq/sparql')

    res = sparql_query(sparql, query)['results']['bindings']
    print('Number of entity:', len(res))
    for r in res:
        wikidata_qid = r['id']['value']
        linkedopendata_qid = r['s']['value'].replace('https://linkedopendata.eu/entity/', '')
        try:
            wikidata_item = pywikibot.ItemPage(wikibase_repo, wikidata_qid)
            wikidata_item.get()
            is_in = False
            if 'P11012' in wikidata_item.claims:
                for claim in wikidata_item.claims['P11012']:
                    if claim.getTarget() == linkedopendata_qid:
                        is_in = True
                        break

            if not is_in:
                print(
                    '\033[91mDo\t',
                    'Wikidata',
                    f'http://www.wikidata.org/entity/{wikidata_qid}',
                    '\tLinkedopendata',
                    f'https://linkedopendata.eu/entity/{linkedopendata_qid}',
                    '\033[0m'
                )
                claim = pywikibot.Claim(wikibase_repo, 'P11012')
                claim.setTarget(linkedopendata_qid)
                wikidata_item.editEntity(
                    {'claims': [claim.toJSON()]},
                    summary='Importing EU Knowledge Graph item to Wikidata'
                )
            else:
                print(
                    '\033[94mDone\t',
                    'Wikidata',
                    f'http://www.wikidata.org/entity/{wikidata_qid}',
                    '\tLinkedopendata',
                    f'https://linkedopendata.eu/entity/{linkedopendata_qid}',
                    '\033[0m'
                )
        except pywikibot.exceptions.IsRedirectPageError:
            print(wikidata_qid, datetime.datetime.now())


if __name__ == '__main__':
    wikibase = pywikibot.Site('wikidata', 'wikidata')
    wikibase_repo = wikibase.data_repository()
    wikibase_repo.login()
    import_to_wikidata(wikibase_repo)
