from types import WrapperDescriptorType
import moviepy
from moviepy.editor import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, VideoFileClip
from moviepy.editor import *
import textwrap

from PIL import Image, ImageFont, ImageDraw

import json
import pyttsx3
import os
import random

import praw
from praw.models import MoreComments


# HELPER FUNCTIONS
def get_post(auth, post_id="", get_body=False):
    reddit = auth
    data = []

    if post_id:
        submission = reddit.submission(post_id)
        if get_body:
            data.append({
                'title': submission.title,
                'body': submission.selftext,
                'author': submission.author,
                'ups': submission.ups,
                'id': submission.id
            })
        else:
            data.append({
                'title': submission.title,
                'author': submission.author,
                'ups': submission.ups,
                'id': submission.id
            })
    else:
        pass
    """
        else:
        for submission in reddit.subreddit(subreddit).hot(limit=25):
            if get_body:
                data.append({
                    'title': submission.title,
                    'body': submission.selftext,
                    'author': submission.author,
                    'ups': submission.ups,
                    'id': submission.id
                })
            else:
                data.append({
                    'title': submission.title,
                    'author': submission.author,
                    'ups': submission.ups,
                    'id': submission.id
                })

    """
    return data


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
    data = []
    submission = reddit.submission(id=post_id)
    return submission.title


def concatenate_video_moviepy(videos, out):
    clips = [VideoFileClip(c) for c in videos]
    final_clip = moviepy.editor.concatenate_videoclips(clips)
    final_clip.write_videofile(out)


def check_folders():
    if os.path.isdir('temp/') and os.path.isdir('images/'):
        pass
    else:
        try:
            os.mkdir('temp')
            os.mkdir('images')
        except FileExistsError:
            pass


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
    # wrapped_text = ""
    # for g in word_list[:-1]:
    #     wrapped_text = wrapped_text + g + '\n'
    # wrapped_text += word_list[-1]
    # return wrapped_text


def filter_nsfw(sentence):
    words = [i for i in sentence.split(' ')]
    result = ""
    for word in words:
        if word == "is":
            pass
        else:
            result += f'{word} '


# MAIN


def auth(client_id, client_secret, username, password):
    return praw.Reddit(
        user_agent="Comment Extraction (by u/USERNAME)",
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
    )


