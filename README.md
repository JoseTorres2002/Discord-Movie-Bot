# MovieKnight 
A discord bot that helps users find movies/shows to watch. It can be added to any discord server and works through commands. The bot retrieves data from TMDB databse using its api.

## Installation

### Getting Your Tokens

Before running the bot, you will need to create two tokens:  
- A **Discord Bot Token** (to connect to Discord)  
- A **TMDB API Key** (to fetch movie and show data)

---

#### 1. Create a Discord Bot Token
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **"New Application"** and give it a name (e.g., `MovieKnight`).
3. Go to the **"Bot"** tab on the left.
4. Click **"Add Bot"** and confirm.
5. Under **"TOKEN"**, click **"Reset Token"** and copy it.  
   ⚠️ **Do not share this token** — anyone with it can control your bot.

---

#### 2. Get a TMDB API Key
1. Go to the [TMDB Developer API page](https://www.themoviedb.org/documentation/api).
2. Sign up for a free account (if you don’t have one already).
3. Navigate to your **account settings** → **API** → **Create**.
4. Copy your **API Key (v3 auth)**.

---

##### 4. Run the Bot
1. **Download and unzip the project folder**  
   If you downloaded the project as a ZIP from GitHub, unzip it to a folder on your computer, for example, `MovieBot`.

2. **In the project folder, create a file named `.env` and add  the following text replacing the placeholders with your actual tokens:**
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   TMDB_API_KEY=your_tmdb_api_key_here
   
3. **Open Command Prompt (Windows) or Terminal (Mac/Linux) and Navigate to the project folder**  
   Use the `cd` (change directory) command to go to the folder where your project files are.


4. **Install dependencies**  
   Run this command to install all necessary Python packages:

   ```bash
   pip install -r requirements.txt
5. **Install dependencies**  
   Start the bot by running:
   ```bash
   python main.py


