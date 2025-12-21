Aquí tienes la **traducción completa al español**, conservando el formato original:

---

<h1 align="center">Static</h3>
<p align="center"> 🇺🇸 <a href="README.md"><b>English</b></a> | 🇪🇸 <a href="README_ES.md">Español</a> </p>
<p align="center">
  <img width="358" height="197" alt="static banner" src="https://github.com/user-attachments/assets/a488bd7e-d760-451e-974b-5fd852077d76" />
</p>

**Static** es una herramienta ligera de **reconocimiento de typosquatting**, escrita en Python puro y sin dependencias. Genera variaciones tipográficas comunes de un dominio objetivo y las verifica usando heurísticas de DNS y HTTP/HTTPS para identificar dominios potencialmente disponibles y comportamientos de redirección.

Diseñada para **testing de seguridad, OSINT e investigación defensiva**, Static se centra en la claridad, estabilidad y una salida limpia en la terminal.

---

## ✨ Características

* Cero dependencias (solo librería estándar de Python)
* Múltiples técnicas de generación de typos
* Comprobaciones de resolución DNS
* Sondeo HTTP/HTTPS con detección de redirecciones
* Visualización limpia del progreso en tiempo real (spinner + barra de progreso)
* Manejo elegante de Ctrl+C con resultados parciales
* Multiplataforma (Linux, macOS, Windows)

---

## 🛠️ Instalación

No requiere instalación.

Solo clona el repositorio y ejecuta el script:

```bash
git clone https://github.com/urdev4ever/static.git
cd static
python3 static.py
```

Se recomienda Python **3.8+**.

---

## 🚀 Uso

```bash
python3 static.py -d target.com
```

### Ejemplo

```bash
python3 static.py -d google.com
```

<img width="508" height="339" alt="static scanning" src="https://github.com/user-attachments/assets/0ba76b64-b38d-41e4-a40a-248dc0f6b016" />

Durante la ejecución, Static:

1. Genera variantes de dominios basadas en errores tipográficos
2. Comprueba la resolución DNS
3. Sondea endpoints HTTP y HTTPS
4. Muestra el progreso en tiempo real
5. Muestra los resultados categorizados

---

## 🧠 Cómo funciona

Static utiliza un enfoque basado en heurísticas:

### Generación de typos

* Eliminación de caracteres
* Duplicación de caracteres
* Intercambio de caracteres adyacentes
* Reemplazo por teclas adyacentes en teclado QWERTY
* Variaciones comunes de TLD (`.com`, `.net`, `.org`, `.co`, `.io`)
* Eliminación del punto en dominios multinivel

### Lógica de verificación de dominios

* **Sin resolución DNS** → Marcado como *Potencialmente disponible*
* **DNS resuelve + redirección HTTP** → Marcado como *Redirección*
* **DNS resuelve + respuesta HTTP** → Marcado como *Ocupado*

> Nota: “Potencialmente disponible” **no** garantiza disponibilidad. La verificación final debe hacerse mediante WHOIS o un registrador de dominios.

---

## 📊 Categorías de salida

* **Dominios potencialmente disponibles**

  * No se detectó resolución DNS

* **Dominios con redirección**

  * Dominios que redirigen a otro host

* **Dominios ocupados**

  * Dominios que resuelven y responden normalmente

Al final se muestra un resumen con la duración del escaneo y la velocidad.

<img width="424" height="547" alt="static results" src="https://github.com/user-attachments/assets/123f512d-a7fc-4156-ab61-764ea079c07e" />

---

## 🔐 Nota sobre SSL

La verificación de certificados SSL está intencionalmente deshabilitada para las comprobaciones HTTPS.
Esto se hace para garantizar estabilidad y cobertura durante el reconocimiento y evitar fallos causados por certificados mal configurados.

---

## 🧪 Requisitos

* Python 3.x
* Sin librerías externas
* Sin claves API
* Sin archivos de configuración

---

## 🧭 Hoja de ruta / Mejoras futuras

Las siguientes funciones están planificadas para versiones futuras:

* Selección personalizada de TLD mediante flags (ej. `--tlds com,net,org`)
* Opción para deshabilitar sondeo HTTP (`--no-http`)
* Modo de salida JSON para automatización y pipelines
* Soporte de salida a archivo (`--output results.txt` / `.json`)
* Escaneo multihilo opcional con límites de velocidad
* Técnicas adicionales de typos
* Heurísticas mejoradas para disponibilidad de dominios

Estas funciones se introducirán gradualmente manteniendo la herramienta ligera y sin dependencias.

---

## ⚠️ Descargo de responsabilidad

Static está destinada **exclusivamente para testing de seguridad defensivo, investigación y fines educativos**.
El autor no aprueba ni respalda el uso malicioso.

Eres responsable de cumplir con todas las leyes y regulaciones aplicables.

---

hecho con <3 por URDev
