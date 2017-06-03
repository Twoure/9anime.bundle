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
#BASE_URL                    = Common.BASE_URL
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
        #Setup Updater to track latest release
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

    if Prefs['login']:
        values = {
            'username': Prefs['username'],
            'password': Prefs['password'],
            'remember': '1'
            }
        ul_url = Prefs['domain'] + '/user/login'
        Network.unCache(ul_url)
        cookies = Network.cookies_from_res(Network.Request(ul_url, values=values))

        oc.add(DirectoryObject(
            key=Callback(OnDeck, title='On Deck', cookies=cookies), title='On Deck'
            ))

        oc.add(DirectoryObject(
            key=Callback(Watchlist, title='Watchlist', cookies=cookies), title='Watchlist'
            ))

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
@route(PREFIX + '/watchlist')
def Watchlist(title, cookies):
    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    headers = {'Referer': base_url, 'Cookie': cookies}
    html = Network.ElementFromURL(base_url + '/user/watchlist', headers=headers)
    for each in html.xpath("//div[@class='tabs']/a"):
        tab = each.xpath("./@data-name")[0]
        title = each.xpath("./text()")[0]
        href = '/user/watchlist?folder=' + tab

        oc.add(DirectoryObject(
            key=Callback(WatchlistTab, title=title, href=href, cookies=cookies),
            title=title
            ))

    return oc

####################################################################################################
@route(PREFIX + '/watchlist/tab')
def WatchlistTab(title, href, cookies):
    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    Network.unCache(base_url + href)
    headers = {'Referer': base_url, 'Cookie': cookies}
    html = Network.ElementFromURL(base_url + href, headers=headers)

    tab = href.split("folder=",1)[1].split("&",1)[0]
    for each in html.xpath("//div[@data-name='%s']/div[@class='links']/div" %tab):
        url = base_url + each.xpath("./div/a/@href")[0]

        title_show = url.split("watch/",1)[1].split(".",1)[0].replace("-"," ")

        thumb = each.xpath("./div/img/@src")[0]
        thumb = thumb.split('url=')[1] if 'url=' in thumb else thumb
        thumb = String.DecodeHTMLEntities(thumb) if '&amp;' in thumb else thumb

        oc.add(DirectoryObject(
            key=Callback(ShowMenu, title=title_show, thumb=thumb, url=url, cookies=cookies),
            title=title_show, thumb=thumb
            ))

    oc.add(DirectoryObject(
        key=Callback(Random, title='Random', tab=tab, cookies=cookies), title='Random'
        ))

    try:
        paging = html.xpath('//div[@data-name="%s"]//div[@class="paging"]//li' %tab)
        #Log(paging)
        paging = paging[len(paging)-1]
        if paging.get('class') == "disabled":
            nhref = None
        else:
            paging = paging.xpath('./a')[0]
            nhref = paging.get('href')
    except Exception as e:
        Log.Warn(u"* Warning, no content for '{}' >>>\n{}".format(base_url + href, e))
        nhref = None

    if nhref:
        nhref = nhref if nhref.startswith('/') else '/'+nhref
        page = nhref.split('page=')[1]
        if Regex(r'P(\d+)$').search(title):
            title = Regex(r'P(\d+)$').sub('P'+page, title)
        else:
            title = title + ' P' + page
        oc.add(NextPageObject(
            key=Callback(WatchlistTab, title=title, href=nhref, cookies=cookies),
            title='Next Page {}>>'.format(int(page)), thumb=R(NEXT_ICON)
            ))

    return oc

####################################################################################################
@route(PREFIX + "/random")
def Random(title, tab, cookies):

    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    headers = {'Referer': base_url, 'Cookie': cookies}
    html = Network.ElementFromURL(base_url + '/user/watchlist', headers=headers)

    try:
        pages = html.xpath("//div[@data-name='%s']//ul[@class='pagination']//li" %tab)
        num_pages = len(pages)-2
        list_show = html.xpath("//div[@data-name='%s']/div[@class='links']/div" %tab)
        num_per_page = len(list_show)
        paging = pages[len(pages)-2]
        paging = paging.xpath('./a')[0]
        href = paging.get('href')

        html = Network.ElementFromURL(base_url + "/" + href, headers=headers)
        list_show = html.xpath("//div[@data-name='%s']/div[@class='links']/div" %tab)
        num_show = len(list_show) + (num_pages - 1)*num_per_page
    except:
        list_show = html.xpath("//div[@data-name='%s']/div[@class='links']/div" %tab)
        num_show = len(list_show)
        num_per_page = len(list_show)

    random_value = int(Datetime.TimestampFromDatetime(Datetime.Now())) % num_show

    page_number = int(random_value/num_per_page) + 1
    wlf_href = "/user/watchlist?folder={0}&{0}-page={1}".format(tab, page_number)

    html = Network.ElementFromURL(base_url + wlf_href, headers=headers)
    list_show = html.xpath("//div[@data-name='%s']/div[@class='links']/div" %tab)

    random_value = random_value - num_per_page*(page_number - 1)
    url = base_url + list_show[random_value].xpath("./div/a/@href")[0]

    title_show = url.split("watch/",1)[1].split(".",1)[0].replace("-"," ")

    thumb = list_show[random_value].xpath("./div/img/@src")[0]
    thumb = thumb.split('url=')[1] if 'url=' in thumb else thumb
    thumb = String.DecodeHTMLEntities(thumb) if '&amp;' in thumb else thumb

    oc.add(DirectoryObject(
        key=Callback(ShowMenu, title=title_show, thumb=thumb, url=url, cookies=cookies),
        title=title_show, thumb=thumb
        ))

    return oc

