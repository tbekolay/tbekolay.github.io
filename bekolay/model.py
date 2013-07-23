import datetime

# from flask import Flask, Markup
from flask import url_for
# from flask import request, send_from_directory

from .filters import get_headings, lead_paragraph, nice_date, slugify, youtubify

TYPE_TEXT = {
    'techreport': 'CTN Tech Report',
    'inbook': 'Book Chapter',
    'inproceedings': 'Conference Proceedings',
    'proceedings': 'Conference Proceedings',
    'book': 'Book',
    'mastersthesis': 'Thesis',
    'article': 'Journal Article',
}


class Model(object):
    def __init__(self, pages_instance):
        self.pages = pages_instance

    def blogpost(self, post):
        post.url = url_for('blog_post', slug=slugify(post['title']))
        post.headings = get_headings(post.html)
        return post

    def blogposts(self, start=None, end=None):
        page = self.pages.get('blog')
        blogposts = sorted([self.blogpost(p) for p in self.pages
                            if p.path.startswith('blog/')],
                           reverse=True, key=lambda post: post['date'])

        for p1, p2 in zip(blogposts[:-1], blogposts[1:]):
            p1.older = url_for('blog_post', slug=slugify(p2['title']))
            p2.newer = url_for('blog_post', slug=slugify(p1['title']))

        if end is not None and len(blogposts) > end:
            blogposts = blogposts[:end]
        if start is not None:
            blogposts = blogposts[start:]
        page.blogposts = blogposts
        return page

    def index(self):
        page = self.pages.get('index')
        page.pages = [self.section(section) for section in page['sections']]
        return page

    def section(self, slug):
        section = self.pages.get(slug)
        section.url = '/' + slug + '.html'
        return section

    # def meetings(self):
    #     return sorted([mtg for mtg in self.pages
    #                    if mtg.path.startswith('meetings/')],
    #                   reverse=True, key=lambda mtg: mtg['year'])

    # def person(self, person):
    #     person.url = url_for('people_page', slug=slugify(person['name']))
    #     return person

    # def people(self, group=None):
    #     if group is None:
    #         test = lambda p: p.path.startswith('people/')
    #     else:
    #         test = lambda p: p.path.startswith('people/') and p['group'] == group

    #     people = sorted([self.person(p) for p in self.pages if test(p)],
    #                     key=lambda p: p['name'])
    #     return people

    def publication(self, pub):
        if pub.meta.has_key('url'):
            pub.fulltext = pub['url']
        if pub['cite_info'].has_key('journal'):
            pub.journal = pub['cite_info']['journal']
        elif pub['type'] == 'techreport':
            pub.journal = "Tech Report"
        elif 'thesis' in pub['type']:
            pub.journal = "Thesis"
        elif 'book' in pub['type']:
            pub.journal = pub['cite_info']['publisher']
        elif pub['cite_info'].has_key('booktitle'):
            pub.journal = pub['cite_info']['booktitle']
        pub.authors = ["<strong>" + name + "</strong>"
                       if name == "Trevor Bekolay" else name
                       for name in pub['authors']]
        pub.type = TYPE_TEXT.get(pub['type'], pub['type'])
        return pub

    def research(self):
        page = self.pages.get('research')
        page.statement = self.pages.get('research/statement')
        page.courses = self.pages.get('research/courses')
        page.publications = [self.publication(self.pages.get('research/' + pub))
                             for pub in page['publications']]
        return page
