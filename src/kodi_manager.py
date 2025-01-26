import argparse
import subprocess
import traceback

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

    def is_kodi_running(self):
        """
        Check if Kodi is running by sending a JSONRPC.Ping request.

        Returns:
            bool: True if Kodi is running, False otherwise.
        """
        try:
            response = self.send_request("JSONRPC.Ping")
            if response and response.get("result") == "pong":
                return True
        except:  # noqa
            print(f"Is Running Error: {traceback.format_exc()}")
            pass
        print("INFO - Kodi is not responding to JSON-RPC requests.")
        return False

    def get_movies(self):
        response = self.send_request(
            "VideoLibrary.GetMovies", {"properties": ["title"]}
        )
        if response and "result" in response and "movies" in response["result"]:
            return response["result"]["movies"]
        print("INFO - Failed to fetch movies.")
        return []

    def play_content(self, content_id, content_type):
        """
        Play any content on Kodi using its ID and type.

        Args:
            content_id (int): The ID of the content to be played.
            content_type (str): The type of the content (e.g., "movie", "episode", "song", "channel").

        Returns:
            None
        """
        # Mapear o tipo de conteúdo para a propriedade esperada
        item_key = f"{content_type}id"
        params = {"item": {item_key: content_id}}

        # Enviar a solicitação para reproduzir o conteúdo
        response = self.send_request("Player.Open", params)

        # Verificar a resposta
        if response and "result" in response:
            print(f"Playing {content_type} ID {content_id}.")
        else:
            print(f"Failed to play {content_type} ID {content_id}.")

    def get_currently_playing(self):
        """
        Get the ID and type of the currently playing content.

        Returns:
            dict or None: A dictionary containing 'content_id' and 'content_type',
                          or None if no content is playing.
        """
        # Verificar players ativos
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("INFO - No active players.")
            return None

        player_id = response["result"][0]["playerid"]

        # Obter o item sendo atualmente reproduzido
        params = {
            "playerid": player_id,
            "properties": ["type"],  # Pedir apenas o tipo do conteúdo
        }
        response = self.send_request("Player.GetItem", params)

        # Verificar a resposta e retornar o ID e tipo do item
        if response and "result" in response and "item" in response["result"]:
            item = response["result"]["item"]
            if "id" in item and "type" in item:
                return {"content_id": item["id"], "content_type": item["type"]}

        print("INFO - Failed to fetch the currently playing item's ID and type.")
        return None

    def clean_library(self):
        response = self.send_request("VideoLibrary.Clean")
        if response and "result" in response:
            print("INFO - Library cleaned successfully.")
        else:
            print("INFO - Failed to clean the library.")

    def scan_library(self):
        response = self.send_request("VideoLibrary.Scan")
        if response and "result" in response:
            print("INFO - Library scan initiated successfully.")
        else:
            print("INFO - Failed to initiate library scan.")

    def pause(self):
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("INFO - No active players to pause.")
            return

        player_id = response["result"][0]["playerid"]
        params = {"playerid": player_id}
        response = self.send_request("Player.PlayPause", params)
        if response and "result" in response:
            print("INFO - Playback paused/resumed.")
        else:
            print("INFO - Failed to pause/resume playback.")

    def stop(self):
        response = self.send_request("Player.GetActivePlayers")
        if not response or "result" not in response or not response["result"]:
            print("INFO - No active players to stop.")
            return

        player_id = response["result"][0]["playerid"]
        params = {"playerid": player_id}
        response = self.send_request("Player.Stop", params)
        if response and "result" in response:
            print("INFO - Playback stopped.")
        else:
            print("INFO - Failed to stop playback.")

    def quit(self):
        """
        Quit Kodi safely.
        """
        response = self.send_request("Application.Quit")
        if response and "result" in response:
            print("INFO - Kodi is shutting down.")
        else:
            print("INFO - Failed to shut down Kodi.")

    @classmethod
    def open_kodi(cls):
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
        print("INFO - Fetching movies...")
        movies = kodi.get_movies()
        if movies:
            for movie in movies:
                print(f"{movie['movieid']}: {movie['title']}")
        else:
            print("INFO - No movies found.")

    # if args.play_movie is not None:
    #     print(f"Playing movie ID {args.play_movie}...")
    #     kodi.play_movie(args.play_movie)

    if args.current:
        print("INFO - Checking currently playing item...")
        playing_item = kodi.get_currently_playing()
        if playing_item:
            title = playing_item.get("title") or playing_item.get("showtitle")
            print(f"Currently playing: {title}")
        else:
            print("INFO - Kodi is not playing anything.")

    if args.clean_library:
        print("INFO - Cleaning library...")
        kodi.clean_library()

    if args.scan_library:
        print("INFO - Scanning library...")
        kodi.scan_library()

    if args.pause:
        print("INFO - Pausing/resuming playback...")
        kodi.pause()

    if args.stop:
        print("INFO - Stopping playback...")
        kodi.stop()

    if args.quit:
        print("INFO - Shutting down Kodi...")
        kodi.quit()


if __name__ == "__main__":
    main()
