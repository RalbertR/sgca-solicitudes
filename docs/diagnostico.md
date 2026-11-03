# Diagnóstico de la versión inicial

Este diagnóstico corresponde al tag `estado-inicial`. Toda la lógica está en `sistema_solicitudes.py`, que tiene 285 líneas y una sola clase. Desde afuera el sistema hace lo que tiene que hacer, y las 24 pruebas de caracterización pasan. El problema está adentro. Para agregar un tipo de certificado, cambiar el archivo por una base de datos o probar una regla sin pasar por la consola, hay que meterse en métodos largos que mezclan todo.

Radon le da a `cambiar_estado` una complejidad ciclomática de 24, que es grado D. Después vienen `filtrar_solicitudes` con 15 y `registrar_solicitud` con 13. El promedio del archivo es 11, grado C. La salida completa está en `evidencias/radon-antes.txt`.

| # | Smell | Evidencia | Ubicación | Impacto | Riesgo de mantenimiento | Prioridad |
|---|---|---|---|---|---|---|
| S1 | God Class | `SistemaSolicitudes` muestra el menú, valida, aplica las reglas, lee y escribe el archivo, arma los certificados y el reporte | `sistema_solicitudes.py:6` | Cualquier cambio toca la misma clase y no hay límites claros entre responsabilidades | Alto. Dos personas no pueden trabajar a la vez sin pisarse | Alta |
| S2 | Long Method | `cambiar_estado` tiene 72 líneas y complejidad 24, y `registrar_solicitud` tiene 45 | `sistema_solicitudes.py:119` y `:61` | Cuesta entender qué hace cada parte y no se pueden probar por separado | Alto. Una corrección en el certificado puede romper la validación de transiciones | Alta |
| S3 | Duplicated Code | Se repite `f = open(self.archivo...)` con `json.load` o `json.dump` 8 veces, y el `for` que busca un estudiante o una solicitud 5 veces | `:66`, `:101`, `:120`, `:143`, `:193`, `:211`, `:218`, `:249` y `:70`, `:124`, `:150`, `:197`, `:238` | Un cambio en el formato del archivo obliga a tocar 8 lugares | Alto. Es fácil que una de las copias quede distinta | Alta |
| S4 | Primitive Obsession | Estados, tipos, prioridades y áreas son strings sueltos, por ejemplo `"pendiente"` o `"Tesorería"`, repetidos en varios métodos | `:76`, `:78`, `:85`, `:88`, `:129`, `:131` a `:138`, `:262` a `:278` | Un error de tipeo en un literal pasa sin aviso y las transiciones válidas no están escritas en un solo lugar | Medio | Media |
| S5 | Long Parameter List | `registrar_solicitud(legajo, tipo, prioridad, motivo)` y `filtrar_solicitudes(estado, tipo, prioridad, legajo)` reciben cuatro strings seguidos | `:61` y `:217` | Al llamarlos es fácil cambiar el orden de dos parámetros del mismo tipo | Medio. Sumar un criterio de búsqueda cambia la firma y todas sus llamadas | Media |
| S6 | Feature Envy | El promedio del analítico se calcula dentro de `cambiar_estado` recorriendo `est["materias"]`, o sea que usa solo datos del estudiante | `:165` a `:178` | La regla de escala de 1 a 10 y sin extracurriculares queda escondida en el flujo de emisión | Medio. Si otro reporte necesita el promedio, se copia el cálculo | Media |
| S7 | Switch Statements | `if s["tipo"] == "alumno_regular" ... elif s["tipo"] == "analitico_parcial"` para armar el texto, para el nombre del tipo en el correo y en el reporte | `:154`, `:160`, `:185`, `:270` | Para sumar un tipo de certificado hay que modificar código que ya funciona, lo que viola OCP | Medio | Media |
| S8 | Errores como strings | Los métodos devuelven `"ERROR: ..."` y quien llama pregunta con `startswith("ERROR")`. `registrar_solicitud` devuelve un dict o un string según el caso | `:28`, `:65` a `:78`, `:116`, `:128` a `:140`, `:201` a `:209` | El tipo de retorno no es predecible y un error que nadie revisa pasa como resultado válido | Alto | Alta |
| S9 | Mezcla de consola y lógica | `procesar` pide datos con `input`, y `cambiar_estado`, `filtrar_solicitudes` y `reporte` imprimen con `print` adentro de la regla de negocio | `:108`, `:147`, `:184`, `:189`, `:233` a `:246`, `:280` a `:285` | Las reglas solo se pueden probar corriendo el programa entero por consola, lo que viola SRP | Alto. Cambiar la interfaz obliga a reescribir la lógica | Alta |
| S10 | Dependencias rígidas | La ruta `"datos.json"` está fija, la carpeta `"certificados"` también y la fecha sale de `datetime.now()` adentro de la lógica | `:9`, `:98`, `:153`, `:180` | No se puede cambiar el almacenamiento ni fijar la fecha en una prueba, lo que viola DIP | Medio | Media |
| S11 | Nombres poco expresivos | Variables `d`, `s`, `x`, `r`, `aux`, `est`, `resp` y un método `procesar` que en realidad cambia el estado | `:27`, `:67`, `:79`, `:107`, `:124` | Hay que leer el código entero para saber qué guarda cada variable | Bajo | Baja |
| S12 | Magic Numbers | La escala de notas aparece como `m["nota"] >= 4 and m["nota"] <= 10` sin nombre | `:169` | Si cambia la nota mínima de aprobación, no hay forma de encontrar dónde se usa | Bajo | Baja |

Para el orden de corrección ponemos primero lo que más traba los cambios siguientes. Separar métodos y nombrar bien hace que el resto sea más fácil de revisar. Los enums y el repositorio sacan la duplicación y los literales, y recién con eso tiene sentido separar la consola del servicio y abrir los certificados a nuevos tipos.

| PR | Autor | Smells que ataca |
|---|---|---|
| 1 | Raúl | S2, S11 |
| 2 | Mariano | S4, S12 |
| 3 | Raúl | S3, S6, S10 |
| 4 | Mariano | S5, S8 |
| 5 | Raúl | S1, S9 |
| 6 | Mariano | S7 |
