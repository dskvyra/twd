import json
import urllib, urllib2

def run_query(search_terms):
    root_url = 'https://api.datamarket.azure.com/Bing/Search/v1/'
    # root_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/'
    source = 'Web'

    results_per_page = 10
    offset = 0

    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    search_url = '{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}'.format(
        root_url,
        source,
        results_per_page,
        offset,
        query
    )

    username = ''
    bing_api_key = 'LV/Wzij1hspKVpDXD4CwgB3WKHML0UmewVjsBqejCuQ'

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, bing_api_key)

    results = []

    try:
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        response = urllib2.urlopen(search_url)

        json_response = json.load(response)
        #
        # import ipdb
        # ipdb.set_trace()

        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']
            })
    except urllib2.URLError, e:
        print 'Error when querying this Bing API: ', e

    return results

def main():
    query = raw_input('Enter your query: ')
    query = query.strip()
    results = []

    if query:
        results = run_query(query)
    else:
        print "You should use correct query"
        return

    ranked_results = zip(xrange(1, len(results) + 1), results)

    for rank, result in ranked_results:
        out = '#{} : {}\ntitle: {}\n'.format(rank, result['link'], result['title'])
        print out

if __name__ == '__main__':
    main()