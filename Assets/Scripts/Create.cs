using UnityEngine;
using Clayxels;
using System.Collections.Generic;
using System;
using UnityEngine.UI;
using Leap.Unity.Interaction;
using Leap.Unity;
using Leap.Unity.Interaction.PhysicsHands;

/*!\ This script generates the environment automatically. 
     This is costly, so currently is only running for the NON VR format. */
public class Create : MonoBehaviour
{
    public Slider Holes;
    public Slider Flows;
    [System.NonSerialized]
    public int holes = 1;
    [System.NonSerialized]
    public int flows = 1;

    /*!\The surface has always the same type of behavior for hand input.
        If useHands is true, and physics is true, only the hands' behavior changes.
        If useHands is false (meaning cursor is true), and physics is true, only the surface's behavior changes. */
    public bool useHands = false;
    public bool physics = false;

    public bool emptyTrial = false;
    [System.NonSerialized]
    public bool start = false;
    [System.NonSerialized]
    public bool running = false;
    [System.NonSerialized]
    public Clayxels.ClayContainer clayContainer;
    [System.NonSerialized]
    public Clayxels.ClayContainer groundContainer;
    [System.NonSerialized]
    public List<GameObject> GroundDetectors;
    [System.NonSerialized]
    public GameObject emitterContainer;
    [System.NonSerialized]
    public GameObject liquidContainer;
    private List<com.zibra.liquid.Manipulators.ZibraLiquidCollider> ColliderList;

    public int totalParticles = 1;
    [System.NonSerialized]
    public int sphereNumber;
    [System.NonSerialized]
    public Dictionary<int, int> SphereIDs;


    private void Update()
    {

        // Check if StartButton is pressed. //
        if (Input.GetMouseButtonDown(0))
        {
            Vector3 mousePoint = Input.mousePosition;
            Ray ray = Camera.main.ScreenPointToRay(mousePoint);

            if (Physics.Raycast(ray, out RaycastHit hit))
            {
                if (hit.collider.gameObject.transform == gameObject.transform) // Start Button pressed. //
                {
                    start = true;
                }
            }
        }

        if (start == true)
        {
            // Disable Start Button. //
            gameObject.GetComponent<BoxCollider>().enabled = false;
            foreach (Collider collider in gameObject.GetComponentsInChildren<Collider>())
            {
                collider.enabled = false;
            }
            foreach (Canvas canvas in gameObject.GetComponentsInChildren<Canvas>())
            {
                canvas.enabled = false;
            }

            // Get number of holes and flows. //
            if (emptyTrial == false)
            {
                holes = Holes.GetComponent<StartSlider>().number;
                flows = Flows.GetComponent<StartSlider>().number;
                gameObject.GetComponentInChildren<Canvas>().enabled = true;
            }

            StartSimulation();

        }

        // Make fluid emitter stop if total created particles is above our totalParticles limit. //
        if (running && !emptyTrial)
        {
            if (emitterContainer.GetComponentInChildren<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().CreatedParticlesTotal >= totalParticles)
            {
                emitterContainer.GetComponentInChildren<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().enabled = false;
                running = false;
            }
        }

    }


    void StartSimulation()
    {
        ColliderList = new List<com.zibra.liquid.Manipulators.ZibraLiquidCollider>();
        GroundDetectors = new List<GameObject>();
        SphereIDs = new Dictionary<int, int>();

        // Create surface. //
        SphereSheet(Rows: 9);

        if (emptyTrial == false)
        {
            // Create environment. //
            Ground(HolesNumber: holes);
            Liquid(FlowsNumber: flows, LiquidColliders: ColliderList, VolumePerFrame: 0.01f);
        }

        // Set type of leapManager and leapProvider for handtracking data. //
        if (useHands && gameObject.GetComponent<GetData>().enabled)
        {
            if (!physics)
            {
                gameObject.GetComponent<GetData>().leapManager = GameObject.FindObjectOfType<InteractionManager>();
                gameObject.GetComponent<GetData>().leapProvider = GameObject.FindObjectOfType<LeapServiceProvider>();
            }
            if (physics)
            {
                gameObject.GetComponent<GetData>().leapManager = null;
                gameObject.GetComponent<GetData>().leapProvider = GameObject.FindObjectOfType<PhysicsProvider>();
            }
        }

        running = true;

        // GetData.cs makes start = false. 
        // If it is disabled, we need to set start = false in this script. //
        if (gameObject.GetComponent<GetData>().enabled == false)
        {
            start = false;
        }

    }



