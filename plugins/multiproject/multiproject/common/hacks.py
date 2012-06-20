import trac

from genshi.builder import tag

from multiproject.core.configuration import conf
from trac.web.chrome import Chrome
from trac.util.text import obfuscate_email_address
import re

def Chrome_format_author_replacement(self, req, author):
    """ Audit Chrome.format_author method so that we get link to user profile

        Downside: This is a hack that interfere with the way trac renders usernames.
                  Will have some unwanted behaviour.

                  One such known unwanted behaviour is in the ticket view where owner and
                  reporter links are changed
    """
    if not author:
        return ""
    unwanted_users = ['trac', 'tracadmin', 'anonymous', 'authenticated', 'somebody']
    not_ticket = req.path_info.rsplit('/', 2)[1] != 'ticket'
    contain_email = bool(re.search('<.+>', author))
    ok_user = author not in unwanted_users
    username = author
    if not contain_email:
        user = conf.getUserStore().getUser(author)
        if user:
            author = user.getDisplayName()
    elif not Chrome(self.env).show_email_addresses:
        author = obfuscate_email_address(author)

    # Create a link to profile page or return author in plain
    if ok_user and not_ticket and not contain_email and conf.public_user_page_url:
        return tag.a(author, **{'href':conf.public_user_page_url + username, 'class':'author'})
    else:
        return author

trac.web.chrome.Chrome.format_author = Chrome_format_author_replacement
