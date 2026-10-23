# Computação Gráfica - Atividade GA (Python e PyOpenGL)

Aplicação desenvolvida em Python utilizando PyOpenGL e GLFW. O projeto implementa um pipeline gráfico 3D com carregamento de modelos (.obj/.mtl), mapeamento de textura, iluminação de Phong, câmera em primeira pessoa e movimentação cíclica de objetos por pontos de controle (waypoints).

---

## Funcionalidades

1. **Pipeline Gráfico e Shaders:**
   - Renderização de objetos 3D utilizando matrizes Model, View e Projection (GLM).
   - Shaders em GLSL para controle de iluminação e texturização.

2. **Iluminação de Phong:**
   - Suporte a componentes ambiente, difusa e especular com luzes configuráveis.

3. **Câmera:**
   - Movimentação em primeira pessoa via teclado (WASD) e orientação controlada pelo mouse.

4. **Trajetória Cíclica (Waypoints):**
   - Os objetos da cena seguem automaticamente uma sequência de pontos de controle de forma contínua e cíclica.
   - Pressionando a tecla `P`, a posição atual do objeto selecionado é adicionada como um novo ponto na trajetória.

---

## Controles

| Tecla / Ação | Função |
| :--- | :--- |
| **W, A, S, D** | Move a câmera |
| **Botão Direito do Mouse + Mover** | Olha ao redor |
| **TAB** | Alterna o objeto ativo na cena |
| **P** | Adiciona waypoint na posição atual do objeto |
| **X** | Liga/desliga a textura |
| **ESC** | Fecha a aplicação |

---

## Tecnologias

- Python 3.8+
- PyOpenGL
- GLFW
- PyGLM

---

## Como Executar

1. Instale as dependências:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate PyGLM glfw