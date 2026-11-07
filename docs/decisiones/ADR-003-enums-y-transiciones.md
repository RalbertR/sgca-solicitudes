# ADR-003. Enums y tabla de transiciones

## Contexto

Los estados, tipos y prioridades eran strings sueltos repetidos en varios métodos, como `"pendiente"` o `"analitico_parcial"`, y las transiciones válidas estaban repartidas en `if` anidados dentro de `cambiar_estado`. Era el smell S4 del diagnóstico. Un error de tipeo pasaba sin aviso y para saber qué cambios de estado se permitían había que leer todo el método.

## Decisión

Creamos `EstadoSolicitud`, `TipoCertificado` y `Prioridad` como `StrEnum` y pusimos las transiciones en el diccionario `TRANSICIONES`, donde cada estado tiene el conjunto de estados a los que puede pasar. `puede_pasar` es la única función que lo consulta. Elegimos `StrEnum` porque cada valor se compara y se muestra como el string de siempre, y así el JSON y los textos de la consola no cambian. Las áreas y la escala de notas quedaron como constantes con nombre.

## Alternativas

Unas constantes de texto sacaban los literales repetidos, pero no agrupaban los valores posibles ni validaban nada. Con `Enum` común había que escribir `.value` en cada lugar donde se muestra o se guarda un valor. El patrón State, con una clase por estado, era demasiado para cuatro estados con dos salidas como mucho.

## Consecuencias

Un valor mal escrito ahora falla al crear el enum y no más adelante. Sumar un estado es agregarlo al enum y a la tabla, y cada transición permitida tiene su prueba en `tests/test_modelos.py`. La parte negativa es la misma que en ADR-002, porque un valor desconocido en `datos.json` corta la operación con `ValueError`.
