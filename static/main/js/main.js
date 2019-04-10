

'use strict';


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
if (!isSecureOrigin) 
{
	alert('getUserMedia() must be run from a secure origin: HTTPS or localhost.' +
	'\n\nChanging protocol to HTTPS');
	location.protocol = 'HTTPS';
}

// Use old-style gUM to avoid requirement to enable the
// Enable experimental Web Platform features flag in Chrome 49

var constraints = 
{
	audio: true,
	video: true
};

function handleSuccess(stream) 
{
	console.log('getUserMedia() got stream: ', stream);
	window.stream = stream;
	if (window.URL) 
	{
		gumVideo.src = window.URL.createObjectURL(stream);
	} 
	else 
	{
		gumVideo.src = stream;
	}
}

function handleError(error) 
{
	console.log('navigator.getUserMedia error: ', error);
}

navigator.mediaDevices.getUserMedia(constraints).
    then(handleSuccess).catch(handleError);

function handleSourceOpen(event)
{
	console.log('MediaSource opened');
	sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
	console.log('Source buffer: ', sourceBuffer);
}

recordedVideo.addEventListener('error', function(ev) 
{
	console.error('MediaRecording.recordedMedia.error()');
	alert('Your browser can not play\n\n' + recordedVideo.src
	+ '\n\n media clip. event: ' + JSON.stringify(ev));
}, true);

function handleDataAvailable(event) 
{
	if (event.data && event.data.size > 0) 
	{
		recordedBlobs.push(event.data);
	}
}

function handleStop(event) 
{
	console.log('Recorder stopped: ', event);
}

function toggleRecording() 
{
	document.getElementById("countdown").style.display = "block"
	
	if (recordButton.textContent === 'Start Recording') 
	{
		startRecording();
	} 
	else 
	{
		stopRecording();
		recordButton.textContent = 'Start Recording';
		//playButton.disabled = false;
		//downloadButton.disabled = false;
	}
}

var isMobile = {
mobilecheck : function() {
return (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino|android|ipad|playbook|silk/i.test(navigator.userAgent||navigator.vendor||window.opera)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test((navigator.userAgent||navigator.vendor||window.opera).substr(0,4)))
}
}




// The nested try blocks will be simplified when Chrome 47 moves to Stable
function startRecording() 
{
	
	document.getElementById('countdown').innerHTML=60;
	countdown();
	recordedBlobs = [];
	if(isMobile.mobilecheck()== false)
	{
	
	var options = {mimeType: 'video/webm;codecs=vp9'};
	if (!MediaRecorder.isTypeSupported(options.mimeType)) 
	{
		
		console.log(options.mimeType + ' is not Supported');
		options = {mimeType: 'video/webm;codecs=vp8'};
		if (!MediaRecorder.isTypeSupported(options.mimeType)) 
		{
			
			console.log(options.mimeType + ' is not Supported');
			options = {mimeType: 'video/webm'};
	
			if (!MediaRecorder.isTypeSupported(options.mimeType)) 
			{
				console.log(options.mimeType + ' is not Supported');
				options = {mimeType: ''};
			}
		
		}
	
	}
	}
	else
	{
		
		var options = {mimeType: 'video/MediaStream;codecs=vp9'};
		if (!MediaRecorder.isTypeSupported(options.mimeType)) 
		{
			console.log(options.mimeType + ' is not Supported');
			options = {mimeType: 'video/MediaStream;codecs=vp8'};
			if (!MediaRecorder.isTypeSupported(options.mimeType)) 
			{
			
					console.log(options.mimeType + ' is not Supported');
					options = {mimeType: 'video/MediaStream'};
			
					if (!MediaRecorder.isTypeSupported(options.mimeType)) 
					{
						console.log(options.mimeType + ' is not Supported');
						options = {mimeType: ''};
					}
				}
			}
		
	
	}
	
	try 
	{
		mediaRecorder = new MediaRecorder(window.stream, options);
	} 
	catch (e) 
	{
		console.error('Exception while creating MediaRecorder: ' + e);
		alert('Exception while creating MediaRecorder: '
		  + e + '. mimeType: ' + options.mimeType);
		return;
	}
	console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
	recordButton.textContent = 'Stop Recording';
	//playButton.disabled = true;
	//downloadButton.disabled = true;
	mediaRecorder.onstop = handleStop;
	mediaRecorder.ondataavailable = handleDataAvailable;
	mediaRecorder.start(10); // collect 10ms of data
	console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() 
{
	stopClock()
	document.getElementById("countdown").style.display = "none"
	mediaRecorder.stop();
	console.log('Recorded Blobs: ', recordedBlobs);
	recordedVideo.controls = true;
	play()
	//document.getElementById("guardar").style.visibility = "visible"
}

function play() 
{
	if(isMobile.mobilecheck()== false)
	{
		var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
	}
	else
	{
		var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
	}
	var base64data="";
	var reader="";
	reader = new window.FileReader();
	reader.readAsDataURL(superBuffer); 
	reader.onloadend = function() 
	{
		//var createObjectURL = (window.URL || window.webkitURL || {}).createObjectURL || function(){};
        
		var videoBlobURL =  window.URL.createObjectURL(superBuffer);
		base64data = reader.result;  
		recordedVideo.src = "";
		recordedVideo.src = videoBlobURL;
		recordedVideo.load();
		document.getElementById("grabacionFinal").src = base64data;
		document.getElementById("videoBlob").value= base64data;
		
		
	}
	document.getElementById("recorded").style.visibility = "visible"
   
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
