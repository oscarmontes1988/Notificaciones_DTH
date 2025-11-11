# vinculacion/models.py

from django.db import models


# --- Entidades Principales ---

class Personas(models.Model):
    """
    [👤] Almacena la información de los individuos que están en el proceso.
    """
    cedula = models.CharField(max_length=20, unique=True, help_text="Cédula de la persona")
    nombre_completo = models.CharField(max_length=255)
    email_personal = models.EmailField(unique=True, null=True, blank=True, help_text="Email personal para notificaciones")
    
    # [cite_start]Campo clave para diferenciar plantillas [cite: 497, 513-517]
    es_funcionario_antiguo = models.BooleanField(default=False, help_text="Indica si la persona ya es funcionaria")

    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula})"

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


class Resoluciones(models.Model):
    """
    [📄] Guarda la información de las resoluciones que disparan el proceso.
    """
    numero_resolucion = models.CharField(max_length=50, unique=True)
    fecha_resolucion = models.DateField()
    fecha_publicacion = models.DateField(null=True, blank=True)
    fecha_desfijacion = models.DateField(null=True, blank=True)
    
    # Podrías usar FileField si quieres que Django gestione la subida del archivo
    archivo_resolucion_path = models.CharField(max_length=500, null=True, blank=True, help_text="Ruta al PDF de la resolución")

    def __str__(self):
        return f"Resolución {self.numero_resolucion}"

    class Meta:
        verbose_name = "Resolución"
        verbose_name_plural = "Resoluciones"


class Cargos(models.Model):
    """
    [🗂️] Información sobre los cargos (OPEP).
    """
    opep_numero = models.CharField(max_length=50, unique=True, help_text="Número de OPEP")
    nombre_cargo = models.CharField(max_length=255)
    
    # Ruta al manual de funciones
    manual_funciones_path = models.CharField(max_length=500, null=True, blank=True, help_text="Ruta al manual de funciones")

    def __str__(self):
        return f"{self.nombre_cargo} ({self.opep_numero})"

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"


# --- Entidad Central (Transaccional) ---

class Procesos_Vinculacion(models.Model):
    """
    [🔄] El corazón del sistema. Rastrea el estado de cada notificación y vinculación.
    """
    
    # --- Opciones para campos "Enum" (Choices) ---
    class TipoProceso(models.TextChoices):
        NOMBRAMIENTO = 'Nombramiento', 'Nombramiento'
        # ENCARGO = 'Encargo', 'Encargo'
        TERMINACION_ENCARGO = 'Terminacion de Encargo', 'Terminación de Encargo'
        INSUBSISTENCIA = 'Insubsistencia', 'Insubsistencia'

    class EstadoProceso(models.TextChoices):
        PENDIENTE = 'Pendiente Notificar', 'Pendiente Notificar'
        NOTIFICADO = 'Notificado', 'Notificado'
        ACEPTADO = 'Aceptado', 'Aceptado'
        PENDIENTE_EXAMENES = 'Pendiente Exámenes', 'Pendiente Exámenes'
        DOCS_COMPLETOS = 'Docs Completos', 'Docs Completos'
        POSESIONADO = 'Posesionado', 'Posesionado'
        RECHAZADO = 'Rechazado', 'Rechazado'

    # --- Claves Foráneas (Foreign Keys) ---
    
    # related_name='procesos' permite hacer: persona.procesos.all()
    persona = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='procesos')
    resolucion = models.ForeignKey(Resoluciones, on_delete=models.CASCADE, related_name='procesos')
    
    # Si se borra el cargo, el proceso sigue existiendo (SET_NULL)
    cargo = models.ForeignKey(Cargos, on_delete=models.SET_NULL, null=True, blank=True, related_name='procesos')

    proceso_origen = models.ForeignKey(
        'self',  # Se relaciona con la misma tabla
        on_delete=models.SET_NULL, # Si se borra el nombramiento, la terminación no se borra
        null=True,
        blank=True,
        related_name='procesos_derivados', # Nombre para consultar los "hijos"
        help_text="El proceso (ej. Nombramiento) que origina este proceso (ej. Terminación)"
    )
    
    # --- Datos del Proceso ---
    tipo_proceso = models.CharField(
        max_length=30,
        choices=TipoProceso.choices,
        default=TipoProceso.NOMBRAMIENTO
    )
    numero_th = models.CharField(max_length=50, null=True, blank=True, help_text="Consecutivo TH")
    email_documentacion_destino = models.EmailField(null=True, blank=True, help_text="Correo específico para recibir documentos")
    
    # --- Columna de Estado (Clave para automatización) ---
    estado_proceso = models.CharField(
        max_length=50,
        choices=EstadoProceso.choices,
        default=EstadoProceso.PENDIENTE
    )
    
    # [cite_start]--- Fechas de Seguimiento (Para control de términos) [cite: 331, 567, 574] ---
    fecha_comunicacion = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora de envío de notificación")
    fecha_maxima_aceptacion = models.DateField(null=True, blank=True)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora de aceptación")
    fecha_maxima_posesion = models.DateField(null=True, blank=True)
    fecha_solicitud_examenes = models.DateTimeField(null=True, blank=True)
    fecha_citacion_posesion = models.DateTimeField(null=True, blank=True)
    
    documentos_completos = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Proceso {self.id} - {self.persona.nombre_completo} - {self.tipo_proceso}"

    class Meta:
        verbose_name = "Proceso de Vinculación"
        verbose_name_plural = "Procesos de Vinculación"
        ordering = ['-id'] # Mostrar los más nuevos primero