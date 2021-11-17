# Reddit text to speech generator

A basic reddit tts video generator

# Current functionality

- Generate videos for subs based on comments,(askreddit) so reading individual comments
- Generate videos for subs with longer posts,(entitledparents), so slicing the post into multiple frames to fit the text.
- Optional customizability options to change the font, backdrop, position of text on the screen

# Todo

- [x] Get comments based on the permalink
- [x] Generate mp3 and jpg of the post and its comments; concatenate both of them for a clip, them combine all the clip into one file
- [x] Migrate to praw
- [x] Ability to generate tts for post based subreddits (r/nosleep or r/relationships)
- Better post/comment formatting
  - [x] Nsfw filter
- Visual enhancements
  - [x] Slicing longer posts into to frames or jpg(s)
  - [ ] Adding the author, and upvotes
- Wrapping it all up into a nice ~~tkinter~~ pysimplegui window
    - [x] Ability to view posts and/or the comments of the id provided
    - [ ] Choosing arguments through a gui (dropdown, slider)
    - [ ] Clicking a button; showing what is going on behind the scenes to the user and creating the file wherever the program is located (for now)

# Usage

- Chug in your [app credentials](https://ssl.reddit.com/prefs/apps/) in `credentials.json`
- do `pip install -r requirements.txt` to install all the dependencies and then, run `main.py`

# Backburners

- Random timing issue with comments and their corresponding mp3(s)
- Converting links and emojis to plain text
