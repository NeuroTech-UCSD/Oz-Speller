using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.UI;
using SocketIO;

public class SocketClient : MonoBehaviour
{
	private SocketIOComponent socket;
    public InputField textBar;
    public Button[] options;
    private int fingerNumber=-1;

	public void Start()
	{
		GameObject go = GameObject.Find("SocketIO");
		socket = go.GetComponent<SocketIOComponent>();

		socket.On("open", TestOpen);
    socket.On("word", HandleWord);
    socket.On("finger", HandleFingerDown);
		socket.On("options", HandleOptions);
    socket.On("delete", HandleDeleteWord);
    socket.On("selection", HandleSelectionMode);

		socket.On("error", TestError);
    }

	public void TestOpen(SocketIOEvent e)
	{
		Debug.Log("[SocketIO] Open received: " + e.name + " " + e.data);
	}

	public void HandleWord(SocketIOEvent e){
	    if(textBar.text == "")
	        textBar.text += e.data["word"].ToString().Trim('"');
        else
           textBar.text += " " + e.data["word"].ToString().Trim('"');
        for (int i =0; i < options.Length; i++){
            options[i].GetComponentInChildren<Text>().text = "";
        }
	}

	public void HandleFingerDown(SocketIOEvent e){
	    Debug.Log(e.data);
	    Debug.Log(e.data["number"].ToString());
	    fingerNumber = Int32.Parse(e.data["number"].ToString().Trim('"'));
	    Debug.Log(fingerNumber);
	}

	public void HandleOptions(SocketIOEvent e){
	    Debug.Log(e.data["words"]);
	    Debug.Log(e.data["words"].Count);
        for (int i =0; i < options.Length; i++){
            string optionText = "";
            if(i < e.data["words"].Count)
                optionText = e.data["words"][i].ToString().Trim('"');
            options[i].GetComponentInChildren<Text>().text = optionText;
        }
	}

    public void HandleDeleteWord(SocketIOEvent e){
        Debug.Log("deleting word");
        string newSentence = textBar.text;
        Debug.Log(newSentence);
        newSentence = newSentence.Trim();
        int endIndex = newSentence.LastIndexOf(" ",newSentence.Length);
        if (endIndex == -1)
            textBar.text = "";
        else
            textBar.text = newSentence.Substring(0,endIndex+1);
    }

    public void HandleSelectionMode(SocketIOEvent e){
        Debug.Log("selection mode on");
    }

	public void TestError(SocketIOEvent e)
	{
		Debug.Log("[SocketIO] Error received: " + e.name + " " + e.data);
		Debug.Log(e);
	}
    // Update is called once per frame
    void Update()
    {
    }

    //expose the current finger number
    public int GetFingerNumber(){
        return fingerNumber;
    }
}
