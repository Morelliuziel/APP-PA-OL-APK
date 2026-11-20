package ar.edu.et35.panolapp.ui;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import android.graphics.drawable.GradientDrawable;

import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;

import java.util.List;
import ar.edu.et35.panolapp.data.PanolDb;
import ar.edu.et35.panolapp.domain.Tablet;
import ar.edu.et35.panolapp.domain.Reglas;
import ar.edu.et35.panolapp.qr.QrCodec;

/** Interfaz Android sin librerías de UI externas; navegación ligera por pantallas. */
public final class MainActivity extends Activity {
    private static final int NAVY = Color.rgb(16,32,57);
    private static final int BLUE = Color.rgb(37,99,235);
    private static final int RED = Color.rgb(185,28,28);
    private static final int GREEN = Color.rgb(21,128,61);
    private static final int MUTED = Color.rgb(79,92,111);
    private static final int BG = Color.rgb(245,248,252);
    private PanolDb db;
    private LinearLayout root;
    private String metodoActual = "CATALOGO";

    @Override public void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        getWindow().setStatusBarColor(NAVY);
        getWindow().setNavigationBarColor(NAVY);
        db = new PanolDb(this);
        inicio();
    }

    @Override protected void onDestroy() {
        if (db != null) db.close();
        super.onDestroy();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void pantalla(String subtitulo) {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(BG);
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(22), dp(18), dp(38));
        scroll.addView(root);
        setContentView(scroll);
        TextView nombre = texto("PAÑOL-APP", 24, NAVY, true);
        nombre.setLetterSpacing(0.045f);
        root.addView(nombre);
        root.addView(texto(subtitulo, 13, MUTED, false));
        espacio(16);
    }

    private TextView texto(String contenido, int size, int color, boolean strong) {
        TextView tv = new TextView(this);
        tv.setText(contenido);
        tv.setTextSize(size);
        tv.setTextColor(color);
        if (strong) tv.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        tv.setPadding(0, dp(4), 0, dp(7));
        return tv;
    }

    private void espacio(int alto) {
        View view = new View(this);
        root.addView(view, new LinearLayout.LayoutParams(1, dp(alto)));
    }

    private void titulo(String contenido) {
        root.addView(texto(contenido, 18, NAVY, true));
        espacio(3);
    }

    private Button boton(String nombre, int color, Runnable action) {
        Button b = new Button(this);
        b.setText(nombre);
        b.setAllCaps(false);
        b.setTextColor(Color.WHITE);
        b.setTextSize(15);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(color); bg.setCornerRadius(dp(11));
        b.setBackground(bg);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, dp(51));
        lp.setMargins(0, dp(5), 0, dp(5));
        root.addView(b, lp);
        b.setOnClickListener(v -> action.run());
        return b;
    }

    private void info(String texto) { root.addView(texto(texto, 15, NAVY, false)); }

    private void error(String mensaje) {
        new AlertDialog.Builder(this).setTitle("Operación no permitida")
            .setMessage(mensaje).setPositiveButton("Entendido", null).show();
    }

    private void exito(String mensaje) { Toast.makeText(this, mensaje, Toast.LENGTH_LONG).show(); }

    private void ejecutar(Runnable accion) {
        try { accion.run(); }
        catch (Exception e) { error(e.getMessage() == null ? "Error inesperado" : e.getMessage()); }
    }

    private void inicio() {
        pantalla("Gestión de tablets · Control físico y trazabilidad");
        List<Tablet> tablets = db.listar();
        int panol = 0, local = 0, externo = 0, servicio = 0;
        for (Tablet t : tablets) {
            if (Reglas.PANOL.equals(t.estado)) panol++;
            else if (Reglas.LOCAL.equals(t.estado)) local++;
            else if (Reglas.EXTERNO.equals(t.estado)) externo++;
            else servicio++;
        }
        titulo("Resumen de inventario");
        info("Total: " + tablets.size() + " tablets");
        info("Disponibles: " + panol + "  ·  Oficina: " + local);
        info("Home Office: " + externo + "  ·  Servicio: " + servicio);
        espacio(13);
        titulo("Identificar dispositivo");
        boton("Escanear QR con la cámara", BLUE, this::escanear);
        boton("Ingresar QR o serie por teclado", NAVY, this::entradaManual);
        espacio(14);
        titulo("Inventario");
        boton("Ver todas las tablets", NAVY, this::catalogo);
        boton("Registrar tablet manualmente", GREEN, this::altaManual);
        espacio(12);
        info("Sistema local: la información queda almacenada en este dispositivo Android.");
    }

    private void escanear() {
        GmsBarcodeScannerOptions options = new GmsBarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .enableAutoZoom()
            .build();
        GmsBarcodeScanner scanner = GmsBarcodeScanning.getClient(this, options);
        scanner.startScan()
            .addOnSuccessListener(barcode -> procesarIdentificacion(barcode.getRawValue(), "QR"))
            .addOnCanceledListener(() -> exito("Escaneo cancelado."))
            .addOnFailureListener(e -> new AlertDialog.Builder(this)
                .setTitle("No se pudo abrir el lector QR")
                .setMessage("Revisá los Servicios de Google Play y la conectividad inicial del módulo de escaneo. " +
                    "Podés ingresar el contenido del QR o la serie por teclado.\n\nDetalle: " + e.getMessage())
                .setPositiveButton("Ingreso manual", (d, w) -> entradaManual())
                .setNegativeButton("Cerrar", null).show());
    }

    private void entradaManual() {
        EditText campo = new EditText(this);
        campo.setHint("Número de serie o JSON/QR delimitado");
        campo.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        campo.setSingleLine(false); campo.setMinLines(2); campo.setMaxLines(5);
        LinearLayout contenedor = contenedorFormulario(campo);
        AlertDialog dialog = new AlertDialog.Builder(this)
            .setTitle("Ingreso por teclado · QR dañado")
            .setMessage("Para una tablet registrada, ingresá su serie. Para una nueva, pegá el JSON o el texto delimitado.")
            .setView(contenedor)
            .setPositiveButton("Buscar / interpretar", null)
            .setNegativeButton("Cancelar", null).create();
        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String entrada = campo.getText().toString().trim();
            if (entrada.isEmpty()) { campo.setError("Ingrese el dato"); return; }
            dialog.dismiss();
            procesarIdentificacion(entrada, "MANUAL");
        }));
        dialog.show();
    }

    private void procesarIdentificacion(String raw, String metodo) {
        ejecutar(() -> {
            if (raw == null || raw.trim().isEmpty()) throw new IllegalArgumentException("El escáner devolvió un QR vacío.");
            String normal = Tablet.normalizarSerie(raw);
            // Una serie simple nunca altera la ficha técnica registrada.
            if (normal.matches("[A-Z0-9][A-Z0-9._-]{2,39}")) {
                Tablet t = db.buscar(normal);
                if (t == null) throw new IllegalArgumentException("La serie " + normal + " no está registrada. Usá el alta manual o un QR completo.");
                ficha(t.serial, metodo);
                return;
            }
            Tablet decoded = QrCodec.decodificar(raw);
            Tablet existente = db.buscar(decoded.serial);
            if (existente == null) {
                previoAlta(decoded, metodo);
            } else {
                // No confiamos en datos QR para sobrescribir inventario ya auditado.
                ficha(existente.serial, metodo);
                if (!mismaFicha(existente, decoded)) {
                    new AlertDialog.Builder(this).setTitle("Aviso de discrepancia")
                        .setMessage("El QR corresponde a una serie registrada, pero algunos datos técnicos difieren. " +
                            "Se conserva la ficha del pañol. Revisá la etiqueta físicamente.")
                        .setPositiveButton("Entendido", null).show();
                }
            }
        });
    }

    private boolean mismaFicha(Tablet a, Tablet b) {
        return a.serial.equals(b.serial) && a.procesador.equals(b.procesador) &&
            a.ramGb == b.ramGb && a.almacenamientoGb == b.almacenamientoGb &&
            Double.compare(a.pantallaPulgadas, b.pantallaPulgadas) == 0 &&
            a.puertos.equals(b.puertos) && a.conectividad.equals(b.conectividad);
    }

    private void previoAlta(Tablet t, String metodo) {
        pantalla("CU-01 · Confirmación de alta desde QR");
        titulo("Tablet nueva: " + t.serial);
        datosTecnicos(t);
        espacio(9);
        info("Estado inicial: En Pañol · Ubicación: Depósito");
        boton("Confirmar alta", GREEN, () -> ejecutar(() -> {
            db.alta(t, metodo); exito("Tablet registrada y movimiento ALTA almacenado.");
            ficha(t.serial, metodo);
        }));
        boton("Cancelar", NAVY, this::inicio);
    }

    private void catalogo() {
        pantalla("Inventario · Listado y estado actual");
        List<Tablet> todas = db.listar();
        titulo("Tablets registradas (" + todas.size() + ")");
        if (todas.isEmpty()) info("Todavía no hay tablets. Escaneá una etiqueta de prueba o registrá una manualmente.");
        for (Tablet t : todas) {
            boton(t.serial + "  ·  " + Reglas.etiquetaEstado(t.estado), NAVY,
                () -> ficha(t.serial, "CATALOGO"));
        }
        boton("Volver al inicio", BLUE, this::inicio);
    }

    private void datosTecnicos(Tablet t) {
        info("Procesador: " + t.procesador);
        info("Memoria RAM: " + t.ramGb + " GB");
        info("Almacenamiento: " + t.almacenamientoGb + " GB");
        info("Pantalla: " + t.pantallaPulgadas + " pulgadas");
        info("Puertos: " + t.puertos);
        info("Conectividad: " + t.conectividad);
    }

    private void ficha(String serial, String metodo) {
        Tablet t = db.buscar(serial);
        if (t == null) { error("Tablet no encontrada."); inicio(); return; }
        metodoActual = metodo;
        pantalla("Ficha del dispositivo · CU-02 / CU-03");
        titulo(t.serial);
        TextView estado = texto(Reglas.etiquetaEstado(t.estado), 19,
            Reglas.PANOL.equals(t.estado) ? GREEN : Reglas.SERVICIO.equals(t.estado) ? RED : BLUE, true);
        root.addView(estado);
        info("Ubicación actual: " + t.ubicacion());
        if (!t.legajo.isEmpty()) info("Responsable · Legajo: " + t.legajo);
        if (!t.tarea.isEmpty()) info("Tarea asociada: " + t.tarea);
        espacio(12);
        titulo("Ficha técnica");
        datosTecnicos(t);
        espacio(13);
        titulo("Operaciones habilitadas");
        if (Reglas.PANOL.equals(t.estado)) boton("Despachar tablet", BLUE, () -> dialogoDespacho(t.serial, metodo));
        if (Reglas.LOCAL.equals(t.estado) || Reglas.EXTERNO.equals(t.estado))
            boton("Recibir devolución", GREEN, () -> dialogoDevolucion(t.serial, metodo));
        if (Reglas.SERVICIO.equals(t.estado))
            boton("Registrar fin de servicio", GREEN, () -> dialogoServicio(t.serial, metodo));
        boton("Compartir QR lógico (JSON)", NAVY, () -> compartirQr(t));
        espacio(12);
        titulo("Historial de movimientos");
        for (String item : db.historial(serial)) {
            TextView linea = texto(item, 13, MUTED, false);
            linea.setPadding(dp(9), dp(8), dp(9), dp(8));
            root.addView(linea);
            espacio(3);
        }
        espacio(12);
        boton("Volver al inventario", NAVY, this::catalogo);
        boton("Inicio", BLUE, this::inicio);
    }

    private LinearLayout contenedorFormulario(View... elementos) {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(dp(20), dp(6), dp(20), dp(7));
        for (View e : elementos) layout.addView(e, new LinearLayout.LayoutParams(-1, -2));
        return layout;
    }

    private EditText campo(String hint, String valor, boolean numerico) {
        EditText field = new EditText(this);
        field.setText(valor);
        field.setHint(hint);
        field.setTextSize(15);
        field.setSingleLine(true);
        if (numerico) field.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        return field;
    }

    private void dialogoDespacho(String serial, String metodo) {
        RadioGroup grupo = new RadioGroup(this);
        grupo.setOrientation(LinearLayout.VERTICAL);
        RadioButton oficina = new RadioButton(this);
        oficina.setText("Uso Local (Oficina)");
        oficina.setId(View.generateViewId());
        RadioButton home = new RadioButton(this);
        home.setText("Uso Externo (Home Office)");
        home.setId(View.generateViewId());
        grupo.addView(oficina); grupo.addView(home);
        grupo.check(oficina.getId());
        EditText legajo = campo("Legajo del empleado (obligatorio)", "", false);
        EditText tarea = campo("Tarea asignada (obligatoria para Home Office)", "", false);
        TextView alerta = texto("", 13, RED, true);
        AlertDialog dialog = new AlertDialog.Builder(this)
            .setTitle("CU-02 · Despachar " + serial)
            .setView(contenedorFormulario(grupo, legajo, tarea, alerta))
            .setPositiveButton("Confirmar despacho", null)
            .setNegativeButton("Cancelar", null).create();
        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            boolean fuera = grupo.getCheckedRadioButtonId() == home.getId();
            String motivo = Reglas.validarDespacho(db.buscar(serial), fuera,
                legajo.getText().toString(), tarea.getText().toString());
            if (motivo != null) { alerta.setText("⚠ " + motivo); return; }
            try {
                db.despachar(serial, fuera, legajo.getText().toString(), tarea.getText().toString(), metodo);
                dialog.dismiss(); exito("Despacho registrado."); ficha(serial, metodo);
            } catch (Exception e) { alerta.setText("⚠ " + e.getMessage()); }
        }));
        dialog.show();
    }

    private void dialogoDevolucion(String serial, String metodo) {
        RadioGroup grupo = new RadioGroup(this);
        grupo.setOrientation(LinearLayout.VERTICAL);
        RadioButton ok = new RadioButton(this);
        ok.setText("Buen estado → Reingresar al Pañol");
        ok.setId(View.generateViewId());
        RadioButton mal = new RadioButton(this);
        mal.setText("Con daños → Enviar a Servicio Técnico");
        mal.setId(View.generateViewId());
        grupo.addView(ok); grupo.addView(mal);
        grupo.check(ok.getId());
        new AlertDialog.Builder(this).setTitle("CU-03 · Recibir devolución")
            .setMessage("Verificá físicamente el dispositivo antes de confirmar.")
            .setView(contenedorFormulario(grupo))
            .setPositiveButton("Registrar devolución", (d, w) -> ejecutar(() -> {
                db.devolver(serial, grupo.getCheckedRadioButtonId() == mal.getId(), metodo);
                exito("Devolución y estado físico registrados."); ficha(serial, metodo);
            }))
            .setNegativeButton("Cancelar", null).show();
    }

    private void dialogoServicio(String serial, String metodo) {
        new AlertDialog.Builder(this).setTitle("CU-04 · Cierre de servicio")
            .setMessage("¿Confirmás que el equipo fue reparado o actualizado, inspeccionado y está apto para volver al Pañol?")
            .setPositiveButton("Aprobar reingreso", (d, w) -> ejecutar(() -> {
                db.finalizarServicio(serial, metodo);
                exito("Fin de servicio registrado."); ficha(serial, metodo);
            }))
            .setNegativeButton("Cancelar", null).show();
    }

    private void compartirQr(Tablet tablet) {
        ejecutar(() -> {
            Intent envio = new Intent(Intent.ACTION_SEND);
            envio.setType("text/plain");
            envio.putExtra(Intent.EXTRA_SUBJECT, "QR lógico · Tablet " + tablet.serial);
            envio.putExtra(Intent.EXTRA_TEXT, QrCodec.codificar(tablet));
            startActivity(Intent.createChooser(envio, "Compartir datos para generar etiqueta QR"));
        });
    }

    private void altaManual() {
        EditText serial = campo("Número de serie (ej. TAB-004)", "", false);
        EditText cpu = campo("Procesador (ej. Snapdragon 680)", "", false);
        EditText ram = campo("RAM GB (ej. 4)", "", true);
        EditText storage = campo("Almacenamiento GB (ej. 64)", "", true);
        EditText screen = campo("Pantalla pulgadas (ej. 10.1)", "", true);
        EditText ports = campo("Puertos (ej. USB-C, Jack 3.5)", "", false);
        EditText net = campo("Conectividad (ej. Wi-Fi, Bluetooth)", "", false);
        TextView alerta = texto("", 13, RED, true);
        AlertDialog dialog = new AlertDialog.Builder(this).setTitle("CU-01 · Alta manual de tablet")
            .setView(contenedorFormulario(serial, cpu, ram, storage, screen, ports, net, alerta))
            .setPositiveButton("Registrar alta", null)
            .setNegativeButton("Cancelar", null).create();
        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            try {
                Tablet t = new Tablet(serial.getText().toString(), cpu.getText().toString(),
                    Integer.parseInt(ram.getText().toString().trim()),
                    Integer.parseInt(storage.getText().toString().trim()),
                    Double.parseDouble(screen.getText().toString().trim().replace(',', '.')),
                    ports.getText().toString(), net.getText().toString());
                db.alta(t, "MANUAL");
                dialog.dismiss(); exito("Tablet registrada en Pañol."); ficha(t.serial, "MANUAL");
            } catch (Exception e) { alerta.setText("⚠ " +
                (e instanceof NumberFormatException ? "Revisá RAM, almacenamiento y pantalla (deben ser números)." : e.getMessage())); }
        }));
        dialog.show();
    }

    @Override public void onBackPressed() {
        inicio();
    }
}
