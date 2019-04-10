/*
*  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
*
*  Use of this source code is governed by a BSD-style license
*  that can be found in the LICENSE file in the root of the source
*  tree.
*/

'use strict';

/* globals MediaRecorder */

// This code is adapted from
// https://rawgit.com/Miguelao/demos/master/mediarecorder.html

'use strict';

/* globals MediaRecorder */
var mediaSource = new MediaSource();
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
var mediaRecorder;
var recordedBlobs;
var sourceBuffer;

var gumVideo = document.querySelector('video#gum');
var recordedVideo = document.querySelector('video#recorded');

var recordButton = document.querySelector('button#record');
//var playButton = document.querySelector('button#play');
//var downloadButton = document.querySelector('button#download');
recordButton.onclick = toggleRecording;
//playButton.onclick = play;
//downloadButton.onclick = download;

// window.isSecureContext could be used for Chrome
var isSecureOrigin = location.protocol === 'https:' ||
location.host === 'localhost';
if (!isSecureOrigin) {
  alert('getUserMedia() must be run from a secure origin: HTTPS or localhost.' +
    '\n\nChanging protocol to HTTPS');
  location.protocol = 'HTTPS';
}

// Use old-style gUM to avoid requirement to enable the
// Enable experimental Web Platform features flag in Chrome 49

var constraints = {
  audio: true,
  video: true
};

function handleSuccess(stream) {
  console.log('getUserMedia() got stream: ', stream);
  window.stream = stream;
  if (window.URL) {
    gumVideo.src = window.URL.createObjectURL(stream);
  } else {
    gumVideo.src = stream;
  }
}

function handleError(error) {
  console.log('navigator.getUserMedia error: ', error);
}

navigator.mediaDevices.getUserMedia(constraints).
    then(handleSuccess).catch(handleError);

function handleSourceOpen(event) {
  console.log('MediaSource opened');
  sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
  console.log('Source buffer: ', sourceBuffer);
}

recordedVideo.addEventListener('error', function(ev) {
  console.error('MediaRecording.recordedMedia.error()');
  alert('Your browser can not play\n\n' + recordedVideo.src
    + '\n\n media clip. event: ' + JSON.stringify(ev));
}, true);

function handleDataAvailable(event) {
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}

function handleStop(event) {
  console.log('Recorder stopped: ', event);
}

function toggleRecording() {
  if (recordButton.textContent === 'Start Recording') {
    startRecording();
  } else {
    stopRecording();
    recordButton.textContent = 'Start Recording';
    //playButton.disabled = false;
    //downloadButton.disabled = false;
  }
}

// The nested try blocks will be simplified when Chrome 47 moves to Stable
function startRecording() {
  recordedBlobs = [];
	if(navigator.getUserMedia) {
	navigator.getUserMedia({ "video": true, "audio": true}, function(stream) {
	mediaRecorder.src = stream;
	mediaRecorder.play();
	}, error);
	}
	// prefijo WebKit
	else if(navigator.webkitGetUserMedia) {
	navigator.webkitGetUserMedia({ "video": true, "audio": true}, function(stream){
	mediaRecorder.src = window.URL.createObjectURL(stream);
	mediaRecorder.play();
	}, error);
	}
	// prefijo Moz
	else if(navigator.mozGetUserMedia) {
	navigator.mozGetUserMedia({ "video": true, function(stream){
	mediaRecorder.src = window.URL.createObjectURL(stream);
	mediaRecorder.play();
	}, error);
	}
	// Navegadores no compatibles
	else {
	alert("Tu navegador no es compatible con getUserMedia");
	}
}


function stopRecording() {
  mediaRecorder.stop();
  console.log('Recorded Blobs: ', recordedBlobs);
  recordedVideo.controls = true;
  play()
}

function play() {
  var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
  
  var base64data;
  var reader = new window.FileReader();
  reader.readAsDataURL(superBuffer); 
  reader.onloadend = function() 
  {
	base64data = reader.result;  
	recordedVideo.src = base64data;
	document.getElementById("videoBlob").value= base64data;
  }
  
 
}
/*
function download() {
  var blob = new Blob(recordedBlobs, {type: 'video/webm'});
  console.log(recordedBlobs)
  var url = window.URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = 'test.webm';
  document.body.appendChild(a);
  a.click();
  setTimeout(function() {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 100);
}
*/
