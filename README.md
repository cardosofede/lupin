# LupinAssistant

LupinAssistant is a sophisticated Telegram bot designed to streamline task and project management. Integrating practical functionalities with data-driven insights and leveraging Language Learning Models (LLMs), it serves as a versatile tool for enhancing personal and professional productivity.

## Key Features

### 1. **Plan**
   - **Create New Projects**: Initiate projects with titles, descriptions, and deadlines.
   - **Add New Tasks**: Detail tasks with scheduling capabilities.
   - **Brainstorm Ideas**: Facilitate effective idea generation for project development.

### 2. **Control**
   - **Project Analysis**: Gain insights with comprehensive project metrics.
   - **Summarize Work**: Utilize advanced LLMs for summarizing work progress.
   - **Edit/Remove Tasks**: Adapt tasks based on feedback and project evolution.

### 3. **Do**
   - **Task Execution Assistance**: Leverage LLM-based tools for task assistance.
   - **Task Status Management**: Efficiently manage and update task statuses.
   - **Pomodoro Timer**: Enhance time management with a built-in Pomodoro timer.
   - **Plan the Day**: Receive intelligent suggestions for daily task planning.

### 4. **Stats**
   - **Performance Overview**: View productivity metrics and performance overviews.
   - **Productivity Insights**: Analyze activity patterns for productivity enhancement.
   - **Project Progress Tracking**: Monitor project progression with detailed statistics.
   - **Task Completion Analysis**: Understand task completion trends for better planning.

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
