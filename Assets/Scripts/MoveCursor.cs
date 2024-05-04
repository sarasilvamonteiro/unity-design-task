using System.Collections.Generic;
using UnityEngine;
using System;
using System.Linq;
using Clayxels;

public class MoveCursor : MonoBehaviour
{
    // list of closeby shperes (max should be 4)
    public List<GameObject> ClosebySpheres = new List<GameObject>();
    public Clayxels.ClayContainer clayContainer;

    // mouse position variables
    private Vector3 mOffset;
    private float mZCoord;

    // max distance constraint
    public float maxDistance;
    private Vector3 pull;
    private Dictionary<int, float> targetDistance = new Dictionary<int, float>();


    void Start()
    {
        // 1.   Find parent object scale to set up max distance
        // 2.   Get sphere info
        // 2.a  Save sphere index and initial distance to dictionary
        // 2.b  Add spheres to list when game starts

        // 1.
        //ClosebySpheres = new List<GameObject>();
        //clayContainer = GameObject.FindGameObjectWithTag("GameController").GetComponent<Create_copy>().clayContainer;
        clayContainer = gameObject.GetComponentInParent<ClayContainer>();
        //clayContainer = FindObjectOfType<Surface>().GetComponent<ClayContainer>();

        maxDistance = 0.8f * gameObject.transform.localScale.x * clayContainer.transform.localScale.x;

        // 2.
        int target_idx = 0;

        foreach (Transform transform in clayContainer.GetComponentInChildren<Transform>())
        {
            GameObject target = transform.gameObject;

            if (gameObject != target && !ClosebySpheres.Contains(target))
            {

                //2.a
                float distance_0 = Vector3.Distance(gameObject.transform.position, target.transform.position);
                targetDistance.Add(target_idx, distance_0);
                target_idx++;

                // 2.b
                if (Vector3.Distance(gameObject.transform.position, target.transform.position) <= maxDistance)
                {
                    ClosebySpheres.Add(target);
                }

            }
        }
    }

    void Update()
    {
        // Make framerate consistens throughout trial (before it changed if it wasn't dragging, which made some trials produce fluid inconsistently)
        Application.targetFrameRate = 100;

    }

    void OnMouseDown()
    {
        // 1. Mouse z coordinate
        // 2. Object position when mouse clicked

        // 1.
        mZCoord = Math.Abs(Camera.main.WorldToScreenPoint(gameObject.transform.position).z);
        // 2.
        mOffset = gameObject.transform.position - GetMouseAsWorldPoint();

    }


    void OnMouseDrag()
    {
        // 1.   Set current sphere new position
        // 2.   Pull closeby spheres

        // 1.
        SphereTransformPosition();

        // 2.
        //PullOtherSpheres();

        Debug.Log(mOffset);

    }


    private Vector3 GetMouseAsWorldPoint()
    {
        // 1. Pixel coordinates of mouse (x,y)
        // 2. z coordinate of game object on screen
        // 3. Convert to world points

        // 1.
        Vector3 mousePoint = Input.mousePosition;
        // 2.
        mousePoint.z = mZCoord;
        
        // 3.
        return Camera.main.ScreenToWorldPoint(mousePoint);

    }