    private void SetActiveChildren(Transform transform, bool value)
    {
        foreach (Transform child in transform)
        {

            child.gameObject.SetActive(value);
            //SetActiveChildren(child, true);
        }    
    }



    /*!\ Create surface. 
         Surface shape is a Rows by Rows square. 
         Surface is created using Clayxels plugin. */
    private void SphereSheet(int Rows)
    {

        sphereNumber = (int)(Mathf.Pow(Rows, 2) + Mathf.Pow(Rows - 1, 2));
        float sphereScale = 0.25f;
        // We chose a sphere ID independent to Unity's gameObject ID. 
        // It starts arbitrarily at 2000, and has a 25 int increment. //
        int sphereID = 2000; // 

        // EDIT: Initial sphere position (we want the surface centered). //
        float x = -sphereScale * (Rows - 1); // -(sphereScale * Rows) / 2;
        float y = 0.5f;
        float z = -sphereScale * (Rows - 1); // -(sphereScale * Rows) / 2;

        // Create ClayContainer. //
        clayContainer = new GameObject().AddComponent<ClayContainer>();
        clayContainer.setInteractive(true);
        clayContainer.name = "Main Object";
        // EDIT: I swapped x with z so that all axes are positive. 
        // We want the container to be centered at x.
        clayContainer.transform.position = new Vector3(0, 4f, 10 - (2.5f + (Rows - 1) * sphereScale));
        clayContainer.transform.localScale = Vector3.one;
        clayContainer.setMaxSolidsPerVoxel(2048);

        // Create one sphere (n) for each loop iteration. //
        for (int n = 0, r = 0; n < sphereNumber; n++, r++)
        {
            /*!\ Start next row.
                 if r == Rows, it means we have created as many spheres as Rows
                 so we want to restart the row counter (r = 0). */
            if (n < Rows * Rows && r == Rows)
            {
                r = 0;
                x = -sphereScale * (Rows - 1);
                z += 2 * sphereScale;
            }
            // if n == Rows, we need to start creating the connection spheres (inside main grid).
            if (n == Rows * Rows)
            {
                r = 0;
                x = -sphereScale * (Rows - 1) + sphereScale;
                z = -sphereScale * (Rows - 1) + sphereScale;
            }
            /*!\ This loop accounts for when the connection spheres rows reach its final limit (r == Rows-1).
                 Connection spheres have a grid of (Rows-1) by (Rows-1) and they sit inside the main Rows by Rows
                 main grid. */
            if (n > Rows * Rows && r == Rows - 1)
            {
                r = 0;
                x = -sphereScale * (Rows - 1) + sphereScale;
                z += 2 * sphereScale;
            }

            // Add colliders to the sphere. //
            GameObject newCollider = new GameObject();
            newCollider.name = "collider_" + n.ToString();
            newCollider.transform.parent = clayContainer.transform;
            newCollider.transform.localScale = 2 * sphereScale * Vector3.one;
            newCollider.transform.localPosition = new Vector3(x, y, z);
            newCollider.AddComponent<SphereCollider>();
            newCollider.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Sphere;
            ColliderList.Add(newCollider.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidCollider>());


            if (useHands)
            {
                newCollider.AddComponent<Rigidbody>().useGravity = false;
                newCollider.GetComponent<Rigidbody>().mass = 1f;
                newCollider.AddComponent<SurfaceInteractionPhysics>();
                newCollider.GetComponent<SphereCollider>().radius = 1f;


                if (!physics)
                {
                    newCollider.AddComponent<InteractionBehaviour>().manager = FindObjectOfType<InteractionManager>();
                    // We don't want the software to recognize a certain finger configuration as grasping, so that it behaves more naturaly. 
                    newCollider.GetComponent<InteractionBehaviour>().moveObjectWhenGrasped = false;
                    //newCollider.GetComponent<SphereCollider>().radius = 0.9f;
                }


                newCollider.AddComponent<OnCollision>();
            }
            if (!useHands)
            {
                if (physics)
                {
                    newCollider.AddComponent<Rigidbody>().useGravity = false;
                    newCollider.GetComponent<Rigidbody>().mass = 100;
                    newCollider.AddComponent<SurfaceInteractionPhysics>();
                    /*!\ PhysicsCursor() applies vector increments to the spheres in the direction of the cursor movement. 
                         Unity's built in physics simulator is responsible for making all the sphere's movement dynamics 
                         under those vector increments. */
                    newCollider.AddComponent<PhysicsCursor>(); 
                    
                }
                if (!physics)
                {
                    // MoveCursor() is responsible for programming all the sphere's movement under cursor control.
                    newCollider.AddComponent<MoveCursor>().enabled = true;
                }

            }
            SphereIDs.Add(newCollider.gameObject.GetInstanceID(), sphereID);
            sphereID += 25;

            // Add new clay object. //
            ClayObject newSphere = clayContainer.addClayObject();
            // sphere primitive type = 1; see claySDF.compute solidType for other shapes.
            newSphere.setPrimitiveType(1); 
            newSphere.name = "clay_" + n.ToString();
            newSphere.transform.parent = newCollider.transform;
            newSphere.transform.localPosition = Vector3.zero;
            newSphere.transform.localScale = 0.5f * Vector3.one;
            //if (useHands)
            //{
             //   newSphere.gameObject.AddComponent<SphereCollider>();
            //}
            newSphere.blend = 0.55f;
            newSphere.color = new Color(0.35f, 0.90f, 1, 1);

            x += 2 * sphereScale;

        }

        // save initial positions //

    }


