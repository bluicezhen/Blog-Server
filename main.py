import click
import datetime
import jinja2
import mistune
import pytoml
import os
import os.path


def jinja2_format_datetime(t: datetime.datetime):
    return t.strftime("%Y-%m-%d %H:%M")


@click.group()
def main():
    pass


@click.command(help='Create a new blog, default name is "blog"')
@click.argument("name", default="blog")
def init(name):
    """Init a blog.

    :arg name: Name of blog directory.
    """
    try:
        os.mkdir(name, mode=0o755)
        os.mkdir("%s/article" % name, mode=0o755)
        os.mkdir("%s/site" % name, mode=0o755)
    except FileExistsError:
        print("Error: Directory %s is existed, continue" % name)
        return


@click.command(help="Create a new article.")
@click.argument("title")
def new(title):
    article_info = {
        "title": title,
        "create_time": datetime.datetime.now().isoformat("T")
    }
    article_default_text = "%s+++++++\n\n##1" % pytoml.dumps(article_info)

    if os.path.isfile("article/%s.md" % title):
        print("Error: Article '%s' is existed." % title)
        return

    file = open("article/%s.md" % title, "wt")
    file.write(article_default_text)
    file.close()


@click.command(help="Create blog website")
def build():
    j_env = jinja2.Environment(loader=jinja2.PackageLoader("main", "template"))
    j_env.filters["format_time"] = jinja2_format_datetime
    j_template = j_env.get_template("article.html")

    articles = []

    file_names = os.listdir("article")
    for file_name in file_names:
        file = open("article/%s" % file_name, "rt")
        article_head_text, article_content_markdown = file.read().split("+++++++")
        file.close()

        article_head = pytoml.loads(article_head_text)
        article_title = article_head["title"]
        article_create_time = datetime.datetime.strptime(article_head["create_time"], '%Y-%m-%dT%H:%M:%S.%f')

        article_content_html = mistune.markdown(article_content_markdown)

        article_html = j_template.render(
            title       = article_title,
            create_time = article_create_time,
            content     = article_content_html
        )
        html_file_name = "%s.%s.html" % (article_create_time.isoformat("T"), article_title)
        file = open("site/%s" % html_file_name, "wt")
        file.write(article_html)
        file.close()

        articles.append({"title": article_title, "file_name": html_file_name, "create_time": article_create_time})

    articles = sorted(articles, key=lambda item: item["create_time"], reverse=True)
    j_template = j_env.get_template("index.html")
    index_html = j_template.render(articles=articles)

    file = open("site/index.html", "wt")
    file.write(index_html)
    file.close()


if __name__ == "__main__":
    main.add_command(init)
    main.add_command(new)
    main.add_command(build)
    main()
