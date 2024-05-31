# 2024年5月30日，我在某天的游戏小屋花了一个半小时手搓了这段解决拼图游戏的代码，从此这个
# 6岁+的游戏再无难度。支持各种不同的拼图形状以及任意高度。只能输出一种正确答案（稍微改动）
# 可以输出所有正确答案。难点在于双重递归，没有对剪枝做任何优化（所以运行贼慢），感兴趣的
# 同学可以自行修改。

NUM_TILES_PER_LAYER = 12
NUM_LAYERS = 3


class Module:
  def __init__(self, shape):
    # shape is a 2D array, representing a module
    self.shape = shape
    self.layers = len(shape)

    max_id = max(map(max, shape))
    invert = []
    for i in range(len(shape) - 1, -1, -1):
      invert.append(list(map(lambda x: max_id - x, shape[i][::-1])))
    # invert is the upside-down representation of `shape`
    self.invert = invert


# These are the modules with circles in the middle. Each layer can and must have
# exactly one circle module.
circle_modules = [
  Module([[0, 1]]),
  Module([[0, 2]]),
  Module([[0, 4]]),
]

# These are the non-circle modules, which can be placed at random.
normal_modules = [
  Module([[0, 1, 2], [1], [1]]),
  Module([[0], [0, 1, 2, 3]]),
  Module([[0, 1], [0, 1, 2]]),
  Module([[0, 1, 2, 3], [2]]),
  Module([[0, 1], [1, 2, 3]]),
  Module([[0], [0, 1, 2], [1]]),
]

# Global state, 0 is empty, 1 is occupied.
global_state = [[0] * NUM_TILES_PER_LAYER for i in range(NUM_LAYERS)]
# Circle status of each layer, 0 is "no circle yet for this layer".
circles = [0] * NUM_LAYERS


def try_to_place(module, invert, layer, offset):
  max_layers_left = NUM_LAYERS - layer
  if module.layers > max_layers_left:
    return False, None

  shape = module.shape
  if invert:
    shape = module.invert
  flipped_tiles = []
  for i in range(module.layers):
    actual_layer = layer + i
    tiles = []
    for j in range(len(shape[i])):
      tile = shape[i][j]
      tile_in_global_state = (tile + offset) % NUM_TILES_PER_LAYER
      if global_state[actual_layer][tile_in_global_state] == 1:
        return False, None
      flipped_tiles.append((actual_layer, tile_in_global_state))
  return True, flipped_tiles


def draw_final_answer(circle_modules, normal_modules):
  ans = [[0] * NUM_TILES_PER_LAYER for i in range(NUM_LAYERS)]
  for i in range(len(circle_modules)):
    shape, x, y = circle_modules[i]
    for j in shape[0]:
      ans[x][(y + j) % NUM_TILES_PER_LAYER] = i
  cur_id = len(circle_modules)
  for m, inv, x, y in normal_modules:
    shape = m.invert if inv else m.shape
    for i in range(len(shape)):
      for j in range(len(shape[i])):
        ans[x + i][(y + shape[i][j]) % NUM_TILES_PER_LAYER] = cur_id
    cur_id += 1
  for line in ans:
    print(' '.join(map(str, line)))


def normal_module_helper(next_module_id=0, prev_modules=[], circle_modules=[]):
  if next_module_id == len(normal_modules):
    # print("Circle modules: ", circle_modules)
    # print("Normal modules: ", prev_modules)
    draw_final_answer(circle_modules, prev_modules)
    return True
  
  module = normal_modules[next_module_id]
  for i in range(NUM_LAYERS):
    for inv in [False, True]:
      for offset in range(NUM_TILES_PER_LAYER):
        res, tiles = try_to_place(module, inv, i, offset)
        if res:
          for x, y in tiles:
            global_state[x][y] = 1
          if normal_module_helper(next_module_id + 1, prev_modules + [(module, inv, i, offset)], circle_modules):
            return True
          for x, y in tiles:
            global_state[x][y] = 0
  return False


def circle_module_helper(next_circle_module_id=0, prev_modules=[]):
  if next_circle_module_id == NUM_LAYERS:
    return normal_module_helper(0, [], prev_modules)
  next_circle_module = circle_modules[next_circle_module_id]
  for i in range(NUM_LAYERS):
    if circles[i] == 0:
      circles[i] = 1
      for j in range(NUM_TILES_PER_LAYER):
        tiles = next_circle_module.shape[0]
        for t in tiles:
          global_state[i][(t + j) % NUM_TILES_PER_LAYER] = 1
        if circle_module_helper(next_circle_module_id + 1, prev_modules + [(next_circle_module.shape, i, j)]):
          return True
        for t in tiles:
          global_state[i][(t + j) % NUM_TILES_PER_LAYER] = 0
      circles[i] = 0
  return False


if __name__ == '__main__':
  if not circle_module_helper(): print("Impossible to solve this puzzle!")
