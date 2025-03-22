// import React from "react";
import YouTube from "react-youtube";
import React from 'react';

class Video extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      stoppedTime: null,
      loadedVideoId: null
    };
    this._onPause = this._onPause.bind(this);
    this._onReady = this._onReady.bind(this);
    this._onError = this._onError.bind(this);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.videoId !== this.props.videoId) {
      console.log(`Video component received new videoId: ${this.props.videoId}`);
    }
  }

  _onReady(event) {
    // Log when the video is ready
    try {
      const videoData = event.target.getVideoData();
      console.log("Video ready:", videoData);
      this.setState({ loadedVideoId: videoData.video_id });
    } catch (error) {
      console.error("Error in onReady:", error);
    }
  }

  _onError(event) {
    // Log any errors that occur
    console.error("YouTube player error:", event.data);
  }

  _onPause(event) {
    // When the video is paused, update the stoppedTime state with the current time
    try {
      const stoppedTime = event.target.getCurrentTime();
      this.setState({ stoppedTime });
      // Log the stopped time to the console
      console.log("Video stopped at:", stoppedTime);

      // Send stopped time and video ID to backend
      const videoId = event.target.getVideoData().video_id;
      this.sendStoppedTimeToBackend(stoppedTime, videoId);
    } catch (error) {
      console.error("Error in onPause:", error);
    }
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

    console.log("Video component rendering with videoId:", this.props.videoId);

    return (
      <div>
        <YouTube
          videoId={this.props.videoId}
          opts={options}
          onPause={this._onPause}
          onReady={this._onReady}
          onError={this._onError}
          iframeClassName={"video-style"}
        />
        {/* Debug info - can be removed in production */}
        <div style={{ display: 'none' }}>
          <p>Prop videoId: {this.props.videoId}</p>
          <p>Loaded videoId: {this.state.loadedVideoId}</p>
        </div>
      </div>
    );
  }
}

export default Video;
