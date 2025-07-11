Privacy Policy for FlexBot (Custom GPT)

Last updated: July 11, 2025

FlexBot is a custom GPT built to help you manage Todoist tasks using a self-hosted API. This assistant does not store or retain any personal data outside of the current chat session. Here’s how it handles your data:

1. Data Collected
FlexBot may send the following information to your external Todoist API:

Task titles, descriptions, priorities, due dates

Section names and identifiers

Completion and deletion commands

Project or section metadata when managing your task list

These requests are sent only when triggered by your direct input (e.g., "create a task called Review Notes").

2. Data Usage
The data is:

Used solely to perform requested actions on your behalf in Todoist

Not stored, logged, or processed outside the context of your current session

The backend API (hosted via Render) receives the request, passes it to the Todoist API, and returns the result.

3. Third-Party Services
This GPT connects to:

Your Render-hosted API (e.g., https://flexbot-api.onrender.com)

Todoist REST API (https://api.todoist.com/)

These services may be subject to their own privacy and data policies. You are responsible for reviewing Todoist’s Privacy Policy separately.

4. Data Retention
No data is stored by FlexBot or its backend. Chat history is retained per your OpenAI settings, but not by the API.

5. Security
FlexBot uses HTTPS for all external requests. Your Todoist API key is stored securely in your hosting environment (e.g., Render) and is not exposed to ChatGPT or OpenAI.

6. Contact
This assistant is maintained by the user Alex Buckle. For questions or issues related to privacy, please reach out via your Render or GitHub contact channels.
