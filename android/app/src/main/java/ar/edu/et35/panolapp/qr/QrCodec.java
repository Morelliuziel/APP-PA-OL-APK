package ar.edu.et35.panolapp.qr;

import ar.edu.et35.panolapp.domain.Reglas;
import ar.edu.et35.panolapp.domain.Tablet;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** QR: datos técnicos declarativos, nunca estado/legajo/tarea (son dinámicos). */
public final class QrCodec {
    private QrCodec() {}

    /** Ej.: JSON o SERIAL|CPU|RAM|STORAGE|PANTALLA|PUERTOS|CONECTIVIDAD */
    public static Tablet decodificar(String bruto) {
        if (bruto == null || bruto.trim().isEmpty()) throw new IllegalArgumentException("QR vacío.");
        if (bruto.length() > 4096) throw new IllegalArgumentException("Contenido QR demasiado largo.");
        String texto = bruto.trim();
        Tablet t;
        try {
            if (texto.startsWith("{")) {
                JSONObject o = new JSONObject(texto);
                String version = o.optString("version", "1");
                if (!"1".equals(version)) throw new IllegalArgumentException("Versión de QR no compatible.");
                t = new Tablet(
                    o.getString("serial"), o.getString("procesador"),
                    o.getInt("ram_gb"), o.getInt("almacenamiento_gb"),
                    o.getDouble("pantalla_pulgadas"),
                    lista(o, "puertos"), lista(o, "conectividad"));
            } else {
                String[] campos = texto.split("\\|", -1);
                if (campos.length != 7) throw new IllegalArgumentException("QR delimitado: se esperaban 7 campos separados por |.");
                t = new Tablet(campos[0], campos[1], Integer.parseInt(campos[2].trim()),
                    Integer.parseInt(campos[3].trim()), Double.parseDouble(campos[4].trim()),
                    campos[5], campos[6]);
            }
            Reglas.validarAlta(t);
            return t;
        } catch (JSONException | NumberFormatException e) {
            throw new IllegalArgumentException("QR inválido: datos técnicos incompletos o mal formados.", e);
        }
    }

    private static String lista(JSONObject o, String clave) throws JSONException {
        Object valor = o.get(clave);
        if (valor instanceof JSONArray) {
            JSONArray a = (JSONArray) valor;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < a.length(); i++) {
                if (i > 0) sb.append(", ");
                sb.append(a.getString(i).trim());
            }
            return sb.toString();
        }
        return o.getString(clave);
    }

    public static String codificar(Tablet t) {
        Reglas.validarAlta(t);
        try {
            JSONObject o = new JSONObject();
            o.put("version", "1"); o.put("serial", t.serial);
            o.put("procesador", t.procesador); o.put("ram_gb", t.ramGb);
            o.put("almacenamiento_gb", t.almacenamientoGb);
            o.put("pantalla_pulgadas", t.pantallaPulgadas);
            o.put("puertos", toArray(t.puertos));
            o.put("conectividad", toArray(t.conectividad));
            return o.toString();
        } catch (JSONException e) {
            throw new IllegalStateException("No se pudo serializar el QR.", e);
        }
    }

    private static JSONArray toArray(String csv) {
        JSONArray a = new JSONArray();
        for (String parte : csv.split(",")) a.put(parte.trim());
        return a;
    }
}
