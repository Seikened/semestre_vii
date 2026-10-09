import { Vista, espejo } from "/vista.js";

const $ = (id) => document.getElementById(id);
const estado = { puntos: [], seleccionado: null, siguienteId: 1, historial: [], revision: 0 };
let info, fft, original, filtrada, imagenFFTOriginal, imagenFFTFiltrada;
let ocupado = false;
let pendiente = false;
let temporizador;
let listo = false;

function avisar(texto, error = false) {
  $("estado").textContent = texto;
  $("estado").parentElement.classList.toggle("error", error);
  $("reintentar").hidden = !error;
}

function codigo() {
  const lineas = [
    "from semestre_vii.vision_de_maquina.ejercicio_fourier.saco import cargar_saco_cuadrado",
    "", "espectro = cargar_saco_cuadrado().fft()",
  ];
  for (const punto of estado.puntos.filter((p) => p.activo)) {
    lineas.push(`espectro = espectro.notch_ideal(centros=[(${punto.fila}, ${punto.columna})], radio=${punto.radio})`);
  }
  lineas.push("filtrada = espectro.inversa(valor_absoluto=True, clip=True)");
  return lineas.join("\n");
}

function recordar() {
  estado.historial.push({ puntos: structuredClone(estado.puntos), seleccionado: estado.seleccionado });
  if (estado.historial.length > 80) estado.historial.shift();
}

function confirmar() {
  estado.revision += 1;
  renderizar();
  clearTimeout(temporizador);
  $("descargar").removeAttribute("href");
  $("descargar").setAttribute("aria-disabled", "true");
  avisar("Aplicando tu filtro…");
  temporizador = setTimeout(aplicar, 160);
}

function validar(punto) {
  if (![punto.fila, punto.columna, punto.radio].every(Number.isFinite) || punto.radio <= 0) {
    throw new Error("Usa fila, columna y radio finitos, con radio mayor que cero.");
  }
  if (!fft.valido(punto)) throw new Error("El punto está fuera del espectro.");
}

function agregar(punto) {
  try {
    validar(punto);
    if (estado.puntos.length >= 128) throw new Error("El experimento admite hasta 128 pares.");
    recordar();
    const nuevo = { ...punto, id: estado.siguienteId++, activo: true };
    estado.puntos.push(nuevo);
    estado.seleccionado = nuevo.id;
    confirmar();
  } catch (error) { avisar(error.message, true); }
}

function seleccionar(id) {
  estado.seleccionado = id;
  renderizar();
}

function cambiar(id, cambio) {
  const punto = estado.puntos.find((p) => p.id === id);
  if (!punto) return;
  try {
    validar({ ...punto, ...cambio });
    recordar();
    Object.assign(punto, cambio);
    confirmar();
  } catch (error) {
    avisar(error.message, true);
    renderizar();
  }
}

function quitar(id) {
  recordar();
  estado.puntos = estado.puntos.filter((p) => p.id !== id);
  if (estado.seleccionado === id) estado.seleccionado = null;
  confirmar();
}

function renderizar() {
  fft.puntos = estado.puntos;
  fft.seleccionado = estado.seleccionado;
  fft.dibujar();
  $("cantidad").textContent = estado.puntos.length;
  $("deshacer").disabled = estado.historial.length === 0;
  $("vaciar").disabled = estado.puntos.length === 0;
  $("guardar").disabled = estado.puntos.length === 0;
  $("codigo").textContent = codigo();
  $("lista").replaceChildren();
  if (!estado.puntos.length) {
    const vacio = document.createElement("p");
    vacio.className = "vacio";
    vacio.textContent = "Marca un punto sobre Fourier para empezar.";
    $("lista").append(vacio);
  }
  estado.puntos.forEach((punto, indice) => {
    const pareja = espejo(punto, info);
    const fila = document.createElement("div");
    fila.className = `par${punto.id === estado.seleccionado ? " seleccionado" : ""}${punto.activo ? "" : " inactivo"}`;
    const activo = document.createElement("input");
    activo.type = "checkbox";
    activo.checked = punto.activo;
    activo.setAttribute("aria-label", `Activar par ${indice + 1}`);
    activo.addEventListener("change", () => cambiar(punto.id, { activo: activo.checked }));
    const seleccion = document.createElement("button");
    seleccion.className = "seleccion";
    const nombre = document.createElement("span");
    nombre.className = "nombre-par";
    nombre.textContent = `Par ${String(indice + 1).padStart(2, "0")} · (${punto.fila}, ${punto.columna})`;
    const posicion = document.createElement("span");
    posicion.className = "posicion";
    posicion.textContent = `Simétrico (${pareja.fila}, ${pareja.columna})`;
    seleccion.append(nombre, posicion);
    seleccion.addEventListener("click", () => seleccionar(punto.id));
    const radio = document.createElement("label");
    radio.className = "radio-par";
    radio.append("r");
    const numero = document.createElement("input");
    numero.type = "number";
    numero.min = ".5";
    numero.step = ".5";
    numero.value = punto.radio;
    numero.setAttribute("aria-label", `Radio del par ${indice + 1}`);
    numero.addEventListener("change", () => cambiar(punto.id, { radio: numero.valueAsNumber }));
    radio.append(numero);
    const eliminar = document.createElement("button");
    eliminar.className = "quitar";
    eliminar.textContent = "×";
    eliminar.setAttribute("aria-label", `Quitar par ${indice + 1}`);
    eliminar.addEventListener("click", () => quitar(punto.id));
    fila.append(activo, seleccion, radio, eliminar);
    $("lista").append(fila);
  });
}

