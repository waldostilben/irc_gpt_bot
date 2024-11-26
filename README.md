# IRC Bot with ChatGPT

This Python script is an IRC bot that answers questions in monitored channels and private messages using ChatGPT. The bot connects to an IRC server, authenticates with NickServ, and interacts with users.

---

## Features

- Responds to `.gpt [question]` commands in monitored channels.
- Adds new channels to the monitored list via `.join [channels]` private commands.
- Automatically detects channels it is added to by the server.

---

## Requirements

- Python 3.10 or higher
- OpenAI library (`pip install openai`)

---

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/waldostilben/irc_gpt_bot
   cd irc_gpt_bot
   ```

2. Install dependencies:

   ```bash
   pip install openai
   ```

3. Update the script with your OpenAI API key in the `api_key` variable:

   ```python
   api_key = "sk-proj-[YOUR-KEY]"
   ```

4. Ensure Python is configured on your system and available in the PATH.

---

## Usage in mIRC

### Step 1: mIRC Setup

1. Use the `/run` command in mIRC to execute the script:

   ```mirc
   /run python "C:\path\to\script.py" irc.your-server.org
   ```

2. Replace `irc.your-server.org` with the desired IRC server address.

---

### Step 2: Available Commands

#### `.gpt` Command

- **Format**: `.gpt [question]`
- **Description**: Send this command in a monitored channel to receive a response from ChatGPT.
- **Example**:
  ```
  .gpt What is the capital of France?
  ```

#### `.join` Command

- **Format**: `.join [channels]`
- **Description**: Send this command in a private message to the bot to add new channels to the monitored list.
- **Example**:
  ```
  /msg YourBotNickName .join #channel1 #channel2
  ```

#### Automatic Channel Detection

- After authentication, the bot will automatically detect channels it has been added to.

---

## Logs

- The bot provides detailed logs of its actions in the terminal, including:
  - Data received from the server.
  - Questions and responses from ChatGPT.
  - Channel join and leave events.

---

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).
