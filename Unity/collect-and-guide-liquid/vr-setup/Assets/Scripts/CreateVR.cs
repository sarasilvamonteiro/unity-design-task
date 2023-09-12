using UnityEngine;
using System.Collections.Generic;
using UnityEngine.UI;
using Leap.Unity.Interaction.PhysicsHands;


/*!\ This script runs in the VR format.
     For that reason, the environment is not generated automatically and needs to be setup previously via prefabs.
     If one wants to generate a different prefab, code is available for doing so (in the furute :( ).
     PREFABS NEEDED: surface, ground, fluid. 
*/
public class CreateVR : MonoBehaviour
{
    
    public bool start = false;
    [System.NonSerialized]
    public bool running = false;

    public Slider HolesSlider;
    public Slider FlowsSlider;
    public int holes = 1;
    public int flows = 1;
    public int totalParticles;
    // The surface has always the same type of behavior for hand input.
    // If useHands is true, and physics is true, only the hands' behavior changes.
    // If useHands is false (meaning cursor is true), and physics is true, only the surface's behavior changes. //
    public bool useHands = false;
    public bool physics = false;
    public bool emptyTrial = false;
    // This is not autimatized yet. Still need to finish that. :( //
    public Clayxels.ClayContainer MainObject;
    public Clayxels.ClayContainer groundContainer;
    [System.NonSerialized]
    public GameObject emitterContainer;
    [System.NonSerialized]
    public GameObject liquidContainer;
    [System.NonSerialized]
    public int sphereNumber;
    [System.NonSerialized]
    public Dictionary<int, int> SphereIDs;



    private void Start()
    {

        emitterContainer = FindObjectOfType<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().gameObject;
        liquidContainer = FindObjectOfType<com.zibra.liquid.Solver.ZibraLiquid>().gameObject;
        groundContainer.gameObject.SetActive(false);
        liquidContainer.SetActive(false);
        emitterContainer.SetActive(false);
        MainObject.gameObject.SetActive(false);

        // We chose a sphere ID independent to Unity's gameObject ID. 
        // It starts arbitrarily at 2000, and has a 25 int increment. //
        SphereIDs = new Dictionary<int, int>();
        int sphereID = 2000;

        foreach (Rigidbody sphere in MainObject.GetComponentsInChildren<Rigidbody>())
        {
            SphereIDs.Add(sphere.gameObject.GetInstanceID(), sphereID);
            sphereID += 25; // 50 to make it the same number as data collected Jul. 23 
        }

        // Set type of leapManager and leapProvider for handtracking data. //
        gameObject.GetComponent<GetData>().leapManager = null;
        gameObject.GetComponent<GetData>().leapProvider = FindObjectOfType<PhysicsProvider>();

    }
    private void Update()
    {
        Debug.Log(start);
        HolesSlider.value = holes;
        FlowsSlider.value = flows;
        
        // Manual game start. We didn't add StartButton to VR yet. //
        if (start == true)
        {
            Debug.Log("This only runs if GetData.cs is disabled");
            running = true;
            
            // GetData.cs makes start = false.
            // If it's disabled we need to set start = false here. //
            if (gameObject.GetComponent<GetData>().enabled == false) 
            {
                start = false;
            }

            // StartButton is not working. This only disables it's display. //
            DisableButton();
            StartSimulation();

        }

        // Stop fluid after totalParticles limit. //
        if ((running || gameObject.GetComponent<GetData>().running) && !emptyTrial)
        {
            running = true;

            if (emitterContainer.GetComponentInChildren<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().CreatedParticlesTotal >= totalParticles)
            {
                emitterContainer.GetComponentInChildren<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().enabled = false;
                running = false;
                Debug.Log("stop sim");
            }
        }

    }


    public void DisableButton()
    {
        gameObject.GetComponent<BoxCollider>().enabled = false;

        foreach (Collider collider in gameObject.GetComponentsInChildren<Collider>())
        {
            collider.enabled = false;
        }
        foreach (Canvas canvas in gameObject.GetComponentsInChildren<Canvas>())
        {
            canvas.enabled = false;
        }

        if (emptyTrial == false)
        {
            holes = HolesSlider.GetComponent<StartSlider>().number;
            flows = FlowsSlider.GetComponent<StartSlider>().number;

            gameObject.GetComponentInChildren<Canvas>().enabled = true;
        }
    }

    public void StartSimulation()
    {
        if (!emptyTrial)
        {
            groundContainer.gameObject.SetActive(true);
            emitterContainer.SetActive(true);
            liquidContainer.SetActive(true);
        }
        
        MainObject.gameObject.SetActive(true);
    }
   
}