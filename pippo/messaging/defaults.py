"""Pippo's built-in messages (used whenever the matching Settings box is empty)."""
from __future__ import annotations

# Replies Pippo can send when someone tags @Pippo outside a Good Morning (placeholders: {mentions} {user}).
DEFAULT_TAG_REPLIES = [
    "🐾 Psst {mentions}! <@{user}> just waved me over, so I paddled straight to you with the news. Over to you! 🐥",
    "👀 Ding ding! <@{user}> tagged me and I'm tapping {mentions} on the shoulder. This one's for you! 🌸",
    "🐥 Little Pippo delivery! <@{user}> sent me with a note, and {mentions}, you're the lucky recipients. Please sign here 📦✨",
    "🔔 Tiny alert from tiny Pippo! <@{user}> called for me, so I'm hopping over to wake up {mentions}. Rise and shine! ☀️🐾",
    "🌸 Hello hello {mentions}! <@{user}> mentioned me and I thought you should know. Flap flap, message delivered! 🐥",
    "📣 Pippo reporting in! <@{user}> tagged me, so I'm doing my duck duty and looping in {mentions}. Quack on! 🦆",
    "🐾 Pawsibly important! <@{user}> tagged me, so {mentions}, consider this your cue to take a peek! ✨",
    "💌 Special delivery for {mentions}! <@{user}> tagged me and I couldn't wait to pass it along. Handled with fluffy care! 🐥",
    "🫧 Bloop! <@{user}> popped me into the conversation, so I'm bubbling over to {mentions}. Take a look when you can! 🐾",
    "🌟 Pippo to the rescue! <@{user}> called my name, and now I'm calling yours, {mentions}. Teamwork makes the dream work! 🐥💛",
    "🍵 Gentle nudge, {mentions}! <@{user}> tagged me, so I waddled over for a friendly tap on the shoulder. No rush, just wanted you to know! 🐾",
    "🎈 Surprise {mentions}! <@{user}> tagged me, which means something's up and you're invited to take a look. Quack-tastic! 🐥✨",
]

# First line of the Good Morning post Pippo makes in the target channel (placeholder: {user}).
DEFAULT_GREETINGS = [
    "☀️ Good Morning <@{user}>! 🐾",
    "🐥 Rise and shine, <@{user}>! Good Morning from your favourite duckling! ☀️",
    "🌸 Good Morning <@{user}>! Pippo's up, fluffed up and ready to go! 🐾",
    "☕ Good Morning <@{user}>! Fresh list, fresh day, and a very happy Pippo! 🐥",
    "🌈 Well hello, <@{user}>! Good Morning, and welcome to a brand new day of projects! 🐾",
    "🐾 Pitter-patter, pitter-patter... Good Morning <@{user}>! Pippo is here with today's status! 🐥",
    "🌞 Good Morning <@{user}>! The sun is up and so are the paws! Let's make today a good one! 🐥",
    "🦆 Quack quack, Good Morning <@{user}>! Pippo has your project status all ready! ✨",
    "✨ Good Morning, sunshine <@{user}>! Pippo waddled in early with the freshest update! 🐾",
    "🥐 Good Morning <@{user}>! Pippo brought the status, you bring the smiles! 🐥",
    "🌼 Hello hello <@{user}>, Good Morning! Pippo has tidied up the list just for you! 🐾",
    "🎀 Good Morning <@{user}>! Fluffy feathers, happy hearts, and a fresh status from Pippo! 🐥",
]

# Reply to a Good Morning on a non-working day (placeholders: {user} {date} {reason}).
DEFAULT_NON_WORKING = [
    "😴💤 Good Morning <@{user}>! Today ({date}) is a non-working day ({reason}), so Pippo is curled up for a little nap. No lists today — see you on the next working day! 🌸🐾",
    "🛌 Shhh <@{user}>, Good Morning! Today ({date}) is a non-working day ({reason}), so Pippo is tucked in under a fluffy blanket. No lists today, see you on the next working day! 🐥💤",
    "🌙 Good Morning <@{user}>! It's {date} ({reason}), which means no work and lots of rest. Pippo is snoozing, see you on the next working day! 🐾",
    "🧸 Aww, Good Morning <@{user}>! {date} is a non-working day ({reason}), so Pippo is cuddling a teddy and skipping lists today. Back soon! 🌸",
    "🍵 Good Morning <@{user}>! Today ({date}) is a day off ({reason}), so Pippo is sipping warm tea and not making any lists. Enjoy the break! 🐥",
    "😴 Yawwwn... Good Morning <@{user}>! {date} is a non-working day ({reason}), so Pippo is going back to sleep. No lists today, see you on the next working day! 🐾",
    "🌴 Good Morning <@{user}>! Pippo is on a tiny holiday today, {date} ({reason}). No lists for now, catch you on the next working day! 🐥☀️",
    "🐾 Good Morning <@{user}>! Pippo checked the calendar and {date} is a non-working day ({reason}). Paws up, lists down, see you soon! 💤",
    "🎈 Good Morning <@{user}>! Today ({date}) is a non-working day ({reason}), so Pippo is floating around happily instead of making lists. See you on the next working day! 🌸",
    "🛋️ Good Morning <@{user}>! {date} ({reason}) is a day to relax, so Pippo is lounging on the sofa. No lists today, enjoy your rest! 🐥💛",
    "🌼 Good Morning <@{user}>! Pippo knows today ({date}) is a non-working day ({reason}), so it's a nap-and-snack kind of day. Lists are back on the next working day! 🐾",
    "🌟 Good Morning <@{user}>! Even Pippo needs a break, and {date} ({reason}) is the perfect day for it. No lists today, see you on the next working day! 🐥💤",
]
