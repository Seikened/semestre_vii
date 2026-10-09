export function espejo(punto, info) {
  const envolver = (valor, longitud, centro) => ((valor + centro) % longitud + longitud) % longitud - centro;
  return {
    fila: envolver(-punto.fila, info.alto, info.dc_fila),
    columna: envolver(-punto.columna, info.ancho, info.dc_columna),
    radio: punto.radio,
  };
}

export class Vista {
  constructor(canvas, info, opciones = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.info = info;
    this.zoom = opciones.zoom || 1;
    this.pan = { x: 0, y: 0 };
    this.opciones = opciones;
    this.puntos = [];
    this.seleccionado = null;
    this.hover = null;
    this.radio = 8;
    this.carga = 0;
    new ResizeObserver(() => this.dibujar()).observe(canvas);
    canvas.addEventListener("pointerdown", (evento) => this.iniciar(evento));
    canvas.addEventListener("pointermove", (evento) => this.mover(evento));
    canvas.addEventListener("pointerup", (evento) => this.terminar(evento));
    canvas.addEventListener("pointercancel", () => { this.arrastre = null; });
    canvas.addEventListener("pointerleave", () => {
      this.hover = null;
      this.dibujar();
    });
    canvas.addEventListener("wheel", (evento) => {
      evento.preventDefault();
      this.zoom = Math.min(16, Math.max(1, this.zoom * (evento.deltaY < 0 ? 1.2 : 1 / 1.2)));
      this.opciones.vistaCambiada?.(this);
      this.dibujar();
    }, { passive: false });
  }

  async imagen(url) {
    const carga = ++this.carga;
    const imagen = new Image();
    imagen.src = url;
    await imagen.decode();
    if (carga === this.carga) {
      this.fondo = imagen;
      this.dibujar();
    }
  }

  escala() {
    return Math.min(this.canvas.clientWidth / this.info.ancho, this.canvas.clientHeight / this.info.alto) * this.zoom;
  }

  posicion(evento) {
    const rect = this.canvas.getBoundingClientRect();
    return { x: evento.clientX - rect.left, y: evento.clientY - rect.top };
  }

  coordenada(evento) {
    const posicion = this.posicion(evento);
    const escala = this.escala();
    return {
      fila: Math.round((posicion.y - this.canvas.clientHeight / 2 - this.pan.y) / escala),
      columna: Math.round((posicion.x - this.canvas.clientWidth / 2 - this.pan.x) / escala),
    };
  }

  iniciar(evento) {
    if (evento.button !== 0) return;
    this.canvas.focus();
    this.canvas.setPointerCapture(evento.pointerId);
    this.arrastre = { ...this.posicion(evento), pan: { ...this.pan }, movido: false };
  }

  mover(evento) {
    if (this.arrastre) {
      const posicion = this.posicion(evento);
      const dx = posicion.x - this.arrastre.x;
      const dy = posicion.y - this.arrastre.y;
      if (Math.hypot(dx, dy) > 4) this.arrastre.movido = true;
      if (this.arrastre.movido) {
        this.pan = { x: this.arrastre.pan.x + dx, y: this.arrastre.pan.y + dy };
        this.opciones.vistaCambiada?.(this);
      }
    }
    this.hover = this.coordenada(evento);
    this.opciones.cursor?.(this.hover);
    this.dibujar();
  }

  terminar(evento) {
    if (!this.arrastre) return;
    if (!this.arrastre.movido) {
      const punto = this.coordenada(evento);
      if (this.valido(punto)) this.opciones.clic?.(punto);
    }
    this.arrastre = null;
  }

  valido(punto) {
    return punto.fila >= -this.info.dc_fila && punto.fila <= this.info.alto - 1 - this.info.dc_fila
      && punto.columna >= -this.info.dc_columna && punto.columna <= this.info.ancho - 1 - this.info.dc_columna;
  }

  ajustarZoom(valor) {
    this.zoom = Number(valor);
    this.pan = { x: 0, y: 0 };
    this.dibujar();
  }

  dibujar() {
    const ancho = this.canvas.clientWidth;
    const alto = this.canvas.clientHeight;
    if (!ancho || !alto) return;
    const dpr = window.devicePixelRatio || 1;
    if (this.canvas.width !== Math.round(ancho * dpr) || this.canvas.height !== Math.round(alto * dpr)) {
      this.canvas.width = Math.round(ancho * dpr);
      this.canvas.height = Math.round(alto * dpr);
    }
    const ctx = this.ctx;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#0d1819";
    ctx.fillRect(0, 0, ancho, alto);
    ctx.translate(ancho / 2 + this.pan.x, alto / 2 + this.pan.y);
    const escala = this.escala();
    ctx.scale(escala, escala);
    if (this.fondo) ctx.drawImage(this.fondo, -this.info.dc_columna - .5, -this.info.dc_fila - .5);
    if (!this.opciones.clic) return;
    ctx.lineWidth = 1 / escala;
    ctx.strokeStyle = "rgba(185,213,201,.28)";
    ctx.beginPath();
    ctx.moveTo(-7 / escala, 0);
    ctx.lineTo(7 / escala, 0);
    ctx.moveTo(0, -7 / escala);
    ctx.lineTo(0, 7 / escala);
    ctx.stroke();
    for (const punto of this.puntos) {
      const elegido = punto.id === this.seleccionado;
      this.circulo(punto, punto.activo ? "#efad46" : "#8b9994", elegido);
      this.circulo(espejo(punto, this.info), punto.activo ? "#99cfb8" : "#8b9994", elegido);
    }
    if (this.hover && !this.arrastre && this.valido(this.hover)) {
      ctx.setLineDash([3 / escala, 3 / escala]);
      const punto = { ...this.hover, radio: this.radio };
      this.circulo(punto, "rgba(239,173,70,.6)", false);
      this.circulo(espejo(punto, this.info), "rgba(153,207,184,.6)", false);
      ctx.setLineDash([]);
    }
  }

  circulo(punto, color, elegido) {
    const ctx = this.ctx;
    const escala = this.escala();
    const { alto, ancho } = this.info;
    ctx.lineWidth = (elegido ? 2 : 1) / escala;
    ctx.strokeStyle = color;
    for (const dy of [-alto, 0, alto]) for (const dx of [-ancho, 0, ancho]) {
      ctx.beginPath();
      ctx.arc(punto.columna + dx, punto.fila + dy, punto.radio, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(punto.columna, punto.fila, 2.4 / escala, 0, Math.PI * 2);
    ctx.fill();
  }
}
