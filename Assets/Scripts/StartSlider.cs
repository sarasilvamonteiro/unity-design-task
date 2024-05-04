using UnityEngine;
using UnityEngine.UI;
using System;



public class StartSlider : MonoBehaviour
{
    
    //[System.NonSerialized]
    public int number;

    private Text sliderText;

    private GameObject addButton;
    private GameObject removeButton;

    // mouse position variables
    private Vector3 mOffset;
    private float mZCoord;

    private void Start()
    {
        number = 1;
        sliderText = gameObject.GetComponentInChildren<Text>();

        addButton = gameObject.GetComponentInChildren<SphereCollider>().gameObject;
        removeButton = gameObject.GetComponentInChildren<BoxCollider>().gameObject;

    } 

    private void Update()
    {
        Vector3 mousePoint = Input.mousePosition;
        Ray ray = Camera.main.ScreenPointToRay(mousePoint);

        if (Physics.Raycast(ray, out RaycastHit hit))
        {

            if (hit.collider.gameObject == addButton)
            {

                if (Input.GetMouseButtonDown(0))
                {
                    gameObject.GetComponent<Slider>().value += 1;
                }
            }

            if (hit.collider.gameObject == removeButton)
            {

                if (Input.GetMouseButtonDown(0))
                {
                    gameObject.GetComponent<Slider>().value -= 1;
                }
            }

        }
    }

    public void OnSliderChanged(float value)
    {
        number = (int)value;
        sliderText.text = value.ToString();
    }


}