    private void Ground(int HolesNumber = 1)
    {

        groundContainer = new GameObject().AddComponent<ClayContainer>();
        groundContainer.name = "Ground";

        ClayObject ground = groundContainer.addClayObject();
        ground.name = "Ground";
        ground.transform.localScale = new Vector3(20, 0.5f, 20);
        ground.color = Color.white;

        GameObject detectors = new GameObject();
        detectors.name = "Detectors";
        detectors.transform.parent = groundContainer.transform;
        detectors.transform.localPosition = Vector3.zero;

        GameObject colliders = new GameObject();
        colliders.name = "Colliders";
        colliders.transform.parent = groundContainer.transform;
        colliders.transform.localPosition = Vector3.zero;

        GameObject holeColor = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        holeColor.name = "Hole Color";
        holeColor.transform.parent = groundContainer.transform;
        holeColor.transform.localPosition = new Vector3(0, 0, 0);
        holeColor.transform.localScale = new Vector3(15f, 0.1f, 15f);
        Destroy(holeColor.GetComponent<CapsuleCollider>());
        Material holeColorMaterial = new Material(Shader.Find("Standard"));
        holeColor.GetComponent<MeshRenderer>().material = holeColorMaterial;
        holeColorMaterial.color = Color.black;

        // Add holes and ground colliders. //
        // EDIT: Swap x by z so that all axis are positive during analysis. 
        
        // Initial x position. //
        float x = HolesNumber + 1;

        for (int h = 1; h <= HolesNumber; h++)
        {
            float z = 1.5f;
            // Center hole at x = 0 if it's either 1 or 3 holes. 
            if (h == HolesNumber && HolesNumber != 2)
            {
                x = 0;
            }
            // Shift side holes to the side by 1.5 when there are 3 total holes.
            if (h != HolesNumber && HolesNumber == 3)
            {
                z = Math.Abs(x) + 1.5f;
            }

            ClayObject hole = groundContainer.addClayObject();
            hole.setPrimitiveType(2);
            hole.name = "hole_" + (h - 1).ToString();
            hole.transform.localPosition = new Vector3(x, 0, z);
            hole.transform.localScale = new Vector3(0.75f, 2, 0.75f);
            hole.blend = -1;
            hole.color = Color.white;
            Vector3 holePosition = hole.transform.localPosition;
            Vector3 holeSize = hole.transform.localScale;

            GameObject holeDetector = new GameObject();
            holeDetector.name = "hole_detector_" + (h - 1).ToString();
            holeDetector.transform.parent = detectors.transform;
            holeDetector.transform.localPosition = new Vector3(holePosition.x, 0, holePosition.z);
            holeDetector.transform.localScale = new Vector3(2f, 0.1f, 2f); // new Vector3(1.5f,1,1.5f);
            holeDetector.AddComponent<SphereCollider>().enabled = false;
            holeDetector.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Sphere;
            holeDetector.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidVoid>();

            GameObject holeCollider = new GameObject();
            holeCollider.name = "hole_collider_" + (h - 1).ToString();
            holeCollider.transform.parent = colliders.transform;
            holeCollider.transform.localPosition = new Vector3(holePosition.x, holePosition.y - 0.25f, holePosition.z);
            holeCollider.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Torus;
            ColliderList.Add(holeCollider.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidCollider>());

            x = -x;

            // Ground colliders. //
            float width = 3 - holeSize.x;
            float length = holePosition.z + holeSize.x;
            Vector3 position = (holeSize.x + width / 2) * Vector3.one;

            for (int g = 1; g <= 4; g++)
            {

                float z_scale = 12;
                float x_scale = width;
                float z_position = 10 - (z_scale / 2);
                float x_position = holePosition.x + position.x;

                if (g % 2 == 0)
                {
                    z_scale = 10 - length;
                    z_position = holePosition.z + 0.5f * position.z + z_scale / 2;
                    x_scale = 2 * width;
                    x_position = holePosition.x;

                    length = z_scale + 2 * length;
                    position = -position;

                }

                GameObject groundCollider = new GameObject();
                groundCollider.name = "ground_collider_" + (g - 1).ToString();
                groundCollider.transform.parent = colliders.transform;
                groundCollider.transform.localScale = new Vector3(Math.Abs(x_scale), 0.5f, z_scale);
                groundCollider.transform.localPosition = new Vector3(x_position, 0, z_position);
                groundCollider.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Box;
                ColliderList.Add(groundCollider.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidCollider>());

            }
        }

        float x_ = 7 - (2.5f - HolesNumber);

        for (int g = 1; g <= 2; g++)
        {

            GameObject groundCollider_ = new GameObject();
            groundCollider_.name = "ground_collider_" + g.ToString();
            groundCollider_.transform.parent = colliders.transform;
            groundCollider_.transform.localScale = new Vector3(2.5f - HolesNumber, 0.5f, Mathf.Pow(4 - HolesNumber, 12));
            groundCollider_.transform.localPosition = new Vector3(x_, 0, 4);
            groundCollider_.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Box;
            ColliderList.Add(groundCollider_.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidCollider>());

            x_ = -x_;

        }

        GameObject groundDetector = new GameObject();
        groundDetector.name = "ground_detector_0";
        groundDetector.transform.parent = detectors.transform;
        groundDetector.transform.localScale = new Vector3(20, 1, 20);
        groundDetector.transform.localPosition = new Vector3(0, 0.5f, 5); // new Vector3(0, 0.34f, 5);
        groundDetector.AddComponent<BoxCollider>().enabled = false;
        groundDetector.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Box;
        groundDetector.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidDetector>();
        GroundDetectors.Add(groundDetector);

        GameObject groundVoidDetector = new GameObject();
        groundVoidDetector.name = "void_detector_0";
        groundVoidDetector.transform.parent = detectors.transform;
        groundVoidDetector.transform.localPosition = new Vector3(0, -0.25f, 6);
        groundVoidDetector.transform.localScale = new Vector3(25, 0.1f, 25);
        groundVoidDetector.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Sphere;
        groundVoidDetector.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidVoid>();

        GameObject groundVoidDetector2 = new GameObject();
        groundVoidDetector2.name = "void_detector_1";
        groundVoidDetector2.transform.parent = detectors.transform;
        groundVoidDetector2.transform.localPosition = new Vector3(0, 0, 6);
        groundVoidDetector2.transform.localScale = new Vector3(1, 1.5f, 1);
        groundVoidDetector2.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Torus;
        groundVoidDetector2.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidVoid>();

        GameObject groundVoidDetector3 = new GameObject();
        groundVoidDetector3.name = "void_detector_2";
        groundVoidDetector3.transform.parent = detectors.transform;
        groundVoidDetector3.transform.localPosition = new Vector3(0, 0, 6);
        groundVoidDetector3.transform.localScale = new Vector3(2, 2, 2);
        groundVoidDetector3.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Sphere;
        groundVoidDetector3.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidVoid>();

    }

