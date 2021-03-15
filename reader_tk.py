#!/usr/bin/python
# -*- coding: utf-8 -*-
import feedparser
import os
import sys
import webbrowser
import errno

try:
    from Tkinter import *   # python2
except:
    from tkinter import *   # python3

import appdirs

appname = "PyRSS"
appauthor = "Adventurous"

# If the data directory doesn't exist, create it
datadir = appdirs.user_data_dir(appname, appauthor)
if (not os.path.isdir(datadir)):
    os.makedirs(datadir)
# Path for saved RSS site feeds
path = os.path.join(datadir, "sites.txt")

urls = []
buttons = []
text = []

root = Tk()
root.wm_title("PyRSS")
addRSSButton = None
refreshRSSButton = None
noMoreEntries = []
websites = []
websiteButtons = []


def mainGUI(text):
    global addRSSButton, refreshRSSButton, noMoreEntries
    global websites, buttons, urls
    # Go through each line in sites.txt
    for line in text:
        line = line.strip()
        # we don't want to process the same URL more than once
        if line in urls:
            continue

        urls.append(line)
        # Feed line found in file to feedparser
        site = feedparser.parse(line)
        # Create labels for each site gotten out of the file
        websites.append(Label(root, text=line))
        websites[-1].pack()

        num = min(3, len(site['entries']))
        # Top three entries from the RSS feed
        for entry in site['entries'][:num]:
            title = entry['title']
            callback = lambda link=entry['link']: openSite(link)
            buttons.append(Button(root, text=title, command=callback))
            buttons[-1].pack(padx=30, pady=15)
        noMoreEntries.append(Label(root, text="No more entries!"))
        noMoreEntries[-1].pack(padx=5, pady=5)

    # Make button for adding RSS feeds to the file
    addRSSButton = Button(root, text="+", command=lambda: addFeedWindow())
    addRSSButton.pack(side="right")
    # Make button for removing RSS feeds from the list
    global removeRSSButton
    removeRSSButton = Button(root, text="-", command=lambda: removeFeedWindow())
    removeRSSButton.pack(side="right")
    refreshRSSButton = Button(root, text="↻", command=lambda: refreshRSS())
    refreshRSSButton.pack(side="right")


def openSite(text):
    webbrowser.get().open(text)


# Create new window for adding new RSS feed to file.
def addFeedWindow():
    global feed
    feed = Toplevel()
    feed.wm_title("Add new RSS feed")

    newFeedButton = Button(feed, text="Add New Feed",
                           command=lambda: addFeed())
    newFeedButton.pack(side="right")

    global newFeedGet
    newFeedGet = Entry(feed, width=50)
    newFeedGet.pack(side="left")

def removeFeed(site):
    for i in range(0, len(urls)):
        if site == urls[i]:
            del urls[i]
        else:
            continue
        with open(path, 'w') as f:
            for i in range(0, len(urls)):
                f.write(urls[i]+"\n")
    remove.destroy()
    refreshRSS()
def removeFeedWindow():
    global remove
    remove = Toplevel()
    remove.wm_title("Remove RSS feed from File")
    for i in range(0, len(urls)):
        website = urls[i]
        # Create a var to hold TK command in, helps with callback looping problem (See button creation)
        removeCommand = lambda websiteURL=website: removeFeed(websiteURL)
        websiteButtons.append(Button(remove, text=website, command=removeCommand))
        websiteButtons[-1].pack(padx=30, pady=15)


def addFeed():
    global text
    # Open the file for appending and just write the new line to it
    new = newFeedGet.get()
    # If you're not subscribed already, subscribe!
    if new.strip() != "":
        if (new not in text):
            text.append(new)
            with open(path, 'a') as f:
                f.write(new + "\n")
            feed.destroy()
            refreshRSS()
    # Do this in two seperate places so that it can be executed before
    # refreshRSS() which is slow and makes it feel less responsive
    else:
        feed.destroy()


def refreshRSS():
    global websites, buttons, urls, text
    global addRSSButton, refreshRSSButton, noMoreEntries
    with open(path, 'r') as f:
        # Get rid of all the newlines while you're reading it in
        text = [x.strip() for x in f.readlines()]
    # Remove button needs to be added, tried to add it but was getting global errors. Will come back to it later.
    addRSSButton.pack_forget()
    refreshRSSButton.pack_forget()
    removeRSSButton.pack_forget()
    for site in websites:
        site.pack_forget()
    for button in buttons:
        button.pack_forget()
    for noMoreLabel in noMoreEntries:
        noMoreLabel.pack_forget()
    noMoreEntries = []
    websites = []
    buttons = []
    urls = []
    mainGUI(text)


# Functions to handle the hotkeys, need to pass "self" to these functions
# kind of a kludge, will request code review later.
# Just wanted to get it up and running
def refreshRSSBind(self):
    refreshRSS()

def addFeedBind(self):
    addFeedWindow()

def removeFeedBind(self):
    removeFeedWindow()

# Open sites.txt
try:
    with open(path, 'r') as f:
        # Get rid of all the newlines while you're reading it in
        text = [x.strip() for x in f.readlines()]
except:
    pass

mainGUI(text)
root.bind("-", removeFeedBind)
root.bind("+", addFeedBind)
root.bind('<F5>', refreshRSSBind)
root.mainloop()
