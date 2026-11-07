# Pruebas de caracterización antes y después

Corrimos las 24 pruebas de `tests/test_caracterizacion.py` sobre `estado-inicial` y sobre `etapa-refactoring`, con el mismo archivo de pruebas y los mismos datos. Como las pruebas se escribieron después de la versión inicial, para correrlas ahí copiamos `tests/` y `pyproject.toml` en una copia del tag. Pasaron todas en las dos versiones y no se modificaron en ningún PR.

| Prueba | `estado-inicial` | `etapa-refactoring` |
|---|---|---|
| `test_registra_solicitud_sin_deuda` | Pasa | Pasa |
| `test_registra_con_deuda_queda_rechazada_en_tesoreria` | Pasa | Pasa |
| `test_registro_legajo_inexistente` | Pasa | Pasa |
| `test_registro_legajo_no_numerico` | Pasa | Pasa |
| `test_registro_tipo_y_prioridad_invalidos` | Pasa | Pasa |
| `test_registro_normaliza_tipo_y_prioridad` | Pasa | Pasa |
| `test_asigna_responsable` | Pasa | Pasa |
| `test_asigna_responsable_de_otra_area` | Pasa | Pasa |
| `test_asigna_responsable_inexistente` | Pasa | Pasa |
| `test_cambia_estado` | Pasa | Pasa |
| `test_transicion_invalida` | Pasa | Pasa |
| `test_estado_final_no_cambia` | Pasa | Pasa |
| `test_estado_invalido` | Pasa | Pasa |
| `test_emitir_sin_responsable` | Pasa | Pasa |
| `test_id_inexistente_y_no_numerico` | Pasa | Pasa |
| `test_emite_alumno_regular` | Pasa | Pasa |
| `test_emite_analitico_excluye_extracurriculares_y_desaprobadas` | Pasa | Pasa |
| `test_emite_analitico_sin_aprobadas` | Pasa | Pasa |
| `test_busca_por_estado_y_tipo` | Pasa | Pasa |
| `test_busca_por_legajo` | Pasa | Pasa |
| `test_busca_sin_resultados` | Pasa | Pasa |
| `test_reporte` | Pasa | Pasa |
| `test_opcion_invalida` | Pasa | Pasa |
| `test_recorrido_completo` | Pasa | Pasa |
