using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class mail : MonoBehaviour
{
    public keywordWindowManager windowManager;
    public collapse collapser;
    // Start is called before the first frame update
    void Start()
    {
        windowManager = GameObject.Find("KeywordWindowManager").GetComponent<keywordWindowManager>();
        collapser = GameObject.Find("ExpandedDock").GetComponent<collapse>();
        windowManager.populateWindows(new List<string>() {"Inbox", "Sent", "Drafts","Back"});
    }

    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown("enter")){
            windowManager.clearWindows();
            collapser.uncollapse();
            Destroy(gameObject);
        }
    }
}
