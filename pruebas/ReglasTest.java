import ar.edu.et35.panolapp.domain.Reglas;
import ar.edu.et35.panolapp.domain.Tablet;

public final class ReglasTest {
    static int pruebas = 0;
    static void ok(boolean condicion, String mensaje) {
        pruebas++;
        if (!condicion) throw new AssertionError(mensaje);
    }
    static Tablet tableta() {
        return new Tablet("tab-001", "Snapdragon 680", 4, 64, 10.1, "USB-C, Jack 3.5", "Wi-Fi, Bluetooth");
    }
    public static void main(String[] args) {
        Tablet t = tableta();
        Reglas.validarAlta(t);
        ok("TAB-001".equals(t.serial), "Normalización de serie");
        ok(Reglas.PANOL.equals(t.estado), "Estado inicial");
        ok("Depósito · Pañol".equals(t.ubicacion()), "Ubicación derivada");
        ok(Reglas.validarDespacho(t, false, "EMP-001", "") == null, "Local sin tarea permitido");
        ok(Reglas.validarDespacho(t, true, "EMP-001", "Proyecto A") == null, "Externo con tarea");
        ok(Reglas.validarDespacho(t, true, "EMP-001", "") != null, "Externo sin tarea bloqueado");
        ok(Reglas.validarDespacho(t, true, "a", "Proyecto A") != null, "Legajo corto bloqueado");
        ok(Reglas.validarDevolucion(t) != null, "No devolver disponible");
        t.estado = Reglas.LOCAL;
        ok(Reglas.validarDespacho(t, false, "EMP-001", "") != null, "Bloquear doble despacho");
        ok(Reglas.validarDevolucion(t) == null, "Devolver desde local");
        t.estado = Reglas.EXTERNO;
        ok(Reglas.validarDevolucion(t) == null, "Devolver desde externo");
        t.estado = Reglas.SERVICIO;
        ok(Reglas.validarDevolucion(t) != null, "No devolver desde servicio");
        ok(Reglas.validarFinServicio(t) == null, "Cerrar servicio");
        t.estado = Reglas.PANOL;
        ok(Reglas.validarFinServicio(t) != null, "No cerrar servicio ajeno");
        try {
            Reglas.validarAlta(new Tablet("@@", "CPU", 4, 64, 10.1, "USB-C", "Wi-Fi"));
            throw new AssertionError("No rechazó serie inválida");
        } catch (IllegalArgumentException expected) { pruebas++; }
        System.out.println("OK: " + pruebas + " pruebas de reglas de negocio.");
    }
}
