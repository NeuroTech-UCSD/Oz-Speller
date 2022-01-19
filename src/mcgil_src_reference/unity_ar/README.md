# AR - Unity
The AR frontend interface to demonstrate an application of the EMGeybard.

## Description
The idea behind the AR frontend was to show how the EMGeyboard redefines the way humans can interact with computers.
We intended to create an AR frontend where users can discretely interact with everyday apps. For example, browse and send emails, or pull up and change music being listened to while on the go.

## Installation and Setup
1. Install unity
1. Open up the console scene
1. Ensure the socketIO components server URL property matches the URL of the socketIO server (backend.py sets the server up as 127.0.0.1:4002)
1. Make sure the backend python script is running and the socketIO server is up
1. Hit the play button

## Usage
The main scene is the console scene which has the main user interface where users would be able to open up apps from a list of favorites:
![console scene screenshot](https://raw.githubusercontent.com/NTX-McGill/NeuroTechX-McGill-2020/main/src/unity_ar/console.png)
The keys above each option map to opening up one of the favorites (for example using the left pointer finger to press F would open up the messages app).<br>
Alternatively, the space bar can be pressed (moving the thumb) and the user has the ability to search from all the apps and open one up.
While searching, the matched options show up above a letter which when pressed opens up the corrosponding app.<br>
Apps open up scenes additively. These scenes can then update options and what letters pressed do in the console scene via the exposed public KeyboardWindowManager game object. For example, the function populateWindows allows for apps to change options and commands showed on screen.

## Example Apps
### Music
The music app shows a simple usecase of an app that users would ideally be able to interact uninvasively whilst going about their day. Current solutions to interact with an AR device can be cumbersome - for example verbally dictating music choice can be awkard in public. With the EMGeyboard users would be able to view, pause, play, and choose music with one movement of the finger
![music app scene screenshot](https://raw.githubusercontent.com/NTX-McGill/NeuroTechX-McGill-2020/main/src/unity_ar/music.png)
### Mail
The mail app offers a way for users to quickly respond to emails after getting a notification from the AR device.
![mail app scene screenshot](https://raw.githubusercontent.com/NTX-McGill/NeuroTechX-McGill-2020/main/src/unity_ar/mail.png)
