import './App.css';
import sendButton from './assets/send.svg';
import userProfilePicture from './assets/user-icon.png';
import gptImageLogo from './assets/chatgptLogo.svg'
import { sendMessageToOpenAI } from './openai';
import React, { useState, useEffect, useRef } from 'react';

import * as sdk from 'microsoft-cognitiveservices-speech-sdk';

const speechKey = process.env.REACT_APP_SPEECH_KEY;
const speechRegion = process.env.REACT_APP_SPEECH_REGION;

function App() {
  // Query to GPT Model
  const [input, setinput] = useState("");
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    {
      text: "Hello, how may I assist you today ",
      isBot: true
    }
  ]);
  const rendered = useRef(0);

  //Text to speech section
  const [isTextToSpeeching, setIsTextToSpeeching] = useState(false);
  const subscriptionKey = "b0f5184c6c2242f78356246fb06082f9";
  const serviceRegion = "eastus";
  const SpeechSDK = window.SpeechSDK;
  var synthesizer;

  var textToSpeechConfig = SpeechSDK.SpeechConfig.fromSubscription(subscriptionKey, serviceRegion);
  var player = new SpeechSDK.SpeakerAudioDestination();
  var audioConfigTextToSpeech = SpeechSDK.AudioConfig.fromSpeakerOutput(player);
  synthesizer = new SpeechSDK.SpeechSynthesizer(textToSpeechConfig, audioConfigTextToSpeech);

  const stopTextToSpeech = () => {
    //turn off speech to text
    setIsTextToSpeeching(false);
    console.log("Stop text to speech");
  }

  const resumeTextToSpeech = () => {
    //turn on speech to text
    setIsTextToSpeeching(true);
    console.log("resume text to speech");
  }

  const HandleTextToSpeech = (response) => {
    // Text to speech for GPT result of user query
    player.onAudioEnd = () => {
      console.log("Finished speaking");
    };

    // synthesizer = new SpeechSDK.SpeechSynthesizer(textToSpeechConfig, SpeechSDK.AudioConfig.fromDefaultSpeakerOutput());

    if (isTextToSpeeching) {
      synthesizer.speakTextAsync(
        response,
        function (result) {
          if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
            console.log("Done");
            // resultDiv.innerHTML += "synthesis finished for [" + response + "].\n";
            // console.log("synthesis finished for [" + response + "].\n");
          } else if (result.reason === SpeechSDK.ResultReason.Canceled) {
            console.log("cancelled");
            // resultDiv.innerHTML += "synthesis failed. Error detail: " + result.errorDetails + "\n";
            // console.log("synthesis failed. Error detail: " + result.errorDetails + "\n");

          }
          // window.console.log(result);
          synthesizer.close();
          synthesizer = undefined;
        },
        function (err) {
          window.console.log(err);
          synthesizer.close();
          synthesizer = undefined;
        }
      );
    }

  }

  //handle sending messages section
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [GPT_response, setGPT_response] = useState("")


  const queryResponse = async () => {
    // console.log("AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH", input)
    setQuery(input);
    setinput("");
    await fetch("http://127.0.0.1:8000/get_chatbot_response_ajax/?query=" + query)
      .then(res => res.json())
      .then(
        (result) => {
          setIsLoaded(true);
          setGPT_response(result.gpt_response)
          // console.log(result.gpt_response)
        },
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      )
  }

  useEffect(() => {
    if (rendered.current >= 2) {
      // console.log("rendered q", query);
      setMessages([
        ...messages,
        { text: query, isBot: false },
        { text: GPT_response, isBot: true }
      ]);
      // console.log("res", GPT_response)
      HandleTextToSpeech(GPT_response);
      return;
    }
    rendered.current++;
  }, [GPT_response])

  useEffect(() => {
    if (input !== "") { setQuery(input); }

  }, [input])

  const HandleSend = async () => {
    // after successfully inputting query(input) by user
    // send the query to openai.js to get result from GPT using sendMessageToOpenAI()
    // then play text to speech if button is enabled
    queryResponse();
  }

  const handleEnter = async (e) => {
    if (e.key === "Enter") await HandleSend();
  }


  // Speech to Text Section
  const [isListening, setIsListening] = useState(true);
  const speechToTextConfig = useRef(null);
  const audioConfigSpeechToText = useRef(null);
  const recognizer = useRef(null);

  const [myTranscript, setMyTranscript] = useState("");
  const [RecTranscript, setRecTranscript] = useState("");

  useEffect(() => {
    speechToTextConfig.current = sdk.SpeechConfig.fromSubscription(
      speechKey,
      speechRegion
    );
    speechToTextConfig.current.speechRecognitionLanguage = 'en-US';

    audioConfigSpeechToText.current = sdk.AudioConfig.fromDefaultMicrophoneInput();
    recognizer.current = new sdk.SpeechRecognizer(
      speechToTextConfig.current,
      audioConfigSpeechToText.current
    );

    const processRecognizedTranscript = (event) => {
      const result = event.result;

      if (result.reason === sdk.ResultReason.RecognizedSpeech) {
        const transcript = result.text;
        // console.log('Transcript: -->', transcript);
        var trimmed_transcript = transcript.toLowerCase();
        trimmed_transcript = trimmed_transcript.replace(",", " ")
        trimmed_transcript = trimmed_transcript.replace(".", " ")
        trimmed_transcript = trimmed_transcript.replace(/\s/g, "");
        trimmed_transcript = trimmed_transcript.trim();


        // console.log('Transcript: -->', trimmed_transcript);
        // Call a function to process the transcript as needed
        if (
          trimmed_transcript === "heygptube" || trimmed_transcript === "heygbtube" || trimmed_transcript === "stop"
          || trimmed_transcript === "stopvideo" || trimmed_transcript === "stopthevideo"
        ) {
          console.log("IS THIS WORKING");
          alert('Button clicked!')
        }
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
        // console.log('Resumed listening...');
      });
    }
  };

  const stopListening = () => {
    setIsListening(false);
    recognizer.current.stopContinuousRecognitionAsync(() => {
      // console.log('Speech recognition stopped.');
    });
  };

  return (
    <div className="App">
      <div className='sideBar'>
        <div className='upperSide'>
          <div className='upperSideTop'><span className='brand'>GPTube</span></div>
          <button className='midButton'> New Chat <span className="edit material-symbols-rounded">edit</span> </button>

        </div>
        {/* <div className='lowerSide'>
          <div className='listItems material-symbols-rounded'> light_mode </div>
          <div className='listItems material-symbols-rounded'> Delete </div>
        </div> */}
      </div>

      <div className='main'>
        <div className="video-div">{<iframe title='video-window' className="video-window" src="https://www.youtube.com/embed/wK0N1Bq3948?rel=0"></iframe>}</div>

        <div className='chats'>
          {messages.map((message, i) => {
            return <div key={i} className={message.isBot ? "chat bot" : "chat"}>
              <img src={message.isBot ? gptImageLogo : userProfilePicture} alt="" className='chatImg' /> <p className="textOutput"> {message.text} </p>
            </div>
          })}
        </div>

        <div className='chatFooter cente'>
          <div className='inputText '>
            <input type='text' name='' id='' placeholder='Send Message' value={input} onKeyDown={handleEnter} onChange={(e) => { setinput(e.target.value) }} />
            {/* if mic is on, replace the turn mic on with turn mic off, and vice versa */}
            {!isListening ? <button onClick={resumeListening} className='send material-symbols-rounded '> mic </button> : <button onClick={stopListening} className=' send material-symbols-rounded stop'> stop </button>}
            <button className='send' onClick={HandleSend}> <img src={sendButton} alt='Send Button' /> </button>

            {/* if TTS is on, replace the TTS on with TTS off, and vice versa */}
            {isTextToSpeeching ? <button onClick={stopTextToSpeech} className='send material-symbols-rounded '> text_to_speech </button> : <button onClick={resumeTextToSpeech} className=' send material-symbols-rounded'> volume_off </button>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
