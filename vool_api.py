"""API client for Vool integration."""
import logging
import aiohttp
import jwt
import time

_LOGGER = logging.getLogger(__name__)

class VoolAPI:
    """API for interacting with Vool."""

    def __init__(self, email, password, device_id):
        """Initialize the API."""
        self.email = email
        self.password = password
        self.device_id = device_id
        self.token = None
        self.session = None

    async def authenticate(self):
        """Authenticate with the Vool API."""
        token = await self.get_auth_token()
        return token is not None

    async def get_auth_token(self):
        """Get authentication token."""
        url = "https://api.vool.com/v2/auth/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        headers = {'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get('token')
                    return self.token
                else:
                    _LOGGER.error("Failed to get auth token. Status: %s", response.status)
                    return None

    def is_token_expired(self):
        """Check if the token is expired."""
        if not self.token:
            return True
        try:
            payload = jwt.decode(self.token, options={"verify_signature": False})
            exp_time = payload.get('exp')
            if exp_time:
                current_time = time.time()
                return current_time > exp_time
            else:
                return True
        except jwt.DecodeError:
            return True

    async def get_device_status(self):
        """Get device status."""
        if self.is_token_expired():
            await self.get_auth_token()

        if not self.token:
            _LOGGER.error("No valid token available")
            return None

        url = f"https://api.vool.com/v2/devices/{self.device_id}/status"
        headers = {'Authorization': f'Bearer {self.token}'}

        if not self.session:
            self.session = aiohttp.ClientSession()

        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.error("Failed to get device status. Status: %s", response.status)
                return None

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""