using UnityEngine;



public class FirstPersonLook : MonoBehaviour
{
    [SerializeField]
    Transform character;
    public float sensitivity = 2;
    public float smoothing = 1.5f;

    Vector2 velocity;
    Vector2 frameVelocity;

    


    void Reset()
    {
        // Get the character from the FirstPersonMovement in parents.
        character = GetComponentInParent<FirstPersonMovement>().transform;
    }

    void Start()
    {
        
        // Lock the mouse cursor to the game screen.
        Cursor.lockState = CursorLockMode.Locked; 
        Cursor.visible = true;        
      
    }

    void Update()
    {
        NonPhysicsCursor();

        // Get smooth velocity.
        Vector2 mouseDelta = new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y"));
        Vector2 rawFrameVelocity = Vector2.Scale(mouseDelta, Vector2.one * sensitivity);
        frameVelocity = Vector2.Lerp(frameVelocity, rawFrameVelocity, 1 / smoothing);
        velocity += frameVelocity;
        velocity.y = Mathf.Clamp(velocity.y, -90, 90);

        // Rotate camera up-down and controller left-right from velocity.
        transform.localRotation = Quaternion.AngleAxis(-velocity.y, Vector3.right);
        character.localRotation = Quaternion.AngleAxis(velocity.x, Vector3.up);

    }

    private void PhysicsCursor()
    {
        Cursor.visible = true;

        if (Input.GetMouseButtonDown(0))
        {
            Cursor.lockState = CursorLockMode.Confined;
            Cursor.visible = false;
            sensitivity = 0.04f; //0.1 // 0.3
        }

        if (Input.GetMouseButton(0))
        {
            Cursor.lockState = CursorLockMode.Confined;
            Cursor.visible = false;

            sensitivity = 0.04f; //0.1 // 0.3
        }

        if (Input.GetMouseButtonUp(0))
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
            sensitivity = 0.7f; //2
        }
    }

    private void NonPhysicsCursor()
    {

        if (Input.GetMouseButtonDown(0))
        {
            Cursor.visible = false;
            sensitivity = 0.1f; //0.1 // 0.3
        }

        if (Input.GetMouseButtonUp(0))
        {
            Cursor.visible = true;
            sensitivity = 0.8f; //2
        }
    }
}
