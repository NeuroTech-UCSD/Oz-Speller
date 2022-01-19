using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class sendForward : MonoBehaviour
{

    public GameObject tile_start;//first email position
    public GameObject tile_end;//email final position

    private Vector3 tile_start_pos;
    private Vector3 tile_end_pos;
    private Vector3 midPoint;
    private float count = 0.0f;

    public float forwardTime = 1.0f;
    private Vector3 bringForward;
    private Vector3 forwardPos;
    private float forwardSpeed;

    private bool movingForward;
    private bool movingToBack;
    private bool movingToFront;

    private bool spreading;
    private bool spread;
    private Vector3 spreadPos;
    private Vector3 returnPos;
    private float spreadSpeed;

    private bool returning;

    void Start()
    {
        bringForward = new Vector3(0.0f, -0.4f, -0.5f);
        forwardSpeed = bringForward.magnitude/forwardTime;

        tile_start_pos = tile_start.transform.position;
        tile_end_pos = tile_end.transform.position;
        midPoint = (tile_start_pos + tile_end_pos) / 2f + Vector3.up*5f;

        movingForward = false;
        movingToBack = false;
        movingToFront = false;
        spreading = false;
        spread = false;
        returning = false;

    }

    bool isFrontEmail(){
        return Vector3.Distance(this.transform.position, tile_start_pos) < 0.001f;
    }

    // Update is called once per frame
    void Update()
    {
       if((Input.GetKeyDown("space")||movingForward) && (!returning && !spread && !spreading)){
           //set the final position to be the next email in front
           if(movingForward == false){
               movingForward=true;
               forwardPos = this.transform.position+bringForward;
               //if the email is all the way in front, make it go to the back instead of further forward
               if(isFrontEmail()){
                  forwardPos = tile_end_pos;
                  movingToBack=true;
                  count=0.0f;
               }
           }
           if(movingToBack){
                count += forwardSpeed*1.5f*Time.deltaTime;

                Vector3 m1 = Vector3.Lerp( tile_start_pos, midPoint, count );
                Vector3 m2 = Vector3.Lerp( midPoint, tile_end_pos, count );
                transform.position = Vector3.Lerp(m1, m2, count);
           }
           else{
               this.transform.position = Vector3.MoveTowards(this.transform.position,forwardPos,forwardSpeed*Time.deltaTime);
           }
           if(Vector3.Distance(this.transform.position,forwardPos) < 0.001f){
                movingForward = false;
                movingToBack=false;
           }
       }
       else if(Input.GetKeyDown("s") || spreading){
             if (!spreading && !spread) {
               spreadPos = positionManager.getSpreadPosition();
               spreadPos.z = this.transform.position.z;
               returnPos = this.transform.position;
               spreadSpeed = Vector3.Distance(this.transform.position,spreadPos)/forwardTime;
               spread = false;
               spreading = true;
            }
            else if (!spreading && spread){
                returning = true;
            }
            else{
               this.transform.position = Vector3.MoveTowards(this.transform.position,spreadPos,spreadSpeed*Time.deltaTime);
               if(Vector3.Distance(this.transform.position,spreadPos) < 0.001f){
                   spreading = false;
                   spread = true;
               }
            }
       }
       else if (returning){
           this.transform.position = Vector3.MoveTowards(this.transform.position,returnPos,spreadSpeed*Time.deltaTime);
           if(Vector3.Distance(this.transform.position,returnPos) < 0.001f){
               returning = false;
               spreading = false;
               spread = false;
               positionManager.resetSpread();
           }
       }
    }
}
