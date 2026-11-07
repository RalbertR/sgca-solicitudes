# ADR-002. Repositorio con interfaz y dependencias por constructor

## Contexto

En la versión inicial el archivo se abría con `open` y `json.load` o `json.dump` en ocho lugares, y la fecha salía de `datetime.now()` adentro de la lógica. Eran los smells S3 y S10 del diagnóstico. Así no se podía probar una regla sin un archivo real ni fijar la fecha en una prueba.

## Decisión

Definimos `RepositorioSolicitudes` como un `Protocol` con los seis métodos que usa el servicio, y `RepositorioJson` es el único que abre `datos.json`. `ServicioSolicitudes` recibe por constructor el repositorio, el reloj y la carpeta de certificados. `main.py` es el único lugar que arma las piezas reales.

## Alternativas

Juntar la lectura y la escritura en un par de funciones sacaba la duplicación, pero la lógica seguía atada al archivo. Una clase abstracta con `abc` también servía, aunque obligaba a heredar de ella. Con `Protocol` el repositorio en memoria de las pruebas encaja sin heredar de nada. Pasar a SQLite quedó afuera porque cambiaba el formato de los datos, que es parte del comportamiento que no queríamos tocar.

## Consecuencias

Las pruebas del servicio usan un `RepositorioEnMemoria` y una fecha fija, sin archivo ni consola. Para cambiar el almacenamiento alcanza con otra clase que cumpla la interfaz, sin tocar el servicio. En contra, `RepositorioJson` lee el archivo completo en cada operación, algo aceptable para un prototipo con pocos datos. Además arma los enums al leer, así que un estado, tipo o prioridad que no existe en `datos.json` corta con `ValueError`. El sistema nunca escribe esos valores y lo dejamos así.
