import './App.css';
import gptLogo from './assets/chatgpt.svg';
import addButton from './assets/add-30.png';
import sendButton from './assets/send.svg';
import userProfilePicture from './assets/user-icon.png';
import gptImageLogo from './assets/chatgptLogo.svg'
import { sendMessageToOpenAI } from './openai';
import React, { useState, useEffect, useRef } from 'react';

import * as sdk from 'microsoft-cognitiveservices-speech-sdk';

const SPEECH_KEY = 'b0f5184c6c2242f78356246fb06082f9';
const SPEECH_REGION = 'eastus';

function App() {
  // Query to GPT Model
  const [input, setinput] = useState("");
  const [messages, setMessages] = useState([
    {
      text: "Hello, how may I assist you today ",
      isBot: true
    }
  ]);

  const handleSend = async () => {
    const text = input;
    setinput("")
    const response = await sendMessageToOpenAI(text);
    setMessages([
      ...messages,
      { text: input, isBot: false },
      { text: response, isBot: true }
    ]);
  }

  const handleEnter = async (e) => {
    if (e.key === "Enter") await handleSend();
  }


  // Speech to Text Section
  const [isListening, setIsListening] = useState(false);
  const speechConfig = useRef(null);
  const audioConfig = useRef(null);
  const recognizer = useRef(null);

  const [myTranscript, setMyTranscript] = useState("");
  const [RecTranscript, setRecTranscript] = useState("");

  const buttonRef = useRef(null);
  const handleClick = (x, y) => {
    const rect = buttonRef.current.getBoundingClientRect();
    const clickEvent = new MouseEvent('click', {
      bubbles: true,
      clientX: rect.left + x,
      clientY: rect.top + y,
    });
    buttonRef.current.dispatchEvent(clickEvent);
  };

  useEffect(() => {
    speechConfig.current = sdk.SpeechConfig.fromSubscription(
      SPEECH_KEY,
      SPEECH_REGION
    );
    speechConfig.current.speechRecognitionLanguage = 'en-US';

    audioConfig.current = sdk.AudioConfig.fromDefaultMicrophoneInput();
    recognizer.current = new sdk.SpeechRecognizer(
      speechConfig.current,
      audioConfig.current
    );

    const processRecognizedTranscript = (event) => {
      const result = event.result;
      // console.log('Recognition result:', result);

      if (result.reason === sdk.ResultReason.RecognizedSpeech) {
        const transcript = result.text;
        // console.log('Transcript: -->', transcript);
        var trimmed_transcript = transcript.toLowerCase();
        trimmed_transcript = trimmed_transcript.replace(",", " ")
        trimmed_transcript = trimmed_transcript.replace(".", " ")
        trimmed_transcript = trimmed_transcript.replace(/\s/g, "");
        trimmed_transcript = trimmed_transcript.trim();


        console.log('Transcript: -->', trimmed_transcript);
        // Call a function to process the transcript as needed
        if (
          trimmed_transcript === "heygptube" || trimmed_transcript === "heygbtube" || trimmed_transcript === "stop"
          || trimmed_transcript === "stopvideo" || trimmed_transcript === "stopthevideo"
        ) {
          console.log("IS THIS WORKING");
          handleClick(50, 50);
          alert('Button clicked!')
        }

        // setinput(transcript)
        // setMyTranscript(transcript);
      }
    };

    const processRecognizingTranscript = (event) => {
      const result = event.result;
      // console.log('Recognition result:', result);
      if (result.reason === sdk.ResultReason.RecognizingSpeech) {
        const transcript = result.text;
        // console.log('Transcript: -->', transcript);
        // Call a function to process the transcript as needed
        setinput(transcript)

        setRecTranscript(transcript);
      }
    }

    recognizer.current.recognized = (s, e) => processRecognizedTranscript(e);
    recognizer.current.recognizing = (s, e) => processRecognizingTranscript(e);


    recognizer.current.startContinuousRecognitionAsync(() => {
      console.log('Speech recognition started.');
      setIsListening(true);
    });

    return () => {
      recognizer.current.stopContinuousRecognitionAsync(() => {
        setIsListening(false);
      });
    };
  }, []);

  const resumeListening = () => {
    if (!isListening) {
      setIsListening(true);
      recognizer.current.startContinuousRecognitionAsync(() => {
        console.log('Resumed listening...');
      });
    }
  };

  const stopListening = () => {
    setIsListening(false);
    recognizer.current.stopContinuousRecognitionAsync(() => {
      console.log('Speech recognition stopped.');
    });
  };

  return (
    <div className="App">
      <div className='sideBar'>
        <div className='upperSide'>
          <div className='upperSideTop'><img src={gptLogo} alt="logo" className='logo' /><span className='brand'>GPTube</span></div>
          <button className='midButton'><img src={addButton} alt='new chat' className='addButton' /> New Chat </button>

        </div>
        <div className='lowerSide'>
          <div className='listItems material-symbols-rounded'> light_mode </div>
          <div className='listItems material-symbols-rounded'> Delete </div>
        </div>
      </div>
      <div className='main'>
        <div className='chats'>
          {messages.map((message, i) => {
            return <div key={i} className={message.isBot ? "chat bot" : "chat"}>
              <img src={message.isBot ? gptImageLogo : userProfilePicture} alt="" className='chatImg' /> <p className="textOutput"> {message.text} </p>
            </div>
          })}
        </div>

        <div className='chatFooter'>
          <div className='inputText'>
            <input type='text' name='' id='' placeholder='Send Message' value={input} onKeyDown={handleEnter} onChange={(e) => { setinput(e.target.value) }} />
            {/* if mic is on, replace the turn mic on with turn mic off, and vice versa */}
            {!isListening ? <button onClick={resumeListening} className='send material-symbols-rounded'> mic </button> : <button onClick={stopListening} className='send material-symbols-rounded stop'> stop </button>}
            <button className='send' onClick={handleSend}> <img src={sendButton} alt='Send Button' /> </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
