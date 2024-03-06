// import React from "react";
import YouTube from "react-youtube";
import React from 'react';

class MovieClip extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      stoppedTime: null
    };
    this._onPause = this._onPause.bind(this);
  }

  _onPause(event) {
    // When the video is paused, update the stoppedTime state with the current time
    const stoppedTime = event.target.getCurrentTime();
    this.setState({ stoppedTime });
    // Log the stopped time to the console
    console.log("Video stopped at:", stoppedTime);

    // Send stopped time and video ID to backend
    const videoId = event.target.getVideoData().video_id;
    this.sendStoppedTimeToBackend(stoppedTime, videoId);
  }

  sendStoppedTimeToBackend(stoppedTime, videoId) {
    // Make a GET request to your backend API
    fetch(`http://127.0.0.1:8000/GetTimeAndID/?stoppedTime=${stoppedTime}&videoId=${videoId}`)
      .then(response => {
        if (response.ok) {
          console.log('Data received successfully');
        } else {
          console.error('Failed to receive data');
        }
      })
      .catch(error => {
        console.error('Error occurred:', error);
      });
  }

  // stopVideo = (event) => {
  //   event.target.pauseVideo();
  // };

  render() {
    const options = {
      //height and width now set in css
      // height: '1', // 390 original size
      // width: '1', // 640 original size
      playerVars: {
        autoplay: 0,
        controls: 1,
      },
    };

    return (
      <div>
        <YouTube videoId="IX0iGf2wYM0" opts={options} onPause={this._onPause} iframeClassName={"video-style"} />
        {/* You can display the stopped time if needed */}
        {this.state.stoppedTime && <p>Video stopped at: {this.state.stoppedTime}</p>}
      </div>
    );
  }
}

export default MovieClip;
