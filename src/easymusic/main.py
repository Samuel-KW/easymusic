

# Variables
file_data = 'data.csv'
file_input = 'urls.txt'

file_output = 'songs/'
new_songs_dir = 'new_songs/'


playlists_dir = 'Takeout/YouTube and YouTube Music/playlists'
file_type = 'm4a'

import os, re

import pafy, youtube_dl
from colorama import Fore, init
from shutil import copyfile

from mutagen.mp4 import MP4


init(convert = True) if os.name == 'nt' else init()

print(Fore.MAGENTA + '\nYouTube Downloader')
print(Fore.WHITE + 'https://github.com/Samuel-UC\n')

# Get downloaded song information
def get_song_data():
    
    songs = []
    lines = open(file_data).read().split('\n')
    
    for line in lines:
        if len(line) > 5:
            songs.append(line.split(','))

    return songs

# Get audio files from YouTube video ID and save to directory        
def get_audio(url, directory, save_new=False):

    try:
        audio = pafy.new('https://www.youtube.com/watch?v=' + url)
        
        print(Fore.CYAN + '\nDownloading' + Fore.YELLOW, audio.title + Fore.WHITE)
        
        # Get best audio quality
        audio_stream = audio.getbestaudio(preftype=file_type, ftypestrict=True)

        # Create filename
        filename = url + '.' + file_type

        # Parse data
        title  = re.sub('[^a-zA-Z0-9_]', '', re.sub(' ', '_', audio.title ))
        artist = re.sub('[^a-zA-Z0-9_]', '', re.sub(' ', '_', audio.author))
        
        # Save the file if isn't a duplicate
        if has_song(url, title, artist, False):

            print(Fore.RED + 'Song is already in collection:', Fore.YELLOW + audio.title)

            return
            
        else:

            filepath = os.path.join(directory, filename)
            audio_stream.download(filepath=filepath)

            try:
                audio = MP4(directory + filename)

                if not audio.tags:
                    audio.add_tags()
                
                audio.tags['\xa9nam'] = title
                audio.tags['\xa9ART'] = artist

                audio.tags['title'] = title
                audio.tags['artist'] = artist

                audio.save()
                
                if save_new:
                    copyfile(directory + filename, new_songs_dir + filename)
                    audio = MP4(new_songs_dir + filename)

                    if not audio.tags:
                        audio.add_tags()
                    
                    audio.tags['\xa9nam'] = title
                    audio.tags['\xa9ART'] = artist

                    audio.tags['title'] = title
                    audio.tags['artist'] = artist

                    audio.save()

            except Exception as e:

                print(Fore.RED + 'Error saving metadata:', e)

            songs.append([url, title, artist, filename])


        return filepath, filename

    except Exception as e:
        print(Fore.RED + str(e))

# Determine if song is already downloaded
def has_song(video_id, title='', artist='', strict=True):
    for song in songs:
        if song[0] == video_id:
            return True, song

        if not strict and song[1] == title and song[2] == artist:
            return True, song

    return False

# Save downloaded songs to file
def save_songs():
    data = []

    for song in songs:
        data.append(','.join(song))
    
    file = open(file_data, 'w')
    file.write('\n'.join(data))
    file.close()

# Start download of songs from array of video IDs
def start(urls, directory, save_new=False):

    index = 0
    for url in urls:
        index += 1

        video_id = url.strip();
        is_downloaded = has_song(video_id);

        if not is_downloaded:
            get_audio(video_id, directory, save_new)
            save_songs()
        else:
            print(Fore.RED + 'Song already downloaded:', Fore.YELLOW + is_downloaded[1][1])
        
        if os.name == 'nt':
            os.system('title Progress: ' + str(index) + ' / ' + str(len(urls)))

    

    print(Fore.CYAN + '\nFinished downloading' + Fore.YELLOW, len(urls), Fore.CYAN + 'audio files.')

# Parse data from Google takeout playlist data
def parse_from_takeout(directory):
    
    playlist_files = os.listdir(directory)
    print(Fore.WHITE + '\nSelect playlist to download:\n')

    for i in range(len(playlist_files)):
        print(Fore.YELLOW, '[' + str(i) + ']', Fore.CYAN, playlist_files[i])

    print(Fore.WHITE)

    selected = None
    while not selected:
        try:
            selected = playlist_files[int(input())]
        except:
            print(Fore.RED + 'Invalid selection.' + Fore.WHITE)

    print(Fore.CYAN + '\nParsing playlist:', Fore.YELLOW + selected)

    contents = open(os.path.join(directory, selected)).read().splitlines()[4:]
    urls = []

    for line in contents:
        if len(line) > 5:
            urls.append(line.split(',')[0])

    return urls

# Delete the contents of a folder
def delete_folder(directory):
    print(Fore.RED + '\nAre you sure you want to delete all files in', Fore.YELLOW + directory + Fore.RED + '?')

    files = os.listdir(directory)
    print(Fore.RED + 'You will be deleting' + Fore.YELLOW, len(files), Fore.RED + 'files.\n')

    if len(files) > 0:
        print(Fore.RED + 'Preview of files:')
        for file in files[:5]:
            print(Fore.YELLOW, file)

    print(Fore.WHITE)

    if input('Are you sure? (y/n): ') == 'y':
        for file in files:
            os.remove(os.path.join(directory, file))

# Get previously downloaded songs
songs = get_song_data()
print(Fore.CYAN + 'Parsed CSV data from' + Fore.YELLOW, file_data)

# List of song IDs to download
urls = []

# Download from urls.txt
if False:
    urls = open(file_input).read().splitlines()
    print(Fore.CYAN + 'Found file with' + Fore.YELLOW, len(urls), Fore.CYAN + 'links.\n')

# Download from takeout
else:
    urls = parse_from_takeout(playlists_dir)
    print(Fore.CYAN + 'Parsed playlist from' + Fore.YELLOW, playlists_dir)


save_new = False

print(Fore.CYAN + '\nWould you like to save new songs to', Fore.YELLOW + new_songs_dir + Fore.CYAN + '?' + Fore.WHITE)

if input('(y/n): ') == 'y':
    save_new = True
    delete_folder(new_songs_dir)

start(urls, file_output, save_new)
