import threading
import PySimpleGUI
import moviepy
from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip
import textwrap
import codeflow as cf

from PIL import Image, ImageFont, ImageDraw

import json
import pyttsx3
import os

import praw
from praw.models import MoreComments


# HELPER FUNCTIONS
def get_post(auth, post_id):
    reddit = auth

    submission = reddit.submission(post_id)
    return {
        'title': submission.title,
        'body': submission.selftext,
        'author': submission.author,
        'ups': submission.ups,
        'id': submission.id
    }


def get_comment(auth, post_id):
    reddit = auth
    data = []

    submission = reddit.submission(id=post_id)
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue

        data.append({
            'body': top_level_comment.body,
            'author': top_level_comment.author,
            'ups': top_level_comment.ups
        })
    return data


def get_title_by_id(auth, post_id):
    reddit = auth
    submission = reddit.submission(id=post_id)
    return {
        'title': submission.title,
        'ups': submission.ups,
    }


def concatenate_video_moviepy(videos, out):
    clips = [VideoFileClip(c) for c in videos]
    final_clip = moviepy.editor.concatenate_videoclips(clips)
    final_clip.write_videofile(out)


def check_folders():
    if os.path.isdir('temp/'):
        pass
    else:
        os.mkdir('temp')


def create_image(text, output_path, backdrop='wp.jpg', font=30, Xcord=100, Ycord=100, color=(237, 230, 211)):
    base = Image.open(f'assets/{backdrop}')
    font = ImageFont.truetype('assets/font.ttf', font)
    base_edit = ImageDraw.Draw(base)
    base_edit.text((Xcord, Ycord), text, color, font=font)
    base.save(output_path)


