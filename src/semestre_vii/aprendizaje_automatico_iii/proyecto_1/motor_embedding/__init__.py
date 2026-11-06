"""Reconocimiento de pan por embeddings, separado en precarga (galería) e inferencia (en vivo).

recorte, encoder y vecinos viven aquí porque ambas fases deben usar exactamente el mismo
código: si el recorte o el encoder difieren, los vectores dejan de ser comparables.
"""
