using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SearchApp : MonoBehaviour
{
    private string[] apps = {"mail","messages","maps","music","weather"};
    public keywordWindowManager windowManager;
    public InputField inputField;
    public float waitThreshold = 1.5f;
    private List<string> matchedApps = new List<string>();
    private string searchText;
    private bool startAppTimer;
    private float appTimer;
    private string startAppName;
    public SocketClient sc;
    private int fingerNumberNew;
    private int fingerNumberOld;

    void Start()
    {
        inputField = GameObject.Find("InputBar").GetComponent<InputField>();
        windowManager = GameObject.Find("KeywordWindowManager").GetComponent<keywordWindowManager>();
        sc = GameObject.Find("SocketClient").GetComponent<SocketClient>();
        searchText = inputField.text;
        startAppTimer = false;
        appTimer = 0.0f;
        inputField.ActivateInputField();
        inputField.Select();
        inputField.placeholder.GetComponent<Text>().text = "Search...";
        fingerNumberOld = sc.GetFingerNumber();
    }

    // Update is called once per frame
    void Update()
    {
        fingerNumberNew = sc.GetFingerNumber();
        if(!startAppTimer){
            startAppTimer = true;
            if(matchedApps.Count >0 && fingerNumberNew != fingerNumberOld && fingerNumberNew==100){
                startAppName= matchedApps[0];
            }
            else if(Input.GetKeyDown("f")){
                startAppName= matchedApps[1];
            }
            else if(Input.GetKeyDown("j")){
                startAppName= matchedApps[2];
            }
            else if(Input.GetKeyDown("enter")){
                startAppName= matchedApps[3];
            }
            else{
                startAppTimer = false;
            }
        }
        else if (Input.anyKeyDown){
            startAppTimer = false;
            appTimer = 0.0f;
        }
        else if (appTimer > waitThreshold){
            inputField.text = "";
            searchText = "";
            Application.LoadLevelAdditive(startAppName);
            windowManager.clearWindows();
            Destroy(gameObject);
        }
        else {
            appTimer+=Time.deltaTime;
        }

        if(!searchText.Equals(inputField.text)){
            searchText=inputField.text;
            matchedApps.Clear();
            for(int i = 0; i<apps.Length;i++){
                if(apps[i].Contains(searchText))
                    matchedApps.Add(apps[i]);
            }
            foreach (string app in matchedApps)
                Debug.Log(app);
            windowManager.populateWindows(matchedApps);
        }

       fingerNumberOld = fingerNumberNew;
    }
}
