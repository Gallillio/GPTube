import './App.css';
import userProfilePicture from './assets/elpopicon.jpg';
import gptImageLogo from './assets/chatgptLogo.svg'
import gptTubeLogo from './assets/GPTUBE_Logo_Black-removebg-preview.png'
import React, { useState, useEffect, useRef } from 'react';
import Video from './Video'; // Import MovieClip component
import * as sdk from 'microsoft-cognitiveservices-speech-sdk';

// Import PowerPoint slides if available, otherwise use empty array
let powerPointSlides = [];
try {
    powerPointSlides = require('./powerpoint_scenario_JSON.json');
} catch (e) {
    console.log("PowerPoint slides not yet generated");
}

// Function to reset scenarios
const resetScenarios = () => {
    // Reset PowerPoint slides to empty array
    powerPointSlides = [];

    // Create empty quiz scenario file
    const emptyQuiz = [];
    localStorage.setItem('quizScenario', JSON.stringify(emptyQuiz));
};

const speechKey = process.env.REACT_APP_SPEECH_KEY;
const speechRegion = process.env.REACT_APP_SPEECH_REGION;

// Left section component
var video_list_string = "{}"

const LeftSection = ({ isOpen, isLeftOpen, ChangeVideoEvent, RefreshVideoSelection }) => {
    const [videoList, setVideoList] = useState({});

    // Automatically load video list when LeftSection is opened
    useEffect(() => {
        if (isOpen) {
            const loadVideoList = async () => {
                try {
                    const response = await fetch(`http://127.0.0.1:8000/RefreshVideoSelection/`);
                    const result = await response.json();
                    video_list_string = result.data;
                    setVideoList(JSON.parse(result.data));
                } catch (error) {
                    console.error("Error loading video list:", error);
                }
            };

            loadVideoList();
        }
    }, [isOpen]);

    return (
        <div className={`left-section ${isOpen ? 'open' : ''}`}>
            {!isLeftOpen ?
                <button className='send material-symbols-rounded hover burger-menu'>menu</button> :
                <button className='send material-symbols-rounded burger-menu-opened'>menu_open</button>
            }

            {isOpen && ( // Conditionally render content only when isOpen is true
                <div className='left-section select-video-section'>
                    {/* <div className="left-section-top-part">
                        <img src={userProfilePicture} alt='user profile' className='user-profile-picture' />
                    </div>
                    El King <br /> */}
                    <hr /><br />
                    <b>Select your video</b>
                    <br /><br />
                    <hr /><br />
                    <b> Or </b>
                    <br /><br />
                    <button onClick={RefreshVideoSelection} className='video_button'>Refresh Video List</button>
                    <br /><br />
                    <hr /><br />

                    <div>
                        {Object.entries(videoList).length > 0 ? (
                            Object.entries(videoList).map(([videoId, videoTitle]) => (
                                <button className='video_button'
                                    key={videoId}
                                    value={videoId}
                                    onClick={(e) => ChangeVideoEvent(e.target.value)}
                                >
                                    {videoTitle}
                                </button>
                            ))
                        ) : (
                            <p>Loading videos...</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

function App() {
    /// Query to GPT Model
    const [input, setinput] = useState("");
    const [query, setQuery] = useState("");

    // Use state for quiz scenario instead of static import
    const [quizScenario, setQuizScenario] = useState([]);

    // Add state for PowerPoint slides
    const [slides, setSlides] = useState([]);

    // Add state for video list
    const [videoList, setVideoList] = useState({});

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
    const [quiz, setQuiz] = useState("")
    const [isInputDisabled, setIsInputDisabled] = useState(false) // Changed to false for better UX
    const [welcomePageDisplayed, setIsWelcompageDisplayed] = useState(false);

    // Add state variables to track if quiz or PowerPoint is available
    const [hasQuiz, setHasQuiz] = useState(false);
    const [hasPowerPoint, setHasPowerPoint] = useState(false);

    // Load video list when component mounts
    useEffect(() => {
        const loadVideoList = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/RefreshVideoSelection/`);
                const result = await response.json();
                video_list_string = result.data;
                setVideoList(JSON.parse(result.data));
                console.log("Video list loaded successfully");
            } catch (error) {
                console.error("Error loading video list:", error);
                // Set an empty object as fallback
                setVideoList({});
            }
        };

        loadVideoList();
    }, []);

    // Add useEffect to reset scenarios on page load
    useEffect(() => {
        // Load quiz scenario on component mount
        try {
            const loadedQuiz = require('./quiz_scenario_JSON.json');
            setQuizScenario(loadedQuiz);
        } catch (e) {
            console.log("Quiz scenario not yet generated");
            setQuizScenario([]);
        }

        // Load PowerPoint slides on component mount
        try {
            const loadedSlides = require('./powerpoint_scenario_JSON.json');
            setSlides(loadedSlides);
            powerPointSlides = loadedSlides; // Update global variable too
        } catch (e) {
            console.log("PowerPoint slides not yet generated");
            setSlides([]);
        }

        // Reset scenarios when component mounts (page refresh)
        resetScenarios();

        // Add event listener for page reload/refresh
        window.addEventListener('beforeunload', resetScenarios);

        return () => {
            // Clean up event listener
            window.removeEventListener('beforeunload', resetScenarios);
        };
    }, []);

    useEffect(() => {
        setIsInputDisabled(false);
        if (rendered.current >= 2) {
            // Only add messages to chat if they're not about scenario generation
            // or if they're already being handled elsewhere
            const isScenarioMessage =
                GPT_response.includes("Presentation has been generated") ||
                GPT_response.includes("Quiz has been generated");

            if (!isScenarioMessage) {
                // Use functional update to avoid dependency on messages
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: query, isBot: false },
                    { text: GPT_response, isBot: true }
                ]);
                HandleTextToSpeech(GPT_response);
            } else {
                // For scenario generation, only add the user query to chat
                setMessages(prevMessages => [
                    ...prevMessages,
                    { text: query, isBot: false }
                ]);
            }
            return;
        }
        rendered.current++;
    }, [GPT_response]) // Remove messages from dependency array

    const [useScenario, setUseScenario] = useState(false) //this is set with every message sent from user, checks if message sent is scenario or just text for chatbox
    const [displayScenarioBox, setDisplayScenario] = useState(false) //this will display the scenario box when useScenario is true once. We do this incase the box is displayed once but we want to keep the box open even if another message is sent 
    const [scenarioType, setScenarioType] = useState("quiz"); // "quiz" or "powerpoint"

    useEffect(() => {
        if (useScenario == true) {
            setDisplayScenario(true)
        }
    }, [useScenario])

    // Function to find the most appropriate video based on user query
    const findMatchingVideo = (query, videoList) => {
        query = query.toLowerCase();
        let bestMatch = null;
        let bestScore = 0;

        // Check if videoList is empty or invalid
        if (!videoList || Object.keys(videoList).length === 0) {
            console.log("Video list is empty, cannot find matching video");
            return null;
        }

        console.log("Available videos for matching:", videoList);

        // Go through each video title and check for keyword matches
        Object.entries(videoList).forEach(([videoId, title]) => {
            const titleLower = title.toLowerCase();
            // Split the query into words
            const queryWords = query.split(/\s+/).filter(word => word.length > 3);
            let score = 0;

            // Debug
            console.log(`Checking video: ${title}`);

            // Score each word
            queryWords.forEach(word => {
                // Only count meaningful words
                if (titleLower.includes(word)) {
                    score += 1;
                    console.log(`Match found for word "${word}" in "${title}" - score: ${score}`);
                }
            });

            // Add extra points for exact phrase matches
            const queryPhrases = [
                query,                              // Full query
                ...queryWords.filter(w => w.length > 5)  // Longer words as phrases
            ];

            queryPhrases.forEach(phrase => {
                if (titleLower.includes(phrase)) {
                    score += 2; // Bonus for phrase match
                    console.log(`Phrase match for "${phrase}" in "${title}" - bonus score: +2`);
                }
            });

            // If this is the best match so far, store it
            if (score > bestScore) {
                bestScore = score;
                bestMatch = videoId;
                console.log(`New best match: "${title}" with score ${score}`);
            }
        });

        // Only return a match if the score is above a minimum threshold
        if (bestScore >= 1) {
            const matchedTitle = Object.entries(videoList).find(([id, _]) => id === bestMatch)?.[1];
            console.log(`Selected video: "${matchedTitle}" with score ${bestScore}`);
            return bestMatch;
        } else {
            console.log("No good match found, score too low");

            // Return a random video from the list instead of always the same one
            const videoIds = Object.keys(videoList);
            if (videoIds.length > 0) {
                const randomIndex = Math.floor(Math.random() * videoIds.length);
                const randomId = videoIds[randomIndex];
                console.log(`Selecting random video: "${videoList[randomId]}"`);
                return randomId;
            }

            return null;
        }
    };

    const queryResponse = async () => {
        setIsInputDisabled(true);

        var user_query = input;
        setQuery(user_query);
        setinput("");

        // Check if video is selected, if not, try to find a matching video
        let videoId;
        try {
            const videoElement = document.querySelector('.video-style');
            if (!videoElement || !videoElement.src || videoElement.src.includes('undefined')) {
                // No video selected yet, try to find a matching one from the video list
                console.log("No video selected, trying to find a match for:", user_query);

                // Use the state videoList if available, otherwise parse from string
                const videoListToUse = Object.keys(videoList).length > 0 ?
                    videoList :
                    (video_list_string !== "{}" ? JSON.parse(video_list_string) : {});

                // Find matching video
                const matchingVideoId = findMatchingVideo(user_query, videoListToUse);

                if (matchingVideoId) {
                    // Automatically select this video
                    console.log("Automatically selecting video:", matchingVideoId);
                    setVideoId(matchingVideoId);
                    videoId = matchingVideoId;

                    // Make sure the video is displayed
                    setIsWelcompageDisplayed(true);

                    // Add delay to ensure UI updates before continuing
                    await new Promise(resolve => setTimeout(resolve, 100));
                } else {
                    // No match found, use default
                    console.log("No matching video found, using default");
                    videoId = 'mpU84OJ5vdQ'; // Default video ID
                    setVideoId(videoId);
                    setIsWelcompageDisplayed(true);
                }
            } else {
                // Video is already selected, extract its ID
                const SrcSplit = videoElement.src.split('/');
                videoId = SrcSplit[SrcSplit.length - 1].split('?')[0];
            }
        } catch (error) {
            console.error("Error determining video:", error);
            videoId = 'mpU84OJ5vdQ'; // Default video ID as fallback
            setVideoId(videoId);
            setIsWelcompageDisplayed(true);
        }

        console.log('Using videoId for query: ', videoId);

        // Now proceed with the query using the selected/matched video ID
        try {
            // Add a dummy stopped_time parameter if it doesn't exist yet
            const stoppedTime = '0'; // Default to the beginning of the video

            const response = await fetch(`http://127.0.0.1:8000/GetChatbotResponseAjax/?query=${user_query}&videoId=${videoId}&stoppedTime=${stoppedTime}`);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();

            setIsLoaded(true);
            setGPT_response(result.gpt_response || "I'm sorry, I couldn't process that request. Please try again.");
            setQuiz(result.quiz || "");
            setUseScenario(result.use_scenario || false);

            // Check if the response contains "PowerPoint" to determine scenario type
            if (result.gpt_response && result.gpt_response.includes("Presentation has been generated")) {
                setScenarioType("powerpoint");
                setHasPowerPoint(true);
                // Refresh the PowerPoint slides
                try {
                    const refreshedSlides = require('./powerpoint_scenario_JSON.json');
                    powerPointSlides = refreshedSlides;
                    setSlides(refreshedSlides); // Update state
                } catch (e) {
                    console.log("Could not load PowerPoint slides");
                }
            } else if (result.gpt_response && result.gpt_response.includes("Quiz has been generated")) {
                setScenarioType("quiz");
                setHasQuiz(true);
                // Refresh the Quiz data
                try {
                    const refreshedQuiz = require('./quiz_scenario_JSON.json');
                    setQuizScenario(refreshedQuiz);
                } catch (e) {
                    console.log("Could not load Quiz data");
                }
            }

            console.log("USE SCENARIO: " + result.use_scenario);
        } catch (error) {
            console.error("Error making API request:", error);
            setIsLoaded(true);
            setError(error);
            setGPT_response("Sorry, there was an error processing your request. Please try again.");
        } finally {
            setIsInputDisabled(false);
        }
    }

    const HandleSend = async () => {
        if (input.trim().length !== 0) {
            console.log("input ", input)
            queryResponse();
        } else {
            console.log("Input field is empty")
        }
        // queryResponse();
        setIsWelcompageDisplayed(true)
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
                        console.log("Done Text to speeching");
                    } else if (result.reason === SpeechSDK.ResultReason.Canceled) {
                        console.log("cancelled text to speeching");

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
    const [isListening, setIsListening] = useState(false);
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
            // Only update input if we're actively listening
            if (result.reason === sdk.ResultReason.RecognizingSpeech && isListening) {
                const transcript = result.text;
                setinput(transcript);
                setRecTranscript(transcript);
            }
        }

        recognizer.current.recognized = (s, e) => processRecognizedTranscript(e);
        recognizer.current.recognizing = (s, e) => processRecognizingTranscript(e);

        // Don't start listening automatically - we'll start it only when the user clicks the button
        setIsListening(false);

        return () => {
            // Clean up if the recognizer is active
            if (recognizer.current) {
                recognizer.current.stopContinuousRecognitionAsync(() => {
                    console.log('Speech recognition stopped.');
                });
            }
        };
    }, []);

    const resumeListening = () => {
        console.log("Resuming microphone listening...");

        if (!isListening && recognizer.current) {
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

    // increase input chat size
    const chatInputRef = useRef(null);
    useEffect(() => {
        // chatInputRef.current.style.height = "auto";
        // chatInputRef.current.style.height = chatInputRef.current.scrollHeight + "px";
    }, [input])

    //Quiz scenario
    const handleGenerateQuizScenario = () => {
        const SrcSplit = document.querySelector('.video-style').src.split('/')
        const videoId = SrcSplit[SrcSplit.length - 1].split('?')[0]
        fetch(`http://127.0.0.1:8000/GetGenerateQuizJson/?videoId=${videoId}`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result.quiz)
                },
                (error) => {
                    console.log("handle generate quiz aint working you dumb fu")
                }
            )
    }
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

                    // Use functional update to avoid dependency issues
                    setMessages(prevMessages => [
                        ...prevMessages,
                        { text: result.quiz_scenario_user_answers_response, isBot: true },
                    ]);
                },
                (error) => {
                    console.log("error fel quiz yasta");
                }
            );
    };

    const [isLeftOpen, setIsLeftOpen] = useState(false);

    const toggleLeft = () => {
        setIsLeftOpen(!isLeftOpen);
    };

    // change the video id by clicking 
    const [videoId, setVideoId] = useState('mpU84OJ5vdQ'); // Default video ID

    const ChangeVideoEvent = (param) => {
        // Log what we're receiving to help debug
        console.log("ChangeVideoEvent called with param:", param);

        // Handle both cases: when param is a string (videoId) or an object with src property
        if (typeof param === 'object' && param.src) {
            console.log("Handling object with src:", param.src);
            // Get all video elements on the page
            const videoElements = document.querySelectorAll("video");
            console.log("Found video elements:", videoElements);
            // Set the source of each video element
            videoElements.forEach((video) => {
                const source = video.querySelector("source");
                if (source) {
                    source.src = param.src;
                    video.load(); // Reload the video with the new source
                }
            });
        } else {
            // Handle case when param is a videoId string
            console.log("Changing video to ID:", param);
            setVideoId(param);
            setIsWelcompageDisplayed(true);
        }

        // Reset scenarios when video changes
        resetScenarios();
        resetScenariosApp();

        // Clear scenario section if it exists
        const scenarioContent = document.querySelector(".scenario-dropdown-content");
        if (scenarioContent) {
            scenarioContent.innerHTML = "";
        }

        // Hide scenario box when video changes
        setDisplayScenario(false);
    };

    const RefreshVideoSelection = async () => {
        // console.log("aaaaa")

        await fetch(`http://127.0.0.1:8000/RefreshVideoSelection/`)
            .then(res => res.json())
            .then(
                (result) => {
                    video_list_string = result.data
                },
                (error) => {
                    setError(error);
                }
            )
    }

    // PowerPoint Slides Navigation
    const [currentSlide, setCurrentSlide] = useState(0);

    const nextSlide = () => {
        if (currentSlide < slides.length - 1) {
            setCurrentSlide(currentSlide + 1);
        }
    };

    const prevSlide = () => {
        if (currentSlide > 0) {
            setCurrentSlide(currentSlide - 1);
        }
    };

    // Function to download PowerPoint slides as a text file
    const downloadPowerPoint = (slides) => {
        // Create content for download
        let content = "PowerPoint Presentation\n\n";

        slides.forEach((slide, index) => {
            content += `SLIDE ${index + 1}: ${slide.title}\n`;
            content += "------------------------------------------------\n";

            slide.content.forEach((point, i) => {
                content += `• ${point}\n`;
            });

            if (slide.note) {
                content += `\nNOTE: ${slide.note}\n`;
            }

            content += "\n\n";
        });

        // Create a blob with the content
        const blob = new Blob([content], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        // Create a temporary link and trigger download
        const a = document.createElement("a");
        a.href = url;
        a.download = "presentation.txt";
        document.body.appendChild(a);
        a.click();

        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 100);
    };

    // Function to reset scenarios
    const resetScenariosApp = () => {
        // Reset PowerPoint slides to empty array
        powerPointSlides = [];
        setSlides([]);

        // Reset scenario availability flags
        setHasQuiz(false);
        setHasPowerPoint(false);

        // Create empty quiz scenario file
        setQuizScenario([]);
        const emptyQuiz = [];
        localStorage.setItem('quizScenario', JSON.stringify(emptyQuiz));
    };

    return (
        <div className="app">
            <div className="burger-menu" onClick={toggleLeft}>
                {/* &#9776; */}
                <LeftSection className='burger-menu-opened' isOpen={isLeftOpen} ChangeVideoEvent={ChangeVideoEvent} RefreshVideoSelection={RefreshVideoSelection} />
            </div>

            <div className="middle-section">

                {!welcomePageDisplayed ? <div ><div style={{ display: 'none' }}><Video /></div><img src={gptTubeLogo} alt="" className='welcome-logo' /><div className='paragraph'>To start ask the Model<div className='welcomePageContainer'>👋</div> </div></div>
                    : <div className='center-video'>
                        <Video videoId={videoId} />
                    </div>
                }

                {/* displays scenario box when displayScenarioBox == true*/}
                {!displayScenarioBox ?
                    null
                    :
                    <div className="scenario-section">
                        {/* Only show tabs if both quiz and PowerPoint are available */}
                        {(hasQuiz && hasPowerPoint) && (
                            <div className="scenario-tabs">
                                <button
                                    className={`tab-button ${scenarioType === "quiz" ? "active" : ""}`}
                                    onClick={() => setScenarioType("quiz")}
                                >
                                    Quiz
                                </button>
                                <button
                                    className={`tab-button ${scenarioType === "powerpoint" ? "active" : ""}`}
                                    onClick={() => setScenarioType("powerpoint")}
                                >
                                    PowerPoint
                                </button>
                            </div>
                        )}

                        <div className="tab-content">
                            {/* If only one is available, show that directly without tabs */}
                            {(scenarioType === "quiz" || (!hasPowerPoint && hasQuiz)) ? (
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
                                    <button type="submit" className="submit-button">Submit</button>
                                </form>
                            ) : (scenarioType === "powerpoint" || (!hasQuiz && hasPowerPoint)) ? (
                                <div className="powerpoint-container">
                                    {slides.length > 0 ? (
                                        <div className="slide">
                                            <div className="slide-actions">
                                                <button
                                                    className="download-button"
                                                    onClick={() => downloadPowerPoint(slides)}
                                                >
                                                    Download PowerPoint
                                                </button>
                                            </div>
                                            <h2 className="slide-title">{slides[currentSlide].title}</h2>
                                            <div className="slide-content">
                                                <ul>
                                                    {slides[currentSlide].content.map((point, index) => (
                                                        <li key={index}>{point}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                            {slides[currentSlide].note && (
                                                <div className="slide-notes">
                                                    <p><strong>Note:</strong> {slides[currentSlide].note}</p>
                                                </div>
                                            )}
                                            <div className="slide-navigation">
                                                <button
                                                    onClick={prevSlide}
                                                    disabled={currentSlide === 0}
                                                    className="slide-nav-button"
                                                >
                                                    Previous
                                                </button>
                                                <span className="slide-counter">
                                                    {currentSlide + 1} / {slides.length}
                                                </span>
                                                <button
                                                    onClick={nextSlide}
                                                    disabled={currentSlide === slides.length - 1}
                                                    className="slide-nav-button"
                                                >
                                                    Next
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="loading-slides">
                                            <p>Ask in the chat to generate a PowerPoint presentation!</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="no-scenario">
                                    <p>No content available. Ask to generate a Quiz or PowerPoint presentation.</p>
                                </div>
                            )}
                        </div>
                    </div>
                }


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
                        <textarea type='text' disabled={isInputDisabled} name='' id='chat-input' placeholder='Send Message' rows={"1"} value={input} onKeyDown={handleEnter} onChange={(e) => { setinput(e.target.value) }} ref={chatInputRef} />

                        {/* if mic is on, replace the turn mic on with turn mic off, and vice versa */}
                        {!isListening ? <button onClick={resumeListening} className='send material-symbols-rounded hover'> mic </button> : <button onClick={stopListening} className=' send material-symbols-rounded stop hover'> stop </button>}

                        <button className='send material-symbols-rounded hover' onClick={HandleSend}> send </button>

                        {/* if TTS is on, replace the TTS on with TTS off, and vice versa */}
                        {isTextToSpeeching ? <button onClick={stopTextToSpeech} className='send material-symbols-rounded hover'> text_to_speech </button> : <button onClick={resumeTextToSpeech} className=' send material-symbols-rounded hover '> volume_off </button>}
                    </div>
                    {/* <button onClick={handleGenerateQuizScenario}> quiz scenario </button> */}
                </div>
            </div>
        </div>
    );
};

export default App;
