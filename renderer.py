from graph import Graph
from intensity import avg_color
from spatial_hash import SpatialHash
from collections.abc import Callable
from PIL import Image
from enum import Enum
import threading


class AntialiasingType(Enum):
    NONE = 1
    SAMPLE_2 = 2
    SAMPLE_4 = 4
    SAMPLE_9 = 9


class Renderer:
    width: int = 100
    height: int = 100
    graph: Graph | None = None
    spatial_hash: SpatialHash | None = None
    line_width: float = 0.3
    thread_count: int = 6
    get_color_sample: Callable[[float, float, Graph, SpatialHash, float], tuple[int, int, int, int]] | None = None
    antialiasing_type: AntialiasingType = AntialiasingType.NONE
    img: Image.Image | None = None

    def __init__(self, thread_count: int = 6, antialiasing_type: AntialiasingType = AntialiasingType.SAMPLE_4):
        self.thread_count = thread_count
        self.antialiasing_type = antialiasing_type
        self.width = 100
        self.height = 100
        self.graph = None
        self.spatial_hash = None
        self.line_width = 0.3
        self.get_color_sample = lambda x, y, g, h, line_width: (0, 0, 0, 255)
        self.img = None

    def set_thread_count(self, value: int):
        self.thread_count = value

    def set_use_antialiasing(self, value: AntialiasingType):
        self.antialiasing_type = value

    def set_color_sample_implementation(
            self,
            f: Callable[[float, float, Graph, SpatialHash, float], tuple[int, int, int, int]]
    ):
        self.get_color_sample = f

    def render(self, width: int, height: int, graph: Graph, spatial_hash: SpatialHash, line_width: float,
               filename: str):
        self.width = width
        self.height = height
        if graph is None:
            raise Exception("Graph is None")
        if spatial_hash is None:
            raise Exception("Spatial hash is None")
        if self.get_color_sample is None:
            raise Exception("You must set a color sample function before rendering")
        self.graph = graph
        self.spatial_hash = spatial_hash
        self.line_width = line_width
        img = Image.new('RGBA', (width, height), color=(0xff, 0xff, 0xff, 0x0))
        self.img = img
        print("Starting  rendering image via thread count: ", self.thread_count)
        threads = []
        for i in range(0, self.thread_count):
            args = (self,  i)
            thread = threading.Thread(target=lambda me, index: me.process_lines(index), args=args)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        print("Done rendering image, saving to: ", filename)
        img.save(filename)
        print("Done!")

    # This is utility function, do not call it on the main
    def process_lines(self, thread_index: int):
        print("Started thread ", thread_index)
        line_width_precision = self.line_width / 2
        for x in range(0, self.width):
            y = thread_index
            while y < self.height:
                x_normal = float(x) / self.width
                y_normal = float(y) / self.height
                color = self._get_average_sample(x_normal, y_normal, line_width_precision)
                self.img.putpixel((x, y), color)
                y = y + self.thread_count
            print("Thread ", thread_index, " done processing ", x)
        print("Finished thread ", thread_index)

    def _get_average_sample(self, x_normal: float, y_normal: float, line_width: float) -> tuple[int, int, int, int]:
        if self.antialiasing_type.value >= AntialiasingType.SAMPLE_4.value:
            samples = []
            # Half pixel on 100 and 0,9 on pixel on 100
            if self.antialiasing_type == AntialiasingType.SAMPLE_4:
                antialiasing_ranges = [0, 0.009]
            else:
                antialiasing_ranges = [0, 0.005, 0.009]
            for x_deviation in antialiasing_ranges:
                for y_deviation in antialiasing_ranges:
                    samples.append(self.get_color_sample(x_normal + x_deviation, y_normal + y_deviation, self.graph,
                                                         self.spatial_hash, line_width))
            return avg_color(samples)
        if self.antializing_type == AntialiaingType.SAMPLE_2:
            value_1 = self.get_color_sample(x_normal, y_normal, self.graph,
                                            self.spatial_hash, line_width)
            value_2 = self.get_color_sample(x_normal + 0.009, y_normal + 0.009, self.graph,
                                            self.spatial_hash, line_width)
            return avg_color([value_1, value_2])
        return self.get_color_sample(x_normal, y_normal, self.graph, self.spatial_hash, line_width)