async function aplicar() {
  if (ocupado) {
    pendiente = true;
    return;
  }
  ocupado = true;
  pendiente = false;
  const revision = estado.revision;
  const puntos = estado.puntos.filter((p) => p.activo).map(({ fila, columna, radio }) => ({ fila, columna, radio }));
  try {
    const respuesta = await fetch("/api/filtrar", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ puntos }),
    });
    const resultado = await respuesta.json();
    if (!respuesta.ok) throw new Error(resultado.mensaje || "No se pudo calcular el filtro.");
    if (revision !== estado.revision) {
      pendiente = true;
      return;
    }
    imagenFFTFiltrada = resultado.espectro;
    await Promise.all([
      filtrada.imagen(resultado.imagen),
      fft.imagen($("fft-original").checked ? imagenFFTOriginal : imagenFFTFiltrada),
    ]);
    if (revision !== estado.revision) {
      pendiente = true;
      return;
    }
    const filtro = encodeURIComponent(JSON.stringify({ puntos }));
    $("descargar").href = `/api/filtrada.png?filtro=${filtro}`;
    $("descargar").setAttribute("aria-disabled", "false");
    const cantidad = `${puntos.length} ${puntos.length === 1 ? "par" : "pares"}`;
    $("estadistica").textContent = `${cantidad} · ${resultado.porcentaje_rechazado.toFixed(2)} % rechazado`;
    $("aviso-dc").hidden = !resultado.dc_rechazada;
    avisar(puntos.length ? "Filtro aplicado. Compara ambas imágenes." : "Imagen completa: agrega tu primer par.");
  } catch (error) {
    if (revision === estado.revision) avisar(error.message, true);
  } finally {
    ocupado = false;
    if (pendiente || revision !== estado.revision) aplicar();
  }
}

function sincronizar(vista, otra) {
  otra.zoom = vista.zoom;
  otra.pan = { ...vista.pan };
  otra.dibujar();
}

function radioNuevo(valor) {
  if (!Number.isFinite(valor) || valor <= 0) return;
  fft.radio = valor;
  $("radio-nuevo").value = valor;
  $("radio-rango").value = Math.min(80, valor);
  $("radio-manual").value = valor;
  fft.dibujar();
}