def make_mp4_posts(auth,  post_id, backdrop='wp.jpg', output='final.mp4', Xcord=100, Ycord=100, color=(255, 255, 255)):

    post = get_post(auth, post_id, get_body=True)[0]
    body = post['body']
    post_author = post['author']

    check_folders()
    base_image_path = 'images'
    base_temp_path = 'temp'
    base_assets_path = 'assets'

    video_clips = []
    engine = pyttsx3.init()
    title = get_title_by_id(a, post_id)

    # Save the title image
    wrapped_title = f"posted by user {post_author} \n"
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    # Save the title
    engine.save_to_file(wrapped_title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    create_image(wrapped_title, f'{base_image_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color)

    create_video_from_audio(
        f'{base_temp_path}/0.mp3', f'{base_image_path}/0.jpg', f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')

    # Create text which is broken down
    unwrapped_text = body

    # Breaks down long texts into paras with width 1200, then its breaks down those pars into short sentences
    # FONT - VERDANA
    # SIZE - 35
    # Main text width (defines how long text in the picture will be) = 2000
    # Sentence width (definines how wide sentences will be) = 110
    wrapped_text = wrap_text(unwrapped_text, width=2200)
    i = 1
    for paragraphs in wrapped_text:
        paragraphs = wrap_text(f'{paragraphs}', width=110)
        st = ""
        for sentences in paragraphs:
            st += sentences + '\n'

        engine.save_to_file(st, f'{base_temp_path}/{i}.mp3')
        engine.runAndWait()

        create_image(st, f'{base_image_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color)

        create_video_from_audio(
            f'{base_temp_path}/{i}.mp3', f'{base_image_path}/{i}.jpg', f'{base_temp_path}/{i}.mp4')

        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')

        i += 1
    concatenate_video_moviepy(video_clips, output)


def make_mp4_comments(auth, post_id, backdrop='wp.jpg', output='final.mp4', number_of_comments=10, font=30, Xcord=100, Ycord=100, color=(237, 230, 211)):
    """
    A function which creates a video from jpg and audio files of reddit posts (based on the permalink).

    permalink: REQUIRED the link of the post after "reddit.com"
    title: WILL BE REMOVED for now, you need to pass in the title
    output: name/path of the output file
    number_of_comments: how many comments to scrape; default 10
    Xcord, Ycord: Define the position of the text on the image
    color: Color of the text
    """
    check_folders()
    base_image_path = 'images'
    base_temp_path = 'temp'
    base_assets_path = 'assets'
    number_of_comments += 1
    backdrop_image = f'{base_assets_path}/{backdrop}'

    video_clips = []
    engine = pyttsx3.init()
    title = get_title_by_id(a, post_id)

    # Save the title
    engine.save_to_file(title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    # Save the title image
    #wrapped_title = f"posted by user {post_author} \n"
    wrapped_title = ""
    for words in wrap_text(title, width=90):
        wrapped_title += words + '\n'

    # Save the title image
    # base = Image.open(backdrop_image)
    # font = ImageFont.truetype(f'{base_assets_path}/font.ttf', 30)
    # base_edit = ImageDraw.Draw(base)
    # base_edit.text((Xcord, Ycord), wrapped_title, color, font=font)
    # base.save(f'{base_image_path}/0.jpg')
    create_image(wrapped_title, f'{base_image_path}/0.jpg', backdrop=backdrop,
                 Xcord=Xcord, Ycord=Ycord, color=color, font=font)

    audio_clip = AudioFileClip(f'{base_temp_path}/0.mp3')
    image_clip = ImageClip(f'{base_image_path}/0.jpg')
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')

    comments = get_comment(auth, post_id)

    i = 1
    while i < number_of_comments:
        try:
            comment = comments[i]
        except IndexError:
            print(f'Only {i} comments were found; stopping.')
            concatenate_video_moviepy(video_clips, output)
            break

        # Saves mp3 of the comment to a file
        engine.save_to_file(comment['body'], f'temp/{i}.mp3')
        engine.runAndWait()

        # Create text which is broken down
        # base = Image.open(backdrop_image)
        unwrapped_text = comment['body']
        wp = textwrap.TextWrapper(width=100)
        word_list = wp.wrap(unwrapped_text)
        wrapped_text = ""
        for g in word_list[:-1]:
            wrapped_text = wrapped_text + g + '\n'
        wrapped_text += word_list[-1]

        # Save a jpg of the text
        # font = ImageFont.truetype('assets/font.ttf', 30)
        # base_edit = ImageDraw.Draw(base)
        # base_edit.text((Xcord, Ycord), wrapped_text,
        #                (237, 230, 211), font=font)
        # base.save(f'{base_image_path}/{i}.jpg')
        create_image(wrapped_text, f'{base_image_path}/{i}.jpg', backdrop=backdrop,
                     Xcord=Xcord, Ycord=Ycord, color=color, font=font)

        # Combine image and audio
        audio_clip = AudioFileClip(f'{base_temp_path}/{i}.mp3')
        image_clip = ImageClip(f'{base_image_path}/{i}.jpg')
        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        video_clip.fps = 1
        video_clip.write_videofile(f'{base_temp_path}/{i}.mp4')
        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')

        i += 1

    concatenate_video_moviepy(video_clips, output)


with open('credentials.json') as file:
    data = json.loads(file.read())

user_agent = data['user_agent']
client_id = data['client_id']
client_secret = data['client_secret']
username = data['username']
password = data['password']

a = auth(client_id, client_secret, username, password)
# Make comment video from the id
#make_mp4_comments(a, 'qugfow', number_of_comments=1, Xcord=50, Ycord=50)
# make_mp4_comments(
#    a, 'askreddit', 'qv7kun', number_of_comments=10,  backdrop='alternate2.jpg', Ycord=150)

"""
desktop = os.path.join(os.getcwd(), '..', 'output.mp4')
make_mp4_comments(a, 'qv7kun', backdrop='alternate1.jpg',
                  number_of_comments=10, output=desktop)
"""
