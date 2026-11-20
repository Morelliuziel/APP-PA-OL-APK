package ar.edu.et35.panolapp.domain;

/** Máquina de estados pura, verificable sin Android y sin base de datos. */
public final class Reglas {
    private Reglas() {}
    public static final String PANOL = "EN_PANOL";
    public static final String LOCAL = "EN_USO_LOCAL";
    public static final String EXTERNO = "EN_USO_EXTERNO";
    public static final String SERVICIO = "EN_SERVICIO_TECNICO";

    public static void validarAlta(Tablet tablet) {
        if (tablet == null || !tablet.serial.matches("[A-Z0-9][A-Z0-9._-]{2,39}"))
            throw new IllegalArgumentException("Serie inválida: use 3 a 40 caracteres alfanuméricos, punto, guion o guion bajo.");
        if (tablet.procesador.isEmpty() || tablet.procesador.length() > 120)
            throw new IllegalArgumentException("Indique el procesador (máximo 120 caracteres).");
        if (tablet.ramGb <= 0 || tablet.ramGb > 1024 || tablet.almacenamientoGb <= 0 || tablet.almacenamientoGb > 65536)
            throw new IllegalArgumentException("RAM o almacenamiento fuera de rango.");
        if (Double.isNaN(tablet.pantallaPulgadas) || tablet.pantallaPulgadas < 4 || tablet.pantallaPulgadas > 30)
            throw new IllegalArgumentException("Tamaño de pantalla fuera de rango (4 a 30 pulgadas).");
        if (tablet.puertos.isEmpty() || tablet.conectividad.isEmpty() ||
            tablet.puertos.length() > 300 || tablet.conectividad.length() > 300)
            throw new IllegalArgumentException("Complete puertos y conectividad (máximo 300 caracteres).");
    }

    public static String validarDespacho(Tablet actual, boolean homeOffice, String legajo, String tarea) {
        if (actual == null) return "Tablet no registrada.";
        if (!PANOL.equals(actual.estado)) return "Operación bloqueada: la tablet no está disponible en Pañol.";
        if (legajo == null || !legajo.trim().matches("[A-Za-z0-9-]{3,24}"))
            return "Debe ingresar un legajo válido (3 a 24 caracteres).";
        if (homeOffice && (tarea == null || tarea.trim().length() < 3))
            return "HOME OFFICE BLOQUEADO: se requiere una tarea asignada (mínimo 3 caracteres).";
        if (tarea != null && tarea.length() > 180) return "La tarea supera 180 caracteres.";
        return null;
    }

    public static String validarDevolucion(Tablet actual) {
        if (actual == null) return "Tablet no registrada.";
        if (!LOCAL.equals(actual.estado) && !EXTERNO.equals(actual.estado))
            return "No se puede devolver: la tablet no está prestada.";
        return null;
    }

    public static String validarFinServicio(Tablet actual) {
        if (actual == null) return "Tablet no registrada.";
        if (!SERVICIO.equals(actual.estado)) return "La tablet no está en Servicio Técnico.";
        return null;
    }

    public static String ubicacion(String estado) {
        switch (estado) {
            case PANOL: return "Depósito · Pañol";
            case LOCAL: return "Oficina de la empresa";
            case EXTERNO: return "Domicilio autorizado · Home Office";
            case SERVICIO: return "Área de Servicio Técnico";
            default: throw new IllegalArgumentException("Estado desconocido: " + estado);
        }
    }

    public static String etiquetaEstado(String estado) {
        switch (estado) {
            case PANOL: return "En Pañol";
            case LOCAL: return "En Uso Local (Oficina)";
            case EXTERNO: return "En Uso Externo (Home Office)";
            case SERVICIO: return "En Servicio Técnico";
            default: return "Estado desconocido";
        }
    }
}
