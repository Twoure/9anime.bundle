####################################################################################################
#                                                                                                  #
#                                   9anime Plex Channel                                            #
#                                                                                                  #
####################################################################################################
Common = SharedCodeService.common
Network = SharedCodeService.network.Network
from DumbTools import DumbKeyboard, DumbPrefs

# setup global variables
TITLE                       = Common.TITLE
PREFIX                      = Common.PREFIX
BASE_URL                    = Common.BASE_URL
GIT_REPO                    = 'Twoure/{}.bundle'.format(TITLE)

# setup Updater and inital run info
from pluginupdateservice import PluginUpdateService
Updater = PluginUpdateService()
Updater.initial_run

# more global variables
MAIN_MENUS = {
    'Newest': '/newest', 'Recent Update': '/updated',
    'On Going': '/ongoing', 'Most Watched': '/most-watched'
    }
ADULT_LIST = set(['Ecchi', 'Yaoi', 'Yuri'])
CP_DATE = ['Plex for Android', 'Plex for iOS', 'Plex Home Theater', 'OpenPHT']

# Set background art and icon defaults
MAIN_ART                    = 'art-default.jpg'
MAIN_ICON                   = 'icon-default.png'
NEXT_ICON                   = 'icon-next.png'
BOOKMARK_ICON               = 'icon-bookmark.png'
BOOKMARK_ADD_ICON           = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON        = 'icon-remove-bookmark.png'
BOOKMARK_CLEAR_ICON         = 'icon-clear-bookmarks.png'
SEARCH_ICON                 = 'icon-search.png'
PREFS_ICON                  = 'icon-prefs.png'
ABOUT_ICON                  = 'icon-about.png'

####################################################################################################
def Start():
    ObjectContainer.art = R(MAIN_ART)
    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(MAIN_ICON)
    DirectoryObject.art = R(MAIN_ART)
    PopupDirectoryObject.art = R(MAIN_ART)

    InputDirectoryObject.art = R(MAIN_ART)

    HTTP.CacheTime = int(Common.CACHE_TIME.total_seconds())  # 1hr cache for release
    version = get_channel_version()

    Log.Debug('*' * 80)
    Log.Debug('* Platform.OS            = {}'.format(Platform.OS))
    Log.Debug('* Platform.OSVersion     = {}'.format(Platform.OSVersion))
    Log.Debug('* Platform.CPU           = {}'.format(Platform.CPU))
    Log.Debug('* Platform.ServerVersion = {}'.format(Platform.ServerVersion))
    Log.Debug('* Channel.Version        = {}'.format(version))
    Log.Debug('*' * 80)

    if Dict['current_ch_version']:
        if Common.ParseVersion(Dict['current_ch_version']) < Common.ParseVersion(version):
            Log(u"* Channel updated from {} to {}".format(Dict['current_ch_version'], version))

    # setup current channel version
    Dict['current_ch_version'] = version

####################################################################################################
@handler(PREFIX, TITLE, MAIN_ICON, MAIN_ART)
def MainMenu():
    """Create the Main Menu"""

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = {}'.format(Client.Product))
    Log.Debug('* Client.Platform        = {}'.format(Client.Platform))
    Log.Debug('* Client.Version         = {}'.format(Client.Version))

    oc = ObjectContainer(title2=TITLE, no_cache=Client.Product in ['Plex Web'])

    cp_match = Client.Platform in Common.LIST_VIEW_CLIENTS

    # set thumbs based on client
    if cp_match:
        bookmark_thumb = None
        prefs_thumb = None
        search_thumb = None
    else:
        bookmark_thumb = R(BOOKMARK_ICON)
        prefs_thumb = R(PREFS_ICON)
        search_thumb = R(SEARCH_ICON)

    if Prefs['update_channel'] == 'Stable':
        # Setup Updater to track latest release
        Updater.gui_update(
            PREFIX + '/updater', oc, GIT_REPO,
            tag='latest', list_view_clients=Common.LIST_VIEW_CLIENTS
            )
    else:
        # Setup Updater to track branch commits
        Updater.gui_update(
            PREFIX + '/updater', oc, GIT_REPO,
            branch='dev', list_view_clients=Common.LIST_VIEW_CLIENTS
            )

    # setup basic main menus
    for (t, h) in MAIN_MENUS.items():
        oc.add(DirectoryObject(
            key=Callback(SubMenu, title=t, href=h), title=t,
            ))

    # setup prefs button
    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=prefs_thumb)
    else:
        oc.add(PrefsObject(title='Preferences', thumb=prefs_thumb))

    # setup search function
    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R(SEARCH_ICON))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', prompt='Search for...', thumb=search_thumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    """check prefs, placeholder for now"""

