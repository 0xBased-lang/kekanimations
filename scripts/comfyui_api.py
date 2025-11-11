#!/usr/bin/env python3
"""
ComfyUI API Wrapper
Provides clean interface for programmatic workflow execution
"""

import json
import uuid
import time
import urllib.request
import urllib.parse
import websocket
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any


class ComfyUIAPI:
    """ComfyUI REST + WebSocket API wrapper"""

    def __init__(self, server_address: str = "127.0.0.1:8188"):
        """
        Initialize API client

        Args:
            server_address: ComfyUI server address (default: 127.0.0.1:8188)
        """
        self.server_address = server_address
        self.http_url = f"http://{server_address}"
        self.ws_url = f"ws://{server_address}/ws"
        self.client_id = str(uuid.uuid4())
        self.ws = None

    def connect_websocket(self) -> websocket.WebSocket:
        """
        Connect to ComfyUI WebSocket for progress monitoring

        Returns:
            WebSocket connection
        """
        if self.ws is None or not self.ws.connected:
            self.ws = websocket.create_connection(
                f"{self.ws_url}?clientId={self.client_id}",
                timeout=10
            )
        return self.ws

    def close_websocket(self):
        """Close WebSocket connection"""
        if self.ws and self.ws.connected:
            self.ws.close()
            self.ws = None

    def queue_prompt(self, workflow: Dict) -> str:
        """
        Submit workflow to ComfyUI execution queue

        Args:
            workflow: ComfyUI workflow JSON dictionary

        Returns:
            prompt_id for tracking execution
        """
        data = json.dumps({
            "prompt": workflow,
            "client_id": self.client_id
        }).encode('utf-8')

        req = urllib.request.Request(f"{self.http_url}/prompt", data=data)

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())

        return result['prompt_id']

    def track_execution(self, prompt_id: str, timeout: int = 600) -> Tuple[bool, float]:
        """
        Monitor workflow execution via WebSocket

        Args:
            prompt_id: Execution ID to monitor
            timeout: Maximum seconds to wait

        Returns:
            (success: bool, duration: float)
        """
        ws = self.connect_websocket()
        start_time = time.time()

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Execution exceeded {timeout}s timeout")

            try:
                message_str = ws.recv()
                if not isinstance(message_str, str):
                    continue

                message = json.loads(message_str)

                # Check for execution completion
                if message.get('type') == 'executing':
                    data = message.get('data', {})
                    if data.get('node') is None and data.get('prompt_id') == prompt_id:
                        # Execution complete
                        duration = time.time() - start_time
                        return True, duration

            except websocket.WebSocketTimeoutException:
                continue
            except Exception as e:
                print(f"WebSocket error: {e}")
                # Try to reconnect
                self.close_websocket()
                ws = self.connect_websocket()

    def get_history(self, prompt_id: str) -> Dict:
        """
        Retrieve execution history and results

        Args:
            prompt_id: Execution ID

        Returns:
            History dictionary with outputs
        """
        url = f"{self.http_url}/history/{prompt_id}"

        with urllib.request.urlopen(url) as response:
            history = json.loads(response.read())

        return history.get(prompt_id, {})

    def get_output_files(self, prompt_id: str) -> List[Dict[str, Any]]:
        """
        Download generated output files (GIFs/images)

        Args:
            prompt_id: Execution ID

        Returns:
            List of output files with data and metadata
        """
        history = self.get_history(prompt_id)
        outputs = history.get('outputs', {})

        files = []

        for node_id, node_output in outputs.items():
            # Handle GIF outputs (from VHS_VideoCombine)
            if 'gifs' in node_output:
                for gif_info in node_output['gifs']:
                    file_data = self._download_file(
                        gif_info['filename'],
                        gif_info.get('subfolder', ''),
                        gif_info.get('type', 'output')
                    )

                    files.append({
                        'data': file_data,
                        'filename': gif_info['filename'],
                        'node_id': node_id,
                        'type': 'gif'
                    })

            # Handle image outputs
            if 'images' in node_output:
                for img_info in node_output['images']:
                    file_data = self._download_file(
                        img_info['filename'],
                        img_info.get('subfolder', ''),
                        img_info.get('type', 'output')
                    )

                    files.append({
                        'data': file_data,
                        'filename': img_info['filename'],
                        'node_id': node_id,
                        'type': 'image'
                    })

        return files

    def _download_file(self, filename: str, subfolder: str = '', file_type: str = 'output') -> bytes:
        """
        Download file from ComfyUI output directory

        Args:
            filename: File to download
            subfolder: Subfolder path
            file_type: File type (output, input, temp)

        Returns:
            File data as bytes
        """
        params = {
            'filename': filename,
            'subfolder': subfolder,
            'type': file_type
        }

        url = f"{self.http_url}/view?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(url) as response:
            return response.read()

    def get_system_stats(self) -> Dict:
        """
        Get ComfyUI system statistics

        Returns:
            System stats dictionary
        """
        url = f"{self.http_url}/system_stats"

        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())

    def upload_image(self, image_path: Path) -> str:
        """
        Upload image to ComfyUI input directory

        Args:
            image_path: Path to image file

        Returns:
            Uploaded filename
        """
        import mimetypes

        with open(image_path, 'rb') as f:
            image_data = f.read()

        boundary = str(uuid.uuid4())

        # Build multipart form data
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'
            f'Content-Type: {mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"}\r\n'
            f'\r\n'
        ).encode() + image_data + f'\r\n--{boundary}--\r\n'.encode()

        req = urllib.request.Request(
            f"{self.http_url}/upload/image",
            data=body,
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())

        return result['name']


