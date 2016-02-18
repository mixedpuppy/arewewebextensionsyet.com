import json
import os
import requests
import glob
import string
import csv

GET_BUGS = True
CHECK_URL = True

MDN_URL = 'https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/%s/%s'
schema_locations = [
    '../firefox/firefox/browser/components/extensions/schemas/',
    '../firefox/firefox/toolkit/components/extensions/schemas/'
]
schema_skip = [
    '../firefox/firefox/browser/components/extensions/schemas/context_menus_internal.json'
]
usage_file = 'usage.csv'

parsed_schema = {}


def parse_usage():
    res = {}
    with open(usage_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for k, row in enumerate(reader):
            res[row['API']] = k
    return res

parsed_usage = parse_usage()


def bugs(whiteboard):
    res = requests.get(
        'https://bugzilla.mozilla.org/rest/bug',
        params={
            'product': 'Toolkit',
            'component': 'WebExtensions',
            'whiteboard': '[%s]' % whiteboard,
            'include_fields': 'summary,status,resolution,id',
            'status': ['NEW', 'ASSIGNED', 'UNCONFIRMED', 'REOPENED']
        }
    )
    return res.json()


status_lookup = {
    "complete": "success",
    "partial": "warning",
    "not yet": "default",
    "unlikely": "default"
}


def formatted(data):
    res = ''
    for api, values in sorted(data.items()):
        res += '\t<h4 id="%s"><a href="#%s" class="anchor">&sect;</a> %s' % (api, api, api)
        res += '&nbsp;<span class="label label-%s">%s</span></h4>\n' % (status_lookup.get(values['status']), values['status'])
        res += '<blockquote>'
        if values['status'] in ['complete', 'partial']:
            res += '\t\t<a href="https://developer.mozilla.org/en-US/Add-ons/WebExtensions/API/%s">Firefox docs</a> &bull;\n' % api
        if 'code' in values:
            res += '\t\t<a href="%s">Firefox code</a> &bull;\n' % values['code']
        res += '\t\t<a href="https://developer.chrome.com/extensions/%s">Chrome docs</a>\n' % api


        pile_of_bugs = None
        if GET_BUGS:
            pile_of_bugs = bugs(api)

        if pile_of_bugs:
            res += '<h5><a id="%s-bugs" class="anchor">&sect;</a> %s bugs</h5>\n' % (api, len(pile_of_bugs['bugs']))
            res += '<table class="table table-striped">\n'
            for bug in pile_of_bugs['bugs']:
                res += '\t<tr>'
                res += '\t\t<td><a href="https://bugzilla.mozilla.org/show_bug.cgi?id=%s">%s: %s</a></td>\n' % (bug['id'], bug['id'], bug['summary'])
            res += '\t</tr>\n'
            res += '</table>'

        schemas = parsed_schema.get(api, {})
        res = htmlify_schema(res, schemas.get('functions', []), 'functions', api)
        res = htmlify_schema(res, schemas.get('events', []), 'events', api)

        res += '\t</blockquote>\n'
    return res


def htmlify_schema(res, schema, type_, api):
    if not schema:
        return res

    res += '<h5><a id="%s-%s" class="anchor">&sect;</a> %s %s</h5>\n' % (api, type_, len(schema), type_)
    res += '<table class="table table-striped">\n'
    for key, value in schema.items():
        res += '\t<tr>'
        res += '\t\t<td><span class="label label-%s">%s</span></td>' % (
            'success' if value['supported'] else 'danger',
            'supported' if value['supported'] else 'not supported'
            )

        if value['url']:
            res += '<td><a href="%s">%s</a></td><td></td>' % (value['url'], value['full'])
        else:
            res += '<td>%s</td><td><span class="label label-default">no docs</span></td>' % (value['full'])

        rank = parsed_usage.get(value['usage'], None)
        if rank:
            res += '<td><span class="label label-info">rank %s</span></td>' % rank
        else:
            res += '<td></td>'

        res += '</tr>\n'
    res += '</table>\n'
    return res


def process_schemas(directories):
    for directory in directories:
        for fname in glob.glob(directory + '*.json'):
            if fname in schema_skip:
                print 'Skipping:', fname
                continue
            print 'Parsing:', fname
            lines = open(fname, 'r').readlines()
            # Strip out stupid comments.
            newlines = []
            for line in lines:
                if not line.startswith('//'):
                    newlines.append(line)

            process_json(json.loads('\n'.join(newlines)))


def process_json(data):
    for element in data:
        for k, v in element.items():
            if k == 'namespace' and v != 'manifest':
                parsed_schema['__current__'] = v

    for element in data:
        for k, v in element.items():
            if k == 'functions':
                for function in v:
                    process_type('functions', function)
            if k == 'events':
                for event in v:
                    process_type('events', event)


def wikify(name):
    return string.capitalize(name[0]) + name[1:]


def check_url(url):
    res = requests.get(url).status_code == 200
    if not res:
        print url, '...failed.'
        return
    return res


def process_type(type, data):
    namespace = parsed_schema['__current__']
    parsed_schema.setdefault(namespace, {})
    parsed_schema[namespace].setdefault(type, {})
    full = 'chrome.%s.%s' % (namespace, data['name'])
    mdn = full[:]
    if type == 'functions':
        mdn += '()'
    url = MDN_URL % (wikify(namespace), data['name'])
    if CHECK_URL:
        url = url if check_url(url) else None
    parsed_schema[namespace][type][data['name']] = {
        'usage': full,
        'full': mdn,
        'supported': not(data.get('unsupported')),
        'url': url
    }


process_schemas(schema_locations)

data = json.load(open('data.json', 'r'))
html = open('template.html', 'r').read().encode('utf8')
data = formatted(data).encode('utf8')
html = html.format(data=data)
open('index.html', 'w').write(html)