####################################################################################################
@route(PREFIX + '/ondeck')
def OnDeck(title, cookies):

    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    wl_url = base_url + '/user/watchlist'
    headers = {'Referer': base_url, 'Cookie': cookies}

    Network.unCache(wl_url)
    html = Network.ElementFromURL(wl_url, headers=headers)

    for each in html.xpath("//div[@data-name='watching']/div[@class='links']/div"):
        try:
            show_url = each.xpath("./div/a/@href")[0].rsplit("?",1)[0]
            title = show_url.split("watch/",1)[1].split(".",1)[0].replace("-"," ")
            episode_number = int(each.xpath("./div[@class='link']/span[@class='current']/text()")[0]) + 1

            try:
                max_episode_number = each.xpath("./div[@class='info']/span[@class='status']/text()")[0]
                max_episode_number = int(Regex(r'\D*(\d+).*\/').search(max_episode_number).group(1))
                episode_number = None if (episode_number > max_episode_number) else episode_number
            except:
                episode_number = 1

        except:
            episode_number = 1

        if episode_number:
            html = Network.ElementFromURL(base_url + show_url)

            dt = [d.strip() for d in html.xpath('//dt[text()="Type:"]/following-sibling::dd/text()') if (d.strip() != ',') and (d.strip() != '')]
            kind = dt[0] if dt else None

            server_node = html.xpath('//div[@data-type="direct"]')
            if not server_node:
                oc.header = 'Warning'
                oc.message = 'There is no episodes for this anime, we will update asap!'

            db = html.xpath("//div[@id='servers']/div[@class='server row'][1]//li/a[@data-base='" + str(episode_number) + "']")[0]

            thumb = html.xpath("//div[@id='info']//img/@src")[0]
            thumb = thumb.split('url=')[1] if 'url=' in thumb else thumb
            thumb = String.DecodeHTMLEntities(thumb) if '&amp;' in thumb else thumb

            ep = db.get('data-base')
            href = db.get('href')
            etitle = db.text

            active = db.get('class')
            if active == 'active':
                etitle = '*' + etitle

            if kind and 'movie' in kind.lower():
                oc.add(MovieObject(
                    title=etitle,
                    thumb=thumb,
                    source_title='9anime',
                    url=href if href.startswith(base_url) else base_url + href
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
                    url=href if href.startswith(base_url) else base_url + href
                    ))

    return oc

####################################################################################################
@route(PREFIX + '/submenu')
def SubMenu(title, href):
    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    headers = {'Referer': base_url, 'User-Agent': Common.USER_AGENT}
    if 'search?' in href:
        cookies = Network.get_cookies()
        if not cookies:
            cookies = Network.unCache(base_url)
        if not cookies:
            oc.header = "Error"
            oc.message = u"{} Cookie Cache Error".format(title)
            return oc
        headers.update({'Cookie': cookies})
    html = Network.ElementFromURL(base_url + href, headers=headers)

    for ci in html.xpath('//div[@class="item"]'):
        img_node = ci.xpath('.//img')[0]
        stitle = img_node.get('alt').strip()
        if not stitle:
            stitle = ci.xpath('.//a[@class="name"]/text()')[0]
        thumb = img_node.get('src')
        thumb = thumb.split('url=')[1] if 'url=' in thumb else thumb
        thumb = String.DecodeHTMLEntities(thumb) if '&amp;' in thumb else thumb

        oc.add(DirectoryObject(
            key=Callback(ShowMenu, title=stitle, thumb=thumb, url=ci.xpath('.//a/@href')[0]),
            title=stitle, thumb=thumb
            ))

    try:
        paging = html.xpath('//div[@class="paging"]/a')[1]
        nhref = paging.get('href')
    except Exception as e:
        Log.Warn(u"* Warning, no content for '{}' >>>\n{}".format(base_url + href, e))
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
def ShowMenu(title, thumb, url, cookies=None):
    oc = ObjectContainer(title2=title)

    base_url = Prefs['domain']
    headers={'Referer': base_url, 'Cookie': cookies} if cookies else None
    html = Network.ElementFromURL(url, headers=headers)

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

        if cookies:
            active = db.get('class')
            if active == 'active':
                etitle = '*' + etitle

        if kind and 'movie' in kind.lower():
            oc.add(MovieObject(
                title=etitle,
                thumb=thumb,
                source_title='9anime',
                url=href if href.startswith(base_url) else base_url + href
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
                url=href if href.startswith(base_url) else base_url + href
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
