import typer

from reddit_sentiment.sentiment import Sentiment
from typing_extensions import Annotated

app = typer.Typer(help="Reddit Sentiment Analyzer")

@app.command()
def user(username: str,
         report: Annotated[bool, typer.Option("--report", "-r")] = False,
         authenticate: Annotated[bool, typer.Option("--auth", "-a")] = False):
    """
    Gets the sentiment of a reddit username
    """
    sentiment = Sentiment(authenticate, report)
    sentiment.get_user_sentiment(username, False)

@app.command()
def listing(subreddit: str,
            article_id: str,
            report: Annotated[bool, typer.Option("--report", "-r")] = False,
            authenticate: Annotated[bool, typer.Option("--auth", "-a")] = False):
    """
    Gets the sentiment of a reddit listing
    """
    sentiment = Sentiment(authenticate, report)
    sentiment.get_listing_sentiment(subreddit, article_id, False)

def main():
    app()

if __name__ == "__main__":
    typer.run(main)