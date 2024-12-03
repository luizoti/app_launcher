import argparse
import subprocess

import requests


class KodiJsonRpc:
    def __init__(self, host, port=8080):
        """
        Initialize the Kodi JSON-RPC wrapper.

        Args:
            host (str): The IP address or hostname of the Kodi server.
            port (int): The port number for Kodi's JSON-RPC. Default is 8080.
        """
        self.url = f"http://{host}:{port}/jsonrpc"
        self.headers = {"Content-Type": "application/json"}

    def send_request(self, method, params=None, request_id=1):
        """
        Send a JSON-RPC request to the Kodi server.

        Args:
            method (str): The JSON-RPC method to call.
            params (dict or None): The parameters for the method. Default is None.
            request_id (int): An identifier for the request. Default is 1.

        Returns:
            dict: The JSON response from the Kodi server.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id,
        }
        if params:
            payload["params"] = params

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Kodi: {e}")
            return None

    def get_movies(self):
        response = self.send_request(
            "VideoLibrary.GetMovies", {"properties": ["title"]}
        )
        if response and "result" in response and "movies" in response["result"]:
            return response["result"]["movies"]
        print("Failed to fetch movies.")
        return []

    def play_movie(self, movie_id):
        params = {"item": {"movieid": movie_id}}
        response = self.send_request("Player.Open", params)
        if response and "result" in response:
            print(f"Playing movie ID {movie_id}.")
        else:
            print(f"Failed to play movie ID {movie_id}.")

    def get_currently_playing(self):
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("No active players.")
            return None

        player_id = response["result"][0]["playerid"]
        params = {
            "playerid": player_id,
            "properties": [
                "title",
                "showtitle",
                "season",
                "episode",
                "album",
                "artist",
            ],
        }
        response = self.send_request("Player.GetItem", params)
        if response and "result" in response and "item" in response["result"]:
            return response["result"]["item"]

        print("Failed to fetch currently playing item.")
        return None

    def clean_library(self):
        response = self.send_request("VideoLibrary.Clean")
        if response and "result" in response:
            print("Library cleaned successfully.")
        else:
            print("Failed to clean the library.")

    def scan_library(self):
        response = self.send_request("VideoLibrary.Scan")
        if response and "result" in response:
            print("Library scan initiated successfully.")
        else:
            print("Failed to initiate library scan.")

    def pause(self):
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("No active players to pause.")
            return

        player_id = response["result"][0]["playerid"]
        params = {"playerid": player_id}
        response = self.send_request("Player.PlayPause", params)
        if response and "result" in response:
            print("Playback paused/resumed.")
        else:
            print("Failed to pause/resume playback.")

    def stop(self):
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("No active players to stop.")
            return

        player_id = response["result"][0]["playerid"]
        params = {"playerid": player_id}
        response = self.send_request("Player.Stop", params)
        if response and "result" in response:
            print("Playback stopped.")
        else:
            print("Failed to stop playback.")

    def quit(self):
        """
        Quit Kodi safely.
        """
        response = self.send_request("Application.Quit")
        if response and "result" in response:
            print("Kodi is shutting down.")
        else:
            print("Failed to shut down Kodi.")

    def open_kodi(self):
        result = subprocess.run(
            ["kodi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="Kodi CLI Manager")
    parser.add_argument("host", help="Kodi server IP address")
    parser.add_argument(
        "--list-movies", action="store_true", help="List all movies in the library"
    )
    parser.add_argument("--play-movie", type=int, help="Play a movie by its ID")
    parser.add_argument(
        "--current", action="store_true", help="Show currently playing item"
    )
    parser.add_argument(
        "--clean-library", action="store_true", help="Clean the Kodi library"
    )
    parser.add_argument(
        "--scan-library",
        action="store_true",
        help="Scan the Kodi library for new items",
    )
    parser.add_argument(
        "--pause", action="store_true", help="Pause or resume the current playback"
    )
    parser.add_argument("--stop", action="store_true", help="Stop the current playback")
    parser.add_argument("--quit", action="store_true", help="Quit Kodi safely")

    args = parser.parse_args()
    kodi = KodiJsonRpc(args.host)

    if args.list_movies:
        print("Fetching movies...")
        movies = kodi.get_movies()
        if movies:
            for movie in movies:
                print(f"{movie['movieid']}: {movie['title']}")
        else:
            print("No movies found.")

    if args.play_movie is not None:
        print(f"Playing movie ID {args.play_movie}...")
        kodi.play_movie(args.play_movie)

    if args.current:
        print("Checking currently playing item...")
        playing_item = kodi.get_currently_playing()
        if playing_item:
            title = playing_item.get("title") or playing_item.get("showtitle")
            print(f"Currently playing: {title}")
        else:
            print("Kodi is not playing anything.")

    if args.clean_library:
        print("Cleaning library...")
        kodi.clean_library()

    if args.scan_library:
        print("Scanning library...")
        kodi.scan_library()

    if args.pause:
        print("Pausing/resuming playback...")
        kodi.pause()

    if args.stop:
        print("Stopping playback...")
        kodi.stop()

    if args.quit:
        print("Shutting down Kodi...")
        kodi.quit()


if __name__ == "__main__":
    main()
