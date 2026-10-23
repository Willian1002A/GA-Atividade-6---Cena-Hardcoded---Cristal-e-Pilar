import glfw
import glm
from OpenGL.GL import *

from camera import Camera
from shader import Shader
from obj_loader import load_obj, parse_mtl, load_texture


class Object3D:
    def __init__(self, name, vao, vertex_count, texture_id, material, pos, rot, scale, waypoints=None, speed=1.0):
        self.name = name
        self.vao = vao
        self.vertex_count = vertex_count
        self.texture_id = texture_id
        self.material = material

        self.pos = glm.vec3(*pos)
        self.rot = glm.vec3(*rot)
        self.scale = glm.vec3(*scale)

        # Sistema de Trajetória Cíclica por Pontos de Controle
        self.waypoints = [glm.vec3(*p) for p in waypoints] if waypoints else [glm.vec3(*pos)]
        self.current_wp_idx = 0
        self.speed = speed
        self.t_segment = 0.0

    def update_trajectory(self, dt):
        if len(self.waypoints) < 2:
            return

        p_start = self.waypoints[self.current_wp_idx]
        next_idx = (self.current_wp_idx + 1) % len(self.waypoints)
        p_end = self.waypoints[next_idx]

        segment_vector = p_end - p_start
        segment_length = glm.length(segment_vector)

        if segment_length > 0.0001:
            self.t_segment += (self.speed * dt) / segment_length
            if self.t_segment >= 1.0:
                self.t_segment = 0.0
                self.current_wp_idx = next_idx
                p_start = self.waypoints[self.current_wp_idx]
                next_idx = (self.current_wp_idx + 1) % len(self.waypoints)
                p_end = self.waypoints[next_idx]
                segment_vector = p_end - p_start

            self.pos = p_start + segment_vector * min(self.t_segment, 1.0)


camera = None
objects = []
lights = []
selected_idx = 0
use_texture = True
keys = {}

mouse_active = False
last_mouse_x = 0.0
last_mouse_y = 0.0
first_mouse = True


def key_callback(window, key, scancode, action, mods):
    global selected_idx, use_texture

    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_TAB:
            selected_idx = (selected_idx + 1) % len(objects)
            obj = objects[selected_idx]
            print(f"Objeto selecionado [{selected_idx + 1}]: {obj.name} | Waypoints: {len(obj.waypoints)}")
        elif key == glfw.KEY_X:
            use_texture = not use_texture
            print(f"Textura: {'ON' if use_texture else 'OFF'}")
        elif key == glfw.KEY_P:
            if objects:
                obj = objects[selected_idx]
                obj.waypoints.append(glm.vec3(obj.pos))
                print(f"Ponto adicionado ao objeto '{obj.name}': {obj.pos.x:.2f}, {obj.pos.y:.2f}, {obj.pos.z:.2f}")

    if action == glfw.PRESS:
        keys[key] = True
    elif action == glfw.RELEASE:
        keys[key] = False


def mouse_button_callback(window, button, action, mods):
    global mouse_active, first_mouse
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            mouse_active = True
            first_mouse = True
        elif action == glfw.RELEASE:
            mouse_active = False


def cursor_pos_callback(window, xpos, ypos):
    global last_mouse_x, last_mouse_y, first_mouse
    if mouse_active:
        if first_mouse:
            last_mouse_x = xpos
            last_mouse_y = ypos
            first_mouse = False
        dx = xpos - last_mouse_x
        dy = last_mouse_y - ypos
        last_mouse_x = xpos
        last_mouse_y = ypos
        camera.process_mouse(dx, dy)


def process_inputs(dt):
    if keys.get(glfw.KEY_W, False): camera.process_keyboard("FORWARD", dt)
    if keys.get(glfw.KEY_S, False): camera.process_keyboard("BACKWARD", dt)
    if keys.get(glfw.KEY_A, False): camera.process_keyboard("LEFT", dt)
    if keys.get(glfw.KEY_D, False): camera.process_keyboard("RIGHT", dt)


