from scipy.spatial import KDTree
import osmnx as ox
import os
import numpy as np
import pathlib
from typing import Literal, Dict, Optional
from shapely.geometry import Point
from functools import lru_cache

ox.settings.use_cache = False  # dont cache http requests


class PathFindingError(Exception):
    pass


class TomTom:
    default_speed = {"drive": 30.0, "walk": 3.4, "bike": 17.0}

    def __init__(
        self,
        place_name="Greater London, UK",
        mode: Literal["drive", "walk", "bike"] = "walk",
        speed: Optional[float] = None,
        mock=False,
    ):
        self.mock = mock
        self.speed = self.default_speed[mode] if speed == None else speed
        self.mode = mode
        print(
            f"Initializing TomTom navigator for {place_name} for {mode} mode at {self.speed}"
        )
        if self.mock:
            return
        self.G = None
        self.nodes = None
        self.nodes_kdtree = None

        cache_path = pathlib.Path(__file__).parent.resolve() / "map_cache"
        os.makedirs(cache_path, exist_ok=True)

        # Load or create graph
        cache_file = (
            f"{cache_path}/{place_name.replace(' ', '').lower()}-{mode}.graphml"
        )
        try:
            if os.path.exists(cache_file):
                print("Loading from cache...")
                self.G = ox.load_graphml(cache_file)
                print("Loaded graph from cache")
            else:
                print("Downloading map data...")
                self.G = ox.graph_from_place(
                    place_name, network_type=mode, simplify=True
                )
                print("Saving to cache...")
                ox.save_graphml(self.G, cache_file)

            # Prepare nodes for routing
            self.nodes = ox.graph_to_gdfs(self.G, edges=False)
            node_coords = np.array(
                [[node["y"], node["x"]] for _, node in self.nodes.iterrows()]
            )
            # print(f"Nodes: {(node_coords)}")
            self.nodes_kdtree = KDTree(node_coords)
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise

    @lru_cache(1024)
    def _find_shortest_path(self, start_node, end_node):
        return ox.shortest_path(self.G, start_node, end_node, weight="length")

    def calculate_route(self, start, end):
        start_node = self._find_nearest_node(start)
        end_node = self._find_nearest_node(end)
        # print(f"Start node: {start_node}, End node: {end_node}")
        route = self._find_shortest_path(start_node, end_node)
        if route is None:
            raise PathFindingError(
                f"Failed on {self.mode} with start={start} and end={end}"
            )
        return route

    def calculate_route_time(self, start, end):
        route = self.calculate_route(start, end)
        length = sum(
            self.G.edges[route[i], route[i + 1], 0]["length"]
            for i in range(len(route) - 1)
        )
        if length == 0:
            raise Exception(f"Route length is zero")
        return self.km_to_minutes(length)

    def _find_nearest_node(self, coords: Point):
        """Find the nearest node to given coordinates."""
        try:
            _, index = self.nodes_kdtree.query([coords.y, coords.x], k=1)
            return list(self.nodes.index)[index]
        except Exception as e:
            raise PathFindingError(f"Error finding nearest node {e}")

    def km_to_minutes(self, meters):
        return round((meters * 60 / self.speed) / 1000)

    def euclidean_distance(self, start, end):
        return np.sqrt((start.x - end.x) ** 2 + (start.y - end.y) ** 2)

    def filter_districts_within_time(
        self, workplace_district, districts, max_travel_time
    ):
        filtered_districts = {}
        for district in districts:
            if self.mock:
                travel_time = self.euclidean_distance(
                    Point(
                        districts[district]["longitude"],
                        districts[district]["latitude"],
                    ),
                    Point(
                        districts[workplace_district]["longitude"],
                        districts[workplace_district]["latitude"],
                    ),
                )

                # Convert lng/lat distance to meters using haversine formula
                R = 6371000  # Earth's radius in meters
                lat1 = districts[district]["latitude"]
                lat2 = districts[workplace_district]["latitude"]
                lng1 = districts[district]["longitude"]
                lng2 = districts[workplace_district]["longitude"]

                dlat = np.radians(lat2 - lat1)
                dlng = np.radians(lng2 - lng1)

                a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(
                    np.radians(lat1)
                ) * np.cos(np.radians(lat2)) * np.sin(dlng / 2) * np.sin(dlng / 2)
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                travel_time = R * c  # Distance in meters

                travel_time = self.km_to_minutes(travel_time)
                if travel_time <= max_travel_time:
                    filtered_districts[district] = travel_time
            else:
                travel_time = self.calculate_route_time(
                    Point(
                        districts[district]["longitude"],
                        districts[district]["latitude"],
                    ),
                    Point(
                        districts[workplace_district]["longitude"],
                        districts[workplace_district]["latitude"],
                    ),
                )
                if travel_time <= max_travel_time:
                    filtered_districts[district] = travel_time
        return filtered_districts


if __name__ == "__main__":
    print("Testing TomTom...")
    start = Point(-0.133390, 51.489066)
    end = Point(-0.076819, 51.509551)

    tt_walk = TomTom(mode="walk")
    if True:
        tt_drive = TomTom(mode="drive")
        tt_cycle = TomTom(mode="bike")
        print(f"walk:  {tt_walk.calculate_route_time(start, end)} min\n")
        print(f"drive: {tt_drive.calculate_route_time(start, end)} min\n")
        print(f"cycle: {tt_cycle.calculate_route_time(start, end)} min\n")
    else:
        print(tt_walk.calculate_route_time(start, end))
