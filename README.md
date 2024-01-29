# hebrew-bot
## Overview
[Hebrew Bot](https://t.me/HebrewTestBot) is a free-to-use Telegram bot, which is designed to help people learn Hebrew words by testing them within a Telegram chat. 
It features a  dictionary with nouns, verbs and adjectives split up by two difficulty levels. The bot support two user languages - English and Russian. 

## Usage ✨
To start using the bot, go through the following link: [Hebrew Bot](https://t.me/HebrewTestBot) and press "Start". 
Then start testing using one of the following commands from the menu:

- "/test_shuffle" - starts testing shuffling over nouns, verbs and adjectives
- "/test_nouns" - starts testing nouns only
- "/test_verbs" - starts testing verbs only
- "/test_adjectives" - starts testing adjectives only

Other commands:

- "/set_language" - allows to choose the user language. Currently English and Russian languages are supported
- "/set_difficulty_level" - allows to choose the difficulty level by typing command. Currently there are two levels to choose from - alef and alef plus
- "/stop" - stops testing and cheers the user for the work done

## Data 🗂
The bot saves the following data about a user:
1. Telegram account user_id
2. First and last name as specified in Telegram
3. System language
4. Answers to the test questions

All user data is stored in a database with restricted access and will not be shared with third parties.

## Algorithms 🎱
The bot has a limited set of words for each level of difficuly, and features a tuned algorithm to provide more relevant words for testing. Words with recent wrong answers will be asked more, and words with right answers will be asked less. The relevance score of the words in the dictionary is being updated daily, and has a retention period of 30 days, with a linear decline of the score towards the end of the retention period.

## Technology stack 🛠
- Telegram API with webhooks
- PostgreSQL Managed Service in Google Cloud
- Python backend on Google Cloud Functions (stateless, serverless)
- SQLAlchemy as a database connector
- Pandas used in the relevance calculation algorithm (weights function)
- Google PubSub event streaming to Google Object Storage (raw API requests, messages)
