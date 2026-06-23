# **AskMeAnonBot \- Anonymous Confession & Q\&A Telegram Bot**

Welcome to **AskMeAnonBot**\! This is an advanced, multi-language Telegram bot designed to let users create anonymous confession or Q\&A links to share on platforms like Instagram, WhatsApp, and TikTok. Users can receive anonymous text, photos, voice notes, and videos, and even reply directly to the sender while keeping both identities completely hidden.

## **🌟 Key Features**

* **Multi-Language Support:** Fully supports English, Turkish, and Russian. The bot adapts to the user's language automatically.  
* **Platform-Specific Links:** Generate clean, categorized links for different platforms (e.g., Instagram \- MyOutfit, TikTok \- AskMeAnything).  
* **Rich Media Support:** Unlike basic bots, this bot supports text, photos, videos, voice notes, and video notes.  
* **Two-Way Anonymous Chat:** Users can reply to the anonymous messages they receive. The sender gets the reply securely, without revealing anyone's identity. (Uses a smart, one-time-use reply token system).  
* **Anti-Spam & Limits:** A user can only send *one* message to a specific link to prevent spamming. (They can send more if the receiver creates a new link).  
* **Built-in SQLite Database:** No external database servers needed. It uses a local SQLite file (bot.db) that creates itself automatically.  
* **Advanced Admin Panel:** A dedicated menu for the admin to view stats, ban/unban users, broadcast messages to all users, download database backups, and activate Maintenance Mode.

## **🛠️ Prerequisites**

* Python 3.8 or higher  
* A Telegram Bot Token (Get one from [@BotFather](https://t.me/BotFather))

## **🚀 Installation & Setup**

### **Step 1: Clone or Download the Repository**

Download these files to your local machine or server.

### **Step 2: Install Required Libraries**

Open your terminal or command prompt in the bot's folder and run the following command to install the required Telegram library:  
`pip install pyTelegramBotAPI`

### **Step 3: Configure the Bot**

Open the telegrambot.py file in a text editor. Look for the **\# \--- SETTINGS \---** section near the top and update the following variables:  
`TOKEN = "YOUR_BOT_TOKEN"          # Replace with the token from BotFather`  
`BOT_USERNAME = "YOUR_BOT_USERNAME"  # E.g., "AskMeAnonBot" (without the @)`  
`ADMIN_ID = 123456789              # Replace with your personal Telegram User ID`  
`ADMIN_USERNAME = "YOUR_ADMIN_USERNAME" # E.g., "MerdanAdmin" (without the @)`

*Tip: You can find your Telegram User ID by messaging [@userinfobot](https://t.me/userinfobot).*

### **Step 4: Run the Bot**

Execute the Python script to start your bot:  
`python telegrambot.py`  
The bot will automatically create the bot.db file and start polling for messages. You will see "Bot is starting..." in your console.

## **👑 How to Use the Admin Panel**

As the defined ADMIN\_ID, when you send the /admin command to the bot, you will access a special dashboard. From here, you can:

* **Statistics:** See total users, total messages sent, and language distribution.  
* **Broadcast:** Send a mass message to every user currently registered in the database.  
* **Maintenance Mode:** Pause the bot for updates. Normal users will be added to a waiting list and notified once maintenance is over.  
* **Backup:** Download the current bot.db SQLite file directly via Telegram.  
* **User List & Ban/Unban:** View recent users, see banned users, and manage access. (You can also ban users globally by typing /ban USER\_ID).

## **⚙️ System Architecture Details**

| File | Description |
| :---- | :---- |
| telegrambot.py | The main logic file containing all UI, handlers, language dictionaries, and callback queries. |
| database.py | Handles all SQLite operations, table creations, user tracking, and stats counting. Includes automated 7-day token cleanup threading. |

## **🤝 Contributing**

Feel free to fork this project, submit pull requests, or open issues to suggest new features or report bugs. This project is open-source and meant to help developers learn and build upon it.