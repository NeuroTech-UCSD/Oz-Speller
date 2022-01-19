using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.Net;
using System.Text;
using System.Net.WebSockets;
using System.Net.Sockets;
using System.IO;
using System.Threading;

public class socketDemo : MonoBehaviour
{
    public InputField textBar;
    public InputField correction1;
    public InputField correction2;

    ClientWebSocket ws = new ClientWebSocket();
    bool reading=true;
    float heartbeatTime = 5.0f;

    void Start()
    {
         Startup();
    }

    private async void Startup(){
          Uri serverUri = new Uri("ws://localhost:8080/socket.io/?EIO=3&transport=websocket");
          await ws.ConnectAsync(serverUri, CancellationToken.None);
          ArraySegment<byte> bytesReceived = new ArraySegment<byte>(new byte[1024]);
          await ws.ReceiveAsync(bytesReceived, CancellationToken.None);
          await ws.ReceiveAsync(bytesReceived, CancellationToken.None);
          reading=false;
    }

    private async void Flush(){
       ArraySegment<byte> bytesReceived = new ArraySegment<byte>(new byte[1024]);
       await ws.ReceiveAsync(bytesReceived, CancellationToken.None);
    }

    private async void Read(){
         //ArraySegment<byte> bytesToSend = new ArraySegment<byte>(Encoding.UTF8.GetBytes("2"));
         //await ws.SendAsync(bytesToSend, WebSocketMessageType.Text, true, CancellationToken.None);
         reading=true;
         ArraySegment<byte> bytesReceived = new ArraySegment<byte>(new byte[1024]);
         WebSocketReceiveResult result = await ws.ReceiveAsync(bytesReceived, CancellationToken.None);
         string read = Encoding.UTF8.GetString(bytesReceived.Array, 0, result.Count);
         if(read!="3"){
             string[] Arr = Encoding.UTF8.GetString(bytesReceived.Array, 0, result.Count).Split(new char[] { '\"' }, StringSplitOptions.RemoveEmptyEntries);
             Debug.Log(Arr[3]);
             textBar.text+=Arr[3];
         }
         reading=false;
    }

    private async void Send(){
        ArraySegment<byte> bytesToSend = new ArraySegment<byte>(Encoding.UTF8.GetBytes("42[\"chat message\",\"hi\"]"));
        await ws.SendAsync(bytesToSend, WebSocketMessageType.Text, true, CancellationToken.None);
    }

    private async void Heartbeat(){
         ArraySegment<byte> bytesToSend = new ArraySegment<byte>(Encoding.UTF8.GetBytes("2"));
         await ws.SendAsync(bytesToSend, WebSocketMessageType.Text, true, CancellationToken.None);
         heartbeatTime=5.0f;
     }

    void Update()
    {
        heartbeatTime-=Time.deltaTime;
        if(ws.State == WebSocketState.Open){
            if(heartbeatTime<0)
                Heartbeat();
            if(!reading)
                Read();
        }
    }
}
