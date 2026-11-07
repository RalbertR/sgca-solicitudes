# ADR-001. Pruebas de caracterización antes de refactorizar

## Contexto

La versión inicial no tenía ninguna prueba y toda la lógica estaba en una clase que mezclaba `input`, `print`, el archivo y las reglas. Íbamos a cambiar casi todo el código por dentro y necesitábamos una forma de saber que el sistema seguía haciendo lo mismo. Una prueba unitaria no se podía escribir sin antes cambiar el código que queríamos proteger.

## Decisión

Antes del primer PR escribimos 24 pruebas de caracterización de caja negra. Cada una corre `main.py` en una carpeta temporal con `tests/datos_prueba.json`, le pasa un guion de entradas por teclado y compara la salida de consola, el JSON resultante y los certificados con lo que producía la versión inicial. La fecha del día se reemplaza por `<HOY>` para que el resultado no dependa de cuándo se corre. Acordamos que ningún PR puede modificar esas pruebas ni sus datos, y lo sumamos al checklist.

## Alternativas

Probar a mano después de cada cambio era lento y no dejaba registro de qué se había probado. Escribir unitarias sobre `SistemaSolicitudes` obligaba a simular `input` y `print`, y quedaban atadas a métodos que íbamos a borrar. También pensamos en comparar solo la salida de consola, pero así un error en el JSON o en un certificado podía pasar sin que nadie lo notara.

## Consecuencias

Pudimos refactorizar con una red que no depende de cómo está organizado el código, y por eso sirvió igual para las dos versiones. En el PR #3 detectaron que a `Tesorería` le faltaba el acento antes de que llegara a `main`. Cuando una falla no dice qué método se rompió, solo que algo cambió desde afuera, por eso cada pieza nueva trajo además sus pruebas unitarias. Si alguna vez hay que cambiar el comportamiento a propósito, primero hay que actualizar estas pruebas en un PR aparte.
