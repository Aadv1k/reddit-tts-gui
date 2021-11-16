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


def auth(client_id, client_secret, username, password):
    return praw.Reddit(
        user_agent="Comment Extraction (by u/USERNAME)",
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
    )


def get_post(auth, subreddit='askreddit', get_body=False):
    reddit = auth
    data = []

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


def make_mp4_comments(auth, post_id, output='final.mp4', number_of_comments=10, Xcord=100, Ycord=100, color=(237, 230, 211)):
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

    video_clips = []
    engine = pyttsx3.init()
    title = get_title_by_id(a, post_id)

    # Save the title
    engine.save_to_file(title, f'{base_temp_path}/0.mp3')
    engine.runAndWait()

    # Save the title image
    base = Image.open('assets/wp.jpg')
    font = ImageFont.truetype(f'{base_assets_path}/font.ttf', 40)
    base_edit = ImageDraw.Draw(base)
    base_edit.text((Xcord, Ycord), title, color, font=font)
    base.save(f'{base_image_path}/0.jpg')

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
        base = Image.open('assets/wp.jpg')
        unwrapped_text = comment['body']
        wp = textwrap.TextWrapper(width=100)
        word_list = wp.wrap(unwrapped_text)
        wrapped_text = ""
        for g in word_list[:-1]:
            wrapped_text = wrapped_text + g + '\n'
        wrapped_text += word_list[-1]

        # Save a jpg of the text
        font = ImageFont.truetype('assets/font.ttf', 30)
        base_edit = ImageDraw.Draw(base)
        base_edit.text((100, 100), wrapped_text, (237, 230, 211), font=font)
        base.save(f'{base_image_path}/{i}.jpg')

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


def create_image(text, output_path, backdrop='wp.jpg', Xcord=100, Ycord=100, color=(237, 230, 211)):
    base = Image.open(f'assets/{backdrop}')
    font = ImageFont.truetype('assets/font.ttf', 35)
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


def make_video_posts(auth, subreddit, post_id, output='final.mp4', Xcord=100, Ycord=100, color=(237, 230, 211)):
    post = get_post(auth, subreddit, get_body=True)
    rand = random.randint(1, len(post))

    body = post[rand]['body']
    post_id = post[rand]['id']
    post_author = post[rand]['author']

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

    create_image(wrapped_title, f'{base_image_path}/0.jpg',
                 Xcord=Xcord, Ycord=Ycord, color=color)
    create_video_from_audio(
        f'{base_temp_path}/0.mp3', f'{base_image_path}/0.jpg', f'{base_temp_path}/0.mp4')
    os.remove(f'{base_temp_path}/0.mp3')
    video_clips.insert(0, f'{base_temp_path}/0.mp4')

    # Create text which is broken down
    unwrapped_text = body

    # Breaks down long texts into paras with width 1200, then its breaks down those pars into short sentences
    wrapped_text = wrap_text(unwrapped_text, width=1300)
    i = 1
    for paragraphs in wrapped_text:
        paragraphs = wrap_text(f'{paragraphs}', width=90)
        st = ""
        for sentences in paragraphs:
            st += sentences + '\n'

        engine.save_to_file(st, f'{base_temp_path}/{i}.mp3')
        engine.runAndWait()

        create_image(st, f'{base_image_path}/{i}.jpg',
                     Xcord=Xcord, Ycord=Ycord, color=color)

        create_video_from_audio(
            f'{base_temp_path}/{i}.mp3', f'{base_image_path}/{i}.jpg', f'{base_temp_path}/{i}.mp4')

        video_clips.append(f'{base_temp_path}/{i}.mp4')
        os.remove(f'{base_temp_path}/{i}.mp3')

        i += 1
    concatenate_video_moviepy(video_clips, 'final.mp4')


with open('credentials.json') as file:
    data = json.loads(file.read())

user_agent = data['user_agent']
client_id = data['client_id']
client_secret = data['client_secret']
username = data['username']
password = data['password']

a = auth(client_id, client_secret, username, password)

# Make comment video from the id
make_mp4_comments(a, 'qugfow', number_of_comments=5, Xcord=50, Ycord=50)

#make_video_posts(a, 'entitledparents')
