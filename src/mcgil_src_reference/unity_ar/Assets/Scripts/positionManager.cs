using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class positionManager : MonoBehaviour
{

    private static int numEmails = 0;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public static Vector3 getSpreadPosition(){
        numEmails++;
        return new Vector3(numEmails*3.0f-6.0f,Random.Range(-1.5f,1.5f),-5.0f);
    }

    public static void resetSpread(){
        numEmails=0;
    }
}
