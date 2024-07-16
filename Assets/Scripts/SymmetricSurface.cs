using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SymmetricSurface : MonoBehaviour
{


    public Dictionary<GameObject, GameObject> spherePairs;


    // Start is called before the first frame update
    void Start()
    {

        // Find Symmetric pairs
        foreach (SphereCollider sphere1 in gameObject.GetComponentsInChildren<SphereCollider>())
        {
            foreach (SphereCollider sphere2 in gameObject.GetComponentsInChildren<SphereCollider>())
            {

                if (sphere1 != sphere2)
                {
                    if (sphere1.transform.localPosition.x == -sphere2.transform.localPosition.x &&
                        sphere1.transform.localPosition.z == sphere2.transform.localPosition.z)
                    {
                        //spherePairs.Add(sphere1.gameObject, sphere2.gameObject);
                        if (!sphere1.gameObject.TryGetComponent<SymmetryLink>(out SymmetryLink component))
                        {
                            sphere1.gameObject.AddComponent<SymmetryLink>().pair = sphere2.gameObject;
                            sphere2.gameObject.AddComponent<SymmetryLink>().pair = sphere1.gameObject;
                        }
                        
                    }

                }

            }
        }
    }
}
