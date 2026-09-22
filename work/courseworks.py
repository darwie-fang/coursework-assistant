"""Personal Columbia CourseWorks reader. Only explicitly allowed GET endpoints."""
import argparse
import datetime
import getpass
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://courseworks2.columbia.edu'
SECRET = Path(__file__).resolve().parent / '.secrets' / 'canvas-token'
PATTERN = re.compile(r'/api/v1/(?:courses|courses/\d+|courses/\d+/assignments(?:/\d+)?|courses/\d+/pages(?:/[A-Za-z0-9_-]+)?|courses/\d+/modules(?:/\d+/items)?|announcements|calendar_events)')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect refused; credentials were not forwarded.')

def validate(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc != 'courseworks2.columbia.edu' or parsed.fragment or not PATTERN.fullmatch(parsed.path):
        raise ValueError('Only approved Columbia course-reading endpoints are allowed.')
    for key, value in urllib.parse.parse_qsl(parsed.query):
        if key not in ('per_page', 'page', 'enrollment_state', 'include[]', 'context_codes[]', 'start_date', 'end_date', 'type') or (key == 'include[]' and value != 'syllabus_body'):
            raise ValueError('Only approved course-content query parameters are allowed.')
    return url

def read(path, params, token):
    url = validate(BASE + '/api/v1/' + path + '?' + urllib.parse.urlencode(params))
    opener = urllib.request.build_opener(NoRedirect())
    rows, seen = [], set()
    while url:
        validate(url)
        if url in seen or len(seen) >= 100:
            raise ValueError('Pagination limit reached; narrow the request.')
        seen.add(url)
        req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'}, method='GET')
        with opener.open(req, timeout=30) as response:
            payload = json.load(response)
            if not isinstance(payload, list):
                return payload
            rows.extend(payload)
            links = response.headers.get('Link', '')
            match = re.search(r'<([^>]+)>;\s*rel="next"', links)
            url = urllib.parse.urljoin(url, match.group(1)) if match else None
    return rows

def content_only(value):
    excluded = {'enrollments', 'user_id', 'calendar', 'uuid', 'submission', 'submissions',
                'score', 'scores', 'grade', 'grades', 'student', 'students'}
    if isinstance(value, dict):
        return {k: content_only(v) for k, v in value.items()
                if k not in excluded and not any(term in k.lower() for term in
                ('grade', 'score', 'submission', 'feedback'))}
    if isinstance(value, list):
        return [content_only(v) for v in value]
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='setup, or courses, courses/ID/assignments, courses/ID/pages, announcements, calendar_events')
    parser.add_argument('--param', action='append', default=[], help='Query parameter KEY=VALUE; repeat for arrays.')
    args = parser.parse_args()
    if args.path == 'setup':
        if not sys.stdin.isatty():
            raise ValueError('Run setup in Terminal so token entry stays hidden.')
        token = getpass.getpass('Paste your CourseWorks token (hidden), then press Return: ').strip()
        if not token or not token.isascii() or any(c.isspace() for c in token):
            raise ValueError('Token must be copied exactly from CourseWorks and contain only ASCII characters without spaces. Please run setup again.')
        SECRET.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(SECRET.parent, 0o700)
        fd = os.open(SECRET, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(token)
        print('Token saved locally with access restricted to your Mac user. Return to Codex and say ready.')
        return
    params = [('per_page', '100')]
    for param in args.param:
        if '=' not in param:
            raise ValueError('Parameters must use KEY=VALUE.')
        params.append(tuple(param.split('=', 1)))
    if not SECRET.exists():
        raise ValueError('Token not configured. Open Connect CourseWorks.command first.')
    token = SECRET.read_text().strip()
    if not token or not token.isascii() or any(c.isspace() for c in token):
        raise ValueError('The saved token contains unsupported characters. Please run Connect CourseWorks.command again and paste the exact token from CourseWorks.')
    result = read(args.path, params, token)
    print(json.dumps({'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': BASE + '/api/v1/' + args.path, 'data': content_only(result)}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        print('CourseWorks request failed (HTTP %s). Check token validity and course access.' % error.code, file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError) as error:
        # Do not print remote error bodies, request headers, or credentials.
        print(str(error) if isinstance(error, ValueError) else 'Could not access local storage or reach CourseWorks.', file=sys.stderr)
        sys.exit(1)