def modify_workflow_params(workflow: Dict, params: Dict) -> Dict:
    """
    Modify ComfyUI workflow parameters

    Args:
        workflow: Original workflow dictionary
        params: Parameters to modify

    Supported parameters:
        - input_image: str (Node 1: LoadImage)
        - positive_prompt: str (Node 3: CLIPTextEncode)
        - negative_prompt: str (Node 4: CLIPTextEncode)
        - seed: int (Node 8: KSampler)
        - steps: int (Node 8: KSampler)
        - cfg_scale: float (Node 8: KSampler)
        - denoise: float (Node 8: KSampler)
        - sampler: str (Node 8: KSampler)
        - scheduler: str (Node 8: KSampler)
        - motion_scale: float (Node 6: AnimateDiff)
        - context_length: int (Node 6: AnimateDiff)

    Returns:
        Modified workflow dictionary
    """
    import copy
    modified = copy.deepcopy(workflow)

    # Node 1: LoadImage
    if "input_image" in params and "1" in modified:
        modified["1"]["inputs"]["image"] = params["input_image"]

    # Node 3: Positive prompt
    if "positive_prompt" in params and "3" in modified:
        modified["3"]["inputs"]["text"] = params["positive_prompt"]

    # Node 4: Negative prompt
    if "negative_prompt" in params and "4" in modified:
        modified["4"]["inputs"]["text"] = params["negative_prompt"]

    # Node 8: KSampler parameters
    if "8" in modified:
        ksampler = modified["8"]["inputs"]

        if "seed" in params:
            ksampler["seed"] = int(params["seed"])
        if "steps" in params:
            ksampler["steps"] = int(params["steps"])
        if "cfg_scale" in params:
            ksampler["cfg"] = float(params["cfg_scale"])
        if "denoise" in params:
            ksampler["denoise"] = float(params["denoise"])
        if "sampler" in params:
            ksampler["sampler_name"] = params["sampler"]
        if "scheduler" in params:
            ksampler["scheduler"] = params["scheduler"]

    # Node 6: AnimateDiff parameters
    if "6" in modified:
        animatediff = modified["6"]["inputs"]

        if "motion_scale" in params:
            animatediff["motion_scale"] = float(params["motion_scale"])

        if "context_length" in params and "context_options" in animatediff:
            animatediff["context_options"]["context_length"] = int(params["context_length"])

    return modified


def load_workflow(workflow_path: Path) -> Dict:
    """
    Load ComfyUI workflow from JSON file

    Args:
        workflow_path: Path to workflow JSON

    Returns:
        Workflow dictionary
    """
    with open(workflow_path, 'r') as f:
        return json.load(f)


def save_workflow(workflow: Dict, output_path: Path):
    """
    Save workflow to JSON file

    Args:
        workflow: Workflow dictionary
        output_path: Path to save JSON
    """
    with open(output_path, 'w') as f:
        json.dump(workflow, f, indent=2)


# Example usage
if __name__ == "__main__":
    # Test connection
    api = ComfyUIAPI()

    try:
        stats = api.get_system_stats()
        print("✅ ComfyUI connection successful!")
        print(f"System stats: {stats}")
    except Exception as e:
        print(f"❌ ComfyUI connection failed: {e}")
        print("Make sure ComfyUI is running on http://127.0.0.1:8188")
