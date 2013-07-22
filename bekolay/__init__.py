import datetime

from flask import Flask, Markup
from flask import abort, g, render_template, url_for
from flask import request, send_from_directory

from .filters import get_headings, lead_paragraph, nice_date, slugify, youtubify
from .pages import FlatPages
from .model import Model

DEBUG = True
SITE_NAME = "bekolay.org"
FREEZER_BASE_URL = 'http://bekolay.org/'

app = Flask(__name__)
app.config.from_object(__name__)
app.jinja_env.filters['lead_paragraph'] = lead_paragraph
app.jinja_env.filters['nice_date'] = nice_date
app.jinja_env.filters['slugify'] = slugify
pages = FlatPages(app)
model = Model(pages)

### Index

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', page=model.index())

serve_static = [
    '/CNAME',
    '/favicon.ico',
    '/humans.txt',
    '/robots.txt',
]

### Blog

@app.route('/blog.html')
@app.route('/blog_index_<int:back>.html')
def blog_index(back=0):
    if back < 0:
        raise ValueError("back is negative. Don't do that.")

    g.topic = 'blog'
    posts_per_page = 5
    start = back
    end = back + posts_per_page
    page = pages.get('blog')
    page.blogposts = model.blogposts(start=start, end=end)
    posts = sum([post.path.startswith('blog/') for post in pages])

    if back > 0:
        page.newer = url_for('blog_index', back=max(0, back - posts_per_page))
    else:
        page.newer = None
    if back < posts - posts_per_page:
        page.older = url_for('blog_index', back=min(posts - 1, end))
    else:
        page.older = None

    return render_template('blog_index.html', page=page)


def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

for url in serve_static:
    app.add_url_rule(url, 'static_from_root', static_from_root)


if __name__ == '__main__':
    app.run()
