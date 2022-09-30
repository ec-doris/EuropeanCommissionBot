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


def remove_duplicate(wikibase_repo):
    query = '''SELECT ?s WHERE { ?s wdt:P11012 ?o. }'''
    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    res = sparql_query(sparql, query)['results']['bindings']
    for r in res:
        qid = r['s']['value'].replace('http://www.wikidata.org/entity/', '')
        wikidata_item = pywikibot.ItemPage(wikibase_repo, qid)
        wikidata_item.get()
        qids = set()
        claims_to_remove = []
        if 'P11012' in wikidata_item.claims:
            for claim in wikidata_item.claims['P11012']:
                if claim.getTarget() not in qids:
                    qids.add(claim.getTarget())
                else:
                    print(f'http://www.wikidata.org/entity/{qid}', 'has duplicate', claim.getTarget(), 'removing it.')
                    claims_to_remove.append(claim)

        if len(claims_to_remove) > 0:
            wikidata_item.removeClaims(claims_to_remove, summary='Removing duplicate')


if __name__ == '__main__':
    wikibase = pywikibot.Site('wikidata', 'wikidata')
    wikibase_repo = wikibase.data_repository()
    wikibase_repo.login()
    remove_duplicate(wikibase_repo)
