import datetime
import pytoml
import os
import os.path
import click

TerminalRed = "\033[1;31m",


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
    article_default_text = "%s+++++++\n" % pytoml.dumps(article_info)

    if not os.path.isfile("article/%s.md"):
        print("Error: Article '%s' is existed." % title)
        return

    file = open("article/%s.md" % title, "wt")
    file.write(article_default_text)
    file.close()


if __name__ == "__main__":
    main.add_command(init)
    main.add_command(new)
    main()