    private void Liquid(int FlowsNumber, List<com.zibra.liquid.Manipulators.ZibraLiquidCollider> LiquidColliders, float VolumePerFrame)
    {

        // Create Liquid Container
        liquidContainer = new GameObject();
        liquidContainer.name = "Liquid";
        liquidContainer.transform.position = new Vector3(0, 5, 5);
        liquidContainer.transform.eulerAngles = new Vector3(0, 180f, 0);

        // Create flows 
        // Create Emitter Container
        emitterContainer = new GameObject();
        emitterContainer.name = "Emitter";
        emitterContainer.transform.parent = liquidContainer.transform;

        float y = 8f;
        float x = FlowsNumber - 1f;
        Vector3 velocity = new Vector3(0, 0.2f, 1.6f); // velocity = new Vector3(1.6f, 0, 0)
        Vector3 rotation = Vector3.zero;


        for (int f = 1; f <= FlowsNumber; f++)
        {
            if (FlowsNumber == 3)
            {
                if (f == 3)
                {
                    y = 10;
                    x = 0;
                }

                velocity = new Vector3(- 0.2f * x, 0.2f, 1.6f);
                rotation = 5 * x * Vector3.up;
            }

            // Create Emitter Container
            GameObject emitter = new GameObject();
            emitter.name = "emitter_" + (f - 1).ToString();
            emitter.transform.parent = emitterContainer.transform;
            emitter.transform.localPosition = new Vector3(x, y, 0);
            emitter.transform.localScale = new Vector3(0.25f, 0.25f, 0.25f);
            emitter.transform.eulerAngles = new Vector3(90, 0, 0); 

            GameObject flow = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            flow.name = "flow";
            flow.transform.parent = emitter.transform;
            flow.transform.localPosition = new Vector3(0, 0, -1.5f);
            flow.transform.localEulerAngles += rotation; // 
            flow.transform.localScale = new Vector3(3, 3, 3);
            Material flowMaterial = new Material(Shader.Find("Standard"));
            Destroy(flow.GetComponent<CapsuleCollider>());
            flow.GetComponent<MeshRenderer>().material = flowMaterial;
            flowMaterial.color = new Color(0.27f, 0.27f, 0.32f, 1);

            GameObject flowDetector = new GameObject();
            flowDetector.name = "flow_detector_" + (f - 1).ToString();
            flowDetector.transform.parent = emitter.transform;
            flowDetector.transform.localPosition = new Vector3(0, 0, 2.5f); // new Vector3(holePosition.x, 0, holePosition.z);
            flowDetector.transform.localScale = new Vector3(1.5f / emitter.transform.localScale.x, 0.07f / emitter.transform.localScale.y, 1.5f / emitter.transform.localScale.z); // new Vector3(1.5f,1,1.5f);
            flowDetector.AddComponent<SphereCollider>().enabled = false;
            flowDetector.AddComponent<com.zibra.liquid.SDFObjects.AnalyticSDF>().ChosenSDFType = com.zibra.liquid.SDFObjects.AnalyticSDF.SDFType.Box;
            flowDetector.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidDetector>();

            // Emitter properties
            emitter.AddComponent<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>();
            emitter.GetComponent<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().InitialVelocity = velocity; //  new Vector3 (velocity.x, 0, velocity.z + 0.2f*z);
            emitter.GetComponent<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>().VolumePerSimTime = Math.Max(VolumePerFrame, 0.01f); // /FlowsNumber

            x = -x;
        }

        liquidContainer.SetActive(false);

        // Liquid properties
        totalParticles = totalParticles * FlowsNumber; //4000000 //200000
        com.zibra.liquid.Solver.ZibraLiquid liquid = liquidContainer.AddComponent<com.zibra.liquid.Solver.ZibraLiquid>();
        liquid.ContainerSize = new Vector3(21, 15, 21);
        liquid.MaxNumParticles = totalParticles;
        liquid.GridResolution = 300;
        //liquid.UseFixedTimestep = true;
        liquid.ReflectionProbeBRP = liquidContainer.AddComponent<ReflectionProbe>();


        foreach (com.zibra.liquid.Manipulators.ZibraLiquidCollider collider in LiquidColliders)
        {
            liquid.AddCollider(collider);
        }

        foreach (com.zibra.liquid.Manipulators.ZibraLiquidEmitter emitter in liquidContainer.GetComponentsInChildren<com.zibra.liquid.Manipulators.ZibraLiquidEmitter>())
        {
            liquid.AddManipulator(emitter);
        }

        foreach (com.zibra.liquid.Manipulators.ZibraLiquidDetector detector in groundContainer.GetComponentsInChildren<com.zibra.liquid.Manipulators.ZibraLiquidDetector>())
        {
            liquid.AddManipulator(detector);
        }
        foreach (com.zibra.liquid.Manipulators.ZibraLiquidVoid voiddetector in groundContainer.GetComponentsInChildren<com.zibra.liquid.Manipulators.ZibraLiquidVoid>())
        {
            liquid.AddManipulator(voiddetector);
        }

        foreach (com.zibra.liquid.Manipulators.ZibraLiquidDetector detector in emitterContainer.GetComponentsInChildren<com.zibra.liquid.Manipulators.ZibraLiquidDetector>())
        {
            liquid.AddManipulator(detector);
        }

        liquidContainer.SetActive(true);

        // Liquid visuals
        liquid.MaterialParameters.AbsorptionAmount = 20;
        liquid.MaterialParameters.ScatteringAmount = 5;
        liquid.MaterialParameters.IndexOfRefraction = 1.2f;
        //liquid.SolverParameters.MinimumVelocity = 0.15f;
        liquid.SolverParameters.MaximumVelocity = 2f;

    }

}