
Python version: Python 3.10.11
Para ejecutarlo: python space_war.py

[DESCRIPCIÓN JUEGO]

Space War es un emocionante juego de simulación donde controlas una nave espacial con el objetivo de esquivar obstáculos y sobrevivir el mayor tiempo posible. Utiliza algoritmos de inteligencia artificial generados por NEAT (NeuroEvolution of Augmenting Topologies) para aprender y mejorar las habilidades de la nave a lo largo del tiempo. El juego pone a prueba la capacidad del jugador para adaptarse a patrones complejos y tomar decisiones rápidas bajo presión, todo ello mientras disfruta de una experiencia de juego dinámica y visualmente atractiva.

[space_war.py]

Este es el archivo principal del juego, que inicializa el entorno de Pygame, crea la nave y los obstáculos, y gestiona la lógica del juego y la simulación. Para iniciar el juego, simplemente ejecuta el archivo con Python 3.10.11 o superior. El juego utilizará la configuración NEAT proporcionada para entrenar la inteligencia artificial de la nave, buscando maximizar su supervivencia esquivando obstáculos.

[config-feedforward.txt]

Este archivo contiene la configuración para el algoritmo NEAT, incluyendo parámetros como el tamaño de la población, la estructura de la red neuronal, y las tasas de mutación. Estos parámetros se pueden ajustar para experimentar con diferentes enfoques de aprendizaje y ver cómo afectan al rendimiento de la IA en el juego. La configuración predeterminada está diseñada para ofrecer un buen punto de partida, pero te animamos a experimentar y ajustar estos valores para optimizar el entrenamiento de tu nave espacial.
