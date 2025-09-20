import os

class Config:
    # Bot configuration
    BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID', 0))
    ADMIN_ONLY_DEPLOY = os.getenv('ADMIN_ONLY_DEPLOY', 'False').lower() == 'true'
    
    # Branding configuration
    BRAND_NAME = os.getenv('BRAND_NAME', 'ArizNodes')
    BRAND_COLOR = int(os.getenv('BRAND_COLOR', '0x7289DA'), 16)
    STATUS_MESSAGE = os.getenv('STATUS_MESSAGE', 'ArizNodes Cloud By Vasplayz90 🚀🚀')
    FOOTER_TEXT = os.getenv('FOOTER_TEXT', 'ArizNodes Cloud By Vasplayz90 🚀🚀')
    
    # VPS configuration
    OS_OPTIONS = [
        "Docker",
        "Ubuntu 22.04",
        "Debian 12",
        "CentOS 9",
        "AlmaLinux 9",
        "Rocky Linux 9"
    ]
    
    # Default resource limits
    MAX_RAM = int(os.getenv('MAX_RAM', 64))
    MAX_DISK = int(os.getenv('MAX_DISK', 500))
    MAX_CPU = int(os.getenv('MAX_CPU', 16))
    
    # Tmate configuration (for SSH access simulation)
    TMATE_ENABLED = os.getenv('TMATE_ENABLED', 'True').lower() == 'true'
