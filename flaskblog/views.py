import io
from typing import Tuple
from urllib.parse import urljoin

from flask import Flask, abort, current_app, g, render_template, request, send_file
from werkzeug.contrib.atom import AtomFeed
from werkzeug.wrappers import Response

from .md import markdown
from .models import Category, Post, Tag, User, Page
from .utils import get_tag_cloud


def load_site_config() -> None:
    if "site" not in g:
        user = User.get_one()
        g.site = user.read_settings()


def home() -> str:
    paginate = (
        Post.query.join(Post.category)
        .filter(Category.text != "About")
        .union(Post.query.filter(Post.category_id.is_(None)))
        .filter(~Post.is_draft)
        .order_by(Post.date.desc())
        .paginate(per_page=current_app.config["BLOG_PER_PAGE"])
    )
    tag_cloud = get_tag_cloud()
    return render_template(
        "index.html", posts=paginate.items, tag_cloud=tag_cloud, paginate=paginate
    )


def post(year: str, date: str, title: str) -> str:
    post = None
    for item in Post.query.all():
        if item.url == request.path:
            post = item
            break
    if not post:
        abort(404)
    return render_template("post.html", post=post)


def tag(text: str) -> str:
    tag = Tag.query.filter_by(url=request.path).first_or_404()
    posts = (
        Post.query.join(Post.tags)
        .filter(Tag.text == tag.text)
        .order_by(Post.date.desc())
    )
    tag_cloud = get_tag_cloud()
    return render_template("index.html", posts=posts, tag_cloud=tag_cloud, tag=tag)


def category(cat_id: int) -> str:
    cat = Category.query.get(cat_id)
    posts = cat.posts
    tag_cloud = get_tag_cloud()
    return render_template("index.html", posts=posts, tag_cloud=tag_cloud, cat=cat)


def favicon() -> Response:
    return current_app.send_static_file("images/favicon.ico")


def feed() -> Response:
    feed = AtomFeed(g.site["name"], feed_url=request.url, url=request.url_root)
    posts = Post.query.filter_by(is_draft=False).order_by(Post.date.desc()).limit(15)
    for post in posts:
        feed.add(
            post.title,
            str(markdown(post.content)),
            content_type="html",
            author=post.author or "Unnamed",
            url=urljoin(request.url_root, post.url),
            updated=post.last_modified,
            published=post.date,
        )
    return feed.get_response()


def sitemap() -> Response:
    posts = Post.query.filter_by(is_draft=False).order_by(Post.date.desc())
    fp = io.BytesIO(render_template("sitemap.xml", posts=posts).encode("utf-8"))
    return send_file(fp, attachment_filename="sitemap.xml")


def not_found(error: Exception) -> Tuple[str, int]:
    return render_template("404.html"), 404


def search() -> str:
    search_str = request.args.get("search")
    paginate = (
        Post.query.filter(~Post.is_draft)
        .whooshee_search(search_str)
        .order_by(Post.date.desc())
        .paginate(per_page=20)
    )
    return render_template("search.html", paginate=paginate, highlight=search_str)


def page(slug: str) -> str:
    item = Page.query.filter_by(slug=slug).first_or_404()
    return render_template("page.html", page=item)


def init_app(app: Flask) -> None:
    app.add_url_rule("/", "home", home)
    app.add_url_rule("/<int:year>/<date>/<title>", "post", post)
    app.add_url_rule("/tag/<text>", "tag", tag)
    app.add_url_rule("/cat/<int:cat_id>", "category", category)
    app.add_url_rule("/feed.xml", "feed", feed)
    app.add_url_rule("/sitemap.xml", "sitemap", sitemap)
    app.add_url_rule("/favicon.ico", "favicon", favicon)
    app.add_url_rule("/search", "search", search)
    app.add_url_rule("/<path:slug>", "page", page)

    app.register_error_handler(404, not_found)
    app.before_request(load_site_config)
