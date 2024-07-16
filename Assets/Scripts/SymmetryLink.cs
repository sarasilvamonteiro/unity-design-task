using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SymmetryLink : MonoBehaviour
{

    public GameObject pair;
    private Vector3 prevPosition;

    void Start()
    {
        prevPosition = gameObject.transform.localPosition;   
    }


    // Update is called once per frame
    void Update()
    {
        // If object moves, we need to update its pair's position
        if (gameObject.transform.localPosition != prevPosition)
        {
            pair.transform.localPosition = new Vector3(-gameObject.transform.localPosition.x, gameObject.transform.localPosition.y, gameObject.transform.localPosition.z);
        }

        prevPosition = gameObject.transform.localPosition;
        
        

    }
}
