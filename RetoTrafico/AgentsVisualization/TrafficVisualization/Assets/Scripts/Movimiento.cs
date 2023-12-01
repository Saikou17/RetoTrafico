using System.Collections;
using System.Collections.Generic;
using UnityEngine;



public class Movimiento : MonoBehaviour
{
    
    //Creamos los parametros de nuestro movimiento
    public GameObject llanta;

    [Header("Escalado:")]
    [SerializeField] float scale; // Escalado en x
    
    [Header("Angulo de rotación:")]
    [SerializeField] float angle; // Angulo de rotacion
    [Header("Eje de rotación:")]
    [SerializeField] AXIS rotationAxis;// Eje de rotacion
    [Header("Velocidad de rotación:")]
    [SerializeField] float spinAngle;

    [Header("Interpolación:")]
    [SerializeField] Vector3 startPosition; // Posicion inicial
    [SerializeField] Vector3 endPosition; // Posicion final
    //float timeAngle = 0f;
    private Vector3 previousInterpolation = Vector3.zero;
    //Creamos y guardamos los elementos del carro
    Mesh carMesh;// Malla del modelo del carro
    Vector3[] carBaseVertices; //Vertices originales del carro
    Vector3[] carNewVertices; //Vertices que iremos guardando del carro

    //Creamos y guardamos los elementos de las ruedas
    GameObject[] wheels = new GameObject[4];// Arreglo de las ruedas
    Mesh[] wheelMeshes = new Mesh[4];// Malla de las ruedas
    Vector3[] wheelPositions = new Vector3[4];// Posicion de las ruedas
    Vector3[][] wheelBaseVertices = new Vector3[4][];// Vertices originales de las ruedas
    Vector3[][] wheelNewVertices = new Vector3[4][]; // Vertices que iremos guardando de las ruedas 

    void Start()
    {   
        //Guardamos la malla del carro para poder manipular sus vertices
        carMesh = GetComponentInChildren<MeshFilter>().mesh;
        //Guardamos los vertices originales del carro
        carBaseVertices = carMesh.vertices;
        //Para cada una de las ruedas, obtenemos su malla y sus vertices originales
        carNewVertices = new Vector3[carBaseVertices.Length];
        //Guardamos los vertices originales en carNewVertices
        for(int i=0; i<carBaseVertices.Length; i++){
            carNewVertices[i] = carBaseVertices[i];
        }

        //Inicializamos las cuatro ruedas
        for (int i = 0; i < 4; i++)
        {
            //Ingresamos de manera manual la posicion de las llantas
            Vector3 wheelPosition;
            if (i == 0)
            {
                wheelPosition = new Vector3(0.12f ,0.1f, 0.3f);
                wheelPositions[i] = wheelPosition;
            }
            else if (i == 1)
            {
                wheelPosition = new Vector3(-0.22f, 0.1f, 0.3f);
                wheelPositions[i] = wheelPosition;
            }
            else if (i == 2)
            {
                wheelPosition = new Vector3(0.12f, 0.1f, -0.22f);
                wheelPositions[i] = wheelPosition;
            }
            else
            {
                wheelPosition = new Vector3(-0.22f, 0.1f, -0.22f);
                wheelPositions[i] = wheelPosition;
            }
            //Instanciamos las llantas con su modelo, posicion y rotacion
            wheels[i] = Instantiate(llanta, new Vector3(0,0,0), Quaternion.identity);
            //Guardamos las mallas de cada una de las ruedas
            wheelMeshes[i] = wheels[i].GetComponentInChildren<MeshFilter>().mesh;
            //Guardamos los vertices originales de cada una de las ruedas
            wheelBaseVertices[i] = wheelMeshes[i].vertices;
            //Guardamos los vertices nuevos de cada una de las ruedas
            wheelNewVertices[i] = new Vector3[wheelBaseVertices[i].Length];
            //Guardamos los vertices nuevos en wheelNewVertices
            for(int j=0; j<wheelBaseVertices[i].Length; j++){
                wheelNewVertices[i][j] = wheelBaseVertices[i][j];
            }
        }
    }

    public void MovementCar(Vector3 interpolacion,Vector3 direccion)
    {
          if (!interpolacion.Equals(previousInterpolation))
         {
            angle = Mathf.Atan2(direccion.x , direccion.z ) * Mathf.Rad2Deg + 180;
            DoTransform(interpolacion,direccion);
            previousInterpolation = interpolacion;
         }
         else{
             DoTransform(interpolacion,direccion);
         }
    }


    //Funcion de movimiento
    void DoTransform(Vector3 interpolation,Vector3 direccion)
    {
        //Matriz de traslacion del carro
        Matrix4x4 move = HW_Transforms.TranslationMat(interpolation.x,
                                                      interpolation.y,
                                                      interpolation.z);

        //Matriz de rotacion del carro
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle , rotationAxis);
        //Matriz de escala del carro


        //Creamos una nueva matriz a partir de los valores de la matriz de traslacion y rotacion
        Matrix4x4 composite = move * rotate;

        //Recorremos los vertices del carro
        for (int i = 0; i < carNewVertices.Length; i++)
        {
            //Creamos un vector temporal para guardar los vectores bases del carro
            Vector4 temp = new Vector4(carBaseVertices[i].x,
                                       carBaseVertices[i].y,
                                       carBaseVertices[i].z,
                                       1);
             
            //Aplicamos la transformacion a los vertices base del carro
            carNewVertices[i] = composite * temp;
        }
        //Recalculamos los nuevos vertices y las normales del carro
        carMesh.vertices = carNewVertices;
        carMesh.RecalculateNormals();

        //Recorremos las ruedas de nuestro arreglo
        for (int i = 0; i < wheels.Length; i++)
        {
            //Guardamos la posicion de nuestras ruedas
            Matrix4x4 moveWheel = HW_Transforms.TranslationMat(wheelPositions[i].x ,
                                                               wheelPositions[i].y ,
                                                               wheelPositions[i].z);
            //Guardamos la rotacion de las ruedas
            Matrix4x4 spin = HW_Transforms.RotateMat(spinAngle * Time.time,
                                                     AXIS.X);
            //Creamos el movimiento y rotacion de las ruedas con respecto al carro
            Matrix4x4 compositeWheel = composite * moveWheel * spin;

            //Recorremos los vertices por cada de nuestras ruedas
            for (int j = 0; j < wheelNewVertices[i].Length; j++)
            {
                //Creamos un vector temporal que guarda los vertices base de las ruedas
                Vector4 temp = new Vector4(wheelBaseVertices[i][j].x,
                                           wheelBaseVertices[i][j].y,
                                           wheelBaseVertices[i][j].z,
                                           1);
                //Aplicamos la transformacion a los vertices base de las ruedas
                wheelNewVertices[i][j] = compositeWheel * temp;
            }
            //Recalculamos los nuevos vertices y las normales de las llantas
            wheelMeshes[i].vertices = wheelNewVertices[i];
            wheelMeshes[i].RecalculateNormals();
        }
    }
}
