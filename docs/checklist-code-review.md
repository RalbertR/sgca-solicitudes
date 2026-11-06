# Checklist de code review

Lo usamos en cada Pull Request. Quien revisa marca cada ítem con sí o no, y cada "no" se convierte en un comentario sobre la línea concreta con lo que habría que cambiar. Un PR se aprueba cuando cumple los criterios de aceptación del final.

## Diseño y SOLID

- [ ] Cada clase o función nueva tiene una sola razón para cambiar.
- [ ] Sumar un caso nuevo, como un tipo de certificado o un estado, no obliga a modificar código que ya funciona.
- [ ] La lógica de negocio no depende de detalles concretos como el archivo, la consola o la fecha del sistema, sino que los recibe.
- [ ] Las interfaces exponen solo lo que usa quien las consume.

## Clean Code

- [ ] Los nombres de variables, métodos y clases dicen qué guardan o qué hacen, sin abreviaturas como `d`, `s` o `aux`.
- [ ] Ningún método nuevo o modificado pasa de 20 líneas, y cada uno trabaja en un solo nivel de abstracción.
- [ ] No hay strings ni números sueltos repetidos que representen un concepto del dominio.
- [ ] Los errores se informan con excepciones y no con valores especiales de retorno.
- [ ] No queda código duplicado que se pueda unificar.

## Pruebas

- [ ] El PR no modifica `tests/test_caracterizacion.py`, `tests/datos_prueba.json` ni `tests/esperados/`.
- [ ] Cada pieza nueva con lógica propia trae su prueba unitaria.
- [ ] `pytest` y `ruff check .` pasan en local y el CI está en verde.

## Repositorio

- [ ] La rama tiene un nombre que describe el cambio y sale de `main` actualizado.
- [ ] Los mensajes de commit dicen qué cambió, en presente y en español.
- [ ] La descripción del PR indica qué smell ataca, qué refactoring aplica y cómo se verificó.

## Criterios de aceptación técnica

Un PR se mergea cuando se cumplen todas estas condiciones:

1. El CI está en verde.
2. Las pruebas de caracterización siguen intactas y pasan, porque son la prueba de que el comportamiento externo no cambió.
3. Tiene al menos una aprobación del otro integrante.
4. Todas las observaciones de la revisión están resueltas con un commit nuevo o respondidas con una justificación.