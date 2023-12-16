# LupinAssistant

LupinAssistant is a sophisticated Telegram bot designed to streamline task and project management. Integrating practical functionalities with data-driven insights and leveraging Language Learning Models (LLMs), it serves as a versatile tool for enhancing personal and professional productivity.

## Key Features

### 1. **Plan**
   - **Add New Tasks**: Quickly add tasks by just entering the task name.
   - **Schedule Tasks**: Plan tasks with an interactive approach.
   - **List Tasks**: View tasks with a comprehensive overview.
   - **Brainstorm Ideas**: Facilitate effective idea generation for project development.

### 2. **Control**
   - **Task Status Management**: Efficiently manage and update task statuses.
   - **Project Analysis**: Gain insights with comprehensive project metrics.
   - **Summarize Work**: Utilize advanced LLMs for summarizing work progress.

### 3. **Do**
   - **AI-Assisted Task Execution**: Work on tasks with an AI Assistant, getting help to find information and solve tasks until paused or completed.
   - **Pomodoro Timer**: Use a built-in Pomodoro timer for enhanced time management, with suggestions for meditation, stretching, or leisure activities during breaks..
   - **Plan the Day**: Receive smart suggestions for daily task planning based on your schedule and recurring commitments..

### Additional Features
   - **Customizable Interface**: Personalize the user experience.
   - **External Tool Integration**: Extend functionality with third-party tools.
   - **Data Security and Privacy**: Prioritize the protection of user data.
   - **User-Centric Design**: Focus on intuitive and user-friendly interaction.

LupinAssistant is more than just an organizational tool; it's a partner in your journey towards achieving efficiency and effectiveness in your daily tasks and long-term projects.

## Installation

### Prerequisites

- Docker
- Telegram Bot API Token

### Setup Instructions

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/cardosofede/lupin.git
   cd lupin-assistant
   ```

2. **Environment Configuration:**
   - Create a `.env` file in the root directory.
   - Add your Telegram Bot API Token:
     ```
     TELEGRAM_TOKEN=your_telegram_bot_token_here
     ```
   - You can also add the telegram bot in the docker-compose.yml

3. **Docker Build:**
   - Build the Docker image for LupinAssistant:
     ```sh
     docker-compose build
     ```

4. **Run LupinAssistant:**
   - Start the bot using Docker:
     ```sh
     docker-compose up
     ```

Now, LupinAssistant should be up and running! You can interact with it via the Telegram interface.
