'''html parts for the scraper'''
from typing import Union
import os


def fail_message(status, reason) -> str:
    '''message returned when the scraper failed'''
    html = "<h1>Search Failed</h1><br>"
    html += "<h2>Status: " + str(status) + "</h2><br>"
    html += "<h2>Reason: " + str(reason) + "</h2><br>"
    return html


def movie_page_link(
        query: str,
        page: int = 1,
        year: Union[int, None] = None,
        label: Union[str, None] = None
) -> str:
    '''creates a link for pagination of movie results'''
    html = "<a href='#' class='onclick' onclick='SearchMovie("
    html += '"' + query + '"' + ", year="
    html += str(year) if year else "null"
    html += ", page=" + str(page) + ");'>"
    html += label if label else str(page)
    html += "</a> "
    return html


def search_info(
        title: str,
        original_title: str,
        original_language: str,
        overview: str,
        release_date: str,
        poster_path: str,
        image_url: str,
        poster_size: str
) -> str:
    '''creates a movie pane for the search results'''
    html = str(open(os.path.dirname(__file__) +
                    "/html/moviesearchitem.html", "r").read())
    html = html.replace("%%TITLE%%", title)
    html = html.replace("%%ORIGINALTITLE%%", original_title)
    html = html.replace("%%ORIGINALLANGUAGE%%", original_language)
    html = html.replace("%%OVERVIEW%%", overview)
    html = html.replace("%%RELEASEDATE%%", release_date)
    if poster_path:
        html = html.replace("%%POSTERURL%%", image_url +
                            poster_size + poster_path)
    else:
        html = html.replace("%%POSTERURL%%", "")
    return html


def tvshow_page_link(query: str, page: int = 1, label: Union[str, None] = None) -> str:
    '''creates a link for pagination of tv show results'''
    html = "<a href='#' class='onclick' onclick='SearchTVShow("
    html += '"' + query + '"' + ", page=" + str(page) + ");'>"
    html += label if label else str(page)
    html += "</a> "
    return html


def yes_no_footer(yes_button: str, no_button: str) -> str:
    '''Footer for yes no'''
    html = str(open(os.path.dirname(__file__) +
                    "/html/yesnofooter.html", "r").read())
    html = html.replace("%%NOBUTTON%%", yes_button)
    html = html.replace("%%YESBUTTON%%", no_button)
    return html
