using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Clayxels;

public class SurfaceInteractionPhysics : MonoBehaviour
{

    public Clayxels.ClayContainer clayContainer;

    // List of closeby shperes (max should be 4)
    public List<GameObject> ClosebySpheres = new List<GameObject>();

    // Distance/Movement constraints
    public float maxDistance;
    private Dictionary<int, float> targetDistance = new Dictionary<int, float>();


    void Start()
    {
        // 1.   Fetch parent object scale to calculate max distance
        // 2.   Ignore collisions between all spheres in the container
        // 3.   Get closeby spheres info
        // 3.a  Save sphere index and initial distance to dictionary
        // 3.b  Add closeby spheres to list when game starts
        // 4.   Define joints limit between closeby spheres


        // 1.
        clayContainer = gameObject.GetComponentInParent<ClayContainer>();
        maxDistance = 0.8f * gameObject.transform.localScale.x * clayContainer.transform.localScale.x;
        //clayContainer.GetComponent<ClayContainer>().setRenderMode(1);
        //clayContainer.setMaxSolidsPerVoxel(2048);


        // 2. 
        foreach (Rigidbody sphere in clayContainer.GetComponentsInChildren<Rigidbody>())
        {
            Physics.IgnoreCollision(sphere.GetComponent<SphereCollider>(), gameObject.GetComponent<SphereCollider>());
        }

        if (GameObject.FindGameObjectWithTag("Player") != null)
        {
            Physics.IgnoreCollision(GameObject.FindGameObjectWithTag("Player").gameObject.GetComponent<CapsuleCollider>(), gameObject.GetComponent<SphereCollider>());
        }
        

        // 3.
        int target_idx = 0;

        foreach (Transform transform in clayContainer.GetComponentInChildren<Transform>())
        {
            GameObject target = transform.gameObject;

            if (gameObject != target && !ClosebySpheres.Contains(target))
            {

                // 3.a
                float distance_0 = Vector3.Distance(gameObject.transform.position, target.transform.position);
                targetDistance.Add(target_idx, distance_0);
                target_idx++;

                // 3.b
                if (Vector3.Distance(gameObject.transform.position, target.transform.position) <= maxDistance)
                {
                    ClosebySpheres.Add(target);
                }
            }
        }


        // 4.
        foreach (GameObject target in ClosebySpheres)
        {
            
            ConfigurableJoint targetJoint = gameObject.AddComponent<ConfigurableJoint>();
            targetJoint.connectedBody = target.GetComponent<Rigidbody>();
            targetJoint.xMotion = ConfigurableJointMotion.Limited;
            targetJoint.yMotion = ConfigurableJointMotion.Limited;
            targetJoint.zMotion = ConfigurableJointMotion.Limited;
            SoftJointLimit linearLimit = new SoftJointLimit();
            linearLimit.limit = 0.72f * clayContainer.transform.localScale.x * gameObject.transform.localScale.x;
            targetJoint.linearLimit = linearLimit;
            targetJoint.autoConfigureConnectedAnchor = false;
            targetJoint.connectedAnchor = Vector3.zero;

        }
    }


    void Update()
    {
        gameObject.GetComponent<Rigidbody>().velocity = Vector3.zero;
        gameObject.GetComponent<Rigidbody>().angularVelocity = Vector3.zero;  
    }
}
