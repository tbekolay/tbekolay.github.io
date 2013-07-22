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

### Blog

@app.route('/blog.html')
@app.route('/blog_index_<int:back>.html')
def blog_index(back=0):
    if back < 0:
        raise ValueError("back is negative. Don't do that.")
    posts_per_page = 10
    start = back
    page = model.blogposts(back, back + posts_per_page)
    posts = len(page.blogposts)

    if back > 0:
        page.newer = url_for('blog_index', back=max(0, back - posts_per_page))
    else:
        page.newer = None
    if back < posts - posts_per_page:
        page.older = url_for('blog_index',
                             back=min(posts - 1, back + posts_per_page))
    else:
        page.older = None

    return render_template('blog_index.html', page=page)


@app.route('/blog_archive.html')
def blog_archive():
    return render_template('blog_archive.html', page=model.blogposts())


@app.route('/blog/<slug>.html')
def blog_post(slug):
    page = model.blogposts()
    post = next(bp for bp in page.blogposts if slugify(bp['title']) == slug)
    return render_template('blog_post.html', post=post)

### Static files

serve_static = [
    '/CNAME',
    '/favicon.ico',
    '/humans.txt',
    '/robots.txt',
]

def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

for url in serve_static:
    app.add_url_rule(url, 'static_from_root', static_from_root)


if __name__ == '__main__':
    app.run()
