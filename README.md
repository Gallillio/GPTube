# GPTube

GPTube is an interactive web application that allows users to engage with video content in a dynamic way. The application leverages AI to generate quizzes, create PowerPoint presentations, and answer questions based on the video being watched. Users can input their own YouTube videos and customize the content by providing a transcript.

![Main Example](Results%20Pictures/main.png)

## Features

- **Generate Quizzes**: Users can ask the application to create quizzes based on the content of the video. The quizzes are generated dynamically and can be tailored to the specific video being watched.

  ![Quiz Example](Results%20Pictures/quiz.png)

- **Create PowerPoint Presentations**: Users can request PowerPoint presentations that summarize the key points from the video. The application generates slides with titles, bullet points, and notes.

  ![PowerPoint Example](Results%20Pictures/powerpoint.png)

- **Interactive Q&A**: Users can ask questions about the video content, and the application will provide answers based on the transcript and context of the video.

  ![Question Example](Results%20Pictures/question.png)

- **Custom Video Input**: Users can input their own YouTube videos that are not included in the provided content list by adding the video transcript to the `reformatted_transcript.csv` file.

## Setup Instructions

### Prerequisites

- Node.js and npm installed on your machine.
- An OpenAI API key and endpoint for the application to function properly.
- An Azure endpoint for speech services.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Gallillio/GPTube.git
   cd GPTube
   ```

2. Install the dependencies:

   ```bash
   npm install
   ```

3. Create a `.env` file in the root directory and add your OpenAI API key and Azure endpoint:

   ```plaintext
   REACT_APP_SPEECH_KEY=your_azure_speech_key
   REACT_APP_SPEECH_REGION=your_azure_speech_region
   ```

   **Note**: The `.env` file is kept public on purpose for easier use, but all keys and endpoints have been deleted. If you try to use it without adding your own keys, it will not work.

4. For the **Master branch**, you will need to input your own OpenAI API key and Azure endpoint for the app to work.

5. Alternatively, you can switch to the **Use-Gemini** branch for free use by utilizing your own Gemini API. Gemini is free to use, but please note that this branch is more buggy as it was created on 22/3/2025 after the project was considered complete. I only did it for anyone who wants to try it for free and did not want to spend too much time on it. I will integrate it properly in the future if I have the time.

   ```bash
   git checkout Use-Gemini
   ```

6. Start the application:
   ```bash
   npm start
   ```

## Usage

- Open the application in your web browser.
- Select a video from the list or input your own YouTube video.
- Interact with the chatbot to generate quizzes, create PowerPoint presentations, or ask questions about the video content.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- To all the video's I've used to showcase this tool.
- Thanks to OpenAI for providing the API that powers the chatbot functionality.
- Thanks to Microsoft Azure for the speech services that enhance the user experience.

---
