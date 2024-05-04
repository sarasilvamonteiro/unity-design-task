using UnityEngine;

public class Fly : MonoBehaviour
{
    Rigidbody Rigidbody;
    private bool Up;
    private bool Down;
    private float lastY;
    private float sensitivity;
    private bool useHands;
    private bool running;


    void Awake()
    {
        // Get rigidbody.
        Rigidbody = GetComponent<Rigidbody>();
        lastY = Rigidbody.transform.position.y;
        useHands = FindObjectOfType<Create>().useHands;
        sensitivity = 0.025f;
    }

    void Update()
    {
        Application.targetFrameRate = 100;

        running = FindObjectOfType<Create>().running;
        Up = false;
        Down = false;
        
        if (useHands && running)
        {
            sensitivity = 0.05f;
        }

        if (Input.GetKey(KeyCode.Space) && !Input.GetMouseButton(0))
        {
            Down = false;
            Up = true;

            //Debug.Log("space");
        }

        if (Input.GetKey(KeyCode.LeftControl) && !Input.GetMouseButton(0)) 
        {
            Up = false;
            Down = true;

            //Debug.Log("shift");
        }

        if (Up)
        {   
            
            Rigidbody.transform.position = Rigidbody.transform.position + sensitivity * Vector3.up;
            //Debug.Log("up");
            lastY = Rigidbody.transform.position.y;     
        }

        if (Down)
        {
            Rigidbody.transform.position = Rigidbody.transform.position - sensitivity * Vector3.up; 
            //Debug.Log("down");
            lastY = Rigidbody.transform.position.y;
        }

        else
        {
            Rigidbody.transform.position = new Vector3(Rigidbody.transform.position.x, lastY, Rigidbody.transform.position.z);
            //Debug.Log("nothing");
        }

    }

}
