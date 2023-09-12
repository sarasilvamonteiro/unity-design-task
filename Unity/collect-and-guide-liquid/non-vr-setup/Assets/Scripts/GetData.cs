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
    
    [System.NonSerialized]
    public LeapProvider leapProvider;
    [System.NonSerialized]
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
    private DataTable sphereData;
    private DataTable leftHandData;
    private DataTable rightHandData;
    private string tableName;
    private string sphere_tableName;
    private string leftHand_tableName;
    private string rightHand_tableName;

    private GameObject sphereHit;
    private int sphereID;
    private Vector3 sphereLastPosition;
    private Vector3 sphereMove;
    private int holes;
    private int flows;
    
    // Fluid data:
    private float totalParticles;
    private float totalEmittedParticles;
    private float totalHoleParticles;
    private float thisHoleParticles;
    private float groundParticles;
    private float totalWastedParticles;
    private float getEmitterParticles;
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
    

    // Conditions:
    private bool start;
    private float startTime;
    private bool running;
    private bool useHands; 
    private bool drag;
    private bool isLeftHand;
    private bool isRightHand;
    private bool fastForward;
    


    void Start()
    {
        start = false;
        drag = false;
        fastForward = false;
        running = false;


    }
    void FixedUpdate()
    {

        if (gameObject.GetComponent<Create>().start)
        {
            InitializeObjects();
            gameObject.GetComponent<Create>().start = false;
        }

        if (running)
        {

            if (useHands)
            {
                HandTracking();
            }

            SphereData();
            CountParticles();
            GeneralData();


            if (gameObject.GetComponent<Create>().running == true)
            {
                PrintData();
            }
            


            
            //GetCompleteGoal();

        }

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

        holes = gameObject.GetComponent<Create>().holes;
        flows = gameObject.GetComponent<Create>().flows;
        useHands = gameObject.GetComponent<Create>().useHands;

        // Fluid:
        totalParticles = gameObject.GetComponent<Create>().totalParticles;
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

        // Containers:
        personController = GameObject.FindGameObjectWithTag("Player");
        clayContainer = gameObject.GetComponent<Create>().clayContainer;
        emitterContainer = gameObject.GetComponent<Create>().emitterContainer;
        groundContainer = gameObject.GetComponent<Create>().groundContainer;
        liquidContainer = gameObject.GetComponent<Create>().liquidContainer;

        //holeColor = groundContainer.GetComponentInChildren<CapsuleCollider>().gameObject;

        generalData = CreateGeneralTable();
        sphereData = CreateSphereTable();

        if (useHands)
        {
            leftHand_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_left_hand_data";
            rightHand_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_right_hand_data";
            
            leftHandData = CreateHandTable(tableName: leftHand_tableName);
            rightHandData = CreateHandTable(tableName: rightHand_tableName);
        }



        //SaveInitialPositions();

    }


    private void HandTracking()
    {

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
                HandData(hand: _hand, dataTable: leftHandData);
                BlankFrame(dataTable: rightHandData);
                Debug.Log("left");
            }
            if (_hand.IsRight && leapProvider.CurrentFrame.Hands.Count == 1)
            {
                isRightHand = true;
                isLeftHand = false;
                HandData(hand: _hand, dataTable: rightHandData);
                BlankFrame(dataTable: leftHandData);
                Debug.Log("right");
            }
            if (_hand.IsLeft && leapProvider.CurrentFrame.Hands.Count == 2)
            {
                isLeftHand = true;
                isRightHand = true;
                HandData(hand: _hand, dataTable: leftHandData);
                Debug.Log("left");
            }
            if (_hand.IsRight && leapProvider.CurrentFrame.Hands.Count == 2)
            {
                isRightHand = true;
                isLeftHand = true;
                HandData(hand: _hand, dataTable: rightHandData);
                Debug.Log("right");

            }

        }
    }

    private void SaveInitialPositions()
    {

        Dictionary<int, int> SphereIDs = gameObject.GetComponent<Create>().SphereIDs;

        string tableName = "initial_positions";

        DataTable initialPositions = new DataTable { TableName = tableName };

        initialPositions.Columns.Add(new DataColumn { ColumnName = "ID", DataType = typeof(string) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "Position", DataType = typeof(Vector3) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "AgentLookingAt", DataType = typeof(Vector3) });
        initialPositions.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });

        DataRow generalRow = initialPositions.NewRow();

        generalRow[0] = "Agent";
        generalRow[1] = personController.transform.position; // Player position
        generalRow[2] = new Vector3(personController.transform.GetChild(0).transform.eulerAngles.x, personController.transform.eulerAngles.y, 0); // Player rotation
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


    //// Create DataTables ////
    ///
    private DataTable CreateGeneralTable()
    {

        tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_general";
        DataTable Data = new DataTable { TableName = tableName };

        Data.Columns.Add(new DataColumn { ColumnName = "AgentPosition", DataType = typeof(Vector3) });  // 0 done
        Data.Columns.Add(new DataColumn { ColumnName = "AgentLookingAt", DataType = typeof(Vector3) }); // 1 done   
        Data.Columns.Add(new DataColumn { ColumnName = "SphereID", DataType = typeof(int) });           // 2 done
        Data.Columns.Add(new DataColumn { ColumnName = "SpherePosition", DataType = typeof(Vector3) }); // 3 done
        Data.Columns.Add(new DataColumn { ColumnName = "SphereMove", DataType = typeof(Vector3) });     // 4 done
        Data.Columns.Add(new DataColumn { ColumnName = "FluidEmitted", DataType = typeof(int) });       // 5 done
        Data.Columns.Add(new DataColumn { ColumnName = "FluidInHole", DataType = typeof(Vector3) });    // 6 done
        Data.Columns.Add(new DataColumn { ColumnName = "FluidInGround", DataType = typeof(int) });      // 7 done
        Data.Columns.Add(new DataColumn { ColumnName = "FluidWasted", DataType = typeof(int) });        // 8 done
        Data.Columns.Add(new DataColumn { ColumnName = "FluidLeft", DataType = typeof(int) });          // 9 done total particles - emitted particles
        Data.Columns.Add(new DataColumn { ColumnName = "ShapeScore", DataType = typeof(bool) }); //float// 10 done
        //Data.Columns.Add(new DataColumn { ColumnName = "FastForward", DataType = typeof(bool) });       
        Data.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });        // 11 done
        if (!useHands)
        {
            Data.Columns.Add(new DataColumn { ColumnName = "MouseDrag", DataType = typeof(bool) });     // 12 done
        }
        if (useHands)
        {
            Data.Columns.Add(new DataColumn { ColumnName = "LeftHand", DataType = typeof(bool) });      // 12 done
            Data.Columns.Add(new DataColumn { ColumnName = "RightHand", DataType = typeof(bool) });     // 13 done
        }
        // add handtouching ?

        return Data;
    }

    private DataTable CreateSphereTable()
    {

        sphere_tableName = holes.ToString() + "_holes_" + flows.ToString() + "_flows_sphere_position";
        DataTable Data = new DataTable { TableName = sphere_tableName };

        Dictionary<int, int> SphereIDs = gameObject.GetComponent<Create>().SphereIDs;
        SphereCollider[] sphere = clayContainer.GetComponentsInChildren<SphereCollider>(); // has length of number of spheres in material

        for (int s = 0; s < sphere.Length; s++)
        {

            int id = sphere[s].gameObject.GetInstanceID();
            int header = SphereIDs[id];

            Data.Columns.Add(new DataColumn { ColumnName = "Sphere" + header.ToString(), DataType = typeof(Vector3) });  // create a column for each sphere in the material
        }

        Data.Columns.Add(new DataColumn { ColumnName = "SphereDragged", DataType = typeof(int) });
        Data.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });
        Data.Columns.Add(new DataColumn { ColumnName = "MouseDrag", DataType = typeof(bool) });

        return Data;
    }

    private DataTable CreateHandTable(string tableName)
    {

        DataTable Data = new DataTable { TableName = tableName };

        Data.Columns.Add(new DataColumn { ColumnName = "PalmPosition", DataType = typeof(Vector3) });       // 0 done
        Data.Columns.Add(new DataColumn { ColumnName = "PalmNormal", DataType = typeof(Vector3) });         // 1 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbMetacarpal", DataType = typeof(Vector3) });    // 2 done
        Data.Columns.Add(new DataColumn { ColumnName = "IndexMetacarpal", DataType = typeof(Vector3) });    // 3 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleMetacarpal", DataType = typeof(Vector3) });   // 4 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingMetacarpal", DataType = typeof(Vector3) });     // 5 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyMetacarpal", DataType = typeof(Vector3) });    // 6 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbProximal", DataType = typeof(Vector3) });      // 7 done
        Data.Columns.Add(new DataColumn { ColumnName = "IndexProximal", DataType = typeof(Vector3) });      // 8 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleProximal", DataType = typeof(Vector3) });     // 9 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingProximal", DataType = typeof(Vector3) });       // 10 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyProximal", DataType = typeof(Vector3) });      // 11 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbIntermediate", DataType = typeof(Vector3) });  // 12 done
        Data.Columns.Add(new DataColumn { ColumnName = "IndexIntermediate", DataType = typeof(Vector3) });  // 13 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleIntermediate", DataType = typeof(Vector3) }); // 14 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingIntermediate", DataType = typeof(Vector3) });   // 15 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyIntermediate", DataType = typeof(Vector3) });  // 16 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbDistal", DataType = typeof(Vector3) });        // 17 done
        Data.Columns.Add(new DataColumn { ColumnName = "IndexDistal", DataType = typeof(Vector3) });        // 18 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleDistal", DataType = typeof(Vector3) });       // 19 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingDistal", DataType = typeof(Vector3) });         // 20 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyDistal", DataType = typeof(Vector3) });        // 21 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbTipPosition", DataType = typeof(Vector3) });   // 22 done
        Data.Columns.Add(new DataColumn { ColumnName = "IndexTipPosition", DataType = typeof(Vector3) });   // 23 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleTipPosition", DataType = typeof(Vector3) });  // 24 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingTipPosition", DataType = typeof(Vector3) });    // 25 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyTipPosition", DataType = typeof(Vector3) });   // 26 done

        Data.Columns.Add(new DataColumn { ColumnName = "ThumbDirection", DataType = typeof(Vector3) });     // 27 done        
        Data.Columns.Add(new DataColumn { ColumnName = "IndexDirection", DataType = typeof(Vector3) });     // 28 done
        Data.Columns.Add(new DataColumn { ColumnName = "MiddleDirection", DataType = typeof(Vector3) });    // 29 done
        Data.Columns.Add(new DataColumn { ColumnName = "RingDirection", DataType = typeof(Vector3) });      // 30 done
        Data.Columns.Add(new DataColumn { ColumnName = "PinkyDirection", DataType = typeof(Vector3) });     // 31 done

        Data.Columns.Add(new DataColumn { ColumnName = "Timestamp", DataType = typeof(float) });            // 32 done

        return Data;

    }
    ////
    
    //// Get Data ////
    private Tuple<int, Vector3, Vector3> GetDraggedIDPositionMove()
    {

        Dictionary<int, int> SphereIDs = gameObject.GetComponent<Create>().SphereIDs;

        Vector3 mousePoint = Input.mousePosition;
        Ray ray = Camera.main.ScreenPointToRay(mousePoint);

        if (Input.GetMouseButtonDown(0)) // mouse is pressed //
        {
            if (Physics.Raycast(ray, out RaycastHit hit))
            {
                if (hit.collider.gameObject.transform.IsChildOf(clayContainer.transform))
                {
                    drag = true;

                    sphereHit = hit.collider.gameObject;
                    sphereID = SphereIDs[sphereHit.GetInstanceID()];
                    sphereLastPosition = sphereHit.transform.position; // initial position of sphere being dragged

                }
            }
        }

        if (Input.GetMouseButtonUp(0)) // mouse is released //
        {
            drag = false;
            sphereID = 0;
            sphereLastPosition = Vector3.zero;
            sphereMove = Vector3.zero;

        }

        if (drag) // mouse is being held //
        {
            Vector3 sphereCurrentPosition = sphereHit.transform.position;

            if (sphereCurrentPosition != sphereLastPosition)
            {
                sphereMove = sphereCurrentPosition - sphereLastPosition; // DATA: move vector in each frame (vector distance between each drag, per frame)
            }

            sphereLastPosition = sphereCurrentPosition; // updates last position

        }

        return Tuple.Create(sphereID, sphereLastPosition, sphereMove);
    }


    private Tuple<Vector3, Vector3> GetSpherePositionPerID(int id)
    {

        Vector3 mousePoint = Input.mousePosition;
        Ray ray = Camera.main.ScreenPointToRay(mousePoint);

        // you have instance id of desired sphere.
        // how to get its position from the instance id??
        Vector3 spherePosition = Vector3.zero;

        foreach (SphereCollider sphere in clayContainer.GetComponentsInChildren<SphereCollider>())
        {

            if (sphere.gameObject.GetInstanceID() == id)
            {

                spherePosition = sphere.gameObject.transform.position;

                if (Input.GetMouseButtonDown(0)) // mouse is pressed //
                {
                    if (Physics.Raycast(ray, out RaycastHit hit))
                    {

                        if (hit.collider.gameObject.transform.IsChildOf(clayContainer.transform))
                        {
                            drag = true;  // mouse is pressed //                           
                        }
                    }

                    sphereLastPosition = sphere.gameObject.transform.position;
                }

                if (drag)
                {

                    Vector3 sphereCurrentPosition = sphere.gameObject.transform.position;

                    if (sphereCurrentPosition != sphereLastPosition)
                    {
                        sphereMove = sphereCurrentPosition - sphereLastPosition; // DATA: move vector in each frame (vector distance between each drag, per frame)
                    }

                    sphereLastPosition = sphereCurrentPosition; // updates last position
                    spherePosition = sphereLastPosition;

                }

                if (Input.GetMouseButtonUp(0)) // mouse is released //
                {

                    drag = false;
                    sphereLastPosition = Vector3.zero;
                    sphereMove = Vector3.zero;

                }
            }
        }

        return Tuple.Create(spherePosition, sphereMove);

    }


    private void CountParticles()
    {
        
        getEmitterParticles = 0;
        

        foreach (ZibraLiquidEmitter emitter in emitterContainer.GetComponentsInChildren<ZibraLiquidEmitter>())
        {
            getEmitterParticles += emitter.CreatedParticlesTotal; // current particles per frame from the emitters
        }

        // Try voids:     
        fractionScore = new List<float>();
        List<float> FrameHoles = new List<float>();
        totalHoleParticles = 0;

        groundParticles = groundContainer.GetComponentInChildren<ZibraLiquidDetector>().ParticlesInside;

        for (int i = 0; i<holes; i++)
        {
            
            ZibraLiquidVoid detector = groundContainer.GetComponentsInChildren<ZibraLiquidVoid>()[i];

            totalWastedParticles = 0;
            float framewaste = 0;

            for (int v = holes; v < holes+3; v++)
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
            fractionScore.Add(Math.Min((groundParticles/100) / holes, framehole) / ((groundParticles/100) / holes) * (100.0f / holes));
            
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
        
        
        Debug.Log(perfectShape);
    }



    private void GeneralData()
    {

        DataRow row = generalData.NewRow();

        // Player:
        row[0] = personController.transform.position;// Player position
        row[1] = new Vector3(personController.transform.GetChild(0).transform.eulerAngles.x, personController.transform.eulerAngles.y, 0); // Player rotation
        // Object:
        row[2] = GetDraggedIDPositionMove().Item1;   // Sphere being dragged ID
        row[3] = GetDraggedIDPositionMove().Item2;   // Sphere position
        row[4] = GetDraggedIDPositionMove().Item3;   // Sphere move
        // Fluid:
        row[5] = getEmitterParticles;                // Total emitted particles  // totalEmittedParticles or getemitterparticles      
        row[6] = singleHoleAllParticles;             // Total in hole
        row[7] = groundParticles;                    // Current in ground
        row[8] = totalWastedParticles;               // Total wasted
        row[9] = percentage_left_to_stop_sim;        // Percentage flow left
        // Data:
        row[10] = perfectShape; //Score();                           // Score percentage
        //row[11] = fastForward;                     // is it fastforward
        row[11] = Time.time - startTime;             // Current timestamp
        if (!useHands)
        {
            row[12] = drag;                          // is it dragging, for debug
        }
        // Hands:
        if (useHands)
        {
            row[12] = isLeftHand;
            row[13] = isRightHand;
        }

        generalData.Rows.Add(row);
    }

    private void SphereData()
    {

        DataRow position_row = sphereData.NewRow();
        SphereCollider[] sphere = clayContainer.GetComponentsInChildren<SphereCollider>(); // has length of number of spheres in material

        for (int s = 0; s < sphere.Length; s++)
        {

            int id = sphere[s].gameObject.GetInstanceID();

            position_row[s] = GetSpherePositionPerID(id).Item1;

        }

        position_row[sphere.Length] = GetDraggedIDPositionMove().Item1;
        position_row[sphere.Length + 1] = Time.time - startTime;
        position_row[sphere.Length + 2] = drag;

        sphereData.Rows.Add(position_row);

    }

    private void HandData(Hand hand, DataTable dataTable)
    {

        DataRow row = dataTable.NewRow();

        Finger thumb = hand.GetThumb();
        Finger index = hand.GetIndex();
        Finger middle = hand.GetMiddle();
        Finger ring = hand.GetRing();
        Finger pinky = hand.GetPinky();
        
        //Debug.Log(hand.PalmPosition);

        row[0] = hand.PalmPosition;
        row[1] = hand.PalmNormal;

        row[2] = thumb.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        row[3] = index.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        row[4] = middle.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        row[5] = ring.Bone(Bone.BoneType.TYPE_METACARPAL).Center;
        row[6] = pinky.Bone(Bone.BoneType.TYPE_METACARPAL).Center;

        row[7] = thumb.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        row[8] = index.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        row[9] = middle.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        row[10] = ring.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;
        row[11] = pinky.Bone(Bone.BoneType.TYPE_PROXIMAL).Center;

        row[12] = thumb.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        row[13] = index.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        row[14] = middle.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        row[15] = ring.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;
        row[16] = pinky.Bone(Bone.BoneType.TYPE_INTERMEDIATE).Center;

        row[17] = thumb.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        row[18] = index.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        row[19] = middle.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        row[20] = ring.Bone(Bone.BoneType.TYPE_DISTAL).Center;
        row[21] = pinky.Bone(Bone.BoneType.TYPE_DISTAL).Center;

        row[22] = thumb.TipPosition;
        row[23] = index.TipPosition;
        row[24] = middle.TipPosition;
        row[25] = ring.TipPosition;
        row[26] = pinky.TipPosition;

        row[27] = thumb.Direction;
        row[28] = index.Direction;
        row[29] = middle.Direction;
        row[30] = ring.Direction;
        row[31] = pinky.Direction;

        row[32] = Time.time - startTime; // Current timestamp

        dataTable.Rows.Add(row);


    }

    private void BlankFrame(DataTable dataTable)
    {

        DataRow row = dataTable.NewRow();

        for (int i = 0; i < 32; i++)
        {
            row[i] = Vector3.zero;
        }

        row[32] = Time.time - startTime; // Current timestamp

        dataTable.Rows.Add(row);

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
           // score.text = "Shape: " + Math.Round(Score()).ToString() + "/100";
            //fiveframelist = new List<float>(20);
       // }
        
        //lastscore = Mathf.Round(Score());



        best.text = "Fluid: " + Math.Round(totalHoleParticles/100).ToString();

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

        string path = @"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_";
        string txtFile = path + subjectNumber.ToString() + "/information.txt";

        System.IO.Directory.CreateDirectory(path + subjectNumber.ToString());

        if (!File.Exists(txtFile))
        {
            using (StreamWriter sw = File.CreateText(txtFile))
            {
                sw.WriteLine("Holes Flows TotalParticles(Create.cs)");
            }
        }

        int idx = 0;

        while (File.Exists(path + subjectNumber.ToString() + @"\" + tableName + "_" + idx.ToString()))
        {

            idx += 1;

        }


        generalData.WriteXml(path + subjectNumber.ToString() + @"\" + tableName + "_" + idx.ToString());
        sphereData.WriteXml(path + subjectNumber.ToString() + @"\" + sphere_tableName + "_" + idx.ToString());

        if (useHands)
        {
            leftHandData.WriteXml(path + subjectNumber.ToString() + @"\" + leftHand_tableName.ToString() + "_" + idx.ToString());
            rightHandData.WriteXml(path + subjectNumber.ToString() + @"\" + rightHand_tableName.ToString() + "_" + idx.ToString());

        }



        if (File.Exists(txtFile))
        {
            using (StreamWriter sw = File.AppendText(txtFile))
            {
                sw.WriteLine(holes.ToString() + " " + flows.ToString() + " " + totalParticles.ToString() + " " + useHands.ToString());
            }
        }

        start = false;
    }


}
