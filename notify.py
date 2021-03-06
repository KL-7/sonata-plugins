# this is the magic interpreted by Sonata, referring to on_enable etc. below:

### BEGIN PLUGIN INFO
# [plugin]
# plugin_format: 0, 0
# name: Notify plugin
# version: 0, 0, 1
# description: A simple notify plugin using pynotify.
# author: Leo Iannacone
# author_email: leo.iannacone@gmail.com
# url: http://en.leoiannacone.com/2009/05/a-simple-plugin-for-sonata/
# license: GPL v3 or later
# [capabilities]
# enablables: on_enable
# playing_song_observers: on_song_change
### END PLUGIN INFO

# nothing magical from here on

import ConfigParser
import os
import pynotify
import re

from sonata.library import library_set_data

cur_songinfo = None

# this gets called when the plugin is loaded, enabled, or disabled:
def on_enable(state):
    global notify, art_cache, art_location, music_dir
    if state:
        if pynotify.init("sonata"):
            notify = pynotify.Notification('sonata')
            filename = os.path.expanduser("~/.config/sonata/art_cache")
            if os.path.exists(filename):
                try:
                    f = open(filename, 'r')
                    r = f.read()
                    art_cache = eval(r)
                    f.close()
                except:
                    art_cache = {}
            else:
                art_cache = {}

            if os.path.isfile(os.path.expanduser('~/.config/sonata/sonatarc')):
                conf = ConfigParser.ConfigParser()
                conf.read(os.path.expanduser('~/.config/sonata/sonatarc'))
                if conf.has_option('player','art_location'):
                    art_location = conf.get('player','art_location')
                else:
                    art_location = None
                if conf.has_option('profiles', 'musicdirs[0]'):
                    music_dir = conf.get('profiles', 'musicdirs[0]')
                else:
                    music_dir = None
        else:
            print ('ALERT from "Notify plugin": Failed to load plugin notify. Module pynotify required.')
    else:
        notify = None
        art_cache = None
        conf = None


# this gets called when a new song is playing:
def on_song_change(songinfo):
    global cur_songinfo
    if songinfo == cur_songinfo:
        return
    else:
        cur_songinfo = songinfo
    if songinfo:
        art_folder = ''
        summary = "Current song:"
        body = songinfo['file']
        icon = "sonata"
        icon_tmp = None

        album = ''
        artist = ''
        genre = None
        year = None
        path = os.path.dirname(songinfo['file'])

        if 'title' in songinfo:
            summary = songinfo['title']
            if not summary[0].isupper():
                summary = summary.capitalize()

        if 'artist' in songinfo:
            body = 'by %s\n' % songinfo['artist']
            artist = songinfo['artist']

        if 'album' in songinfo:
            body += 'from %s' % songinfo['album']
            album = songinfo['album']

        if 'year' in songinfo:
            genre = songinfo['year']

        if 'genre' in songinfo:
            genre = songinfo['genre']

        cache_key = library_set_data (album=album, artist=artist, genre=genre, year=year, path=path)

        try:
            icon = art_cache[cache_key]
        except:
            try:
                cache_key = library_set_data (album=album, artist=artist, path=path)
                icon = art_cache[cache_key]
            except:
                icon = "sonata"

        if 'sonata-album.png' in icon:
            icon = 'sonata'

        if icon is 'sonata' and music_dir is not None:
            song_dir = '%s/%s' % (music_dir, path)
            # convert path like 'artist/album/CD 2' into 'artist/album'
            if re.compile(r'(?i)cd\s*\d+').match(os.path.split(song_dir)[1]):
                song_dir = os.path.split(song_dir)[0]
            arts = [os.path.join(song_dir, name) for name in 'cover.jpg', 'artwork.jpg', 'album.jpg', 'folder.jpg']
            arts.append(os.path.expanduser('~/.covers/%s-%s.jpg' % (artist, album)))
            arts = filter(os.path.isfile, arts)
            icon = arts and arts[0] or 'sonata'

        notify.set_property('body', body)
        notify.set_property('summary', summary)
        notify.set_property('icon-name', icon)

        if not notify.show():
            print ('ALERT from "Notify plugin": Failed to send notification')

