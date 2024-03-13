import './App.css';
import userProfilePicture from './assets/user-icon.png';
import gptImageLogo from './assets/chatgptLogo.svg'
import React, { useState, useEffect, useRef } from 'react';
import Video from './Video'; // Import MovieClip component
import quizScenario from './quiz_scenario_JSON.json'

import * as sdk from 'microsoft-cognitiveservices-speech-sdk';

const speechKey = process.env.REACT_APP_SPEECH_KEY;
const speechRegion = process.env.REACT_APP_SPEECH_REGION;

function App() {
    /// Query to GPT Model
    const [input, setinput] = useState("");
    const [query, setQuery] = useState("");

    const [messages, setMessages] = useState([
        {
            text: "Hello, how may I assist you today ",
            isBot: true
        }
    ]);
    const rendered = useRef(0);

    /// handle sending messages section
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [GPT_response, setGPT_response] = useState("")
    const [isInputDisabled, setIsInputDisabled] = useState(true)

    useEffect(() => {
        setIsInputDisabled(false);
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

    const queryResponse = async () => {
        setIsInputDisabled(true);

        var user_query = input;
        setQuery(user_query);
        setinput("");

        await fetch("http://127.0.0.1:8000/GetChatbotResponseAjax/?query=" + user_query)
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

    const HandleSend = async () => {

        if (input.trim().length !== 0) {
            console.log("input ", input)
            queryResponse();
        } else {
            console.log("Input field is empty")
        }
        // queryResponse();
    }

    const handleEnter = async (e) => {
        if (e.key === "Enter") await HandleSend();
    }

    /// scroll down button start 
    const chatContainerRef = useRef(null);
    const scrollToBottom = () => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        scrollToBottom();
    })

    /// Text to speech section
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


    /// Speech to Text Section
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
                stopListening();
                // HandleSend();

                const transcript = result.text;
                console.log('Transcript: -->', transcript);
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
        console.log(isListening)

        if (!isListening) {
            setIsListening(true);
            recognizer.current.startContinuousRecognitionAsync(() => {
                console.log('Resumed listening...');
            });
        }
    };


    const stopListening = () => {
        console.log(isListening)

        setIsListening(false);
        recognizer.current.stopContinuousRecognitionAsync(() => {
            console.log('Speech recognition stopped.');
        });
    };

    //Quiz scenario
    const handleQuizScenarioAnswers = (e) => {
        e.preventDefault(); // prevents page from refreshing on submit

        const quiz_scenario_data = new FormData(e.target);
        const quiz_scenario_OBJECT = Object.fromEntries(quiz_scenario_data.entries());
        const quiz_scenario_JSON = JSON.stringify(quiz_scenario_OBJECT);

        fetch("http://127.0.0.1:8000/GetQuizAnswers/?quiz_scenario_user_answers=" + quiz_scenario_JSON)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result.quiz_scenario_user_answers_response);

                    setMessages([
                        ...messages,
                        { text: result.quiz_scenario_user_answers_response, isBot: true },
                    ]);
                },
                (error) => {
                    console.log("error fel quiz yasta");
                }
            );
    };


    return (
        <div className="App">
            <div className='left-section'>
                <div className="left-section-top-part">
                    <img src={userProfilePicture} alt='user profile' className='user-profile-picture' />
                    <hr />
                </div>

                <div className="left-section-lower-part">
                    <hr />
                    <div className='left-section-icons'>
                        <span className='material-symbols-rounded left-section-icon-size' id="theme-btn"> upgrade </span> <span className='left-section-font'> Upgrade to Premium Plan </span>
                    </div>
                    <div className='left-section-icons'>
                        <span className='material-symbols-rounded left-section-icon-size'> Settings </span> Settings
                    </div>
                    <div className='left-section-icons'>
                        <span className='material-symbols-rounded left-section-icon-size'> Logout </span> Logout
                    </div>
                </div>
            </div>
            <div className="middle-section">
                <div className='center-video'>
                    <Video />
                </div>
                <div className="scenario-section">
                    <form onSubmit={handleQuizScenarioAnswers}>
                        {quizScenario.map(item => {
                            return (
                                <div className='quiz-scenraio-box'>
                                    <span><b> {item.question} </b></span>
                                    {item.options.map(option => {
                                        return (
                                            <div>
                                                {Object.keys(option).map(key => {
                                                    return (
                                                        <div>
                                                            <input
                                                                type="radio"
                                                                id={item.question + key}
                                                                name={item.question}
                                                                value={key}
                                                                required
                                                            />
                                                            <label for={item.question + key}> {option[key]} </label>
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        )
                                    })}
                                </div>
                            )
                        })}

                        <input type="submit" value="Get Results" />
                    </form>

                </div>
            </div>
            <div className="right-section">
                <div className='livechat-title'>
                    <h2> Live Chat </h2>
                    <hr />
                    <br />
                </div>
                <div className="chatbox" ref={chatContainerRef}>
                    {messages.map((message, i) => {
                        return <div key={i} className={message.isBot ? "chat bot" : "chat"}>
                            <img src={message.isBot ? gptImageLogo : userProfilePicture} alt="" className='chatImg' /> <p className="textOutput"> {message.text} </p>
                        </div>
                    })}
                </div>

                <div className='chatFooter center'>
                    <div className='inputText '>
                        <textarea type='text' disabled={isInputDisabled} name='' id='chat-input' placeholder='Send Message' value={input} onKeyDown={handleEnter} onChange={(e) => { setinput(e.target.value) }} />

                        {/* if mic is on, replace the turn mic on with turn mic off, and vice versa */}
                        {!isListening ? <button onClick={resumeListening} className='send material-symbols-rounded hover'> mic </button> : <button onClick={stopListening} className=' send material-symbols-rounded stop hover'> stop </button>}

                        <button className='send material-symbols-rounded hover' onClick={HandleSend}> send </button>

                        {/* if TTS is on, replace the TTS on with TTS off, and vice versa */}
                        {isTextToSpeeching ? <button onClick={stopTextToSpeech} className='send material-symbols-rounded hover '> text_to_speech </button> : <button onClick={resumeTextToSpeech} className=' send material-symbols-rounded hover '> volume_off </button>}

                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;