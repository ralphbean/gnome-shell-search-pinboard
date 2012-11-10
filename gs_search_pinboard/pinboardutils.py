import bs4
import getpass
import keyring
import requests


def load_auth():
    """ Load auth from the keyring daemon.

    This is kind of a bummer.  It would be awesome if we could keep this in
    gnome-shell's Online Accounts thing, but I guess they built that as a Silo
    on purpose (for some reason).  It's not pluggable so we can't just DIY
    without diving into gnome-shell proper.  Gotta do that some day, I guess.
    """
    keyring_service = 'pinboard-search-' + getpass.getuser()
    username = keyring.get_password(keyring_service, 'username')
    password = keyring.get_password(keyring_service, 'password')
    return username, password


def get_all(username, auth, term):
    url = "https://pinboard.in/search/"
    auth_dict = dict(username=auth[0], password=auth[1])
    data = dict(
        query=term,
        mine="Search Mine",
        fulltext="on",
    )

    # TODO -- persist the session.  it would be faster.
    with requests.session() as sess:
        response = sess.post("https://pinboard.in/auth", data=auth_dict)
        response = sess.get(url, params=data)

    soup = bs4.BeautifulSoup(response.content)

    result = soup.find_all("a", 'bookmark_title')
    results = []
    for link in result:
        results.append(dict(
            description=link.text.strip(),
            link=link['href'].strip()
        ))
    return results
