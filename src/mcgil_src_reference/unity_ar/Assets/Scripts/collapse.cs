using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class collapse : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject dock;
    public GameObject[] views;
    public GameObject[] text;
    public InputField inputField;
    public SocketClient sc;
    public float collapseTime = 1.0f;
    private bool collapsing;
    private bool collapsed;
    private bool uncollapsing;
    private string appName;
    private int fingerNumberNew;
    private int fingerNumberOld;
    private bool appOpen;

    void Start()
    {
       collapsing = false;
       uncollapsing = false;
       collapsed = false;
       appOpen = false;
       fingerNumberOld = sc.GetFingerNumber();
    }

    // Update is called once per frame
    void Update()
    {
        fingerNumberNew = sc.GetFingerNumber();
        if(collapsing){
            collapsing = false;
            collapsed = true;
            if(dock.transform.localScale.z>235.0f-150.0f){
                dock.transform.localScale -= new Vector3(0.0f,0.0f,150.0f/collapseTime*Time.deltaTime);
                collapsing = true;
            }
            foreach (GameObject v in views) {
                if(v.transform.localScale.z>0.1){
                    v.transform.localScale -= new Vector3(0.0f,0.0f,176.0f/collapseTime*Time.deltaTime);
                    collapsing = true;
                }
                else{
                    v.SetActive(false);
//                  v.GetComponent<Renderer>().enabled = false;
//                  foreach (Transform child in v.transform)
//                      child.gameObject.SetActive(false);
                }
            }
            foreach (GameObject t in text) {
                if(t.transform.position.y>5.4-1.5){
                    t.transform.position -= new Vector3(0.0f,1.5f/collapseTime*Time.deltaTime,0.0f);
                    collapsing = true;
                }
                else
                    t.GetComponent<TextMesh>().color = Color.black;
            }
       }
       else if (uncollapsing){
            uncollapsing = false;
            collapsed = false;
            if(dock.transform.localScale.z<235.0f){
                dock.transform.localScale += new Vector3(0.0f,0.0f,150.0f/collapseTime*Time.deltaTime);
                uncollapsing = true;
            }
            foreach (GameObject v in views) {
                if(v.transform.localScale.z<176){
                    v.SetActive(true);
                    v.transform.localScale += new Vector3(0.0f,0.0f,176.0f/collapseTime*Time.deltaTime);
                    uncollapsing = true;
                }
            }
            foreach (GameObject t in text) {
                if(t.transform.position.y<5.4){
                    t.GetComponent<TextMesh>().color = Color.white;
                    t.transform.position += new Vector3(0.0f,1.5f/collapseTime*Time.deltaTime,0.0f);
                    uncollapsing = true;
                }
            }
       }
       else if (!appOpen && fingerNumberNew != fingerNumberOld ){
          if (fingerNumberNew==1){
               collapsing = true;
               Application.LoadLevelAdditive("search");
               appOpen=true;
          }
          else if (fingerNumberNew==7){
               collapsing = true;
               Application.LoadLevelAdditive("mail");
               appOpen=true;
          }
       }
       fingerNumberOld = fingerNumberNew;
    }

    public void uncollapse(){
        uncollapsing=true;
        appOpen=false;
    }
/*
    public void collapseDock(){
        collapsing = true;
    }

    public bool getCollapsed(){
        return collapsed;
    }

    public bool getCollapsing(){
        return collapsing;
    }
*/
}
