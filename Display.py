
from DispatcherBot.DBQueries import PlayerDB
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont
from RoomGenerator.AssetManager import SceneryManager, PlayerIconManager
import xlsxwriter
from RoomGenerator.Cell import Cell
from random import randint

class ImageMaker():
    def __init__(self):

        self.PIM = PlayerIconManager()
        self.SM = SceneryManager()

        self.scaling_method = Image.NEAREST
        self.base_tile_size = (10, 10)
        self.animation_frames = 2
        self.animation_length = 300  # ms

        self.fonts = {
            "oryx_single_digit": ImageFont.truetype(os.path.join(self.SM.asset_folder, "Fonts/oryx-simplex.ttf"), 7),
            "oryx_double_digit": ImageFont.truetype(os.path.join(self.SM.asset_folder, "Fonts/oryx-simplex.ttf"), 6)
        }

    def create_base(self, shape):
        """
            Create the unfurnished Room.
            @args:
             - Shape: Size of room
        """
        def draw_grid_reference(canvas, idx, h_or_v):
            draw = ImageDraw.Draw(canvas)
            if h_or_v == "h":
                # A..ZZ
                coords = ((idx+1)*self.base_tile_size[1], 0)
                label = xlsxwriter.utility.xl_col_to_name(idx)
            elif h_or_v == "v":
                # 0..99
                coords = (0, (idx+1)*self.base_tile_size[0])
                label = str(idx)
            else:
                raise ValueError

            if len(label) == 1:
                font_choice = self.fonts["oryx_single_digit"]
            elif len(label) == 2:
                font_choice = self.fonts["oryx_double_digit"]
            else:
                raise NotImplementedError

            draw.text(coords, label, font=font_choice)

        shape = (shape[0] + 1, shape[1] + 1)
        size = (shape[0] * self.base_tile_size[0], shape[1] * self.base_tile_size[1])
        self.canvas = [Image.new("RGBA", size, self.SM.get_background()) for _ in range(self.animation_frames)]
        self.canvas[0].save("background.png")

        for c in self.canvas:
            # Draw Grid Coordinates (A0, etc)
            for x in range(shape[0]):
                draw_grid_reference(c, x, "h")
            for y in range(shape[1]):
                draw_grid_reference(c, y, "v")

    def paintTile(self, cell, y, x):

        # Offset for Grid Index
        x = x+1
        y = y+1 
        if cell.type != Cell.Type.PLAYER:
            display_lookup = {
                Cell.Type.EMPTY: ("dungeon", [(4, 0), (4, 0)]),
                Cell.Type.WALL: ("dungeon", [(0, 0), (0, 0)]),
                Cell.Type.DOOR: ("dungeon", [(0, 1), (0, 1)]),
                Cell.Type.PORTAL: ("dungeon", [(6, 4), (6, 4)]),
                Cell.Type.FIRE: ("dungeon", [(5, 2), (5, 3)]),
                Cell.Type.PLAYER: ("monster", [(1, 0), (1, 4)])
            }
            tile = self.SM.get_tile(cell.type)
        else:
            PDB = PlayerDB()
    
            ico = PDB.get(cell.contentID)["icon"]
            tile = self.PIM.getIcon(ico)

        for canvas_idx, t in enumerate(tile[1]):
            tileset = self.SM.tile_sets[tile[0]]
            offset = tileset["initial_offset"]
            tile_file = tileset["file"]
            spacing = tileset["spacing"]

            # Get Tile
            y_begin = offset[0] + t[0] * (self.base_tile_size[0] + spacing[0])
            y_end = y_begin + self.base_tile_size[0]

            x_begin = offset[1] + t[1] * (self.base_tile_size[1] + spacing[1])
            x_end = x_begin + self.base_tile_size[1]

            tile_area = (x_begin, y_begin, x_end, y_end)
            cropped_t = tile_file.crop(tile_area)

            # Place
            where = (y * self.base_tile_size[0], x * self.base_tile_size[1])

            self.canvas[canvas_idx].paste(cropped_t, where, cropped_t)


    def prepare_for_screen(self, resize=True):
        scale_width = 10
        scale_height = 10
        upscaled_canvas = []
        for f in range(self.animation_frames):
            new_size = (self.canvas[f].size[0] * scale_height, self.canvas[f].size[1] * scale_width)
            upscaled_canvas.append(self.canvas[f].resize(new_size, self.scaling_method))
        return upscaled_canvas

    def save(self):
        canvases = self.prepare_for_screen()
        filename = "TestImage" + str(randint(0, 10000)) + ".gif"
        canvases[0].save(
            filename,
            format="GIF",
            append_images=[c for c in canvases[1:]],
            save_all=True,
            duration=self.animation_length,
            loop=0,
        )
        return filename
