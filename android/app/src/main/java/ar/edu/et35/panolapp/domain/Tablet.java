package ar.edu.et35.panolapp.domain;

import java.util.Locale;

/** Entidad de inventario; el estado vigente se guarda una sola vez por serie. */
public class Tablet {
    public String serial, procesador, puertos, conectividad;
    public int ramGb, almacenamientoGb;
    public double pantallaPulgadas;
    public String estado = Reglas.PANOL;
    public String legajo = "";
    public String tarea = "";
    public long creadoEn, actualizadoEn;

    public Tablet(String serial, String procesador, int ramGb, int almacenamientoGb,
                  double pantallaPulgadas, String puertos, String conectividad) {
        this.serial = normalizarSerie(serial);
        this.procesador = procesador.trim();
        this.ramGb = ramGb;
        this.almacenamientoGb = almacenamientoGb;
        this.pantallaPulgadas = pantallaPulgadas;
        this.puertos = puertos.trim();
        this.conectividad = conectividad.trim();
    }

    public static String normalizarSerie(String valor) {
        return valor == null ? "" : valor.trim().toUpperCase(Locale.ROOT);
    }

    public String ubicacion() { return Reglas.ubicacion(estado); }
}
