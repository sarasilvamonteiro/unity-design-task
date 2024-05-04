using UnityEngine;
using System;
using System.Data;
using System.Collections.Generic;
using System.IO;
using UnityEngine.UI;
using Leap;
using Leap.Unity;
using Leap.Unity.Interaction;
using com.zibra.liquid.Manipulators;
using System.Linq;


public class GetData : MonoBehaviour
{

    //get time counter
    // save particle ID + movement vector + timestamp to array
    // get detector particle count
    // get ground plane's color
    // get liquid emitter
    // define goal completion
    // save array when goal completed
    // turn ground green
    // stop liquid emitter


    // Data: //
    // agent position
    // agent looking at
    // sphere ID
    // move vector
    // sphere position
    // amount of fluid in environment
    // amount of fluid going past hole

    public int subjectNumber;
    
    //[System.NonSerialized]
    public LeapProvider leapProvider;
    //[System.NonSerialized]
    public InteractionManager leapManager;

    private Clayxels.ClayContainer clayContainer;
    private Clayxels.ClayContainer groundContainer;
    private GameObject emitterContainer;
    private GameObject liquidContainer;
    private GameObject personController;
    private List<GameObject> holeDetector = new List<GameObject>();
    private GameObject holeColor;
    //private GameObject groundDetector;
    private List<GameObject> GroundDetectors = new List<GameObject>();

    // DataTables:
    private DataTable generalData;
    private DataTable surfaceData;
    private DataTable fluidData;
    private DataTable leftHandData;
    private DataTable rightHandData;
    private string general_tableName;
    private string fluid_tableName;
    private string surface_tableName;
    private string leftHand_tableName;
    private string rightHand_tableName;
    private int rowCounter;

    private GameObject sphereHit;
    private int sphereHitID;
    private Vector3 sphereHitPosition;
    private Vector3 sphereLastPosition;
    private Vector3 sphereMove;
    private int sphereNumber;

    // Fluid data:
    private float totalParticles;
    private float totalEmittedParticles;
    private float totalHoleParticles;
    private float thisHoleParticles;
    private float groundParticles;
    private float totalWastedParticles;
    private float getEmitterParticles;
    private float perFrameEmitterParticles;
    private Vector3 singleHoleAllParticles;
    private List<float> fractionScore;
    private float percentage_left_to_stop_sim;
    private List<bool> tenperfectlist = new List<bool>(10);
    private bool perfectShape;
    private float fluidHoleLimit;


    // Display Text:
    private Text flow;
    private Text score;
    private Text best;
    private float score_counter;
    private int rowsNumber = 360;


    // Conditions:
    private bool start;
    private float startTime;
    private bool running;
    private bool useHands;
    private bool physics;
    private bool VR;
    private bool emptyTrial;
    private int holes;
    private int flows;
    private bool drag;
    private Vector3 lookingAt;
    // Check if hands is detected
    private bool isLeftHand;
    private bool isRightHand;
    // Detect which hand is deforming the surface
    private bool LHandTouch;
    private bool RHandTouch;

    private int frames = 0;
    private int frameStep;

    private Dictionary<int, int> SphereIDs;



    void Start()
    {
        start = false;
        drag = false;
        running = false;


    }
    void FixedUpdate()
    {
        frameStep = 1;
        if (VR)
        {
            frameStep = 15;
        }

        if (gameObject.GetComponent<Create>().start)
        {
            InitializeObjects();
            gameObject.GetComponent<Create>().start = false;
        }

        if (running && rowCounter < rowsNumber && (frames % frameStep == 0))
        {

            if (!emptyTrial)
            {
                CountParticles();
                FluidData();
            }

            GeneralData();
            SurfaceData();


            if (useHands)
            {
                HandTracking();
            }

            CountParticles();
            GeneralData();

            rowCounter++;
            if (rowCounter == rowsNumber - 10) // give them some frames to finish movement //
            {
                if (!emptyTrial)
                {   // turn fluid emitter off
                    liquidContainer.GetComponentInChildren<ZibraLiquidEmitter>().enabled = false;
                }
            }

            //if (gameObject.GetComponent<Create>().running == true)
            //{
            //PrintData();
            //}
            //GetCompleteGoal();

        }
        frames++;

        //if (Input.GetKey(KeyCode.KeypadEnter))
        //{
        //Time.timeScale = 100;
        //fastForward = true;
        //}

    }

