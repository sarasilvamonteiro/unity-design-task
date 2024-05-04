using System.Collections.Generic;
using UnityEngine;
using System;
using Clayxels;


public class PhysicsCursor : MonoBehaviour

{

    private Vector3 mOffset;
    private float mZCoord;

    public List<GameObject> ClosebySpheres = new List<GameObject>();
    public Clayxels.ClayContainer clayContainer;
    public float maxDistance;

    private void Start()
    {
        //clayContainer = GameObject.FindGameObjectWithTag("GameController").GetComponent<Create_copy>().clayContainer;
        clayContainer = gameObject.GetComponentInParent<ClayContainer>();
        maxDistance = 0.8f * gameObject.transform.localScale.x * clayContainer.transform.localScale.x;

        foreach (Transform transform in clayContainer.GetComponentInChildren<Transform>())
        {
            GameObject target = transform.gameObject;

            if (gameObject != target && !ClosebySpheres.Contains(target))
            {
                if (Vector3.Distance(gameObject.transform.position, target.transform.position) <= maxDistance)
                {
                    ClosebySpheres.Add(target);
                }
            }
        }
    }


    void OnMouseDown()
    {
        mZCoord = Camera.main.WorldToScreenPoint(gameObject.transform.position).z;
        mOffset = gameObject.transform.position - GetMouseAsWorldPoint();
    }



    private Vector3 GetMouseAsWorldPoint()
    {
        
        Vector3 mousePoint = Input.mousePosition;
        mousePoint.z = mZCoord;

        return Camera.main.ScreenToWorldPoint(mousePoint);

    }


    // activate to generate current surface collider
    void GenerateCollider() 

    {
        GameObject emptyCollider = clayContainer.GetComponentsInChildren<Transform>()[1].gameObject;
        emptyCollider.name = "este";
        // Aply mesh to collider
        emptyCollider.GetComponent<MeshCollider>().sharedMesh = clayContainer.generateMesh(detail: 10);
        emptyCollider.GetComponent<MeshFilter>().mesh = clayContainer.generateMesh(detail: 10);

    }


    void OnMouseDrag()
    {

        Vector3 direction = (GetMouseAsWorldPoint() + mOffset - gameObject.transform.position).normalized;

        Vector3 positionVector = gameObject.transform.position + 0.035f * direction;
        //WobbleTolerance(positionVector: positionVector);
        transform.position = positionVector;

        transform.position += 0.035f * direction; //0.035 non physics cursor

        foreach (GameObject target in ClosebySpheres)
        {
            target.transform.position += 0.035f * direction; //0.035 nonphysics cursor
        }

    }


    void WobbleTolerance(Vector3 positionVector)
    {

        float wobble_tolerance = 0.03f;

        for (int axis = 0; axis < 3; axis++)
        {

            if (Math.Abs(gameObject.transform.position[axis] - positionVector[axis]) > wobble_tolerance * maxDistance)
            {
                Debug.Log(wobble_tolerance * maxDistance);
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

    }

    private void Update()
    {
        Application.targetFrameRate = 100;
    }


}
