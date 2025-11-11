import pandas as pd
from django.db import transaction
from django.core.management.base import CommandError
from notificaciones.models import (
    Personas, Resoluciones, Cargos, Procesos_Vinculacion
)

# --- CONFIGURACIÓN DE NOMBRES DE COLUMNAS ---
# Asegúrate de que estos nombres coincidan 100% con tu Excel
COL_RESOLUCION = 'resolucion'
COL_FECHA_RESOLUCION = 'fecha_resolucion'

# Columnas de Nombramiento
COL_NOM_CEDULA = 'cedula_funcionario_carrera'
COL_NOM_NOMBRE = 'nombre_completo_funcionario_carrera'
COL_NOM_CARGO = 'cargo_funcionario_carrera'

# Columnas de Terminación de Encargo
COL_TERM_CEDULA = 'cedula_terminacion_encargo'
COL_TERM_NOMBRE = 'nombre_completo_terminacion_encargo'
COL_TERM_CARGO_DEJA = 'cargo_encargo_que_termina' # Usado también por Insubsistencia
COL_TERM_CARGO_RETORNA = 'cargo_al_que_retorna'

# Columnas de Insubsistencia
COL_INSUB_CEDULA = 'cedula_Insubsistencia'
COL_INSUB_NOMBRE = 'nombre_completo_Insubsistencia'