####################################################################################################
@route(PREFIX + '/submenu')
def SubMenu(title, href):
    oc = ObjectContainer(title2=title)

    headers = {'Referer': BASE_URL, 'User-Agent': Common.USER_AGENT}
    if 'search?' in href:
        headers.update({'Cookie': Network.get_cookies()})
    html = Network.ElementFromURL(BASE_URL + href, headers=headers)

    for ci in html.xpath('//div[@class="item"]'):
        img_node = ci.xpath('.//img')[0]
        stitle = img_node.get('alt').strip()
        if not stitle:
            stitle = ci.xpath('.//a[@class="name"]/text()')[0]
        thumb = img_node.get('src')
        thumb = DecodeHTMLEntities(thumb) if '&amp;' in thumb else thumb
        thumb = thumb.split('url=')[1] if 'url=' in thumb else thumb

        oc.add(DirectoryObject(
            key=Callback(ShowMenu, title=stitle, thumb=thumb, url=ci.xpath('.//a/@href')[0]),
            title=stitle, thumb=thumb
            ))

    try:
        paging = html.xpath('//div[@class="paging"]/a')[1]
        nhref = paging.get('href')
    except Exception as e:
        Log.Warn(u"* Warning, no content for '{}' >>>\n{}".format(BASE_URL + href, e))
        nhref = None

    if nhref:
        nhref = nhref if nhref.startswith('/') else '/'+nhref
        page = nhref.split('page=')[1]
        if Regex(r'P(\d+)$').search(title):
            title = Regex(r'P(\d+)$').sub('P' + page, title)
        else:
            title = title + ' P' + page
        oc.add(NextPageObject(
            key=Callback(SubMenu, title=title, href=nhref),
            title='Next Page {}>>'.format(int(page)), thumb=R(NEXT_ICON)
            ))

    if len(oc) == 0:
        oc.header = "Warning"
        if href.startswith('/search?'):
            oc.message = u"No Search results for '{}'".format(String.Unquote(href.split('keyword=')[-1], True))
        else:
            oc.message = u"{} Menu Empty".format(title)

    return oc

####################################################################################################
@route(PREFIX + '/showmenu')
def ShowMenu(title, thumb, url):
    oc = ObjectContainer(title2=title)

    html = Network.ElementFromURL(url)

    dt = [d.strip() for d in html.xpath('//dt[text()="Type:"]/following-sibling::dd/text()') if (d.strip() != ',') and (d.strip() != '')]
    kind = dt[0] if dt else None

    server_node = html.xpath('//div[@data-type="direct"]')
    if not server_node:
        oc.header = 'Warning'
        oc.message = 'There is no episodes for this anime, we will update asap!'
        return oc

    for db in server_node[0].xpath('.//a[@data-base]'):
        ep = db.get('data-base')
        href = db.get('href')
        etitle = db.text

        if kind and 'movie' in kind.lower():
            oc.add(MovieObject(
                title=etitle,
                thumb=thumb,
                source_title='9anime',
                url=href if href.startswith(BASE_URL) else BASE_URL + href
                ))
        else:
            if kind:
                season = 1 if 'tv' in kind.lower() else 0
            else:
                season = 0

            oc.add(EpisodeObject(
                title=etitle,
                show=title,
                index=int(ep),
                season=season,
                thumb=thumb,
                source_title='9anime',
                url=href if href.startswith(BASE_URL) else BASE_URL + href
                ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    query = query.strip()
    title = u'Search for "{}"'.format(query)
    href = u'/search?keyword={}'.format(String.Quote(query, True))
    return SubMenu(title, href)

####################################################################################################
def get_channel_version():
    plist = Plist.ObjectFromString(Core.storage.load(Core.plist_path))
    return plist['CFBundleVersion'] if 'CFBundleVersion' in plist.keys() else 'Current'