def create_video_from_audio(audio_path, image_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(output_path)


def wrap_text(unwrapped_text, width=80):
    wp = textwrap.TextWrapper(width=width)
    word_list = wp.wrap(unwrapped_text)
    return word_list


filter_list = {
    'fuck': 'frick',
    'fucking': 'fricking',
    'bitch': 'female dog',
    'shit': 'poop',
    'nta': 'not the ahole',
    'aita': 'am I the ahole',
    'wibta': 'Would I be the ahole',
}


def filter_nsfw(sentence, filter_list):
    nsfw_list = list(filter_list.keys())
    sentence = sentence.split('\n')
    split_sentence = " ".join(sentence)

    words = [i for i in (split_sentence.lower().split(' '))]
    result = ""
    for word in words:
        if word in nsfw_list:
            result += filter_list[word] + ' '
        else:
            result += word + ' '
    return result


# https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text
# MAIN

def auth():
    print(cf.auth()['token'])
    return praw.Reddit(
        client_id="LYQy5q5ICwT-QaTY2hcCow",
        client_secret="uvk6k7CGGgVIRqg40AfGlB_EC0FOtQ",
        refresh_token=cf.auth()['token'],
        user_agent="testscript by u/fakebot3",
    )


def make_mp4_posts(praw_auth, post_id, event_window, output='output.mp4', voice_id=1, backdrop='alternate1.jpg', filter_dict=filter_list,
                   Xcord=100, Ycord=100,
                   color=(255, 255, 255)):
    """
    A functions which created post videos; Taking a long post and slicing it into different frams; putting it all together in one video

    - auth: a praw auth object
    - post_id: id of the post
    - backdrop: looks for the backdrop image in assets/
    - output: output file path with name
    - Xcord, Ycord: specifies where the text should be located in the string.
    - color: Color in the rgb format as a tuple
    """

    text_area = event_window['-ML-']
    post = get_post(praw_auth, post_id)
    body = post['body']
    post_author = post['author']

    check_folders()
    base_temp_path = 'temp'

    video_clips = []
    # TODO change settings for mape_mp4_comments too
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 170)
    engine.setProperty('voice', voices[voice_id].id)
    title = get_title_by_id(praw_auth, post_id)['title']

    # Save the title image
    wrapped_title = f"posted by user {post_author} \n"
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    filtered_title = filter_nsfw(wrapped_title, filter_dict)
    print(filtered_title)
    # Save the title
    engine.save_to_file(filtered_title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    create_image(wrapped_title, f'{base_temp_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color)

    create_video_from_audio(
        f'{base_temp_path}/0.mp3', f'{base_temp_path}/0.jpg', f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')
    text_area.print(f'Created 0.mp4, at {base_temp_path}')

    # Create text which is broken down
    unwrapped_text = filter_nsfw(body, filter_dict)

    # Breaks down long texts into paras with width 1200, then its breaks down those pars into short sentences
    # FONT - VERDANA
    # SIZE - 35
    # Main text width (defines the length of the text in the picture) = 2000
    # Sentence width (defines the width of the sentence) = 110
    wrapped_text = wrap_text(unwrapped_text, width=2200)
    i = 1
    for paragraphs in wrapped_text:
        paragraphs = wrap_text(f'{paragraphs}', width=120)
        st = ""
        for sentences in paragraphs:
            st += sentences + '\n'

        engine.save_to_file(filter_nsfw(st, filter_dict),
                            f'{base_temp_path}/{i}.mp3')
        engine.runAndWait()

        create_image(st, f'{base_temp_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color)

        create_video_from_audio(
            f'{base_temp_path}/{i}.mp3', f'{base_temp_path}/{i}.jpg', f'{base_temp_path}/{i}.mp4')

        video_clips.append(f'{base_temp_path}/{i}.mp4')
        text_area.print(f'Created {i}.mp4 at {base_temp_path}')
        os.remove(f'{base_temp_path}/{i}.mp3')
        os.remove(f'{base_temp_path}/{i}.jpg')

        i += 1

    text_area.print(f'Combining clips...')
    concatenate_video_moviepy(video_clips, output)
    text_area.print(f'DONE, VIDEO AT {output}', text_color='Orange')


def make_mp4_comments(praw_auth, post_id, window, number_of_comments=10, voice=1, output='final.mp4', backdrop='alternate1.jpg',
                      filter_dict=filter_list, font_size=30, Xcord=100, Ycord=100, color=(237, 230, 211)):
    """
    A function which creates a video from jpg and audio files of reddit posts with the id.

    - auth: a praw instance, can be created by passing in credentials to the auth function
    - post_id: The id of the post; example - qvcxdt
    - backdrop: Looks for the image in assets/
    - output: path (with name) of the output file
    - number_of_comments: Number of comments to be scraped
    - font: Font size
    - Xcord, Ycord: Define the position of the text on the image
    - color: Color of the text
    """
    text_area = window['-ML-']
    check_folders()
    base_temp_path = 'temp'

    video_clips = []
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 175)
    engine.setProperty('voice', voices[voice].id)
    title = get_title_by_id(praw_auth, post_id)['title']

    # Save the title audio
    engine.save_to_file(title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    # Save the title image
    wrapped_title = ""
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    filtered_title = filter_nsfw(wrapped_title, filter_dict)
    engine.save_to_file(filtered_title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    create_image(filtered_title, f'{base_temp_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color, font=font_size)

    audio_clip = AudioFileClip(f'{base_temp_path}/0.mp3')
    image_clip = ImageClip(f'{base_temp_path}/0.jpg')
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    os.remove(f'{base_temp_path}/0.jpg')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')
    text_area.print(f'Saved 0.mp4 at {base_temp_path}/')
    comments = get_comment(praw_auth, post_id)

    i = 1
    while i < number_of_comments:
        try:
            comment = comments[i]
        except IndexError:
            print(f'Only {i} comments were found; stopping.')
            concatenate_video_moviepy(video_clips, output)
            break

        filtered_text = filter_nsfw(comment['body'], filter_dict)

        # Saves mp3 of the comment to a file
        engine.save_to_file(filtered_text, f'{base_temp_path}/{i}.mp3')
        engine.runAndWait()

        # Create text which is broken down
        unwrapped_text = filtered_text
        wp = textwrap.TextWrapper(width=100)
        word_list = wp.wrap(unwrapped_text)
        wrapped_text = ""
        for g in word_list[:-1]:
            wrapped_text = wrapped_text + g + '\n'
        wrapped_text += word_list[-1]

        # Save a jpg of the text
        create_image(wrapped_text, f'{base_temp_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color, font=font_size)

        # Combine image and audio
        audio_clip = AudioFileClip(f'{base_temp_path}/{i}.mp3')
        image_clip = ImageClip(f'{base_temp_path}/{i}.jpg')
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        video_clip.fps = 1
        video_clip.write_videofile(f'{base_temp_path}/{i}.mp4')
        text_area.print(f'Saved {i}.mp4 at {base_temp_path}/')
        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')
        os.remove(f'{base_temp_path}/{i}.jpg')

        i += 1

    text_area.print(f'Combining clips...')
    concatenate_video_moviepy(video_clips, output)
    text_area.print(f'DONE, VIDEO AT {output}', text_color='Green')


"""
USAGE
make_mp4_comments(a, 'qv7kun')
is all you need to get going, unless you removed the assets folder, in which case I would suggest you pull the repo
again
make_mp4_comments(a, 'qv7kun', backdrop='wp.jpg', number_of_comments=2)
"""


def get_ids(auth, sub):
    reddit = auth
    ids = []
    for submission in reddit.subreddit(sub).hot(limit=25):
        ids.append(f"{submission.title} --- {submission.id}")

    return ids


def gui(gui_auth):
    engine = pyttsx3.init()
    voice_names = []
    for voice_properties in engine.getProperty('voices'):
        voice_names.append(voice_properties.name)
    pg = PySimpleGUI
    pg.theme('DarkAmber')

    post_selection = [
        [
            pg.Text('Subreddit: '),
            pg.In(key='-SUBREDDIT-'),
            pg.Button('GO')
        ],

        [
            pg.Listbox(values=[], size=(60, 15),
                       key='-ID-', enable_events=True),
        ],

        [
            pg.Button('Select Id')
        ]

    ]

    video_options = [

        [pg.Frame('Post Selection', post_selection)],
        [pg.Frame('Video options', [
            [
                pg.Text('Number of comments: '),
                pg.Slider(orientation='h', range=(1, 50),
                          key='-SLIDER-', size=(30, 20))
            ],

            [
                pg.Text('Output path: '), pg.In(
                    size=(40, 10), key='-PATH_IN-'),
                pg.FolderBrowse(button_text='browse',
                                key='-FB-', initial_folder='.')
            ],

            [
                pg.Text('Voice: '),
                pg.Combo(voice_names, default_value=engine.getProperty('voices')[0].name,
                         size=(40, 20), key='-VOICE_LIST-')
            ],
        ])],

    ]

    frame = [
        [pg.Frame('Post information', [[pg.Multiline(size=(35, 10), do_not_clear=True,
                                                     key='-SL-', font=('Consolas', 12))]])],

        [pg.Frame('Video status', [[pg.Multiline(size=(40, 10), do_not_clear=True,
                                                 key='-ML-', font=('Consolas', 11))]])],

        [pg.Frame('Buttons', [[
            pg.Button('Get post'),
            pg.Button('Get comment')
        ]])]
    ]

    layout = [[pg.Column(video_options), pg.Column(frame)]]

    window = pg.Window('TTS SCRAPER', layout)

    while True:
        event, values = window.read()
        com_count = values['-SLIDER-']
        out_path = os.path.join(values['-PATH_IN-'], 'output.mp4')
        try:
            voice_id = voice_names.index(values['-VOICE_LIST-'])
        except ValueError:
            voice_id = 1

        if event == pg.WIN_CLOSED:
            break

        elif event == 'GO':
            sub = values['-SUBREDDIT-']
            try:
                post_ids = get_ids(gui_auth, sub)

                window['-ID-'].Update(values=post_ids)

            except Exception as e:
                window['-SL-'].print(
                    f'INVALID SUBREDDIT NAME, PLEASE TRY AGAIN', text_color='Orange')

        elif event == 'Select Id':
            try:
                post_id = (values['-ID-'][0]).split('---')[1]
                info = get_title_by_id(gui_auth, post_id)
                window['-SL-'].print(
                    f"Title: {info['title']}\nUpvotes: {info['ups']}", text_color='Orange')

            except IndexError:
                window['-SL-'].print(
                    f"SELECT AN ID", text_color='Orange')

        elif event == 'Get post':
            post_id = (values['-ID-'][0]).split('---')[1]
            print(post_id)

            title = get_title_by_id(gui_auth, post_id)['title']
            window['-ML-'].print(
                f'type: Reddit post\nvoice: {voice_names[voice_id]}\ngenerating video...')
            window['-ML-'].print(
                'WARNING - This might take some time, Do not close the window.', text_color='Orange')
            try:
                threading.Thread(target=make_mp4_posts, args=(
                    gui_auth, post_id, window, out_path, voice_id), daemon=True).start()

            except Exception as err:
                window['-ML-'].print(err)

        elif event == 'Get comment':
            post_id = (values['-ID-'][0]).split('---')[1]
            try:
                title = get_title_by_id(gui_auth, post_id)['title']
                window['-ML-'].print(
                    f'type: Reddit comment\nvoice: {voice_names[voice_id]}\ngenerating video...')
                window['-ML-'].print(
                    'WARNING - This might take some time, Do not close the window.', text_color='Orange')
                try:
                    threading.Thread(target=make_mp4_comments, args=(
                        gui_auth, post_id, window, com_count, voice_id, out_path), daemon=True).start()

                except Exception as err:
                    window['-ML-'].print(err)

            except Exception as err:
                window['-ML-'].print(err, text_color='Orange')

        elif event == '-POST_END-':
            print(values[event])


gui(auth())