    private void InitializeObjects()
    {

        running = true;
        startTime = Time.time;

        // DisplayText:
        flow = gameObject.GetComponentsInChildren<Text>()[0];
        score = gameObject.GetComponentsInChildren<Text>()[1];
        best = gameObject.GetComponentsInChildren<Text>()[2];
        //score.text = "Shape: 0/100";

        Create getCreate = gameObject.GetComponent<Create>();
        holes = getCreate.holes;
        flows = getCreate.flows;
        useHands = getCreate.useHands;
        physics = getCreate.physics;
        //VR = getCreate.VR;
        emptyTrial = getCreate.emptyTrial;

        // Fluid:
        totalParticles = getCreate.totalParticles;
        totalEmittedParticles = 0;
        totalHoleParticles = 0;
        totalWastedParticles = 0;
        singleHoleAllParticles = Vector3.zero;
        // We add extra 150 for each hole
        if (useHands)
        {
            fluidHoleLimit = 700 + holes * 200;
        }
        if (!useHands)
        {
            fluidHoleLimit = 400 + holes * 150;
        }
        

        Debug.Log("Initialize");

        rowCounter = 0;

        // Containers:
        clayContainer = getCreate.clayContainer;
        if (!useHands && !physics)
        {
            sphereNumber = clayContainer.GetComponentsInChildren<SphereCollider>().Length;
        }
        else
        {
            sphereNumber = clayContainer.GetComponentsInChildren<Rigidbody>().Length;
        }
        Debug.Log(sphereNumber);
        SphereIDs = getCreate.SphereIDs;
        Debug.Log(SphereIDs.Count);

        // DataTables:     
        generalData = GeneralDataTable();
        surfaceData = SurfaceDataTable();

        if (!emptyTrial)
        {
            // Containers:
            emitterContainer = getCreate.emitterContainer;
            groundContainer = getCreate.groundContainer;
            liquidContainer = getCreate.liquidContainer;
            //holeColor = groundContainer.GetComponentInChildren<CapsuleCollider>().gameObject;
            // DataTables:     
            fluidData = FluidDataTable();
        }
        if (useHands)
        {
            // DataTables:
            leftHand_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_left_hand";
            rightHand_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_right_hand";
            leftHandData = HandDataTable(tableName: leftHand_tableName);
            rightHandData = HandDataTable(tableName: rightHand_tableName);
        }

        // Player is only used for the cursor setup
        if (GameObject.FindGameObjectWithTag("Player") != null)
        {
            personController = GameObject.FindGameObjectWithTag("Player");
        }

        //SaveInitialPositions();

    }

    private void SaveInitialPositions()
    {

        string tableName = "initial_positions";
        DataTable initialPositions = new DataTable { TableName = tableName };

        initialPositions.Columns.Add(new DataColumn { ColumnName = "ID", DataType = typeof(string) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "Position", DataType = typeof(Vector3) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "AgentLookingAt", DataType = typeof(Vector3) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });

        DataRow generalRow = initialPositions.NewRow();

        generalRow[0] = "Agent";
        generalRow[1] = FindObjectOfType<Camera>().transform.position;//personController.transform.position; // Player position
        generalRow[2] = new Vector3(FindObjectOfType<Camera>().transform.GetChild(0).transform.eulerAngles.x, FindObjectOfType<Camera>().transform.eulerAngles.y, 0); // Player rotation
        generalRow[3] = Time.time - startTime;

        initialPositions.Rows.Add(generalRow);

        foreach (SphereCollider sphere in clayContainer.GetComponentsInChildren<SphereCollider>())
        {
            Vector3 spherePosition = sphere.gameObject.transform.position;
            int sphereID = sphere.gameObject.GetInstanceID();

            DataRow sphereRow = initialPositions.NewRow();
            sphereRow[0] = SphereIDs[sphereID];
            sphereRow[1] = spherePosition;
            sphereRow[2] = Vector3.zero;
            sphereRow[3] = Time.time - startTime;

            initialPositions.Rows.Add(sphereRow);
        }

        string path = @"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_";
        System.IO.Directory.CreateDirectory(path + subjectNumber.ToString());
        initialPositions.WriteXml(path + subjectNumber.ToString() + @"\initial_positions");
    }


