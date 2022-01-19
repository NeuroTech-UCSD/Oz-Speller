using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class keywordWindowManager : MonoBehaviour
{
    public GameObject windowA;
    public GameObject windowF;
    public GameObject windowJ;
    public GameObject windowEnter;
    private GameObject[] windows= new GameObject[4];
    private Color disappear;
    private Color appear;
    private string[] windowText = new string[4];
    // Start is called before the first frame update
    void Start()
    {
        appear = new Color(1.0f,1.0f,1.0f,1.0f);
        disappear = new Color(1.0f,1.0f,1.0f,0.0f);
        windows[0] = windowA;
        windowText[0] = "";
        windows[1] = windowF;
        windowText[1] = "";
        windows[2] = windowJ;
        windowText[2] = "";
        windows[3] = windowEnter;
        windowText[3] = "";
    }

    // Update is called once per frame
    void Update()
    {
         for(int i=0; i<4; i++){
             if(windowText[i]!=""){
                 windows[i].GetComponent<MeshRenderer>().materials[0].color = Color.Lerp(windows[i].GetComponent<MeshRenderer>().materials[0].color, appear, 1f * Time.deltaTime);
                 windows[i].GetComponent<MeshRenderer>().materials[1].color = Color.Lerp(windows[i].GetComponent<MeshRenderer>().materials[1].color, appear, 1f * Time.deltaTime);
                 windows[i].transform.GetChild(0).GetComponent<TextMesh>().text = windowText[i];
             }
             else{
                 windows[i].GetComponent<MeshRenderer>().materials[0].color = Color.Lerp(windows[i].GetComponent<MeshRenderer>().materials[0].color, disappear, 10f * Time.deltaTime);
                 windows[i].GetComponent<MeshRenderer>().materials[1].color = Color.Lerp(windows[i].GetComponent<MeshRenderer>().materials[1].color, disappear, 10f * Time.deltaTime);
                 windows[i].transform.GetChild(0).GetComponent<TextMesh>().text = "";
             }
        }
    }

    public void populateWindows(List<string> values){
        for(int i=0;i<4;i++){
            if(i<values.Count)
                windowText[i] = values[i];
            else
                windowText[i] = "";
        }
    }

    public void clearWindows(){
         for(int i=0;i<4;i++){
             windowText[i] = "";
         }
    }
    public void setAWindow(string text){
        windowText[0] = text;
    }
    public void setFWindow(string text){
        windowText[1] = text;
    }
    public void setJWindow(string text){
        windowText[2] = text;
    }
    public void setEnterWindow(string text){
        windowText[3] = text;
    }
}