@transaction.atomic
def procesar_carga_excel(ruta_archivo):
    """
    Función centralizada para procesar el Excel de vinculaciones.
    Recibe la ruta a un archivo .xlsx y devuelve una lista de logs (strings).
    """
    logs = [] # Lista para guardar los mensajes de log

    try:
        # Lee el Excel, forzando todas las columnas a ser texto (str)
        df = pd.read_excel(ruta_archivo, dtype=str)
        # Reemplaza los 'NaN' (Not a Number) de Pandas por 'None' (Nulo) de Python
        df = df.where(pd.notna(df), None)
        logs.append(f'Archivo {ruta_archivo} leído correctamente.')
        
        # columnas_leidas = df.columns.to_list()
        # logs.append(f"DEBUG: Columnas encontradas en el Excel: {columnas_leidas}")

        # (Aquí puedes mantener tu bloque de DEBUG: Test de Verificación de Constantes)

    except Exception as e:
        logs.append(f'ERROR: No se pudo leer el archivo Excel. Detalle: {e}')
        return logs

    # Inicializa fila_num ANTES del bucle try
    fila_num = 2 
    
    try:
        # Iteramos sobre cada FILA del Excel
        for index, fila in df.iterrows():
            fila_num = index + 2 # Actualizamos fila_num para el reporte de errores
            
            # (Aquí puedes mantener tu bloque DEBUG: TESTEO DE CÉDULAS)
            
            # --- 0. OBTENER RESOLUCIÓN (Requerida para todo) ---
            num_resolucion = fila.get(COL_RESOLUCION)
            fecha_res_raw = fila.get(COL_FECHA_RESOLUCION) # <-- Obtenemos el texto/timestamp

            if not num_resolucion or not fecha_res_raw:
                logs.append(f'WARNING: Fila {fila_num} omitida. Faltan datos de resolución.')
                continue

            # --- ¡INICIO DEL AJUSTE DE FECHA! ---
            try:
                # Pandas convierte la fecha (ej. "2025-08-05 00:00:00")
                fecha_obj = pd.to_datetime(fecha_res_raw)
                # Extraemos solo la parte de la fecha (YYYY-MM-DD)
                fecha_res = fecha_obj.date()
            except Exception:
                logs.append(f'WARNING: Fila {fila_num} omitida. Formato de fecha inválido: {fecha_res_raw}')
                continue
            # --- ¡FIN DEL AJUSTE DE FECHA! ---

            resolucion, _ = Resoluciones.objects.get_or_create(
                numero_resolucion=num_resolucion,
                # Ahora 'fecha_res' es un objeto 'date' (YYYY-MM-DD)
                defaults={'fecha_resolucion': fecha_res} 
            )
            
            proceso_nombramiento_actual = None # Para vincular procesos

            # --- 1. LÓGICA DE NOMBRAMIENTO ---
            if fila.get(COL_NOM_CEDULA):
                cargo_obj, _ = Cargos.objects.get_or_create(
                    opep_numero=fila[COL_NOM_CARGO],
                    defaults={'nombre_cargo': fila[COL_NOM_CARGO]}
                )
                
                persona_obj, _ = Personas.objects.get_or_create(
                    cedula=fila[COL_NOM_CEDULA],
                    defaults={'nombre_completo': fila[COL_NOM_NOMBRE]}
                )

                proceso_nombramiento_actual, _ = Procesos_Vinculacion.objects.get_or_create(
                    persona=persona_obj,
                    resolucion=resolucion,
                    cargo=cargo_obj,
                    tipo_proceso=Procesos_Vinculacion.TipoProceso.NOMBRAMIENTO,
                    defaults={'estado_proceso': 'Pendiente Notificar'}
                )
                
                logs.append(f'Fila {fila_num}: Procesado Nombramiento para {persona_obj.nombre_completo}')

            # --- 2. LÓGICA DE TERMINACIÓN DE ENCARGO ---
            if fila.get(COL_TERM_CEDULA):
                
                cargo_retorna_obj, _ = Cargos.objects.get_or_create(
                    opep_numero=fila[COL_TERM_CARGO_RETORNA],
                    defaults={'nombre_cargo': fila[COL_TERM_CARGO_RETORNA]}
                )
                
                persona_obj, _ = Personas.objects.get_or_create(
                    cedula=fila[COL_TERM_CEDULA],
                    defaults={'nombre_completo': fila[COL_TERM_NOMBRE]}
                )

                Procesos_Vinculacion.objects.get_or_create(
                    persona=persona_obj,
                    resolucion=resolucion,
                    cargo=cargo_retorna_obj, # El cargo al que retorna
                    tipo_proceso=Procesos_Vinculacion.TipoProceso.TERMINACION_ENCARGO,
                    proceso_origen=proceso_nombramiento_actual, # Vínculo
                    defaults={'estado_proceso': 'Pendiente Notificar'}
                )
                
                logs.append(f'Fila {fila_num}: Procesada Terminación para {persona_obj.nombre_completo}')
            
            # --- 3. LÓGICA DE INSUBSISTENCIA ---
            if fila.get(COL_INSUB_CEDULA):
                cargo_opep_termina = fila.get(COL_TERM_CARGO_DEJA)

                if cargo_opep_termina:
                    cargo_deja_obj, _ = Cargos.objects.get_or_create(
                        opep_numero=cargo_opep_termina,
                        defaults={'nombre_cargo': cargo_opep_termina}
                    )

                    persona_obj, _ = Personas.objects.get_or_create(
                        cedula=fila[COL_INSUB_CEDULA],
                        defaults={'nombre_completo': fila[COL_INSUB_NOMBRE]}
                    )

                    Procesos_Vinculacion.objects.get_or_create(
                        persona=persona_obj,
                        resolucion=resolucion,
                        cargo=cargo_deja_obj, # El cargo que deja
                        tipo_proceso=Procesos_Vinculacion.TipoProceso.INSUBSISTENCIA,
                        proceso_origen=proceso_nombramiento_actual, # Vínculo
                        defaults={'estado_proceso': 'Pendiente Notificar'}
                    )
                    
                    logs.append(f'Fila {fila_num}: Procesada Insubsistencia para {persona_obj.nombre_completo}')
                
                else:
                    # logs.append(f'WARNING: Fila {fila_num}: Omitida Insubsistencia para {fila.get(COL_INSUB_NOMBRE)} (la columna "{COL_TERM_CARGO_DEJA}" está vacía).')
                    pass

    except Exception as e:
        # Si un error (ej. KeyError) ocurre, 'fila_num' tendrá el valor
        # de la fila que estaba siendo procesada, gracias a la inicialización.
        logs.append(f'ERROR: Fila {fila_num}: No se pudo procesar. Detalle: {e}')
        # Levanta el error para que @transaction.atomic haga rollback
        raise CommandError(f'Error en fila {fila_num}: {e}')

    logs.append('¡Carga completada exitosamente!')
    return logs