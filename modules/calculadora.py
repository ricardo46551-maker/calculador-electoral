class CalculadoraElectoral:
    def __init__(self):
        # Valor oficial UIT 2025 según D.S. N° 260-2024-EF
        self.UIT = 5350.00 
        
        # Porcentajes según Ley N° 28859
        self.PORCENTAJES = {
            # Multa única por no asistir o negarse a integrar la mesa (5% UIT)
            "miembro_mesa": 5.0,
            
            # Escala diferenciada por clasificación del distrito (INEI)
            "No Pobre": 2.0,            # 2% UIT
            "Pobre": 1.0,               # 1% UIT
            "Pobre Extremo": 0.5        # 0.5% UIT
        }

    def calcular_deuda(self, es_miembro_mesa, voto, categoria_distrito):
        """
        Calcula la deuda electoral basada en la UIT vigente.
        Retorna: (monto_total, lista_de_detalles)
        """
        deuda_total = 0.0
        detalles = []

        # 1. Multa por No Instalar Mesa (Si fue sorteado y no asistió)
        # Nota: Esta multa es independiente de si votó o no.
        if es_miembro_mesa:
            monto_mesa = self.UIT * (self.PORCENTAJES["miembro_mesa"] / 100)
            deuda_total += monto_mesa
            detalles.append(f"Multa Miembro de Mesa (5% UIT): S/ {monto_mesa:.2f}")

        # 2. Multa por No Votar (Omiso al sufragio)
        if not voto:
            # Buscamos el porcentaje según la categoría del distrito.
            # Si la categoría no existe en el diccionario, asumimos "No Pobre" (2%) por defecto.
            porcentaje = self.PORCENTAJES.get(categoria_distrito, 2.0)
            
            monto_voto = self.UIT * (porcentaje / 100)
            deuda_total += monto_voto
            
            detalles.append(f"Multa por No Votar ({categoria_distrito} - {porcentaje}% UIT): S/ {monto_voto:.2f}")
        
        return deuda_total, detalles