using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Leap;
using Leap.Unity;
using Leap.Unity.Interaction;
using Leap.Unity.Interaction.PhysicsHands;

public class OnCollision : MonoBehaviour
{
    private Component handTracking;
    private bool useHands;
    private bool physics;
    private LeapProvider leapProvider;
    private InteractionBehaviour interactionBehaviour;
    private PhysicsProvider physicsProvider;

    public bool LHandTouch;
    public bool RHandTouch;



    void Start()
    {

        //if (FindObjectOfType<Create>() == null)
        //{
        //    useHands = FindObjectOfType<Settings>().useHands;
        //    physics = FindObjectOfType<Settings>().physics;
        //}
        //else
        //{
        useHands = FindObjectOfType<Create>().useHands;
        physics = FindObjectOfType<Create>().physics;
        //}

        if (useHands)
        {

            if (!physics)
            {
                leapProvider = FindObjectOfType<LeapServiceProvider>();
                interactionBehaviour = GetComponent<InteractionBehaviour>();
            }
            if (physics)
            {
                leapProvider = FindObjectOfType<PhysicsProvider>();
                physicsProvider = FindObjectOfType<PhysicsProvider>();
            }

        }
 
    }

    private void Update()
    {
        // So far, hand collision is only available for the physics setup.
        if (useHands)
        {
            GetHand();
        }
    }


    private void OnCollisionStay(Collision collision)
    {
      //Debug.Log("Collision continues.");
    }

    private void OnCollisionEnter(Collision collision)
    {
       //Debug.Log("Collision enters.");
    }

    private void OnCollisionExit(Collision collision)
    {
        //Debug.Log("Collision exits.");
    }


    void GetHand()
    {
        if (physics)
        {
            LHandTouch = physicsProvider.LeftHand.IsObjectInHandRadius(rigid: gameObject.GetComponent<Rigidbody>());
            RHandTouch = physicsProvider.RightHand.IsObjectInHandRadius(rigid: gameObject.GetComponent<Rigidbody>());
        }
        if (!physics)
        {

            // This is not ideal with non-physics, because in only tracks the closest hovering hand...
            if (!interactionBehaviour.isHovered)
            {
                LHandTouch = false;
                RHandTouch = false;
            }
            if (interactionBehaviour.isHovered)
            {
                LHandTouch = interactionBehaviour.closestHoveringHand.IsLeft;
                RHandTouch = interactionBehaviour.closestHoveringHand.IsRight;
            }   
        }

        Debug.Log("Left hand touch: " + LHandTouch.ToString());
        Debug.Log("Right hand touch: " + RHandTouch.ToString());

    }

}
