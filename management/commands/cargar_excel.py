from django.core.management.base import BaseCommand, CommandError

# 1. Importa la lógica centralizada desde el nuevo archivo
from notificaciones.importer_logic import procesar_carga_excel 

class Command(BaseCommand):
    """
    Este comando actúa como un 'envoltorio' (wrapper).
    Toda la lógica de procesamiento de Excel reside en 'importer_logic.py'.
    Este script solo maneja la entrada (ruta del archivo) y la salida (imprimir en consola).
    """
    help = 'Carga los procesos de vinculación desde un archivo Excel.'

    def add_arguments(self, parser):
        """
        Define el argumento 'ruta_excel' que recibirá el comando.
        """
        parser.add_argument(
            'ruta_excel', 
            type=str, 
            help='La ruta completa al archivo Excel que se va a cargar.'
        )

    def handle(self, *args, **options):
        """
        Lógica principal: obtiene la ruta, llama a la función de lógica e imprime los resultados.
        """
        
        # 1. Obtenemos la ruta del archivo que el usuario pasó
        ruta_archivo = options['ruta_excel']
        
        self.stdout.write(self.style.NOTICE(f'Iniciando carga desde: {ruta_archivo}'))
        
        try:
            # 2. Llama a la lógica centralizada
            #    Esta función (procesar_carga_excel) hace todo el trabajo.
            resultados_log = procesar_carga_excel(ruta_archivo)
            
            # 3. Itera sobre los logs devueltos y los imprime con estilo
            #    Ahora, la lógica de impresión está aquí, separada del procesamiento.
            for linea in resultados_log:
                if linea.startswith('ERROR:'):
                    self.stdout.write(self.style.ERROR(linea))
                elif linea.startswith('WARNING:'):
                    self.stdout.write(self.style.WARNING(linea))
                elif linea.startswith('¡Carga completada'):
                    self.stdout.write(self.style.SUCCESS(linea))
                else:
                    # Imprime mensajes de éxito estándar (ej. "Procesado Nombramiento...")
                    self.stdout.write(linea)

        except CommandError as e:
            # Captura errores fatales levantados por la lógica (ej. @transaction.atomic)
            self.stdout.write(self.style.ERROR(f'Error fatal en la transacción: {e}'))
        except Exception as e:
            # Captura cualquier otro error inesperado
            self.stdout.write(self.style.ERROR(f'Ocurrió un error inesperado en el comando: {e}'))