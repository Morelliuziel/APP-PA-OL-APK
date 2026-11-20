package ar.edu.et35.panolapp.data;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import java.util.ArrayList;
import java.util.List;
import ar.edu.et35.panolapp.domain.Reglas;
import ar.edu.et35.panolapp.domain.Tablet;

/** Todas las transiciones son atómicas; la UI nunca escribe directamente los estados. */
public final class PanolDb extends SQLiteOpenHelper {
    private static final String NAME = "panol_v1.db";
    public PanolDb(Context context) { super(context, NAME, null, 1); }

    @Override public void onConfigure(SQLiteDatabase db) {
        super.onConfigure(db);
        db.setForeignKeyConstraintsEnabled(true);
    }

    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE tablets (" +
          "serial TEXT PRIMARY KEY NOT NULL, procesador TEXT NOT NULL, ram_gb INTEGER NOT NULL CHECK(ram_gb>0), " +
          "almacenamiento_gb INTEGER NOT NULL CHECK(almacenamiento_gb>0), pantalla_pulgadas REAL NOT NULL CHECK(pantalla_pulgadas>=4), " +
          "puertos TEXT NOT NULL, conectividad TEXT NOT NULL, " +
          "estado TEXT NOT NULL CHECK(estado IN ('EN_PANOL','EN_USO_LOCAL','EN_USO_EXTERNO','EN_SERVICIO_TECNICO')), " +
          "legajo TEXT NOT NULL DEFAULT '', tarea TEXT NOT NULL DEFAULT '', " +
          "creado_en INTEGER NOT NULL, actualizado_en INTEGER NOT NULL, " +
          "CHECK ((estado IN ('EN_PANOL','EN_SERVICIO_TECNICO') AND legajo='') OR " +
          "(estado IN ('EN_USO_LOCAL','EN_USO_EXTERNO') AND length(legajo)>=3)), " +
          "CHECK (estado!='EN_USO_EXTERNO' OR length(trim(tarea))>=3) )");
        db.execSQL("CREATE TABLE movimientos (" +
          "id INTEGER PRIMARY KEY AUTOINCREMENT, serial TEXT NOT NULL REFERENCES tablets(serial) ON DELETE RESTRICT, " +
          "tipo TEXT NOT NULL, desde_estado TEXT, hacia_estado TEXT NOT NULL, legajo TEXT NOT NULL DEFAULT '', " +
          "tarea TEXT NOT NULL DEFAULT '', condicion_fisica TEXT NOT NULL DEFAULT '', metodo_identificacion TEXT NOT NULL, " +
          "fecha INTEGER NOT NULL)");
        db.execSQL("CREATE INDEX idx_movimientos_serial_fecha ON movimientos(serial, fecha DESC)");
        db.execSQL("CREATE INDEX idx_tablets_estado ON tablets(estado)");
    }

    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        throw new IllegalStateException("Migración de base pendiente para versión " + newVersion);
    }

    private static ContentValues valoresTablet(Tablet t) {
        ContentValues v = new ContentValues();
        v.put("serial", t.serial); v.put("procesador", t.procesador);
        v.put("ram_gb", t.ramGb); v.put("almacenamiento_gb", t.almacenamientoGb);
        v.put("pantalla_pulgadas", t.pantallaPulgadas); v.put("puertos", t.puertos);
        v.put("conectividad", t.conectividad);
        v.put("estado", t.estado); v.put("legajo", t.legajo); v.put("tarea", t.tarea);
        v.put("creado_en", t.creadoEn); v.put("actualizado_en", t.actualizadoEn);
        return v;
    }

    private static Tablet leerTablet(Cursor c) {
        Tablet t = new Tablet(c.getString(c.getColumnIndexOrThrow("serial")),
          c.getString(c.getColumnIndexOrThrow("procesador")),
          c.getInt(c.getColumnIndexOrThrow("ram_gb")),
          c.getInt(c.getColumnIndexOrThrow("almacenamiento_gb")),
          c.getDouble(c.getColumnIndexOrThrow("pantalla_pulgadas")),
          c.getString(c.getColumnIndexOrThrow("puertos")),
          c.getString(c.getColumnIndexOrThrow("conectividad")));
        t.estado = c.getString(c.getColumnIndexOrThrow("estado"));
        t.legajo = c.getString(c.getColumnIndexOrThrow("legajo"));
        t.tarea = c.getString(c.getColumnIndexOrThrow("tarea"));
        t.creadoEn = c.getLong(c.getColumnIndexOrThrow("creado_en"));
        t.actualizadoEn = c.getLong(c.getColumnIndexOrThrow("actualizado_en"));
        return t;
    }

    private Tablet buscarEn(SQLiteDatabase db, String serial) {
        try (Cursor c = db.query("tablets", null, "serial=?", new String[]{ Tablet.normalizarSerie(serial) },
              null, null, null)) {
            return c.moveToFirst() ? leerTablet(c) : null;
        }
    }

    public Tablet buscar(String serial) { return buscarEn(getReadableDatabase(), serial); }

    public List<Tablet> listar() {
        List<Tablet> resultado = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query("tablets", null, null, null, null, null, "serial ASC")) {
            while (c.moveToNext()) resultado.add(leerTablet(c));
        }
        return resultado;
    }

    private static String metodo(String valor) {
        return ("QR".equals(valor) || "MANUAL".equals(valor)) ? valor : "CATALOGO";
    }

    private static void movimiento(SQLiteDatabase db, String tipo, String serial,
       String desde, String hacia, String legajo, String tarea, String condicion, String identificacion) {
        ContentValues m = new ContentValues();
        m.put("serial", serial); m.put("tipo", tipo); m.put("desde_estado", desde);
        m.put("hacia_estado", hacia); m.put("legajo", legajo); m.put("tarea", tarea);
        m.put("condicion_fisica", condicion); m.put("metodo_identificacion", metodo(identificacion));
        m.put("fecha", System.currentTimeMillis());
        if (db.insertOrThrow("movimientos", null, m) == -1) throw new IllegalStateException("No se registró movimiento.");
    }

    public void alta(Tablet t, String metodo) {
        Reglas.validarAlta(t);
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            if (buscarEn(db, t.serial) != null) throw new IllegalStateException("Serie duplicada: ya está registrada.");
            long now = System.currentTimeMillis();
            t.estado = Reglas.PANOL; t.legajo = ""; t.tarea = "";
            t.creadoEn = now; t.actualizadoEn = now;
            db.insertOrThrow("tablets", null, valoresTablet(t));
            movimiento(db, "ALTA", t.serial, null, Reglas.PANOL, "", "", "NUEVA", metodo);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    /** Emplea UPDATE condicional para impedir dos despachos ante estados obsoletos. */
    public void despachar(String serial, boolean home, String legajo, String tarea, String metodo) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            Tablet actual = buscarEn(db, serial);
            String error = Reglas.validarDespacho(actual, home, legajo, tarea);
            if (error != null) throw new IllegalStateException(error);
            String destino = home ? Reglas.EXTERNO : Reglas.LOCAL;
            String empleado = legajo.trim().toUpperCase(java.util.Locale.ROOT);
            String trabajo = tarea == null ? "" : tarea.trim();
            ContentValues v = new ContentValues();
            v.put("estado", destino); v.put("legajo", empleado); v.put("tarea", trabajo);
            v.put("actualizado_en", System.currentTimeMillis());
            int changed = db.update("tablets", v, "serial=? AND estado=?", new String[]{actual.serial, Reglas.PANOL});
            if (changed != 1) throw new IllegalStateException("Conflicto de estado: recargue la ficha.");
            movimiento(db, "DESPACHO", actual.serial, Reglas.PANOL, destino, empleado, trabajo, "", metodo);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    public void devolver(String serial, boolean danada, String metodo) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            Tablet actual = buscarEn(db, serial);
            String error = Reglas.validarDevolucion(actual);
            if (error != null) throw new IllegalStateException(error);
            String destino = danada ? Reglas.SERVICIO : Reglas.PANOL;
            ContentValues v = new ContentValues();
            v.put("estado", destino); v.put("legajo", ""); v.put("tarea", "");
            v.put("actualizado_en", System.currentTimeMillis());
            int changed = db.update("tablets", v, "serial=? AND estado=?",
                new String[]{actual.serial, actual.estado});
            if (changed != 1) throw new IllegalStateException("Conflicto de estado: recargue la ficha.");
            movimiento(db, "DEVOLUCION", actual.serial, actual.estado, destino,
                actual.legajo, actual.tarea, danada ? "DANADA" : "CORRECTA", metodo);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    public void finalizarServicio(String serial, String metodo) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            Tablet actual = buscarEn(db, serial);
            String error = Reglas.validarFinServicio(actual);
            if (error != null) throw new IllegalStateException(error);
            ContentValues v = new ContentValues();
            v.put("estado", Reglas.PANOL); v.put("actualizado_en", System.currentTimeMillis());
            int changed = db.update("tablets", v, "serial=? AND estado=?",
                new String[]{actual.serial, Reglas.SERVICIO});
            if (changed != 1) throw new IllegalStateException("Conflicto de estado: recargue la ficha.");
            movimiento(db, "FIN_SERVICIO", actual.serial, Reglas.SERVICIO,
                Reglas.PANOL, "", "", "REPARADA", metodo);
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    public List<String> historial(String serial) {
        List<String> resultado = new ArrayList<>();
        try (Cursor c = getReadableDatabase().query("movimientos", null, "serial=?",
            new String[]{Tablet.normalizarSerie(serial)}, null, null, "id DESC")) {
            while (c.moveToNext()) {
                long fecha = c.getLong(c.getColumnIndexOrThrow("fecha"));
                String when = new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm", java.util.Locale.getDefault())
                    .format(new java.util.Date(fecha));
                String tipo = c.getString(c.getColumnIndexOrThrow("tipo"));
                String desde = c.getString(c.getColumnIndexOrThrow("desde_estado"));
                String hacia = c.getString(c.getColumnIndexOrThrow("hacia_estado"));
                String legajo = c.getString(c.getColumnIndexOrThrow("legajo"));
                String tarea = c.getString(c.getColumnIndexOrThrow("tarea"));
                String condicion = c.getString(c.getColumnIndexOrThrow("condicion_fisica"));
                String identificacion = c.getString(c.getColumnIndexOrThrow("metodo_identificacion"));
                StringBuilder sb = new StringBuilder(when).append(" · ").append(tipo).append("\n")
                    .append(desde == null ? "ALTA" : Reglas.etiquetaEstado(desde))
                    .append(" → ").append(Reglas.etiquetaEstado(hacia));
                if (!legajo.isEmpty()) sb.append("\nLegajo: ").append(legajo);
                if (!tarea.isEmpty()) sb.append(" · Tarea: ").append(tarea);
                if (!condicion.isEmpty()) sb.append("\nCondición: ").append(condicion);
                sb.append(" · Identificación: ").append(identificacion);
                resultado.add(sb.toString());
            }
        }
        return resultado;
    }
}