    private Vector3 PositionVector()
    {
        // 1.   Get distance between current sphere (gameObject) and closeby spheres (targets)        
        // 1.a  Get each axis distance from target
        // 1.b  Get distance magnitude from target

        // 2.   Position constraints        
        // 2.a  Spherical constraints
        // 2.a.a    Correct each axis if target is above max distance and is the furthest away        
        // 2.b  Linear corrections
        // 2.b.a    Correct each axis for gameObject to not wobble

        ///// 1. /////
        ///
        Dictionary<GameObject, List<float>> Distance_dict = new Dictionary<GameObject, List<float>>();
        List<float> getDistance = new List<float>();

        foreach (GameObject target in ClosebySpheres)
        {
            // 1.a
            List<float> Distance_list = new List<float>(3);

            float x_distance = (GetMouseAsWorldPoint() + mOffset)[0] - target.transform.position.x;
            float y_distance = (GetMouseAsWorldPoint() + mOffset)[1] - target.transform.position.y;
            float z_distance = (GetMouseAsWorldPoint() + mOffset)[2] - target.transform.position.z;

            Distance_list.Add(x_distance);
            Distance_list.Add(y_distance);
            Distance_list.Add(z_distance);

            Distance_dict.Add(target, Distance_list);

            // 1.b
            getDistance.Add(Vector3.Distance(target.transform.position, GetMouseAsWorldPoint() + mOffset));

        }

        ///// 2. /////
        ///
        Vector3 positionVector = GetMouseAsWorldPoint() + mOffset;

        int target_idx = -1;

        // 2.a
        foreach (KeyValuePair<GameObject, List<float>> entry in Distance_dict)
        {
            target_idx++;

            GameObject target = entry.Key;
            // 2.a.a
            List<float> Distance_list = entry.Value;

            //2.a.b 
            if (getDistance[target_idx] >= maxDistance && getDistance[target_idx] >= getDistance.Max())
            {

                foreach (var axis in Distance_list.Select((v, i) => new { Distance = v, Index = i }))
                {
                    positionVector[axis.Index] = target.transform.position[axis.Index] + (maxDistance * axis.Distance / getDistance[target_idx]);
                }
            }

        }

        // 2.b
        //2.b.a
        float wobble_tolerance = 0.02f;

        for (int axis = 0; axis < 3; axis++)
        {

            if (Math.Abs(gameObject.transform.position[axis] - positionVector[axis]) > wobble_tolerance * maxDistance)
            {

                if (gameObject.transform.position[axis] < positionVector[axis])
                {
                    positionVector[axis] = positionVector[axis] - (Math.Abs(gameObject.transform.position[axis] - positionVector[axis]) - wobble_tolerance * maxDistance);
                }

                if (gameObject.transform.position[axis] > positionVector[axis])
                {
                    positionVector[axis] = positionVector[axis] + (Math.Abs(gameObject.transform.position[axis] - positionVector[axis]) - wobble_tolerance * maxDistance);
                }

            }
        }

        return positionVector;
    }

   
    private void SphereTransformPosition()
    {
        
        // 3.   Move gameObject
        // 3.a  Get pull vector and move (if all targets are bellow max distance limit)

        Vector3 positionVector = PositionVector();
      
        ///// 3. /////
        ///
        List<float> finalDistance = new List<float>();

        foreach (GameObject target in ClosebySpheres)
        {
            if (target != null)
            {
                finalDistance.Add(Vector3.Distance(target.transform.position, positionVector));
            }
        }

        // 3.a 
        if (finalDistance.Count(x => x <= maxDistance) == finalDistance.Count)
        {
            pull = positionVector - transform.position;
            transform.position = positionVector;
            Debug.Log(pull);
            PullOtherSpheres();
        }

    }


    private void PullOtherSpheres()
    {
        // 1.   Type of pull vector 
        // 2.   Check if all closeby obey max distance limit
        // 2.a  Add pull vector do current position

        int target_idx = 0;

        foreach (Transform transform in clayContainer.GetComponentInChildren<Transform>())
        {
            GameObject target = transform.gameObject;

            if (gameObject != target)
            {

                // 1.
                //Vector3 pull_vector = ExponentialPull(sphereID: target_idx);
                Vector3 pull_vector = LinearPull(sphereID: target_idx);

                target_idx++;
                int is_closeby = 0;

                // 2.
                foreach (GameObject next_target in target.GetComponent<MoveCursor>().ClosebySpheres)
                {

                    if (Vector3.Distance(next_target.transform.position, target.transform.position + pull_vector) <= maxDistance)
                    {
                        is_closeby += 1;
                    }

                }

                // 2.a
                if (is_closeby == target.GetComponent<MoveCursor>().ClosebySpheres.Count)
                {
                    target.transform.position += pull_vector;
                }

            }
        }
    }


    private Vector3 ExponentialPull(int sphereID)
    {

        // 1.   Define exponential factor
        // 1.a  Set base
        // 1.b  Set x variable (x = distance from target sphere)
        // 2.   Get exponential pull vector

        // 1.
        // 1.a
        float x_min_factor_distance = 2f;
        float y_min_factor = 0.005f;
        float exp_base = Mathf.Pow(y_min_factor, 1.0f / -x_min_factor_distance);
        // 1.b
        float distance = targetDistance[sphereID];

        float factor = Mathf.Pow(exp_base, -distance);
        //float speed = 1;

        // 2.
        Vector3 pull_vector = factor * pull;

        return pull_vector;
    }

    private Vector3 LinearPull(int sphereID)
    {

        // 1.   Define linear factor
        // 1.a  x variable = distance from target sphere; pull slope (smaller moves more)
        // 1.b  factor can't be lower than 0
        // 2.   Get exponential pull vector

        // 1.
        // 1.a
        float distance = targetDistance[sphereID];
        float factor = -0.8f * distance + 1; 
        // 1.b
        if (factor < 0)
        {
            factor = 0;
        }

        // 2.
        Vector3 pull_vector = factor * pull;

        return pull_vector;
    }

}