function conectar() {
  $("zoom-fft").addEventListener("change", (evento) => fft.ajustarZoom(evento.target.value));
  $("zoom-imagen").addEventListener("change", (evento) => {
    original.ajustarZoom(evento.target.value);
    filtrada.ajustarZoom(evento.target.value);
  });
  $("fft-original").addEventListener("change", () => {
    fft.imagen($("fft-original").checked ? imagenFFTOriginal : imagenFFTFiltrada).catch((error) => avisar(error.message, true));
  });
  $("radio-rango").addEventListener("input", (evento) => radioNuevo(Number(evento.target.value)));
  $("radio-nuevo").addEventListener("change", (evento) => radioNuevo(evento.target.valueAsNumber));
  $("deshacer").addEventListener("click", () => {
    const anterior = estado.historial.pop();
    if (!anterior) return;
    estado.puntos = anterior.puntos;
    estado.seleccionado = anterior.seleccionado;
    confirmar();
  });
  $("vaciar").addEventListener("click", () => {
    recordar();
    estado.puntos = [];
    estado.seleccionado = null;
    confirmar();
  });
  $("formulario").addEventListener("submit", (evento) => {
    evento.preventDefault();
    agregar({ fila: $("fila").valueAsNumber, columna: $("columna").valueAsNumber, radio: $("radio-manual").valueAsNumber });
  });
  $("fourier").addEventListener("keydown", (evento) => {
    if (estado.seleccionado === null) return;
    if (evento.key === "Delete" || evento.key === "Backspace") {
      evento.preventDefault();
      quitar(estado.seleccionado);
    }
    const desplazamientos = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    if (desplazamientos[evento.key]) {
      evento.preventDefault();
      const punto = estado.puntos.find((p) => p.id === estado.seleccionado);
      const [dy, dx] = desplazamientos[evento.key];
      const paso = evento.shiftKey ? 5 : 1;
      cambiar(punto.id, { fila: punto.fila + dy * paso, columna: punto.columna + dx * paso });
    }
  });
  $("copiar").addEventListener("click", async () => {
    $("codigo").parentElement.open = true;
    avisar("Código disponible en «Ver el código del filtro».");
    try {
      await navigator.clipboard.writeText(codigo());
      avisar("Código copiado para usarlo en la librería.");
    } catch {
      avisar("Abre «Ver el código del filtro» para copiarlo manualmente.", true);
    }
  });
  $("guardar").addEventListener("click", () => {
    const puntos = estado.puntos.map(({ fila, columna, radio, activo }) => ({ fila, columna, radio, activo }));
    const filtro = encodeURIComponent(JSON.stringify({ puntos }));
    const enlace = document.createElement("a");
    enlace.href = `/api/puntos.json?filtro=${filtro}`;
    enlace.download = "notches_saco.json";
    enlace.click();
  });
  $("cargar").addEventListener("click", () => $("archivo").click());
  $("archivo").addEventListener("change", async (evento) => {
    try {
      const archivo = evento.target.files[0];
      if (!archivo) return;
      if (archivo.size > 65536) throw new Error("El archivo debe ocupar hasta 64 KiB.");
      const datos = JSON.parse(await archivo.text());
      if (datos.imagen !== info.nombre || datos.alto !== info.alto || datos.ancho !== info.ancho || datos.recorte !== "inferior") {
        throw new Error("Los puntos deben corresponder al cuadrado inferior de este saco.");
      }
      if (!Array.isArray(datos.puntos) || datos.puntos.length > 128) throw new Error("Se necesitan hasta 128 pares.");
      const puntos = datos.puntos.map((punto) => {
        validar(punto);
        if (punto.activo !== undefined && typeof punto.activo !== "boolean") throw new Error("El estado activo debe ser booleano.");
        return { fila: punto.fila, columna: punto.columna, radio: punto.radio, activo: punto.activo !== false, id: estado.siguienteId++ };
      });
      recordar();
      estado.puntos = puntos;
      estado.seleccionado = null;
      confirmar();
    } catch (error) { avisar(`No se cargaron los puntos: ${error.message}`, true); }
    finally { evento.target.value = ""; }
  });
}

async function iniciar() {
  try {
    const respuesta = await fetch("/api/info");
    if (!respuesta.ok) throw new Error("No se pudo cargar la información del saco.");
    info = await respuesta.json();
    fft = new Vista($("fourier"), info, {
      zoom: 4,
      cursor: (punto) => { $("coordenadas").textContent = `Fila ${punto.fila} · Columna ${punto.columna}`; },
      clic: (punto) => {
        const cercano = estado.puntos.find((p) => {
          const simetrico = espejo(p, info);
          return Math.min(Math.hypot(p.fila - punto.fila, p.columna - punto.columna), Math.hypot(simetrico.fila - punto.fila, simetrico.columna - punto.columna)) * fft.escala() < 7;
        });
        if (cercano) seleccionar(cercano.id);
        else agregar({ ...punto, radio: fft.radio });
      },
    });
    original = new Vista($("original"), info, { vistaCambiada: (vista) => sincronizar(vista, filtrada) });
    filtrada = new Vista($("filtrada"), info, { vistaCambiada: (vista) => sincronizar(vista, original) });
    imagenFFTOriginal = "/api/espectro.png";
    imagenFFTFiltrada = imagenFFTOriginal;
    await Promise.all([fft.imagen(imagenFFTOriginal), original.imagen("/api/original.png"), filtrada.imagen("/api/original.png")]);
    $("fila").min = -info.dc_fila;
    $("fila").max = info.alto - 1 - info.dc_fila;
    $("columna").min = -info.dc_columna;
    $("columna").max = info.ancho - 1 - info.dc_columna;
    $("fuente").textContent = `${info.nombre} · ${info.ancho}×${info.alto} · cuadrado inferior`;
    $("cargar").disabled = false;
    $("copiar").disabled = false;
    conectar();
    listo = true;
    renderizar();
    await aplicar();
  } catch (error) { avisar(`No se pudo abrir el laboratorio: ${error.message}`, true); }
}

$("reintentar").addEventListener("click", () => listo ? aplicar() : iniciar());
iniciar();
