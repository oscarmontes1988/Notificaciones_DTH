# notificaciones/views.py

import os # Necesario para manejar rutas de archivos
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage # Necesario para guardar archivos
from .forms import CargaExcelForm
from .models import Procesos_Vinculacion # Mantenemos esta para la vista de consolidados
from .importer_logic import procesar_carga_excel
from django.db.models import Q



def vista_carga(request):
    """
    Esta vista maneja la subida del archivo Excel.
    NO contiene lógica de Pandas. Solo guarda el archivo,
    llama a 'procesar_carga_excel' y muestra los resultados.
    """
    if request.method == 'POST':
        form = CargaExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            
            # 1. Guarda el archivo subido temporalmente
            temp_path = default_storage.save(f"tmp/{archivo.name}", archivo)
            ruta_completa_temp = os.path.join(default_storage.location, temp_path)

            try:
                # 2. Llama a la lógica centralizada (de importer_logic.py)
                resultados_log = procesar_carga_excel(ruta_completa_temp)
                
                # 3. Muestra los logs al usuario usando 'messages'
                # (O puedes pasarlos al contexto si lo prefieres)
                contador_exito = 0
                for linea in resultados_log:
                    if linea.startswith('ERROR:'):
                        messages.error(request, linea)
                    elif linea.startswith('WARNING:'):
                        messages.warning(request, linea)
                    elif linea.startswith('¡Carga completada'):
                        messages.success(request, linea)
                    elif "Procesado Nombramiento" in linea:
                         contador_exito += 1 # Contamos solo los nombramientos
                
                if contador_exito > 0:
                    messages.info(request, f"Se procesaron {contador_exito} registros de nombramiento.")

            except Exception as e:
                # Captura cualquier error fatal que haya detenido la lógica
                messages.error(request, f"Error crítico al procesar el archivo: {e}")
            
            finally:
                # 4. Borra el archivo temporal después de usarlo
                default_storage.delete(temp_path)
            
            # Redirige a la vista de consolidados para ver los resultados
            return redirect('vista_consolidados') 

    else: # Si es un método GET
        form = CargaExcelForm()

    return render(request, 'notificaciones/carga.html', {'form': form})


def vista_consolidados(request):
    """
    Esta vista no necesita cambios. 
    Muestra los procesos usando 'consolidados.html'
    """
    # 1. Obtenemos la consulta de búsqueda de la URL (ej. ?q=oscar)
    #    Si no hay 'q', usamos un string vacío.
    query = request.GET.get('q', '')
    
    procesos = Procesos_Vinculacion.objects.select_related(
        'persona', 'resolucion', 'cargo'
    ).order_by('id')
    
    if query:
        # Creamos un objeto de búsqueda
        #   __icontains = "case-insensitive contains" (busca sin importar mayúsculas)
        #   Los | (pipe) significan "OR"
        lookup = (
            Q(persona__nombre_completo__icontains=query) |
            Q(persona__cedula__icontains=query) |
            Q(resolucion__numero_resolucion__icontains=query) |
            Q(cargo__nombre_cargo__icontains=query) |
            Q(tipo_proceso__icontains=query)
        )
        
        # Aplicamos el filtro a nuestra consulta
        procesos = procesos.filter(lookup)
    
    # 4. Pasamos los 'procesos' (ya filtrados) y también la 'query'
    #    al contexto.
    context = {
        'procesos': procesos,
        'query': query  # Pasamos la 'query' para mostrarla en la barra de búsqueda
    }
    return render(request, 'notificaciones/consolidados.html', context)