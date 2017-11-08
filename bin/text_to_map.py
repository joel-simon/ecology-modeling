from draw import PygameDraw
import numpy as np
import pygame

w, h = (350, int(350 / (8.5/11.0)))

view = PygameDraw(w, h, flip_y=False)
view.start_draw()

# view.draw_text((w//2, h//2), 'F I G U R A T I O N', 75//2, center=True, fontfamily='Oxygen')
view.draw_rect((10, 10, w-20, h-20), (0,0,0), width=10)
view.draw_text((w//2, 50), 'Chimera Corp.', 60, center=True, fontfamily='Oxygen')
view.draw_text((w//2, 200), 'Become your', 40, center=True, fontfamily='Oxygen')
view.draw_text((w//2, 250), 'better self.', 40, center=True, fontfamily='Oxygen')

view.end_draw()
pxarray = pygame.surfarray.array2d(view.surface)
pxarray[pxarray == -256] = 1
# pxarray[10:40, :] = 0

view.hold()
# np.save('figuration.npy', pxarray.astype('uint8'))
# np.save('chimeracorp.npy', pxarray.astype('uint8'))