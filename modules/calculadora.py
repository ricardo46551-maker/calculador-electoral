class CalculadoraElectoral:
    def __init__(self):
        # Valor UIT estimado para 2025 (ajustable)
        self.UIT = 5350 
        
        # Porcentajes de ley
        self.PORCENTAJES = {
            "miembro_mesa": 10.0,       # 10% UIT
            "No Pobre": 2.0,            # 2% UIT
            "Pobre": 1.0,               # 1% UIT
            "Pobre Extremo": 0.5        # 0.5% UIT
        }

    def calcular_deuda(self, es_miembro_mesa, voto, categoria_distrito):
        """
        Calcula la deuda total y devuelve el desglose.
        """
        deuda_total = 0.0
        detalles = []

        # 1. Multa por No Instalar Mesa (Si fue sorteado y no fue)
        if es_miembro_mesa:
            monto = self.UIT * (self.PORCENTAJES["miembro_mesa"] / 100)
            deuda_total += monto
            detalles.append(f"Multa Miembro de Mesa (10%): S/ {monto:.2f}")

        # 2. Multa por No Votar
        if not voto:
            # Buscamos el porcentaje según la categoría del distrito
            porcentaje = self.PORCENTAJES.get(categoria_distrito, 2.0) # 2.0 por defecto
            monto = self.UIT * (porcentaje / 100)
            deuda_total += monto
            detalles.append(f"Multa por No Votar ({categoria_distrito} - {porcentaje}%): S/ {monto:.2f}")
        
        return deuda_total, detalles