    // GENERAL DATA //
    private DataTable GeneralDataTable()
    {
        general_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_general";
        DataTable generalData = new DataTable { TableName = general_tableName };

        generalData.Columns.Add(new DataColumn { ColumnName = "AgentPosition", DataType = typeof(Vector3) });
        generalData.Columns.Add(new DataColumn { ColumnName = "AgentLookingAt", DataType = typeof(Vector3) });  // use eyetracking if in VR mode, else, use head direction    
                                                                                                                // generalData.Columns.Add(new DataColumn { ColumnName = "ShapeScore", DataType = typeof(bool) });      // score in terms of surface shape (does it look "ideal"?)

        if (!useHands)
        {
            generalData.Columns.Add(new DataColumn { ColumnName = "SphereID", DataType = typeof(int) });           // sphere being clicked on
            generalData.Columns.Add(new DataColumn { ColumnName = "SpherePosition", DataType = typeof(Vector3) }); // position of sphere being clicked on
            generalData.Columns.Add(new DataColumn { ColumnName = "MouseDrag", DataType = typeof(bool) });         // is mouse clicking on sphere
        }
        if (useHands)
        {
            generalData.Columns.Add(new DataColumn { ColumnName = "SphereID_LTouch", DataType = typeof(string) });
            generalData.Columns.Add(new DataColumn { ColumnName = "SphereID_RTouch", DataType = typeof(string) });
            generalData.Columns.Add(new DataColumn { ColumnName = "LTouch", DataType = typeof(bool) });   // is left hand being tracked
            generalData.Columns.Add(new DataColumn { ColumnName = "Rtouch", DataType = typeof(bool) });  // is right hand being tracked
            generalData.Columns.Add(new DataColumn { ColumnName = "isLeftHand", DataType = typeof(bool) });   // is left hand being tracked
            generalData.Columns.Add(new DataColumn { ColumnName = "isRightHand", DataType = typeof(bool) });  // is right hand being tracked
        }
        generalData.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });

        // Add 300 rows
        for (int i = 1; i <= rowsNumber; i++)
        {
            DataRow newRow = generalData.NewRow();
            generalData.Rows.Add(newRow);
        }
        return generalData;
    }
    private void GeneralData()
    {
        // Surface:
        GetDraggedSphere();
        // Player:
        generalData.Rows[rowCounter][0] = FindObjectOfType<Camera>().transform.position;// Player position
                                                                                        // 
        if (VR)
        {
            // Debug.Log("eyes: "+FindObjectOfType<EyeTracking>().gazeTarget.transform.position.ToString());
            //generalData.Rows[rowCounter][1] = FindObjectOfType<EyeTracking>().gazeTarget.transform.position;  // Player looking at
        }
        if (!VR)
        {
            //generalData.Rows[rowCounter][1] = new Vector3(personController.transform.GetChild(0).transform.eulerAngles.x, personController.transform.eulerAngles.y, 0); // Player looking at
            generalData.Rows[rowCounter][1] = lookingAt; // Player looking at
        }
        if (!useHands)
        {
            // Surface:
            generalData.Rows[rowCounter][2] = GetDraggedSphere().Item1; ;           // Sphere being dragged ID
            generalData.Rows[rowCounter][3] = GetDraggedSphere().Item2;   // Sphere position
            generalData.Rows[rowCounter][4] = drag;                    // is mouse dragging
        }
        if (useHands)
        {
            // Hands:
            generalData.Rows[rowCounter][6] = isLeftHand;
            generalData.Rows[rowCounter][7] = isRightHand;
        }
        generalData.Rows[rowCounter][generalData.Columns.Count - 1] = Time.time - startTime;   // Current timestamp      
    }


    // FLUID DATA //
    private DataTable FluidDataTable()
    {
        fluid_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_fluid";
        DataTable fluidData = new DataTable { TableName = fluid_tableName };

        fluidData.Columns.Add(new DataColumn { ColumnName = "FluidEmitted", DataType = typeof(int) });       // 
        fluidData.Columns.Add(new DataColumn { ColumnName = "FluidInHole", DataType = typeof(Vector3) });    // fluid in EACH hole (Vector3: max 3 holes)
        fluidData.Columns.Add(new DataColumn { ColumnName = "FluidInGround", DataType = typeof(int) });      // 
        fluidData.Columns.Add(new DataColumn { ColumnName = "FluidWasted", DataType = typeof(int) });        // 
        fluidData.Columns.Add(new DataColumn { ColumnName = "FluidLeft", DataType = typeof(int) });          // total particles - emitted particles
        fluidData.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });        // 

        // Add 300 rows
        for (int i = 1; i <= rowsNumber; i++)
        {
            DataRow newRow = fluidData.NewRow();
            fluidData.Rows.Add(newRow);
        }

        return fluidData;
    }
    private void FluidData()
    {
        // Fluid:
        fluidData.Rows[rowCounter][0] = getEmitterParticles;                // Total emitted particles  // totalEmittedParticles or getemitterparticles      
        fluidData.Rows[rowCounter][1] = singleHoleAllParticles;             // Total in hole
        fluidData.Rows[rowCounter][2] = groundParticles;                    // Current in ground
        fluidData.Rows[rowCounter][3] = totalWastedParticles;               // Total wasted
        fluidData.Rows[rowCounter][4] = percentage_left_to_stop_sim;        // Percentage flow left
        fluidData.Rows[rowCounter][fluidData.Columns.Count - 1] = Time.time - startTime;
        //generalData.Rows[rowCounter][10] = perfectShape; //Score();                           // Score percentage
    }
    private void CountParticles()
    {
        getEmitterParticles = 0;
        perFrameEmitterParticles = 0;

        foreach (ZibraLiquidEmitter emitter in emitterContainer.GetComponentsInChildren<ZibraLiquidEmitter>())
        {
            getEmitterParticles += emitter.CreatedParticlesTotal; // current particles per frame from the emitters
            perFrameEmitterParticles += emitter.CreatedParticlesPerFrame;
        }
        // Try voids:     
        fractionScore = new List<float>();
        List<float> FrameHoles = new List<float>();
        totalHoleParticles = 0;
        groundParticles = groundContainer.GetComponentInChildren<ZibraLiquidDetector>().ParticlesInside;

        for (int i = 0; i < holes; i++)
        {
            ZibraLiquidVoid detector = groundContainer.GetComponentsInChildren<ZibraLiquidVoid>()[i];
            totalWastedParticles = 0;
            float framewaste = 0;

            for (int v = holes; v < holes + 3; v++)
            {
                ZibraLiquidVoid groundvoid = groundContainer.GetComponentsInChildren<ZibraLiquidVoid>()[v];
                totalWastedParticles += groundvoid.DeletedParticleCountTotal;
                framewaste += groundvoid.DeletedParticleCountPerFrame;
            }

            thisHoleParticles = detector.DeletedParticleCountTotal;
            float framehole = detector.DeletedParticleCountPerFrame;
            FrameHoles.Add(framehole);
            totalHoleParticles += thisHoleParticles;
            singleHoleAllParticles[i] = thisHoleParticles;
            // We need to divide ground particles by 100 because the ground detector's volume is 100x bigger than the hole void detector's volume: ground_volume = 20*20*1; hole_volume = 20*20*0.1
            fractionScore.Add(Math.Min((groundParticles / 100) / holes, framehole) / ((groundParticles / 100) / holes) * (100.0f / holes));

            if (groundParticles < fluidHoleLimit && singleHoleAllParticles[i] > 100 && FrameHoles.Count(x => x > 0) == FrameHoles.Count)
            {
                tenperfectlist.Add(true);
            }
            else if (groundParticles > fluidHoleLimit || singleHoleAllParticles[i] < 100 || !(FrameHoles.Count(x => x > 0) == FrameHoles.Count))
            {
                tenperfectlist.Add(false);
            }
            if (tenperfectlist.Count == 15 && tenperfectlist.Count(x => x == true) == tenperfectlist.Count)
            {
                perfectShape = true;
                tenperfectlist = new List<bool>(15);
            }
            else if (tenperfectlist.Count == 15 && tenperfectlist.Count(x => x == true) != tenperfectlist.Count)
            {
                perfectShape = false;
                tenperfectlist = new List<bool>(15);
            }
        }
        totalWastedParticles = getEmitterParticles - groundParticles - totalHoleParticles;
        percentage_left_to_stop_sim = (totalParticles - getEmitterParticles) / totalParticles * 100.0f;
        //Debug.Log(perfectShape);
    }


    // SURFACE DATA //
    private DataTable SurfaceDataTable()
    {
        surface_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_surface";
        DataTable surfaceData = new DataTable { TableName = surface_tableName };

        if (!useHands && !physics)
        {
            if (!physics)
            {
                SphereCollider[] surface = clayContainer.GetComponentsInChildren<SphereCollider>();
                for (int s = 0; s < sphereNumber; s++)
                {
                    int id = surface[s].gameObject.GetInstanceID();
                    int header = SphereIDs[id];
                    surfaceData.Columns.Add(new DataColumn { ColumnName = "Sphere" + header.ToString(), DataType = typeof(Vector3) });  // create a column for each sphere in the material
                }
            }
        }
        else
        {
            Rigidbody[] surface = clayContainer.GetComponentsInChildren<Rigidbody>(); // has length of number of spheres in material
            for (int s = 0; s < sphereNumber; s++)
            {
                int id = surface[s].gameObject.GetInstanceID();
                int header = SphereIDs[id];
                surfaceData.Columns.Add(new DataColumn { ColumnName = "Sphere" + header.ToString(), DataType = typeof(Vector3) });  // create a column for each sphere in the material
            }
        }
        if (!useHands)
        {
            surfaceData.Columns.Add(new DataColumn { ColumnName = "MouseDrag", DataType = typeof(bool) });  // is mouse clicking on sphere
        }
        if (useHands)
        {
            surfaceData.Columns.Add(new DataColumn { ColumnName = "LTouch", DataType = typeof(bool) });   // is left hand touching sphere
            surfaceData.Columns.Add(new DataColumn { ColumnName = "RTouch", DataType = typeof(bool) });  // is right hand touching sphere
        }
        surfaceData.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });

        // Add 300 rows
        for (int i = 1; i <= rowsNumber; i++)
        {
            DataRow newRow = surfaceData.NewRow();
            surfaceData.Rows.Add(newRow);
        }

        return surfaceData;
    }
    private void SurfaceData()  // Save sphere positions at each frame //
    {
        int s = 0;
        if (!useHands)
        {
            if (!physics)
            {
                foreach (SphereCollider sphere in clayContainer.GetComponentsInChildren<SphereCollider>())
                {
                    surfaceData.Rows[rowCounter][s] = sphere.transform.position;
                    s++;
                }
            }
            if (physics)
            {
                foreach (Rigidbody sphere in clayContainer.GetComponentsInChildren<Rigidbody>())
                {
                    surfaceData.Rows[rowCounter][s] = sphere.transform.position;
                    s++;
                }
            }
            surfaceData.Rows[rowCounter][s] = drag;
        }
        if (useHands)
        {
            List<int> LHandSpheres = new List<int>();
            List<int> RHandSpheres = new List<int>();
            LHandTouch = false;
            RHandTouch = false;

            foreach (Rigidbody sphere in clayContainer.GetComponentsInChildren<Rigidbody>())
            {
                surfaceData.Rows[rowCounter][s] = sphere.transform.position;

                bool isLHandTouch = sphere.gameObject.GetComponent<OnCollision>().LHandTouch;
                bool isRHandTouch = sphere.gameObject.GetComponent<OnCollision>().RHandTouch;

                if (isLHandTouch)
                {
                    // Add current sphere
                    LHandSpheres.Add(SphereIDs[sphere.gameObject.GetInstanceID()]);
                    foreach (GameObject closebySphere in sphere.GetComponent<SurfaceInteractionPhysics>().ClosebySpheres)
                    {
                        // Add closeby spheres
                        if (!LHandSpheres.Contains(SphereIDs[closebySphere.GetInstanceID()]))
                        {
                            LHandSpheres.Add(SphereIDs[closebySphere.GetInstanceID()]);
                        }
                    }
                    LHandTouch = true;
                }
                if (isRHandTouch)
                {
                    // Add current sphere
                    RHandSpheres.Add(SphereIDs[sphere.gameObject.GetInstanceID()]);
                    //Debug.Log("sphereids" + SphereIDs[sphere.gameObject.GetInstanceID()]);
                    foreach (GameObject closebySphere in sphere.GetComponent<SurfaceInteractionPhysics>().ClosebySpheres)
                    {
                        // Add closeby spheres
                        if (!RHandSpheres.Contains(SphereIDs[closebySphere.GetInstanceID()]))
                        {
                            RHandSpheres.Add(SphereIDs[closebySphere.GetInstanceID()]);
                        }
                    }
                    RHandTouch = true;
                }
                s++;
            }

            string Lserialized = SerializeIntList(LHandSpheres);
            string Rserialized = SerializeIntList(RHandSpheres);

            // Debug.Log("rhands" + Rserialized);

            generalData.Rows[rowCounter][2] = Lserialized;
            generalData.Rows[rowCounter][3] = Rserialized;
            generalData.Rows[rowCounter][4] = LHandTouch;
            generalData.Rows[rowCounter][5] = RHandTouch;

            leftHandData.Rows[rowCounter][32] = LHandTouch;   // is left hand touching
            leftHandData.Rows[rowCounter][33] = RHandTouch;   // is right hand touching
            rightHandData.Rows[rowCounter][32] = LHandTouch;  // is left hand touching
            rightHandData.Rows[rowCounter][33] = RHandTouch;  // is right hand touching

            surfaceData.Rows[rowCounter][s] = LHandTouch;     // is left hand touching
            surfaceData.Rows[rowCounter][s + 1] = RHandTouch; // is right hand touching
        }
        surfaceData.Rows[rowCounter][surfaceData.Columns.Count - 1] = Time.time - startTime;
    }
    private Tuple<int, Vector3> GetDraggedSphere()
    {
        Dictionary<int, int> SphereIDs = gameObject.GetComponent<Create>().SphereIDs;

        Vector3 mousePoint = Input.mousePosition;
        Ray ray = Camera.main.ScreenPointToRay(mousePoint);
        lookingAt = ray.direction;

        // We check if the mouse was pressed during this frame
        if (Input.GetMouseButtonDown(0)) // mouse is pressed //
        {
            if (Physics.Raycast(ray, out RaycastHit hit))
            {
                // Update its status to "drag"
                if (hit.collider.gameObject.transform.IsChildOf(clayContainer.transform))
                {
                    drag = true; // mouse is being held //
                    sphereHit = hit.collider.gameObject;
                    sphereHitID = SphereIDs[sphereHit.GetInstanceID()];
                }
            }
        }
        if (sphereHitID != 0)
        {
            sphereHitPosition = sphereHit.transform.position;
        }
        // We check if the mouse was released
        if (Input.GetMouseButtonUp(0)) // mouse is released //
        {
            // And set its status to "not dragged"
            drag = false;
            sphereHitID = 0;
            sphereHitPosition = Vector3.zero;
        }

        return Tuple.Create(sphereHitID, sphereHitPosition);
    }
    static string SerializeIntList(List<int> list)
    {
        return string.Join(",", list);
    }


    // HANDS DATA //
    private DataTable HandDataTable(string tableName)
    {
        DataTable handData = new DataTable { TableName = tableName };

        handData.Columns.Add(new DataColumn { ColumnName = "PalmPosition", DataType = typeof(Vector3) });       // 0 done
        handData.Columns.Add(new DataColumn { ColumnName = "PalmNormal", DataType = typeof(Vector3) });         // 1 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbMetacarpal", DataType = typeof(Vector3) });    // 2 done
        handData.Columns.Add(new DataColumn { ColumnName = "IndexMetacarpal", DataType = typeof(Vector3) });    // 3 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleMetacarpal", DataType = typeof(Vector3) });   // 4 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingMetacarpal", DataType = typeof(Vector3) });     // 5 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyMetacarpal", DataType = typeof(Vector3) });    // 6 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbProximal", DataType = typeof(Vector3) });      // 7 done
        handData.Columns.Add(new DataColumn { ColumnName = "IndexProximal", DataType = typeof(Vector3) });      // 8 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleProximal", DataType = typeof(Vector3) });     // 9 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingProximal", DataType = typeof(Vector3) });       // 10 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyProximal", DataType = typeof(Vector3) });      // 11 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbIntermediate", DataType = typeof(Vector3) });  // 12 done
        handData.Columns.Add(new DataColumn { ColumnName = "IndexIntermediate", DataType = typeof(Vector3) });  // 13 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleIntermediate", DataType = typeof(Vector3) }); // 14 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingIntermediate", DataType = typeof(Vector3) });   // 15 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyIntermediate", DataType = typeof(Vector3) });  // 16 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbDistal", DataType = typeof(Vector3) });        // 17 done
        handData.Columns.Add(new DataColumn { ColumnName = "IndexDistal", DataType = typeof(Vector3) });        // 18 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleDistal", DataType = typeof(Vector3) });       // 19 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingDistal", DataType = typeof(Vector3) });         // 20 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyDistal", DataType = typeof(Vector3) });        // 21 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbTipPosition", DataType = typeof(Vector3) });   // 22 done
        handData.Columns.Add(new DataColumn { ColumnName = "IndexTipPosition", DataType = typeof(Vector3) });   // 23 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleTipPosition", DataType = typeof(Vector3) });  // 24 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingTipPosition", DataType = typeof(Vector3) });    // 25 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyTipPosition", DataType = typeof(Vector3) });   // 26 done

        handData.Columns.Add(new DataColumn { ColumnName = "ThumbDirection", DataType = typeof(Vector3) });     // 27 done        
        handData.Columns.Add(new DataColumn { ColumnName = "IndexDirection", DataType = typeof(Vector3) });     // 28 done
        handData.Columns.Add(new DataColumn { ColumnName = "MiddleDirection", DataType = typeof(Vector3) });    // 29 done
        handData.Columns.Add(new DataColumn { ColumnName = "RingDirection", DataType = typeof(Vector3) });      // 30 done
        handData.Columns.Add(new DataColumn { ColumnName = "PinkyDirection", DataType = typeof(Vector3) });     // 31 done

        handData.Columns.Add(new DataColumn { ColumnName = "LTouch", DataType = typeof(bool) });              // is left hand touching sphere
        handData.Columns.Add(new DataColumn { ColumnName = "RTouch", DataType = typeof(bool) });             // is right hand touching sphere
        handData.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });            // 34 done

        // Add 300 rows
        for (int i = 1; i <= rowsNumber; i++)
        {
            DataRow newRow = handData.NewRow();
            handData.Rows.Add(newRow);
        }

        return handData;
    }
    private void HandData(Hand hand, DataTable handData)
    {

        Finger thumb = hand.GetThumb();
        Finger index = hand.GetIndex();
        Finger middle = hand.GetMiddle();
        Finger ring = hand.GetRing();
        Finger pinky = hand.GetPinky();

        handData.Rows[rowCounter][0] = hand.PalmPosition;
        handData.Rows[rowCounter][1] = hand.PalmNormal;

        handData.Rows[rowCounter][2] = thumb.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        handData.Rows[rowCounter][3] = index.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        handData.Rows[rowCounter][4] = middle.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        handData.Rows[rowCounter][5] = ring.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        handData.Rows[rowCounter][6] = pinky.Bone(Bone.BoneType.TYPE_METACARPAL).Center;

        handData.Rows[rowCounter][7] = thumb.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        handData.Rows[rowCounter][8] = index.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        handData.Rows[rowCounter][9] = middle.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        handData.Rows[rowCounter][10] = ring.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        handData.Rows[rowCounter][11] = pinky.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;

        handData.Rows[rowCounter][12] = thumb.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        handData.Rows[rowCounter][13] = index.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        handData.Rows[rowCounter][14] = middle.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        handData.Rows[rowCounter][15] = ring.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        handData.Rows[rowCounter][16] = pinky.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;

        handData.Rows[rowCounter][17] = thumb.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        handData.Rows[rowCounter][18] = index.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        handData.Rows[rowCounter][19] = middle.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        handData.Rows[rowCounter][20] = ring.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        handData.Rows[rowCounter][21] = pinky.Bone(Bone.BoneType.TYPE_DISTAL).Center;

        handData.Rows[rowCounter][22] = thumb.TipPosition;
        handData.Rows[rowCounter][23] = index.TipPosition;
        handData.Rows[rowCounter][24] = middle.TipPosition;
        handData.Rows[rowCounter][25] = ring.TipPosition;
        handData.Rows[rowCounter][26] = pinky.TipPosition;

        handData.Rows[rowCounter][27] = thumb.Direction;
        handData.Rows[rowCounter][28] = index.Direction;
        handData.Rows[rowCounter][29] = middle.Direction;
        handData.Rows[rowCounter][30] = ring.Direction;
        handData.Rows[rowCounter][31] = pinky.Direction;

        handData.Rows[rowCounter][34] = Time.time - startTime; // Current timestamp
    }
    private void BlankFrame(DataTable dataTable)
    {
        for (int i = 0; i < dataTable.Columns.Count - 3; i++)
        {
            Debug.Log(i);
            dataTable.Rows[rowCounter][i] = Vector3.zero;
        }
        dataTable.Rows[rowCounter][32] = LHandTouch; // is left hand touching
        dataTable.Rows[rowCounter][33] = RHandTouch; // is right hand touching
        dataTable.Rows[rowCounter][34] = Time.time - startTime; // Current timestamp
    }
    private void HandTracking() // If hands are being tracked, save hand data //
    {

        // add collision with spheres///

        if (leapProvider.CurrentFrame.Hands.Count == 0)
        {
            isLeftHand = false;
            isRightHand = false;
            BlankFrame(dataTable: leftHandData);
            BlankFrame(dataTable: rightHandData);
        }

        Debug.Log(leapProvider.CurrentFrame.Hands.Count);
        for (int i = 0; i < leapProvider.CurrentFrame.Hands.Count; i++)
        {
            Hand _hand = leapProvider.CurrentFrame.Hands[i];

            if (_hand.IsLeft && leapProvider.CurrentFrame.Hands.Count == 1)
            {
                isLeftHand = true;
                isRightHand = false;
                HandData(hand: _hand, handData: leftHandData);
                BlankFrame(dataTable: rightHandData);
                //Debug.Log("left");
            }
            if (_hand.IsRight && leapProvider.CurrentFrame.Hands.Count == 1)
            {
                isRightHand = true;
                isLeftHand = false;
                HandData(hand: _hand, handData: rightHandData);
                BlankFrame(dataTable: leftHandData);
                //Debug.Log("right");
            }
            if (_hand.IsLeft && leapProvider.CurrentFrame.Hands.Count == 2)
            {
                isLeftHand = true;
                isRightHand = true;
                HandData(hand: _hand, handData: leftHandData);
                //Debug.Log("left");
            }
            if (_hand.IsRight && leapProvider.CurrentFrame.Hands.Count == 2)
            {
                isRightHand = true;
                isLeftHand = true;
                HandData(hand: _hand, handData: rightHandData);
                // Debug.Log("right");
            }
        }
    }


















    private void PrintData()
    {
        flow.text = "Flow left: " + Math.Max(0, Math.Round(percentage_left_to_stop_sim)).ToString() + "/100 ";
        float currentscore = Mathf.Round(Score());
        //fiveframelist.Add(currentscore);
        //if (Math.Round(Score()) % 20 == 0) //20
        //{
        //score.text = "Shape: " + Math.Round(Score()).ToString() + "/100";
        //}
        //if (fiveframelist.Count(x => x == currentscore) == fiveframelist.Count)// && (currentscore % 3 == 0))//Math.Abs(lastscore - currentscore) < 5 )
        //{
        //score.text = "Shape: " + Math.Round(Score()).ToString() + "/100";
        //fiveframelist = new List<float>(20);
        //}
        //lastscore = Mathf.Round(Score());

        best.text = "Fluid: " + Math.Round(totalHoleParticles / 100).ToString();
        if (percentage_left_to_stop_sim <= 0)
        {
            liquidContainer.GetComponentInChildren<ZibraLiquidEmitter>().enabled = false;
        }
    }

    private float Score()
    {
        float finalScore = 0;

        foreach (float i in fractionScore)
        {
            finalScore += i;
        }
        if (float.IsNaN(finalScore))
        {
            finalScore = 0;
        }
        return finalScore; //finalscore
    }

    private void GetCompleteGoal()
    {
        if (Score() < 90)
        {
            score_counter = 0;
        }
        if (Score() >= 90)
        {
            score_counter += Score();

            if (score_counter >= 10 * 90)
            {
                holeColor.GetComponent<MeshRenderer>().material.color = new Color(0f, 0.4f, 0f, 1f);  // change ground color
                emitterContainer.GetComponent<ZibraLiquidEmitter>().enabled = false; // disable liquid emitter      
            }
        }
    }


    private void OnApplicationQuit()
    {
        // Create information.txt file
        string path = @"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_";
        string txtFile = path + subjectNumber.ToString() + "/information.txt";

        System.IO.Directory.CreateDirectory(path + subjectNumber.ToString());

        if (!File.Exists(txtFile))
        {
            using (StreamWriter sw = File.CreateText(txtFile))
            {
                sw.WriteLine("Trial Holes Flows TotalParticles(Create.cs) Hands");
            }
        }

        if (emptyTrial)
        {
            holes = 0;
            flows = 0;
            totalParticles = 0;
            // Save empty trial data
            SaveData(emptyTrial: true, path: path, idx: "empty");
        }
        if (!emptyTrial)
        {
            // Start trial number at 1
            int idx = 1;

            while (File.Exists(path + subjectNumber.ToString() + @"\" + general_tableName + "_" + idx.ToString()))
            {
                idx += 1;
            }
            // Save normal trial data
            SaveData(emptyTrial: false, path: path, idx: idx.ToString());

            if (File.Exists(txtFile))
            {
                using (StreamWriter sw = File.AppendText(txtFile))
                {
                    // Add row to information.txt file
                    sw.WriteLine(idx.ToString() + " " + holes.ToString() + " " + flows.ToString() + " " + totalParticles.ToString() + " " + useHands.ToString());
                }
            }
        }

        start = false;
    }


    private void SaveData(bool emptyTrial, string path, string idx)
    {

        if (!emptyTrial)
        {
            //SaveDataTableToExcel(generalData, path + subjectNumber.ToString() + @"\" + general_tableName + "_" + idx.ToString());
            //SaveDataTableToExcel(fluidData, path + subjectNumber.ToString() + @"\" + fluid_tableName + "_" + idx.ToString());
            generalData.WriteXml(path + subjectNumber.ToString() + @"\" + general_tableName + "_" + idx.ToString());
            fluidData.WriteXml(path + subjectNumber.ToString() + @"\" + fluid_tableName + "_" + idx.ToString());
        }
        //SaveDataTableToExcel(surfaceData, path + subjectNumber.ToString() + @"\" + surface_tableName + "_" + idx.ToString());
        //surfaceData.WriteXml(path + subjectNumber.ToString() + @"\" + surface_tableName + "_" + idx.ToString());
        surfaceData.WriteXml(path + subjectNumber.ToString() + @"\" + surface_tableName + "_" + idx.ToString());


        if (useHands)
        {
            //SaveDataTableToExcel(leftHandData, path + subjectNumber.ToString() + @"\" + leftHand_tableName.ToString() + "_" + idx.ToString());
            //SaveDataTableToExcel(rightHandData, path + subjectNumber.ToString() + @"\" + rightHand_tableName.ToString() + "_" + idx.ToString());
            leftHandData.WriteXml(path + subjectNumber.ToString() + @"\" + leftHand_tableName.ToString() + "_" + idx.ToString());
            rightHandData.WriteXml(path + subjectNumber.ToString() + @"\" + rightHand_tableName.ToString() + "_" + idx.ToString());
        }
    }
    static void SaveDataTableToExcel(DataTable dataTable, string filePath)
    {
        // Create a StreamWriter to write to the CSV file
        using (StreamWriter writer = new StreamWriter(filePath))
        {
            // Write the column headers
            foreach (DataColumn column in dataTable.Columns)
            {
                writer.Write(column.ColumnName);
                if (column.Ordinal < dataTable.Columns.Count - 1)
                    writer.Write(",");
            }
            writer.WriteLine();

            // Write the data
            foreach (DataRow row in dataTable.Rows)
            {
                for (int i = 0; i < dataTable.Columns.Count; i++)
                {
                    writer.Write(row[i].ToString());
                    if (i < dataTable.Columns.Count - 1)
                        writer.Write(",");
                }
                writer.WriteLine();
            }
        }
    }

}


