"""Generate discoverability metadata after repo name is known in GitHub Actions."""
from __future__ import annotations

import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1] / 'docs'


def pages_url(repository: str) -> str:
    parts = repository.split('/')
    if len(parts) != 2 or not all(parts):
        raise ValueError('Expected GitHub repository owner/name')
    owner, repo = parts
    if not all(part.replace('-', '').replace('_', '').isalnum() for part in (owner, repo)):
        raise ValueError('Invalid repository name')
    return f'https://{owner.lower()}.github.io/{repo}/'


def write_metadata(repository: str, root: Path = ROOT) -> str:
    url = pages_url(repository)
    file = root / 'index.html'
    html = file.read_text(encoding='utf-8')
    html = html.replace('<!-- SITE_URL_METADATA -->',
       f'<link rel="canonical" href="{url}" />\n'
       f'  <meta property="og:url" content="{url}" />\n'
       f'  <meta name="twitter:url" content="{url}" />')
    file.write_text(html, encoding='utf-8')
    (root / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {url}sitemap.xml\n', encoding='utf-8')
    (root / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{escape(url)}</loc></url>\n</urlset>\n', encoding='utf-8')
    return url


if __name__ == '__main__':
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        raise SystemExit('GITHUB_REPOSITORY is required to generate sitemap/canonical URLs')
    print('Canonical public URL:', write_metadata(repo))