def setup_scene_hardcoded():
    global camera, lights, objects

    # Configuração da Câmera
    camera = Camera(position=[0.0, 3.2, 6.8], yaw=-90.0, pitch=-18.0, fov=45.0)

    # Configuração de Luzes Phong
    lights = [
        {
            "enabled": True,
            "position": [3.5, 5.0, 3.5],
            "ambient": [0.08, 0.08, 0.09],
            "diffuse": [0.95, 0.90, 0.82],
            "specular": [1.0, 0.98, 0.90],
            "constant": 1.0, "linear": 0.09, "quadratic": 0.032
        }
    ]

    # Definição direta dos objetos da cena (Cristal e Pilar) com waypoints cíclicos
    scene_data = [
        {
            "name": "Cristal Místico",
            "obj_path": "assets/crystal.obj",
            "mtl_path": "assets/crystal.mtl",
            "texture_path": "assets/crystal_diffuse.png",
            "position": [0.0, 1.8, 0.0],
            "rotation": [0.0, 45.0, 0.0],
            "scale": [0.55, 0.55, 0.55],
            "trajectory_points": [
                [-0.8, 1.4, -0.6],
                [1.0, 2.4, -0.4],
                [-1.0, 2.6, 0.4],
                [0.8, 1.5, 0.6]
            ]
        }
    ]

    for item in scene_data:
        # load_obj retorna (vao, vbo, vertex_count) corretos
        vao, vbo, vertex_count = load_obj(item["obj_path"])
        
        # Pega o material diretamente do dicionário hardcoded
        material = parse_mtl(item.get("mtl_path"))
        tex_path = item.get("texture_path") or material["texture_path"]
        tex_id = load_texture(tex_path)

        obj = Object3D(
            name=item["name"],
            vao=vao,
            vertex_count=vertex_count,
            texture_id=tex_id,
            material=material,
            pos=item["position"],
            rot=item["rotation"],
            scale=item["scale"],
            waypoints=item["trajectory_points"],
            speed=1.2
        )
        objects.append(obj)


def main():
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(1280, 720, "GA Atividade 6 - Cena Hardcoded - Cristal e Pilar", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

    shader = Shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
    setup_scene_hardcoded()

    print("Aplicação iniciada com objetos fixos no código!")
    print("Controles: WASD (Câmera), TAB (Trocar objeto ativo), P (Adicionar waypoint), ESC (Sair)")

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        process_inputs(dt)

        for obj in objects:
            obj.update_trajectory(dt)

        if objects:
            cur = objects[selected_idx]
            glfw.set_window_title(window, f"Objeto: [{selected_idx+1}] {cur.name} | Posição: [{cur.pos.x:.2f}, {cur.pos.y:.2f}, {cur.pos.z:.2f}]")

        width, height = glfw.get_framebuffer_size(window)
        glViewport(0, 0, width, height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader.use()

        # Matrizes de transformação
        projection = camera.get_projection_matrix(width / max(height, 1))
        view = camera.get_view_matrix()

        shader.set_mat4("projection", projection)
        shader.set_mat4("view", view)
        shader.set_vec3("viewPos", camera.position)

        for i, light in enumerate(lights[:3]):
            shader.set_bool(f"lights[{i}].enabled", light.get("enabled", True))
            shader.set_vec3(f"lights[{i}].position", light.get("position", [3.5, 5.0, 3.5]))
            shader.set_vec3(f"lights[{i}].ambient", light.get("ambient", [0.08, 0.08, 0.09]))
            shader.set_vec3(f"lights[{i}].diffuse", light.get("diffuse", [0.95, 0.90, 0.82]))
            shader.set_vec3(f"lights[{i}].specular", light.get("specular", [1.0, 0.98, 0.90]))
            shader.set_float(f"lights[{i}].constant", light.get("constant", 1.0))
            shader.set_float(f"lights[{i}].linear", light.get("linear", 0.09))
            shader.set_float(f"lights[{i}].quadratic", light.get("quadratic", 0.032))

        for obj in objects:
            model = glm.mat4(1.0)
            model = glm.translate(model, obj.pos)
            model = glm.rotate(model, glm.radians(obj.rot.x), glm.vec3(1, 0, 0))
            model = glm.rotate(model, glm.radians(obj.rot.y), glm.vec3(0, 1, 0))
            model = glm.rotate(model, glm.radians(obj.rot.z), glm.vec3(0, 0, 1))
            model = glm.scale(model, obj.scale)

            shader.set_mat4("model", model)
            shader.set_vec3("material.Ka", obj.material["Ka"])
            shader.set_vec3("material.Kd", obj.material["Kd"])
            shader.set_vec3("material.Ks", obj.material["Ks"])
            shader.set_float("material.shininess", obj.material["shininess"])

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, obj.texture_id)
            shader.set_int("texture_diffuse", 0)
            shader.set_bool("useTexture", use_texture)

            glBindVertexArray(obj.vao)
            glDrawArrays(GL_TRIANGLES, 0, obj.vertex_count)
            glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()