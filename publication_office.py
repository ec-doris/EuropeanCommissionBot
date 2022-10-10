import pywikibot
import pandas as pd


def publication_office(wikibase_repo, filepath: str, edit_limit: int = 0):
    df = pd.read_csv(
        filepath,
        sep=','
    )
    nedit = 0
    for _, row in df.iterrows():
        if nedit < edit_limit or edit_limit <= 0:
            if not pd.isna(row['wikidata']) and row['confidence'] > 0.3:
                wid = row['wikidata'].replace('http://www.wikidata.org/entity/', '')
                # print(_, row['publication'], row['wikidata'], row['confidence'], wid)
                item = pywikibot.ItemPage(wikibase_repo, wid)
                try:
                    item.get()
                except pywikibot.exceptions.IsRedirectPageError:
                    item = item.getRedirectTarget()
                    item.get()
                    print(f'\033[91mRedirect\033[0m {wid} to {item.getID()}')
                is_in = False
                if 'P2888' in item.claims:
                    for claim in item.claims['P2888']:
                        if claim.getTarget() == row['publication']:
                            is_in = True

                if not is_in:
                    claim = pywikibot.Claim(wikibase_repo, 'P2888')
                    claim.setTarget(row['publication'])
                    item.editEntity(
                        data={'claims': [claim.toJSON()]},
                        summary='Adding exact Match to entity form the publication office of the European Union'
                    )
                    print(f'Adding {row["publication"]} to {row["wikidata"]}')


if __name__ == '__main__':
    wikibase = pywikibot.Site('wikidata', 'wikidata')
    wikibase_repo = wikibase.data_repository()
    wikibase_repo.login()
    publication_office(wikibase_repo, 'alignment-1.csv', 50)
